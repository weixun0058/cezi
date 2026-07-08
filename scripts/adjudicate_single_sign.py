"""单签综合评定模块（DeepSeek 综合评定）

用途：对指定签号做 DeepSeek 综合评定。
      基于 Gemini 审查报告，对比中文原文（reinterpreted.json）和英文翻译（en.json），
      做出独立的综合评定，并自动应用修改到 en.json。

设计原则：
- 单一职责：只负责综合评定，不负责翻译/解读/Gemini prompt 生成
- 可独立调用：既可作为模块被 reprocess_single_sign.py import，也可直接命令行运行
- 进度可判别：根据现有文件判断当前状态，自动跳过已完成步骤
- 挂起机制：无 Gemini 结果/重大分歧时挂起，交用户评判

使用方式：
  # 作为模块被调用
  from adjudicate_single_sign import adjudicate
  result = adjudicate(sign_number, api_key, sign, interpretation, en_result)

  # 直接命令行运行（续跑模式，自动从现有 JSON 加载数据）
  python scripts/adjudicate_single_sign.py --sign 142
  python scripts/adjudicate_single_sign.py --sign 142 --resume
"""

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# 确保能 import 同目录下的模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

# 复用 translate_oracle_signs 的 API 调用逻辑
from translate_oracle_signs import (
    call_deepseek as call_deepseek_api,
)
from reinterpret_oracle_signs import load_api_key

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger("adjudicate_single_sign")

# 权威文件路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REINTERPRETED_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_reinterpreted.json"
EN_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_en.json"
REVIEW_LOG_DIR = PROJECT_ROOT / "data" / "content" / "_review_log"
ADJUDICATOR_PROMPT = PROJECT_ROOT / "prompts" / "adjudicator_system_prompt.md"

# 7个解读字段（中英共有的解读字段）
INTERPRETATION_FIELDS = ["interpretation1", "career", "wealth",
                         "love", "health", "study", "general"]


# ============================================================================
# 进度判别
# ============================================================================


def detect_review_status(sign_number):
    """检测指定签号的审查进度状态。

    根据现有文件判断当前签走到了哪一步：
    - 无 Gemini 审查结果文件 → "pending_gemini_review"
    - 有 Gemini 审查结果文件，无 adjudication 文件 → "pending_adjudication"
    - 有 adjudication 文件 → "finalized"

    同时检测批量文件（如 gemini_review_result_signs_69-80.md 覆盖了 69-80 签）。

    Args:
        sign_number: 签号

    Returns:
        dict: {
            "status": "pending_gemini_review" | "pending_adjudication" | "finalized",
            "gemini_file": Path | None,  # Gemini 审查结果文件路径
            "adjudication_file": Path | None,  # 评定记录文件路径
            "prompt_file": Path | None,  # Gemini prompt 文件路径
        }
    """
    # 检查单签 Gemini 审查结果文件
    single_gemini = REVIEW_LOG_DIR / f"gemini_review_result_sign_{sign_number}.md"
    # 检查批量 Gemini 审查结果文件（如 signs_69-80.md）
    batch_gemini = None
    if REVIEW_LOG_DIR.exists():
        for p in REVIEW_LOG_DIR.glob("gemini_review_result_signs_*.md"):
            m = re.search(r"signs[_\-]?(\d+)[_\-](\d+)", p.name)
            if m:
                start, end = int(m.group(1)), int(m.group(2))
                if start <= sign_number <= end:
                    batch_gemini = p
                    break

    gemini_file = single_gemini if single_gemini.exists() else (
        batch_gemini if batch_gemini and batch_gemini.exists() else None
    )

    # 检查单签 adjudication 文件
    single_adjudication = REVIEW_LOG_DIR / f"adjudication_sign_{sign_number}.md"
    # 检查批量 adjudication 文件
    batch_adjudication = None
    if REVIEW_LOG_DIR.exists():
        for p in REVIEW_LOG_DIR.glob("adjudication_signs_*.md"):
            m = re.search(r"signs[_\-]?(\d+)[_\-](\d+)", p.name)
            if m:
                start, end = int(m.group(1)), int(m.group(2))
                if start <= sign_number <= end:
                    batch_adjudication = p
                    break

    adjudication_file = (
        single_adjudication if single_adjudication.exists() else (
            batch_adjudication if batch_adjudication and batch_adjudication.exists() else None
        )
    )

    # 检查 Gemini prompt 文件
    prompt_file = REVIEW_LOG_DIR / f"gemini_review_prompt_sign_{sign_number}.md"

    if adjudication_file:
        status = "finalized"
    elif gemini_file:
        status = "pending_adjudication"
    else:
        status = "pending_gemini_review"

    return {
        "status": status,
        "gemini_file": gemini_file,
        "adjudication_file": adjudication_file,
        "prompt_file": prompt_file if prompt_file.exists() else None,
    }


