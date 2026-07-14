"""Gemini 审查 prompt 构建共享模块。

用途：为单签/批量两种入口提供统一的 Gemini 审查 prompt 生成逻辑。
      数据源为权威 JSON 文件（reinterpreted.json + en.json），不读数据库。

设计原则：
- 单一职责：只负责构建 Gemini 审查 prompt 文本，不负责调用 API/保存文件
- 数据源：权威 JSON（reinterpreted.json + en.json）
- 无副作用：纯函数，不修改任何文件
- 可复用：被 build_gemini_review_prompt.py 和 reprocess_single_sign.py 共同调用
"""

import json
from datetime import datetime
from pathlib import Path

# 权威文件路径（只读）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REINTERPRETED_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_reinterpreted.json"
EN_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_en.json"

# 8 个对照字段（sign_text + 7 个解读字段）
FIELDS = [
    ("sign_text", "签文诗"),
    ("interpretation1", "整体解读"),
    ("career", "事业"),
    ("wealth", "财运"),
    ("love", "情感"),
    ("health", "健康"),
    ("study", "学业"),
    ("general", "总论"),
]


def load_chinese_signs(start, limit):
    """从权威 JSON 读取中文签文。

    Args:
        start: 起始签号
        limit: 读取条数

    Returns:
        list[dict]: 中文签文列表，每签含 sign_number + 8 个字段
    """
    data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))
    end = start + limit - 1
    return [s for s in data if start <= s["sign_number"] <= end]


def load_english_signs(start, limit):
    """从权威 JSON 读取英文签文。

    Args:
        start: 起始签号
        limit: 读取条数

    Returns:
        list[dict]: 英文签文列表
    """
    data = json.loads(EN_JSON.read_text(encoding="utf-8"))
    end = start + limit - 1
    return [s for s in data if start <= s["sign_number"] <= end]


def load_single_sign(sign_number):
    """从权威 JSON 读取单签的中英文数据。

    Args:
        sign_number: 签号

    Returns:
        tuple: (cn_sign, en_sign)
            - cn_sign: 中文签文 dict（含 sign_number + 8字段）
            - en_sign: 英文签文 dict（9字段）
    """
    cn_data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))
    en_data = json.loads(EN_JSON.read_text(encoding="utf-8"))

    cn_sign = next((s for s in cn_data if s["sign_number"] == sign_number), None)
    en_sign = next((s for s in en_data if s["sign_number"] == sign_number), None)

    return cn_sign, en_sign


def build_gemini_review_prompt(cn_signs, en_signs):
    """构建批量 Gemini 审查 prompt（中英对照）。

    Args:
        cn_signs: 中文签文列表
        en_signs: 英文签文列表

    Returns:
        str: 审查 prompt 文本
    """
    lines = []

    # 任务说明
    lines.append("# 翻译质量审核任务")
    lines.append("")
    lines.append("请审核以下诸葛神算签文的英文翻译质量。")
    lines.append(f"共 {len(cn_signs)} 条签文，按签号排列。")
    lines.append("")
    lines.append("## 审核要求")
    lines.append("")
    lines.append("1. 对每条签文，按 System Instructions 中定义的维度评分（A/B/C/D）")
    lines.append("2. 列出问题清单，按严重度排序（Critical > High > Medium > Low）")
    lines.append("3. 指出翻译亮点")
    lines.append("4. 对 Critical 和 High 问题给出具体修改建议")
    lines.append(f"5. 最后给出整体总结：{len(cn_signs)} 条翻译的总体质量、共性问题、优先修改项")
    lines.append("")
    lines.append("## 字段说明")
    lines.append("")
    for en_key, cn_label in FIELDS:
        lines.append(f"- `{en_key}`：{cn_label}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 逐条对照
    cn_map = {s["sign_number"]: s for s in cn_signs}
    en_map = {s["sign_number"]: s for s in en_signs}

    all_nums = sorted(set(cn_map.keys()) | set(en_map.keys()))
    for sn in all_nums:
        cn = cn_map.get(sn)
        en = en_map.get(sn)

        lines.append(f"## 第 {sn} 签")
        lines.append("")

        if cn and en:
            lines.append("### 中文原文")
            lines.append("```json")
            lines.append(json.dumps(cn, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
            lines.append("### 英文翻译")
            lines.append("```json")
            lines.append(json.dumps(en, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
        elif cn and not en:
            lines.append("⚠️ **缺少英文翻译**")
            lines.append("")
            lines.append("### 中文原文")
            lines.append("```json")
            lines.append(json.dumps(cn, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
        elif en and not cn:
            lines.append("⚠️ **缺少中文原文**")
            lines.append("")
            lines.append("### 英文翻译")
            lines.append("```json")
            lines.append(json.dumps(en, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append("")

    # 总结要求
    lines.append("## 整体总结要求")
    lines.append("")
    lines.append("审核完所有签文后，请给出：")
    lines.append("")
    lines.append(f"1. **总体评分**：{len(cn_signs)} 条翻译的平均质量（A/B/C/D）")
    lines.append("2. **共性问题**：多条签文反复出现的问题")
    lines.append("3. **优先修改项**：必须修改的 Critical/High 问题清单（按签号排列）")
    lines.append("4. **可接受项**：虽有瑕疵但可接受的翻译，无需立即修改")
    lines.append("5. **建议重译项**：质量过差需要重新翻译的签号")
    lines.append("")

    return "\n".join(lines)


def build_single_sign_prompt(sign_number, cn_sign, en_sign):
    """构建单签 Gemini 审查 prompt。

    Args:
        sign_number: 签号
        cn_sign: 中文签文 dict（含 8 个字段）
        en_sign: 英文签文 dict（9字段）

    Returns:
        str: 单签审查 prompt 文本
    """
    lines = [
        f"# 第 {sign_number} 签 Gemini 审查 prompt",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 签号：{sign_number}",
        "",
        "## 审查任务",
        "请审查以下签文的英文翻译，重点关注：",
        "1. **英文文学性**：sign_text 的英文是否保留诗意、节奏感、押韵（如有）",
        "2. **欧美可理解性**：英文表达是否能让欧美读者理解，有无文化冒犯",
        "3. **语言地道性**：是否符合英语母语表达习惯，有无 Chinglish 痕迹",
        "",
        "## 审查范围说明",
        "- **只审英文质量**，不审语义忠实度（语义忠实度由中文母语模型负责）",
        "- **不需要对比中文原文**判断是否漏译/误译",
        "- **不审占卜硬要素**（方位/五行/时令等是否漏译）",
        "- **不审 will 用法**（will 软化由综合评定环节处理）",
        "- **不审吉凶评级**（favorable/unfavorable 等不是禁止词）",
        "- 禁止过度审查（如禁用 with 等常见词），避免神经质敏感",
        "- sign_text 行数应与中文原文句数大致对应，允许合理合并短句",
        "",
        "## 中英对照",
        "",
    ]

    for field_key, field_name in FIELDS:
        cn_text = cn_sign.get(field_key, "") if cn_sign else ""
        en_text = en_sign.get(field_key, "") if en_sign else ""

        lines.extend(
            [
                f"### {field_name}（{field_key}）",
                "",
                "**中文原文**：",
                cn_text,
                "",
                "**英文翻译**：",
                en_text,
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## 审查输出格式",
            "请按字段逐条给出审查意见：",
            "- 严重问题（Critical）：必须修改",
            "- 改进建议（High/Medium/Low）：可选修改",
            "- 评级（A/B/C）：A=优秀，B=合格，C=需重译",
            "",
        ]
    )

    return "\n".join(lines)
