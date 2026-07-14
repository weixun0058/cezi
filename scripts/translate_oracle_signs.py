"""Wise Oracle 英文签文翻译脚本（DeepSeek 初译版）

用途：从 oracle_signs_reinterpreted.json 提取中文签文，调用 DeepSeek API 批量翻译为英文。
输入：data/content/oracle_signs_reinterpreted.json（权威中文解读，9 字段）
输出：data/content/oracle_signs_en.json + 翻译日志

使用方式：
  1. 在项目根目录创建 .env 文件，写入 AI_API_KEY=sk-xxxx
  2. 运行：python scripts/translate_oracle_signs.py
     - 不加 --start：自动从上次完成位置+1 继续
     - 加 --start N：从签号 N 开始（用于重译某签会覆盖旧翻译）
  3. 可选参数：--limit 24（默认 24 条）、--batch-size 4（每批条数）
  4. 重试失败：python scripts/translate_oracle_signs.py --retry-failed
     - 从运行日志中识别失败签号，重新分批翻译并覆盖旧结果

特性：
  - 追加模式：新翻译按 sign_number 去重合并到已有文件，不会丢失之前的内容
  - 重译覆盖：显式指定 --start 重译某签时，会替换该签的旧翻译
  - 自动续跑：不加 --start 时，自动从文件中最大签号+1 开始
  - 自动排序：输出文件始终按 sign_number 升序排列
  - 失败重试：--retry-failed 从日志识别失败签号，重新翻译并覆盖

注意：API key 留空时脚本会提示用户填入，不会硬编码。
"""

import argparse
import json
import logging
import os
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
LOGGER = logging.getLogger("translate_oracle")

# 路径常量
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REINTERPRETED_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_reinterpreted.json"
PROMPT_FILE = PROJECT_ROOT / "prompts" / "translator_system_prompt.md"
OUTPUT_DIR = PROJECT_ROOT / "data" / "content"
OUTPUT_FILE = OUTPUT_DIR / "oracle_signs_en.json"
LOG_DIR = OUTPUT_DIR / "_review_log"
TRANSLATE_LOG = LOG_DIR / "translate_log.jsonl"

# DeepSeek API 配置（与项目 .env 一致：AI_API_KEY / deepseek-v4-flash）
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-flash"


def load_api_key():
    """从环境变量或 .env 文件读取 AI_API_KEY（与项目 .env 一致）。

    Returns:
        str: API key 字符串

    Raises:
        SystemExit: 未找到 API key 时退出并提示用户。
    """
    # 优先读环境变量
    api_key = os.environ.get("AI_API_KEY", "").strip()
    if api_key:
        return api_key

    # 尝试从 .env 文件读取
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("AI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip("\"'")
                if api_key:
                    return api_key

    LOGGER.error("未找到 AI_API_KEY。请在 .env 文件中配置 AI_API_KEY。")
    raise SystemExit(1)


def load_system_prompt():
    """读取系统提示词文件。

    Returns:
        str: 系统提示词文本
    """
    if not PROMPT_FILE.exists():
        LOGGER.error("系统提示词文件不存在：%s", PROMPT_FILE)
        raise SystemExit(1)
    return PROMPT_FILE.read_text(encoding="utf-8")


def fetch_signs(start: int, limit: int):
    """从 reinterpreted.json 提取指定范围的中文签文（9 字段）。

    Args:
        start: 起始签号（含）
        limit: 提取条数

    Returns:
        list[dict]: 签文字典列表
    """
    if not REINTERPRETED_JSON.exists():
        LOGGER.error("中文解读文件不存在：%s", REINTERPRETED_JSON)
        raise SystemExit(1)

    data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))
    signs = [s for s in data if s["sign_number"] >= start][:limit]
    LOGGER.info(
        "从 reinterpreted.json 提取 %d 条签文（签号 %d-%d）",
        len(signs),
        start,
        start + len(signs) - 1 if signs else start,
    )
    return signs


def call_deepseek(
    api_key: str, system_prompt: str, user_message: str, max_retries: int = 3, timeout: int = 180
):
    """调用 DeepSeek API 完成翻译。

    Args:
        api_key: DeepSeek API key
        system_prompt: 系统提示词
        user_message: 用户消息（含待翻译签文 JSON）
        max_retries: 最大重试次数
        timeout: 请求超时秒数

    Returns:
        str: API 返回的文本内容

    Raises:
        RuntimeError: 重试后仍失败时抛出。
    """
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "max_tokens": 16000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        LOGGER.info("调用 DeepSeek API（第 %d/%d 次）...", attempt, max_retries)
        try:
            req = Request(DEEPSEEK_API_URL, data=data, headers=headers, method="POST")
            with urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                LOGGER.info("API 调用成功，返回 %d 字符", len(content))
                return content
        except HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            LOGGER.warning("HTTP 错误 %d（第 %d 次）：%s", e.code, attempt, error_body[:200])
        except URLError as e:
            LOGGER.warning("网络错误（第 %d 次）：%s", attempt, e.reason)
        except (KeyError, json.JSONDecodeError) as e:
            LOGGER.warning("解析错误（第 %d 次）：%s", attempt, e)

        if attempt < max_retries:
            wait = 5 * attempt
            LOGGER.info("等待 %d 秒后重试...", wait)
            time.sleep(wait)

    raise RuntimeError(f"DeepSeek API 调用失败，已重试 {max_retries} 次")