# ============================================================================
# 提示词加载与消息构建
# ============================================================================


def load_adjudicator_prompt():
    """读取综合评定系统提示词文件。

    Returns:
        str: 系统提示词文本

    Raises:
        SystemExit: 提示词文件不存在时退出。
    """
    if not ADJUDICATOR_PROMPT.exists():
        LOGGER.error("综合评定提示词文件不存在：%s", ADJUDICATOR_PROMPT)
        raise SystemExit(1)
    return ADJUDICATOR_PROMPT.read_text(encoding="utf-8")


def build_adjudication_message(sign, interpretation, en_result, gemini_review_text):
    """构建 DeepSeek 综合评定的用户消息。

    包含：签号、吉凶/卦属、中文原文、英文翻译、Gemini 审查报告。

    Args:
        sign: 签文数据（含 sign_number/fortune/gua_type/sign_text）
        interpretation: 7 个中文解读字段
        en_result: 英文翻译结果（9 字段）
        gemini_review_text: Gemini 审查报告全文

    Returns:
        str: 用户消息文本
    """
    sign_number = sign["sign_number"]
    lines = [
        f"# 第 {sign_number} 签综合评定任务",
        f"> 签号：{sign_number}",
        f"> 吉凶：{sign['fortune']}",
        f"> 卦属：{sign['gua_type']}",
        "",
        "## 中文原文（reinterpreted.json）",
        "",
        f"**sign_text**：{sign['sign_text']}",
        "",
    ]

    for field in INTERPRETATION_FIELDS:
        lines.append(f"**{field}**：{interpretation.get(field, '')}")
        lines.append("")

    lines.extend([
        "## 英文翻译（en.json）",
        "",
        f"**sign_text**：{en_result.get('sign_text', '')}",
        "",
    ])

    for field in INTERPRETATION_FIELDS:
        lines.append(f"**{field}**：{en_result.get(field, '')}")
        lines.append("")

    lines.extend([
        "## Gemini 审查报告",
        "",
        gemini_review_text,
        "",
        "## 评定要求",
        "",
        "请基于以上信息，逐条核查 Gemini 的指控是否属实，并输出结构化 JSON。",
        "若 Gemini 指控与中文原文不符，判定为幻觉并否决。",
        "若 Gemini 指控属实，给出修改后的完整字段文本。",
        "若出现重大分歧，将 status 设为 pending_user_review。",
        "",
        "请只输出合法 JSON，不要输出其他文本。",
    ])

    return "\n".join(lines)


# ============================================================================
# DeepSeek API 调用与响应解析
# ============================================================================


def call_deepseek_for_adjudication(api_key, system_prompt, user_message):
    """调用 DeepSeek API 做综合评定。

    复用 translate_oracle_signs.call_deepseek 的调用逻辑，
    但使用更大的 timeout（评定结果较长）。

    Args:
        api_key: DeepSeek API key
        system_prompt: 综合评定系统提示词
        user_message: 用户消息（含中英文对照 + Gemini 审查报告）

    Returns:
        str: API 返回的 JSON 文本

    Raises:
        RuntimeError: API 调用失败时抛出。
    """
    return call_deepseek_api(
        api_key, system_prompt, user_message,
        max_retries=3, timeout=300,
    )


