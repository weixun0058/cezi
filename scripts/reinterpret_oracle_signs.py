"""诸葛神算中文解签重写脚本（DeepSeek）

用途：从权威 CSV 读取签号/签文诗，调用 DeepSeek API 重新生成
      7 个解读字段（interpretation1/career/wealth/love/health/study/general），
      输出 Markdown 文件供人工审阅 + JSON 文件供程序处理。

背景：现有数据库的解签内容由本地 qwen2.5 4B 生成，质量差（空洞、套话、不贴签）。
      本脚本用 DeepSeek 重新解签，审校确认后再更新数据库。

使用方式：
  1. 确认 .env 文件中有 AI_API_KEY（项目已配置）
  2. 运行：python scripts/reinterpret_oracle_signs.py
  3. 可选参数：--start 1（起始签号）、--limit 24（条数，默认 24）

输出文件：
  - data/content/oracle_signs_reinterpreted.md  （人工审阅）
  - data/content/oracle_signs_reinterpreted.json（程序处理）
  - data/content/_review_log/reinterpret_log.jsonl（运行日志）

特性：
  - 逐条调用（每条签文独立解读，质量更高）
  - 断点续跑（检查 md 文件已有签号，跳过已完成）
  - 失败跳过（某条重试 3 次仍失败，记录错误，继续下一条）
  - 实时写入（每完成一条立即写入，中途崩溃不丢数据）
"""

import argparse
import csv
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger("reinterpret_oracle")

# 路径常量
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE_CSV = PROJECT_ROOT / "data" / "reference" / "oracle_signs_authoritative_sc.csv"
PROMPT_FILE = PROJECT_ROOT / "prompts" / "interpreter_system_prompt.md"
OUTPUT_DIR = PROJECT_ROOT / "data" / "content"
MD_FILE = OUTPUT_DIR / "oracle_signs_reinterpreted.md"
JSON_FILE = OUTPUT_DIR / "oracle_signs_reinterpreted.json"
LOG_DIR = OUTPUT_DIR / "_review_log"
RUN_LOG = LOG_DIR / "reinterpret_log.jsonl"

# DeepSeek API 配置（与项目 .env 一致）
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_MODEL = "deepseek-v4-pro"


def load_api_key():
    """从环境变量或 .env 文件读取 AI_API_KEY。

    Returns:
        str: API key 字符串

    Raises:
        SystemExit: 未找到 API key 时退出并提示。
    """
    api_key = os.environ.get("AI_API_KEY", "").strip()
    if api_key:
        return api_key

    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("AI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip("\"'")
                if api_key:
                    return api_key

    LOGGER.error("未找到 AI_API_KEY。请在 .env 文件中配置。")
    raise SystemExit(1)


def load_system_prompt():
    """读取解签系统提示词文件。

    Returns:
        str: 系统提示词文本
    """
    if not PROMPT_FILE.exists():
        LOGGER.error("系统提示词文件不存在：%s", PROMPT_FILE)
        raise SystemExit(1)
    return PROMPT_FILE.read_text(encoding="utf-8")


def fetch_signs(start: int, limit: int):
    """从权威 CSV 提取签文原始数据（签号/签文诗）。

    CSV 是最权威的源头，仅含 sign_number 和 sign_text 两列。

    Args:
        start: 起始签号（含）
        limit: 提取条数

    Returns:
        list[dict]: 签文字典列表，含 sign_number/sign_text
    """
    if not AUTHORITATIVE_CSV.exists():
        LOGGER.error("权威 CSV 不存在：%s", AUTHORITATIVE_CSV)
        raise SystemExit(1)

    signs = []
    with AUTHORITATIVE_CSV.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sn = int(row["sign_number"])
            if sn >= start:
                signs.append(
                    {
                        "sign_number": sn,
                        "sign_text": row["sign_text"],
                    }
                )
            if len(signs) >= limit:
                break

    LOGGER.info(
        "从权威 CSV 提取 %d 条签文（签号 %d-%d）",
        len(signs),
        start,
        start + len(signs) - 1 if signs else start,
    )
    return signs


def load_completed_sign_numbers():
    """从已有 md 文件中解析已完成的签号，用于断点续跑。

    Returns:
        set[int]: 已完成的签号集合
    """
    if not MD_FILE.exists():
        return set()

    completed = set()
    # 匹配 md 文件中的签号标题，如 "## 第1签" 或 "## 第 1 签"
    pattern = re.compile(r"##\s*第\s*(\d+)\s*签")
    for line in MD_FILE.read_text(encoding="utf-8").splitlines():
        match = pattern.search(line)
        if match:
            completed.add(int(match.group(1)))
    LOGGER.info("已完成签号（断点续跑跳过）：%s", sorted(completed) if completed else "无")
    return completed