def parse_translation_response(content: str, expected_count: int):
    """解析 API 返回的 JSON 翻译结果。

    Args:
        content: API 返回的文本
        expected_count: 期望的签文条数

    Returns:
        list[dict]: 解析后的签文列表

    Raises:
        ValueError: JSON 解析失败或条数不匹配时抛出。
    """
    # 尝试直接解析
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 数组部分
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            data = json.loads(content[start:end])
        else:
            raise ValueError(f"无法解析返回内容为 JSON：{content[:200]}...") from None

    # 兼容两种返回格式：直接数组 或 {"signs": [...]} 或 {"data": [...]}
    if isinstance(data, dict):
        for key in ("signs", "data", "results", "translations"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            raise ValueError(f"返回 JSON 不是数组且无已知字段：{list(data.keys())}")

    if not isinstance(data, list):
        raise ValueError(f"返回 JSON 不是数组：{type(data)}")

    if len(data) != expected_count:
        LOGGER.warning("返回条数 %d 与期望 %d 不一致", len(data), expected_count)

    return data


def load_existing_translations():
    """读取已有的翻译结果文件。

    Returns:
        list[dict]: 已有的翻译列表（按 sign_number 升序）。文件不存在时返回空列表。
    """
    if not OUTPUT_FILE.exists():
        return []
    try:
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        LOGGER.warning("已有文件格式异常（非数组），忽略：%s", OUTPUT_FILE)
        return []
    except json.JSONDecodeError as e:
        LOGGER.warning("已有文件 JSON 解析失败，忽略：%s", e)
        return []


def merge_translations(existing, new_translations):
    """按 sign_number 合并翻译结果（新翻译覆盖旧翻译）。

    Args:
        existing: 已有翻译列表
        new_translations: 本次新翻译列表

    Returns:
        tuple[list[dict], list[int]]: (合并后的列表, 被替换的签号列表)
    """
    existing_map = {t["sign_number"]: t for t in existing if "sign_number" in t}
    replaced = []
    for t in new_translations:
        sn = t.get("sign_number")
        if sn is None:
            continue
        if sn in existing_map:
            replaced.append(sn)
        existing_map[sn] = t
    merged = sorted(existing_map.values(), key=lambda x: x["sign_number"])
    return merged, replaced


def write_output(translations, source_signs):
    """写入翻译结果和日志（追加模式，按 sign_number 去重合并）。

    Args:
        translations: 翻译结果列表
        source_signs: 源签文列表（用于对照记录）
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 读取已有翻译，合并去重
    existing = load_existing_translations()
    before_count = len(existing)
    merged, replaced = merge_translations(existing, translations)
    after_count = len(merged)

    # 写入合并后的翻译结果
    OUTPUT_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    LOGGER.info("翻译结果已写入：%s", OUTPUT_FILE)
    LOGGER.info(
        "合并统计：原有 %d 条，新增 %d 条，替换 %d 条，总计 %d 条",
        before_count,
        len(translations) - len(replaced),
        len(replaced),
        after_count,
    )
    if replaced:
        LOGGER.info("被替换的签号：%s", replaced)

    # 写入翻译日志
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": DEEPSEEK_MODEL,
        "source_count": len(source_signs),
        "output_count": len(translations),
        "source_sign_numbers": [s["sign_number"] for s in source_signs],
        "output_sign_numbers": [t.get("sign_number") for t in translations],
        "replaced_sign_numbers": replaced,
        "total_after_merge": after_count,
    }
    with TRANSLATE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    LOGGER.info("翻译日志已写入：%s", TRANSLATE_LOG)


def append_run_log(sign_number, status, detail=""):
    """追加单签级别的运行日志（用于 --retry-failed 识别失败签号）。

    与批次级日志共存于同一文件，通过 "level": "sign" 字段区分；
    旧的批次级条目无此字段，会被 load_failed_sign_numbers 自动忽略。

    Args:
        sign_number: 签号
        status: 状态（success/failed）
        detail: 详情（失败原因等）
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "sign",
        "sign_number": sign_number,
        "status": status,
        "detail": detail,
    }
    with TRANSLATE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_failed_sign_numbers():
    """从运行日志中提取失败的签号（用于 --retry-failed）。

    按签号去重，保留每个签号最近一次状态；仅识别 "level": "sign" 条目，
    忽略旧的批次级日志。

    Returns:
        set[int]: 失败的签号集合
    """
    if not TRANSLATE_LOG.exists():
        return set()

    last_status = {}
    for line in TRANSLATE_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("level") != "sign":
            continue
        sign_number = entry.get("sign_number")
        status = entry.get("status")
        if sign_number and status:
            last_status[sign_number] = status

    failed = {sn for sn, st in last_status.items() if st == "failed"}
    LOGGER.info("从日志中识别失败签号：%s", sorted(failed) if failed else "无")
    return failed