def parse_adjudication_response(content):
    """解析 DeepSeek 综合评定返回的 JSON。

    Args:
        content: API 返回的文本

    Returns:
        dict: 评定结果，含字段：
            - sign_number: 签号
            - status: finalized / pending_user_review / pending_gemini_review
            - summary: 摘要
            - gemini_overview: Gemini 评定概述
            - adjudications: 逐条评定列表
            - highlights: 亮点列表
            - pending_reason: 挂起原因

    Raises:
        ValueError: JSON 解析失败或字段缺失时抛出。
    """
    data = None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # 容错：尝试提取首个完整 JSON 对象
        start = content.find("{")
        if start >= 0:
            depth = 0
            for i in range(start, len(content)):
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            data = json.loads(content[start:i+1])
                            break
                        except json.JSONDecodeError:
                            continue

    if data is None:
        raise ValueError(f"无法解析 DeepSeek 评定结果为 JSON：{content[:200]}")

    # 校验必需字段
    if "status" not in data:
        raise ValueError("DeepSeek 评定结果缺少 status 字段")
    if data["status"] not in ("finalized", "pending_user_review", "pending_gemini_review"):
        raise ValueError(f"DeepSeek 评定结果 status 字段非法：{data['status']}")

    if "adjudications" not in data:
        data["adjudications"] = []

    return data


# ============================================================================
# 应用修改到 en.json
# ============================================================================