def call_deepseek(
    api_key: str, system_prompt: str, user_message: str, max_retries: int = 3, timeout: int = 120
):
    """调用 DeepSeek API 生成解签内容。

    Args:
        api_key: DeepSeek API key
        system_prompt: 系统提示词
        user_message: 用户消息（含签号/吉凶/卦属/签文诗）
        max_retries: 最大重试次数
        timeout: 请求超时秒数

    Returns:
        str: API 返回的文本内容

    Raises:
        RuntimeError: 重试后仍失败时抛出。
    """
    payload = {
        "model": API_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.5,
        "response_format": {"type": "json_object"},
        "max_tokens": 4000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            LOGGER.info("  调用 API（第 %d/%d 次）...", attempt, max_retries)
            req = Request(API_URL, data=data, headers=headers, method="POST")
            with urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                return content
        except HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            LOGGER.warning("  HTTP 错误 %d（第 %d 次）：%s", e.code, attempt, error_body[:200])
        except URLError as e:
            LOGGER.warning("  网络错误（第 %d 次）：%s", attempt, e.reason)
        except (KeyError, json.JSONDecodeError) as e:
            LOGGER.warning("  解析错误（第 %d 次）：%s", attempt, e)

        if attempt < max_retries:
            wait = 3 * attempt
            time.sleep(wait)

    raise RuntimeError(f"API 调用失败，已重试 {max_retries} 次")


def parse_interpretation(content: str):
    """解析 API 返回的 JSON 解签结果。

    Args:
        content: API 返回的文本

    Returns:
        dict: 含 interpretation1/career/wealth/love/health/study/general

    Raises:
        ValueError: JSON 解析失败或字段缺失时抛出。
    """
    # 尝试直接解析
    data = None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # 容错 1：尝试提取首个完整 JSON 对象（处理 Extra data 情况）
        start = content.find("{")
        if start >= 0:
            # 逐个尝试嵌套结束位置，找第一个可解析的对象
            depth = 0
            for i in range(start, len(content)):
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            data = json.loads(content[start : i + 1])
                            break
                        except json.JSONDecodeError:
                            continue
        if data is None:
            # 容错 2：去除尾随逗号后重试
            cleaned = re.sub(r",\s*([}\]])", r"\1", content)
            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError:
                start = cleaned.find("{")
                end = cleaned.rfind("}") + 1
                if start >= 0 and end > start:
                    try:
                        data = json.loads(cleaned[start:end])
                    except json.JSONDecodeError:
                        pass
        if data is None:
            raise ValueError(f"无法解析返回内容为 JSON：{content[:200]}...") from None

    required_fields = ["interpretation1", "career", "wealth", "love", "health", "study", "general"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"返回 JSON 缺少字段：{missing}")

    return {f: data[f] for f in required_fields}


def build_user_message(sign):
    """构建发送给 DeepSeek 的用户消息。

    Args:
        sign: 签文字典，含 sign_number/sign_text

    Returns:
        str: 用户消息文本
    """
    return (
        f"请为以下签文生成完整的中文解读。\n\n"
        f"签号：第{sign['sign_number']}签\n"
        f"签文：{sign['sign_text']}\n\n"
        f"请严格按照系统提示词的风格、字数、文化边界和输出格式要求，"
        f"返回 JSON 对象，包含 interpretation1/career/wealth/love/health/study/general "
        f"七个字段。"
    )


def format_md_section(sign, interpretation):
    """把一条签文及其解读格式化为 Markdown 片段。

    Args:
        sign: 签文原始数据（含 sign_number/sign_text）
        interpretation: 解读字段字典

    Returns:
        str: Markdown 文本
    """
    lines = [
        f"## 第{sign['sign_number']}签",
        "",
        "### 签文",
        sign["sign_text"],
        "",
        "### 解签",
        interpretation["interpretation1"],
        "",
        "### 事业",
        interpretation["career"],
        "",
        "### 财运",
        interpretation["wealth"],
        "",
        "### 情感",
        interpretation["love"],
        "",
        "### 健康",
        interpretation["health"],
        "",
        "### 学业",
        interpretation["study"],
        "",
        "### 泛论",
        interpretation["general"],
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def write_md_header():
    """写入 md 文件头部（仅在文件不存在时创建）。"""
    if MD_FILE.exists():
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    header = (
        f"# 诸葛神算解签重写（DeepSeek）\n\n"
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"> 模型：{API_MODEL}\n"
        f"> 提示词：{PROMPT_FILE.name}\n\n"
        f"---\n\n"
    )
    MD_FILE.write_text(header, encoding="utf-8")


def append_md_section(sign, interpretation):
    """追加一条签文的 Markdown 片段到 md 文件。

    Args:
        sign: 签文原始数据
        interpretation: 解读字段字典
    """
    section = format_md_section(sign, interpretation)
    with MD_FILE.open("a", encoding="utf-8") as f:
        f.write(section)


def update_json_file(results):
    """重写 JSON 文件（每完成一条都重写，保证完整）。

    Args:
        results: 已完成的所有签文结果列表
    """
    JSON_FILE.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_run_log(sign_number, status, detail=""):
    """追加运行日志。

    Args:
        sign_number: 签号
        status: 状态（success/failed）
        detail: 详情
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "sign_number": sign_number,
        "status": status,
        "detail": detail,
    }
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_failed_sign_numbers():
    """从运行日志中提取失败的签号（用于 --retry-failed）。

    只返回最近一次运行中失败的签号（按签号去重，保留最后一次状态）。

    Returns:
        set[int]: 失败的签号集合
    """
    if not RUN_LOG.exists():
        return set()

    # 按签号记录最后一次状态
    last_status = {}
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            sign_number = entry.get("sign_number")
            status = entry.get("status")
            if sign_number and status:
                last_status[sign_number] = status
        except json.JSONDecodeError:
            continue

    failed = {sn for sn, st in last_status.items() if st == "failed"}
    LOGGER.info("从日志中识别失败签号：%s", sorted(failed) if failed else "无")
    return failed


def remove_md_section(sign_number):
    """从 md 文件中移除指定签号的章节（用于重试前清理）。

    Args:
        sign_number: 签号
    """
    if not MD_FILE.exists():
        return

    content = MD_FILE.read_text(encoding="utf-8")
    # 匹配签号章节：从 "## 第N签" 开始到下一个 "## 第" 或文件末尾的 "---"
    pattern = re.compile(
        r"(##\s*第\s*" + str(sign_number) + r"\s*签.*?)(?=\n##\s*第\s*\d+\s*签|\Z)",
        re.DOTALL,
    )
    new_content = pattern.sub("", content)
    if new_content != content:
        MD_FILE.write_text(new_content, encoding="utf-8")
        LOGGER.info("  已从 md 移除第 %d 签旧片段", sign_number)


def remove_json_entry(sign_number, results):
    """从 JSON 结果列表中移除指定签号的条目（用于重试前清理）。

    Args:
        sign_number: 签号
        results: JSON 结果列表（原地修改）

    Returns:
        list: 清理后的结果列表
    """
    before = len(results)
    results[:] = [r for r in results if r.get("sign_number") != sign_number]
    removed = before - len(results)
    if removed:
        LOGGER.info("  已从 json 移除第 %d 签旧条目", sign_number)
    return results


def retry_process(signs, api_key, system_prompt, results):
    """重试失败签号的处理流程。

    每条签文先清理 md 和 json 中的旧片段，再重新调用 API 生成。

    Args:
        signs: 待重试的签文列表
        api_key: API key
        system_prompt: 系统提示词
        results: 已有 JSON 结果列表
    """
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, sign in enumerate(signs, 1):
        sign_number = sign["sign_number"]
        LOGGER.info("[%d/%d] 重试第%d签", i, len(signs), sign_number)

        # 清理旧片段
        remove_md_section(sign_number)
        remove_json_entry(sign_number, results)

        user_message = build_user_message(sign)

        try:
            content = call_deepseek(api_key, system_prompt, user_message)
            interpretation = parse_interpretation(content)

            # 写入 md 和 json
            append_md_section(sign, interpretation)
            results.append({**sign, **interpretation})
            update_json_file(results)
            append_run_log(sign_number, "success")

            success_count += 1
            LOGGER.info("  重试成功（%d 字）", sum(len(v) for v in interpretation.values()))

        except (RuntimeError, ValueError) as e:
            fail_count += 1
            LOGGER.error("  重试失败：%s", e)
            append_run_log(sign_number, "failed", str(e))

        # 避免 API 速率限制
        if i < len(signs):
            time.sleep(1)

    elapsed = time.time() - start_time
    LOGGER.info("=== 重试完成 ===")
    LOGGER.info("成功：%d 条，失败：%d 条，耗时：%.1f 秒", success_count, fail_count, elapsed)
    LOGGER.info("Markdown 文件：%s", MD_FILE)
    LOGGER.info("JSON 文件：%s", JSON_FILE)
    if fail_count > 0:
        LOGGER.warning("仍有 %d 条失败，可再次运行 --retry-failed", fail_count)


def main():
    parser = argparse.ArgumentParser(description="诸葛神算中文解签重写（DeepSeek）")
    parser.add_argument(
        "--start", type=int, default=None, help="起始签号（默认：自动从上次完成位置+1 继续）"
    )
    parser.add_argument("--limit", type=int, default=24, help="解签条数（默认 24）")
    parser.add_argument(
        "--retry-failed", action="store_true", help="重试之前失败的签文（从运行日志中识别）"
    )
    args = parser.parse_args()

    LOGGER.info("=== 诸葛神算解签重写启动 ===")

    if args.retry_failed:
        # 重试失败模式：从日志中找失败签号
        failed_numbers = load_failed_sign_numbers()
        if not failed_numbers:
            LOGGER.info("没有失败签号需要重试，退出。")
            return

        # 加载 API key 和提示词
        api_key = load_api_key()
        LOGGER.info("API key 已加载（前 6 位：%s...）", api_key[:6])
        system_prompt = load_system_prompt()
        LOGGER.info("系统提示词已加载（%d 字符）", len(system_prompt))

        # 从权威 CSV 提取所有失败签号的数据
        all_signs = []
        if AUTHORITATIVE_CSV.exists():
            with AUTHORITATIVE_CSV.open(encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sn = int(row["sign_number"])
                    if sn in failed_numbers:
                        all_signs.append(
                            {
                                "sign_number": sn,
                                "sign_text": row["sign_text"],
                            }
                        )
        all_signs.sort(key=lambda x: x["sign_number"])

        LOGGER.info("待重试签文：%d 条", len(all_signs))

        # 准备输出文件
        write_md_header()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # 加载已有 JSON 结果
        results = []
        if JSON_FILE.exists():
            try:
                results = json.loads(JSON_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                results = []

        # 对失败签号单独处理：从 md 和 json 中移除旧片段，重新生成
        retry_process(all_signs, api_key, system_prompt, results)
        return

    # 自动确定起始签号
    if args.start is None:
        completed = load_completed_sign_numbers()
        if completed:
            args.start = max(completed) + 1
            LOGGER.info("自动从上次完成位置继续：第 %d 签开始", args.start)
        else:
            args.start = 1
            LOGGER.info("无已完成记录，从第 1 签开始")

    LOGGER.info("签号范围：%d-%d", args.start, args.start + args.limit - 1)

    # 1. 加载 API key
    api_key = load_api_key()
    LOGGER.info("API key 已加载（前 6 位：%s...）", api_key[:6])

    # 2. 加载系统提示词
    system_prompt = load_system_prompt()
    LOGGER.info("系统提示词已加载（%d 字符）", len(system_prompt))

    # 3. 提取签文
    signs = fetch_signs(args.start, args.limit)
    if not signs:
        LOGGER.error("未提取到签文，退出")
        raise SystemExit(1)

    # 4. 断点续跑：跳过已完成
    completed = load_completed_sign_numbers()
    pending = [s for s in signs if s["sign_number"] not in completed]
    LOGGER.info("待解签：%d 条（跳过已完成 %d 条）", len(pending), len(signs) - len(pending))

    if not pending:
        LOGGER.info("全部已完成，无需重跑。如需重新生成，请删除 md 文件后再跑。")
        return

    # 5. 准备输出文件
    write_md_header()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 加载已有 JSON 结果（断点续跑时合并）
    results = []
    if JSON_FILE.exists():
        try:
            results = json.loads(JSON_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            results = []

    # 6. 逐条解签
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, sign in enumerate(pending, 1):
        sign_number = sign["sign_number"]
        LOGGER.info("[%d/%d] 第%d签", i, len(pending), sign_number)

        user_message = build_user_message(sign)

        try:
            content = call_deepseek(api_key, system_prompt, user_message)
            interpretation = parse_interpretation(content)

            # 写入 md 和 json
            append_md_section(sign, interpretation)
            results.append({**sign, **interpretation})
            update_json_file(results)
            append_run_log(sign_number, "success")

            success_count += 1
            LOGGER.info("  完成（%d 字）", sum(len(v) for v in interpretation.values()))

        except (RuntimeError, ValueError) as e:
            fail_count += 1
            LOGGER.error("  失败：%s", e)
            append_run_log(sign_number, "failed", str(e))

        # 避免 API 速率限制
        if i < len(pending):
            time.sleep(1)

    elapsed = time.time() - start_time
    LOGGER.info("=== 解签完成 ===")
    LOGGER.info("成功：%d 条，失败：%d 条，耗时：%.1f 秒", success_count, fail_count, elapsed)
    LOGGER.info("Markdown 文件：%s", MD_FILE)
    LOGGER.info("JSON 文件：%s", JSON_FILE)
    LOGGER.info("运行日志：%s", RUN_LOG)
    if fail_count > 0:
        LOGGER.warning("有 %d 条失败，请查看日志后重跑（断点续跑会跳过已成功的）", fail_count)


if __name__ == "__main__":
    main()