def fetch_signs_by_numbers(sign_numbers):
    """从 reinterpreted.json 提取指定签号的中文签文（用于重试失败签号）。

    Args:
        sign_numbers: 签号集合/列表

    Returns:
        list[dict]: 签文字典列表（按 sign_number 升序）
    """
    if not sign_numbers:
        return []
    if not REINTERPRETED_JSON.exists():
        LOGGER.error("中文解读文件不存在：%s", REINTERPRETED_JSON)
        raise SystemExit(1)

    data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))
    num_set = set(sign_numbers)
    signs = sorted(
        [s for s in data if s["sign_number"] in num_set],
        key=lambda x: x["sign_number"],
    )
    LOGGER.info("从 reinterpreted.json 提取 %d 条签文", len(signs))
    return signs


def build_translate_message(batch_signs):
    """构建发送给 DeepSeek 的翻译用户消息。

    Args:
        batch_signs: 待翻译签文字典列表

    Returns:
        str: 用户消息文本
    """
    return (
        f"请把以下 {len(batch_signs)} 条中文签文翻译成英文。"
        f"严格按照系统提示词的风格、禁止词、字段规范和输出格式要求。"
        f"返回 JSON 数组，每个元素对应一条签文。\n\n"
        f"待翻译签文：\n"
        f"{json.dumps(batch_signs, ensure_ascii=False, indent=2)}"
    )