def apply_adjudication_to_en(sign_number, adjudication):
    """根据 DeepSeek 评定结果，修改 en.json。

    仅应用 verdict=accept 或 verdict=modify 的评定，
    将 modified_text 写入对应字段。

    Args:
        sign_number: 签号
        adjudication: 评定结果 dict

    Returns:
        list: 已修改的字段名列表
    """
    modified_fields = []

    # 读取 en.json
    en_data = json.loads(EN_JSON.read_text(encoding="utf-8"))

    # 找到对应签
    sign_idx = None
    for i, s in enumerate(en_data):
        if s["sign_number"] == sign_number:
            sign_idx = i
            break

    if sign_idx is None:
        raise ValueError(f"en.json 中找不到第 {sign_number} 签")

    # 逐条应用修改
    for adj in adjudication.get("adjudications", []):
        verdict = adj.get("verdict", "")
        field = adj.get("field", "")
        modified_text = adj.get("modified_text", "")

        if verdict in ("accept", "modify") and field and modified_text:
            if field in en_data[sign_idx]:
                old_text = en_data[sign_idx][field]
                en_data[sign_idx][field] = modified_text
                modified_fields.append(field)
                LOGGER.info("  修改字段 %s（verdict=%s）", field, verdict)
                LOGGER.info("    旧：%s", old_text[:80] + "..." if len(old_text) > 80 else old_text)
                LOGGER.info("    新：%s", modified_text[:80] + "..." if len(modified_text) > 80 else modified_text)

    # 写回 en.json
    if modified_fields:
        EN_JSON.write_text(
            json.dumps(en_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        LOGGER.info("en.json 已更新（修改 %d 个字段）", len(modified_fields))
    else:
        LOGGER.info("无需修改 en.json（DeepSeek 评定无 accept/modify 项）")

    return modified_fields


# ============================================================================
# 生成评定记录
# ============================================================================


def generate_adjudication_record(sign, adjudication, modified_fields, gemini_file):
    """生成综合评定记录文件（adjudication_sign_{N}.md）。

    Args:
        sign: 签文数据
        adjudication: DeepSeek 评定结果
        modified_fields: 已修改的字段名列表
        gemini_file: Gemini 审查结果文件路径

    Returns:
        Path: 评定记录文件路径
    """
    sign_number = sign["sign_number"]
    REVIEW_LOG_DIR.mkdir(parents=True, exist_ok=True)
    record_file = REVIEW_LOG_DIR / f"adjudication_sign_{sign_number}.md"

    lines = [
        f"# 第 {sign_number} 签 综合评定记录",
        "",
        f"> 评定时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> Gemini 审查结果：{gemini_file.name if gemini_file else '无'}",
        f"> 评定人：DeepSeek（综合评定）",
        f"> 评定原则：纠偏 Gemini 过度审查，主动否决神经质敏感；语义忠实度以中文原文为准",
        "",
        "## 综合评定",
        "",
        f"- **状态**：{adjudication.get('status', 'unknown')}",
        f"- **摘要**：{adjudication.get('summary', '')}",
        f"- **Gemini 概述**：{adjudication.get('gemini_overview', '')}",
        "",
        "## 逐条评定",
        "",
        "| 字段 | Gemini 指控 | 评定 | 理由 | 处理 |",
        "|---|---|---|---|---|",
    ]

    for adj in adjudication.get("adjudications", []):
        field = adj.get("field", "")
        issue = adj.get("gemini_issue", "").replace("|", "\\|")
        verdict = adj.get("verdict", "")
        reason = adj.get("reason", "").replace("|", "\\|")
        if verdict in ("accept", "modify") and field in modified_fields:
            handling = "已修改"
        elif verdict == "reject":
            handling = "沿用原翻译"
        else:
            handling = "—"
        lines.append(f"| {field} | {issue} | {verdict} | {reason} | {handling} |")

    lines.append("")
    if adjudication.get("highlights"):
        lines.append("## 亮点")
        lines.append("")
        for h in adjudication["highlights"]:
            lines.append(f"- {h}")
        lines.append("")

    if adjudication.get("status") == "pending_user_review":
        lines.append("## 挂起原因")
        lines.append("")
        lines.append(adjudication.get("pending_reason", "（未说明）"))
        lines.append("")
        lines.append("**请用户评判后决定：**")
        lines.append("- 重新翻译")
        lines.append("- 重新审查")
        lines.append("- 手动修改 en.json")
        lines.append("")

    lines.extend([
        "## 状态",
        "",
        f"- **综合评定完成**：{datetime.now().strftime('%Y-%m-%d')}",
        f"- **en.json 已修改**：{'是' if modified_fields else '否'}",
        f"- **修改字段**：{', '.join(modified_fields) if modified_fields else '无'}",
        f"- **状态**：{'定稿' if adjudication.get('status') == 'finalized' else '挂起（待用户评判）'}",
    ])

    record_file.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("评定记录已生成：%s", record_file)

    return record_file


# ============================================================================
# 数据加载（命令行直接运行时使用）
# ============================================================================


def load_sign_from_json(sign_number):
    """从现有 JSON 文件加载签文数据。

    从 reinterpreted.json 和 en.json 读取现有数据，
    用于命令行直接运行模式（不需要 reprocess_single_sign 的翻译结果）。

    Args:
        sign_number: 签号

    Returns:
        tuple: (sign, interpretation, en_result)
            - sign: 含 sign_number/fortune/gua_type/sign_text
            - interpretation: 7 个中文解读字段
            - en_result: 英文翻译结果（9 字段）

    Raises:
        SystemExit: 数据不存在时退出。
    """
    # 从 reinterpreted.json 读取中文数据
    cn_data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))
    cn_sign = None
    for s in cn_data:
        if s["sign_number"] == sign_number:
            cn_sign = s
            break

    if not cn_sign:
        LOGGER.error("reinterpreted.json 中找不到第 %d 签", sign_number)
        raise SystemExit(1)

    sign = {
        "sign_number": sign_number,
        "fortune": cn_sign.get("fortune", ""),
        "gua_type": cn_sign.get("gua_type", ""),
        "sign_text": cn_sign.get("sign_text", ""),
    }

    interpretation = {
        field: cn_sign.get(field, "")
        for field in INTERPRETATION_FIELDS
    }

    # 从 en.json 读取英文数据
    en_data = json.loads(EN_JSON.read_text(encoding="utf-8"))
    en_result = None
    for s in en_data:
        if s["sign_number"] == sign_number:
            en_result = s
            break

    if not en_result:
        LOGGER.error("en.json 中找不到第 %d 签", sign_number)
        raise SystemExit(1)

    LOGGER.info("从现有 JSON 加载第 %d 签数据", sign_number)
    return sign, interpretation, en_result


# ============================================================================
# 主入口：完整评定流程
# ============================================================================