def main():
    parser = argparse.ArgumentParser(description="Wise Oracle 英文签文翻译（DeepSeek 初译）")
    parser.add_argument(
        "--start", type=int, default=None, help="起始签号（默认：自动从上次完成位置+1 继续）"
    )
    parser.add_argument("--limit", type=int, default=24, help="翻译条数（默认 24）")
    parser.add_argument(
        "--batch-size", type=int, default=4, help="每批翻译条数（默认 4，避免 API 响应截断）"
    )
    parser.add_argument(
        "--retry-failed", action="store_true", help="重试之前失败的签文（从运行日志中识别）"
    )
    args = parser.parse_args()

    # 重试失败模式：从日志中识别失败签号，重新分批翻译
    if args.retry_failed:
        failed_numbers = load_failed_sign_numbers()
        if not failed_numbers:
            LOGGER.info("没有失败签号需要重试，退出。")
            return

        LOGGER.info("=== Wise Oracle 英文签文翻译（重试失败）启动 ===")
        LOGGER.info("待重试签号 %d 个：%s", len(failed_numbers), sorted(failed_numbers))

        api_key = load_api_key()
        LOGGER.info("API key 已加载（前 6 位：%s...）", api_key[:6])
        system_prompt = load_system_prompt()
        LOGGER.info("系统提示词已加载（%d 字符）", len(system_prompt))

        signs = fetch_signs_by_numbers(failed_numbers)
        if not signs:
            LOGGER.error("未能从 reinterpreted.json 提取失败签文，退出")
            raise SystemExit(1)

        # 复用正常批次翻译流程（重试同样分批，同样记录 per-sign 日志）
        all_translations = []
        all_source_signs = []
        total_batches = (len(signs) + args.batch_size - 1) // args.batch_size
        start_time = time.time()

        for batch_idx in range(total_batches):
            batch_start = batch_idx * args.batch_size
            batch_end = min(batch_start + args.batch_size, len(signs))
            batch_signs = signs[batch_start:batch_end]
            batch_num = batch_idx + 1
            sn_range = f"{batch_signs[0]['sign_number']}-{batch_signs[-1]['sign_number']}"

            LOGGER.info(
                "--- 重试批次 %d/%d（签号 %s，%d 条）---",
                batch_num,
                total_batches,
                sn_range,
                len(batch_signs),
            )

            user_message = build_translate_message(batch_signs)

            try:
                batch_start_time = time.time()
                content = call_deepseek(api_key, system_prompt, user_message)
                batch_translations = parse_translation_response(content, len(batch_signs))
                all_translations.extend(batch_translations)
                all_source_signs.extend(batch_signs)
                # 记录每个签号成功状态（覆盖之前的 failed 状态）
                for s in batch_signs:
                    append_run_log(s["sign_number"], "success")
                elapsed = time.time() - batch_start_time
                LOGGER.info(
                    "重试批次 %d 完成（%d 条，耗时 %.1f 秒）",
                    batch_num,
                    len(batch_translations),
                    elapsed,
                )
            except Exception as e:
                LOGGER.error("重试批次 %d 失败：%s", batch_num, e)
                for s in batch_signs:
                    append_run_log(s["sign_number"], "failed", str(e))

            if batch_idx < total_batches - 1:
                time.sleep(2)

        elapsed_total = time.time() - start_time
        LOGGER.info("重试全部批次完成，总耗时 %.1f 秒", elapsed_total)

        if all_translations:
            write_output(all_translations, all_source_signs)

        LOGGER.info("=== 重试流程结束 ===")
        LOGGER.info("输出文件：%s", OUTPUT_FILE)
        LOGGER.info("日志文件：%s", TRANSLATE_LOG)
        LOGGER.info(
            "成功 %d 条，仍失败 %d 条",
            len(all_translations),
            len(failed_numbers) - len(all_translations),
        )
        if len(all_translations) < len(failed_numbers):
            LOGGER.warning("仍有失败签号，可再次运行 --retry-failed")
        return

    # 自动确定起始签号
    if args.start is None:
        existing = load_existing_translations()
        if existing:
            args.start = max(t["sign_number"] for t in existing) + 1
            LOGGER.info(
                "自动续跑：从已有翻译最大签号 %d 之后开始（起始签号 %d）",
                args.start - 1,
                args.start,
            )
        else:
            args.start = 1
            LOGGER.info("无已有翻译，从第 1 签开始")

    LOGGER.info("=== Wise Oracle 英文签文翻译启动 ===")
    LOGGER.info(
        "签号范围：%d-%d，每批 %d 条", args.start, args.start + args.limit - 1, args.batch_size
    )

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

    # 4. 分批翻译
    all_translations = []
    all_source_signs = []
    failed_batches = []
    total_batches = (len(signs) + args.batch_size - 1) // args.batch_size
    start_time = time.time()

    for batch_idx in range(total_batches):
        batch_start = batch_idx * args.batch_size
        batch_end = min(batch_start + args.batch_size, len(signs))
        batch_signs = signs[batch_start:batch_end]
        batch_num = batch_idx + 1
        sn_range = f"{batch_signs[0]['sign_number']}-{batch_signs[-1]['sign_number']}"

        LOGGER.info(
            "--- 批次 %d/%d（签号 %s，%d 条）---",
            batch_num,
            total_batches,
            sn_range,
            len(batch_signs),
        )

        # 构建用户消息
        user_message = build_translate_message(batch_signs)

        try:
            batch_start_time = time.time()
            content = call_deepseek(api_key, system_prompt, user_message)
            batch_translations = parse_translation_response(content, len(batch_signs))
            all_translations.extend(batch_translations)
            all_source_signs.extend(batch_signs)
            # 记录每个签号成功状态（用于 --retry-failed 识别）
            for s in batch_signs:
                append_run_log(s["sign_number"], "success")
            elapsed = time.time() - batch_start_time
            LOGGER.info(
                "批次 %d 完成（%d 条，耗时 %.1f 秒）", batch_num, len(batch_translations), elapsed
            )
        except Exception as e:
            LOGGER.error("批次 %d 失败：%s", batch_num, e)
            failed_batches.append((batch_num, sn_range, str(e)))
            # 记录每个签号失败状态（用于 --retry-failed 识别）
            for s in batch_signs:
                append_run_log(s["sign_number"], "failed", str(e))

        # 批次间小延迟，避免 API 限流
        if batch_idx < total_batches - 1:
            time.sleep(2)

    elapsed_total = time.time() - start_time
    LOGGER.info("全部批次完成，总耗时 %.1f 秒", elapsed_total)
    if failed_batches:
        LOGGER.warning(
            "失败批次 %d 个：%s",
            len(failed_batches),
            ", ".join(f"批次{b[0]}({b[1]})" for b in failed_batches),
        )

    # 5. 写入输出
    if all_translations:
        write_output(all_translations, all_source_signs)

    LOGGER.info("=== 翻译流程结束 ===")
    LOGGER.info("输出文件：%s", OUTPUT_FILE)
    LOGGER.info("日志文件：%s", TRANSLATE_LOG)
    LOGGER.info("成功 %d 条，失败 %d 条", len(all_translations), args.limit - len(all_translations))
    LOGGER.info("下一步：用网页版 Gemini 审核 %s 的内容", OUTPUT_FILE)


if __name__ == "__main__":
    main()