def adjudicate(sign_number, api_key, sign=None, interpretation=None, en_result=None):
    """单签综合评定主入口。

    流程：
    1. 检测 Gemini 审查结果是否存在
       - 不存在 → 挂起，返回 pending 状态
    2. 若 sign/interpretation/en_result 未传入，从 JSON 文件加载
    3. 调 DeepSeek 做综合评定
    4. 解析返回的 JSON
    5. 若 status=finalized → 自动应用修改到 en.json
    6. 若 status=pending_user_review → 挂起，交用户评判
    7. 生成评定记录文件

    Args:
        sign_number: 签号
        api_key: DeepSeek API key
        sign: 签文数据（可选，未传则从 JSON 加载）
        interpretation: 7 个中文解读字段（可选，未传则从 JSON 加载）
        en_result: 英文翻译结果（可选，未传则从 JSON 加载）

    Returns:
        dict: {
            "status": "finalized" | "pending_user_review" | "pending_gemini_review",
            "adjudication": dict | None,
            "modified_fields": list,
            "record_file": Path | None,
            "message": str,
        }
    """
    LOGGER.info("=" * 60)
    LOGGER.info("综合评定第 %d 签", sign_number)
    LOGGER.info("=" * 60)

    # 1. 检测 Gemini 审查结果
    review_status = detect_review_status(sign_number)
    gemini_file = review_status["gemini_file"]

    if not gemini_file:
        msg = (f"Gemini 审查结果文件不存在，无法做综合评定。\n"
               f"请先把 Gemini prompt 贴入 Gemini Studio 审查，\n"
               f"结果存为：data/content/_review_log/gemini_review_result_sign_{sign_number}.md\n"
               f"然后重新运行")
        LOGGER.warning(msg)
        return {
            "status": "pending_gemini_review",
            "adjudication": None,
            "modified_fields": [],
            "record_file": None,
            "message": msg,
        }

    LOGGER.info("Gemini 审查结果文件：%s", gemini_file)
    gemini_review_text = gemini_file.read_text(encoding="utf-8")

    # 2. 若未传入数据，从 JSON 文件加载
    if sign is None or interpretation is None or en_result is None:
        sign, interpretation, en_result = load_sign_from_json(sign_number)

    # 3. 加载综合评定提示词
    adjudicator_prompt = load_adjudicator_prompt()
    LOGGER.info("综合评定提示词已加载（%d 字符）", len(adjudicator_prompt))

    # 4. 构建用户消息
    user_message = build_adjudication_message(sign, interpretation, en_result, gemini_review_text)

    # 5. 调 DeepSeek 做综合评定
    LOGGER.info("调用 DeepSeek 做综合评定...")
    content = call_deepseek_for_adjudication(api_key, adjudicator_prompt, user_message)
    LOGGER.info("API 返回 %d 字符", len(content))

    # 6. 解析返回的 JSON
    try:
        adjudication = parse_adjudication_response(content)
    except ValueError as e:
        LOGGER.error("解析 DeepSeek 评定结果失败：%s", e)
        LOGGER.error("原始返回内容（前500字符）：%s", content[:500])
        return {
            "status": "pending_user_review",
            "adjudication": None,
            "modified_fields": [],
            "record_file": None,
            "message": f"解析 DeepSeek 评定结果失败：{e}",
        }

    LOGGER.info("DeepSeek 评定状态：%s", adjudication.get("status"))
    LOGGER.info("DeepSeek 评定摘要：%s", adjudication.get("summary", ""))

    # 7. 根据 status 处理
    status = adjudication.get("status")

    if status == "pending_user_review":
        # 挂起，交用户评判
        record_file = generate_adjudication_record(
            sign, adjudication, [], gemini_file
        )
        msg = (f"DeepSeek 评定返回 pending_user_review，已挂起。\n"
               f"原因：{adjudication.get('pending_reason', '（未说明）')}\n"
               f"评定记录：{record_file}\n"
               f"请用户评判后决定下一步。")
        LOGGER.warning(msg)
        return {
            "status": "pending_user_review",
            "adjudication": adjudication,
            "modified_fields": [],
            "record_file": record_file,
            "message": msg,
        }

    # status == "finalized"，自动应用修改
    modified_fields = apply_adjudication_to_en(sign_number, adjudication)

    # 8. 生成评定记录
    record_file = generate_adjudication_record(
        sign, adjudication, modified_fields, gemini_file
    )

    LOGGER.info("综合评定完成，状态：%s，修改字段：%s",
                status, modified_fields if modified_fields else "无")

    return {
        "status": status,
        "adjudication": adjudication,
        "modified_fields": modified_fields,
        "record_file": record_file,
        "message": "综合评定完成",
    }


# ============================================================================
# 批量调度
# ============================================================================


def find_pending_adjudication_signs():
    """扫描所有签号，找出待评定的签（pending_adjudication 状态）。

    扫描逻辑：
    1. 遍历 1-384 所有签号
    2. 调用 detect_review_status 判断状态
    3. 收集 status == "pending_adjudication" 的签号
       （即 Gemini 审查结果已存在，但 adjudication 文件不存在）

    Returns:
        list[int]: 待评定的签号列表（按签号升序）
    """
    pending_signs = []
    for sign_number in range(1, 385):
        status = detect_review_status(sign_number)
        if status["status"] == "pending_adjudication":
            pending_signs.append(sign_number)

    return pending_signs


def run_batch():
    """批量综合评定模式。

    流程：
    1. 扫描所有签号，找出 pending_adjudication 状态的签
    2. 若无待评定的签 → 提示并退出
    3. 逐签调用 adjudicate() 处理
       - finalized → 计入成功，继续下一签
       - pending_user_review → 计入挂起，继续下一签
       - pending_gemini_review → 计入跳过（不应出现，因已检测过）
       - 异常 → 计入失败，继续下一签（不中断批量）
    4. 输出批量处理报告

    Returns:
        dict: {
            "total": int,           # 待评定总数
            "finalized": int,       # 成功定稿数
            "pending": int,         # 挂起数
            "failed": int,          # 失败数
            "results": list,        # 每签评定结果列表
            "batch_report": Path,   # 批量报告文件路径
        }
    """
    LOGGER.info("#" * 60)
    LOGGER.info("# 批量综合评定模式启动")
    LOGGER.info("#" * 60)

    # 1. 扫描待评定的签
    pending_signs = find_pending_adjudication_signs()
    if not pending_signs:
        LOGGER.info("没有待评定的签（pending_adjudication 状态）。")
        LOGGER.info("可能的原因：")
        LOGGER.info("  - 所有签已定稿")
        LOGGER.info("  - 还有签未做 Gemini 审查（pending_gemini_review）")
        LOGGER.info("  - 还没有生成 Gemini prompt（需先运行 reprocess_single_sign.py）")
        return {
            "total": 0, "finalized": 0, "pending": 0, "failed": 0,
            "results": [], "batch_report": None,
        }

    LOGGER.info("找到 %d 签待评定：%s",
                len(pending_signs),
                ", ".join(str(n) for n in pending_signs[:10]) +
                ("..." if len(pending_signs) > 10 else ""))
    LOGGER.info("")

    # 2. 加载 API key
    api_key = load_api_key()

    # 3. 逐签评定
    results = []
    finalized_count = 0
    pending_count = 0
    failed_count = 0

    for idx, sign_number in enumerate(pending_signs, 1):
        LOGGER.info("")
        LOGGER.info("=" * 60)
        LOGGER.info("批量进度：%d/%d（第 %d 签）", idx, len(pending_signs), sign_number)
        LOGGER.info("=" * 60)

        try:
            result = adjudicate(sign_number, api_key)
            results.append({
                "sign_number": sign_number,
                "status": result["status"],
                "modified_fields": result["modified_fields"],
                "message": result["message"],
                "record_file": str(result["record_file"]) if result["record_file"] else None,
            })

            if result["status"] == "finalized":
                finalized_count += 1
                LOGGER.info("第 %d 签定稿 ✓", sign_number)
            elif result["status"] == "pending_user_review":
                pending_count += 1
                LOGGER.warning("第 %d 签挂起（待用户评判）", sign_number)
            else:
                failed_count += 1
                LOGGER.error("第 %d 签异常状态：%s", sign_number, result["status"])

        except Exception as e:
            # 不中断批量，记录失败继续下一签
            failed_count += 1
            LOGGER.error("第 %d 签评定失败：%s", sign_number, e)
            results.append({
                "sign_number": sign_number,
                "status": "failed",
                "modified_fields": [],
                "message": str(e),
                "record_file": None,
            })

    # 4. 生成批量报告
    batch_report = generate_batch_report(
        pending_signs, results,
        finalized_count, pending_count, failed_count,
    )

    return {
        "total": len(pending_signs),
        "finalized": finalized_count,
        "pending": pending_count,
        "failed": failed_count,
        "results": results,
        "batch_report": batch_report,
    }


def generate_batch_report(pending_signs, results, finalized_count, pending_count, failed_count):
    """生成批量评定报告文件。

    Args:
        pending_signs: 待评定签号列表
        results: 每签评定结果列表
        finalized_count: 成功定稿数
        pending_count: 挂起数
        failed_count: 失败数

    Returns:
        Path: 报告文件路径
    """
    REVIEW_LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = REVIEW_LOG_DIR / f"batch_adjudication_report_{timestamp}.md"

    lines = [
        "# 批量综合评定报告",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 评定人：DeepSeek（综合评定）",
        "",
        "## 总览",
        "",
        f"- 待评定签数：**{len(pending_signs)}**",
        f"- 成功定稿：**{finalized_count}**",
        f"- 挂起（待用户评判）：**{pending_count}**",
        f"- 失败：**{failed_count}**",
        f"- 成功率：{finalized_count * 100 // len(pending_signs) if pending_signs else 0}%",
        "",
        "## 逐签详情",
        "",
        "| 签号 | 状态 | 修改字段 | 评定记录 | 说明 |",
        "|---|---|---|---|---|",
    ]

    for r in results:
        sign_number = r["sign_number"]
        status = r["status"]
        modified = ", ".join(r["modified_fields"]) if r["modified_fields"] else "无"
        record = r["record_file"]
        if record:
            record_name = Path(record).name
        else:
            record_name = "无"
        message = r["message"].replace("|", "\\|").replace("\n", " ")[:100]
        lines.append(f"| {sign_number} | {status} | {modified} | {record_name} | {message} |")

    lines.append("")
    if pending_count > 0:
        lines.append("## 挂起签列表（待用户评判）")
        lines.append("")
        for r in results:
            if r["status"] == "pending_user_review":
                lines.append(f"- **第 {r['sign_number']} 签**：{r['message'][:200]}")
        lines.append("")

    if failed_count > 0:
        lines.append("## 失败签列表")
        lines.append("")
        for r in results:
            if r["status"] == "failed":
                lines.append(f"- **第 {r['sign_number']} 签**：{r['message']}")
        lines.append("")

    lines.extend([
        "## 后续操作建议",
        "",
    ])
    if pending_count > 0:
        lines.append(f"- 有 {pending_count} 签挂起，请逐签评判后决定：重新翻译 / 重新审查 / 手动修改")
    if failed_count > 0:
        lines.append(f"- 有 {failed_count} 签失败，请检查日志排查原因后重试")
    if finalized_count > 0:
        lines.append(f"- 有 {finalized_count} 签已定稿，如需同步数据库请运行 backfill_reinterpreted_to_db.py")
    lines.append("")

    report_file.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("批量报告已生成：%s", report_file)

    return report_file


# ============================================================================
# 命令行入口
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="综合评定（DeepSeek 综合评定，自动应用修改到 en.json）。\n"
                   "无参数时进入批量模式，自动处理所有待评定的签。"
    )
    parser.add_argument(
        "--sign", type=int, default=None,
        help="要评定的签号（如 --sign 142）。不指定时进入批量模式。"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="续跑模式（单签时使用）：检测当前进度，从断点继续。"
             "若已定稿（adjudication 文件存在），则跳过。"
    )
    args = parser.parse_args()

    start_time = time.time()

    # 无 --sign 参数：进入批量模式
    if args.sign is None:
        batch_result = run_batch()

        elapsed = time.time() - start_time
        LOGGER.info("")
        LOGGER.info("#" * 60)
        LOGGER.info("# 批量综合评定完成")
        LOGGER.info("# 总耗时：%.1f 秒", elapsed)
        LOGGER.info("#" * 60)
        LOGGER.info("")
        LOGGER.info("批量统计：")
        LOGGER.info("  待评定：%d 签", batch_result["total"])
        LOGGER.info("  成功定稿：%d 签", batch_result["finalized"])
        LOGGER.info("  挂起（待用户评判）：%d 签", batch_result["pending"])
        LOGGER.info("  失败：%d 签", batch_result["failed"])
        if batch_result["batch_report"]:
            LOGGER.info("")
            LOGGER.info("批量报告：%s", batch_result["batch_report"])
        if batch_result["finalized"] > 0:
            LOGGER.info("")
            LOGGER.info("已定稿的签如需同步数据库，请运行 backfill_reinterpreted_to_db.py")
        return

    # 单签模式
    sign_number = args.sign
    LOGGER.info("#" * 60)
    LOGGER.info("# 单签综合评定启动")
    LOGGER.info("# 签号：第 %d 签", sign_number)
    if args.resume:
        LOGGER.info("# 模式：续跑（--resume）")
    LOGGER.info("#" * 60)

    # 检测进度
    review_status = detect_review_status(sign_number)
    status = review_status["status"]
    LOGGER.info("当前进度状态：%s", status)
    LOGGER.info("  Gemini 审查文件：%s",
                review_status["gemini_file"].name if review_status["gemini_file"] else "无")
    LOGGER.info("  评定记录文件：%s",
                review_status["adjudication_file"].name if review_status["adjudication_file"] else "无")

    if status == "finalized":
        LOGGER.info("第 %d 签已定稿（adjudication 文件已存在），无需继续。", sign_number)
        LOGGER.info("如需重新评定，请删除对应的 adjudication 文件后再运行。")
        return

    if status == "pending_gemini_review":
        LOGGER.warning("Gemini 审查结果文件不存在，无法做综合评定。")
        LOGGER.info("请按以下步骤操作：")
        if review_status["prompt_file"]:
            LOGGER.info("  1. Gemini prompt 已生成：%s", review_status["prompt_file"])
        else:
            LOGGER.info("  1. 先运行 reprocess_single_sign.py 生成 Gemini prompt")
        LOGGER.info("  2. 把 prompt 贴入 Gemini Studio 审查")
        LOGGER.info("  3. 结果存为：data/content/_review_log/gemini_review_result_sign_%d.md", sign_number)
        LOGGER.info("  4. 重新运行：python scripts/adjudicate_single_sign.py --sign %d", sign_number)
        return

    # status == "pending_adjudication"：Gemini 审查已完成，可以继续评定
    LOGGER.info("Gemini 审查已完成，开始 DeepSeek 综合评定...")

    # 加载 API key
    api_key = load_api_key()

    # 执行综合评定（从现有 JSON 加载数据）
    result = adjudicate(sign_number, api_key)

    elapsed = time.time() - start_time
    LOGGER.info("#" * 60)
    LOGGER.info("# 综合评定流程完成")
    LOGGER.info("# 总耗时：%.1f 秒", elapsed)
    LOGGER.info("#" * 60)
    LOGGER.info("")
    LOGGER.info("评定结果：")
    LOGGER.info("  状态：%s", result["status"])
    if result["modified_fields"]:
        LOGGER.info("  已修改字段：%s", ", ".join(result["modified_fields"]))
    if result["record_file"]:
        LOGGER.info("  评定记录：%s", result["record_file"])
    LOGGER.info("")
    LOGGER.info("说明：%s", result["message"])

    if result["status"] == "pending_user_review":
        LOGGER.info("")
        LOGGER.info("该签已挂起，请用户评判后决定下一步。")
    elif result["status"] == "finalized":
        LOGGER.info("")
        LOGGER.info("该签已定稿。如需同步数据库，请运行 backfill_reinterpreted_to_db.py")


if __name__ == "__main__":
    main()
