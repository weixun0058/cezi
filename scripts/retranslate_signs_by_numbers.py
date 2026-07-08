"""按签号列表重译英文签文（用于中文原文修正后的定向重译）

用途：从 reference.db 提取指定签号的完整中文签文（9 字段），调用 DeepSeek API
      重译为英文，合并覆盖到 oracle_signs_en.json（按 sign_number 去重，新翻译覆盖旧翻译）。

输入：data/reference/reference.db 的 gua 表（完整 9 字段中文内容）
输出：data/content/oracle_signs_en.json（合并覆盖）+ 翻译日志

使用方式：
  python scripts/retranslate_signs_by_numbers.py
      （默认重译 96 142 146 260 332 —— 因中文权威文本修正导致意义反转的 5 签）

  python scripts/retranslate_signs_by_numbers.py 96 142 146 260 332
      （位置参数指定签号）

  python scripts/retranslate_signs_by_numbers.py --signs-csv 96,142,146,260,332
      （逗号分隔指定签号）

  python scripts/retranslate_signs_by_numbers.py --batch-size 1
      （每批 1 条，最安全但最慢；每签含 9 字段，内容较长）

特性：
  - 复用 translate_oracle_signs.py 的所有核心函数（fetch_signs_by_numbers/call_deepseek/merge_translations/write_output）
  - 按 sign_number 去重合并，新翻译覆盖同号旧翻译，其他签号保留
  - 分批翻译避免 API 响应截断
  - 记录每签成功/失败日志（与 --retry-failed 机制兼容）

背景：这 5 签因 oracle_signs_authoritative_sc.csv 修正导致中文原文意义反转，
      旧英文翻译基于过时中文，必须重译。详见
      data/content/_review_log/english_retranslation_needed_signs.md
"""

import argparse
import sys
import time
from pathlib import Path

# 确保能 import 同目录下的 translate_oracle_signs 模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from translate_oracle_signs import (
    LOGGER,
    load_api_key,
    load_system_prompt,
    fetch_signs_by_numbers,
    call_deepseek,
    parse_translation_response,
    write_output,
    append_run_log,
    build_translate_message,
)

# 默认重译签号：因中文权威文本修正导致意义反转的 5 签
# 详见 data/content/_review_log/english_retranslation_needed_signs.md
DEFAULT_SIGNS = [96, 142, 146, 260, 332]


def main():
    parser = argparse.ArgumentParser(
        description="按签号列表重译英文签文（定向重译，合并覆盖到 oracle_signs_en.json）"
    )
    parser.add_argument(
        "signs", nargs="*", type=int, default=DEFAULT_SIGNS,
        help="要重译的签号列表（空格分隔，默认：96 142 146 260 332）"
    )
    parser.add_argument(
        "--signs-csv", type=str, default=None,
        help="以逗号分隔的签号列表（替代位置参数，如 --signs-csv 96,142,146,260,332）"
    )
    parser.add_argument(
        "--batch-size", type=int, default=2,
        help="每批翻译条数（默认 2，避免 API 响应截断；每签含 9 字段，内容较长）"
    )
    args = parser.parse_args()

    # 确定签号列表（去重升序）
    if args.signs_csv:
        sign_numbers = [int(s.strip()) for s in args.signs_csv.split(",") if s.strip()]
    else:
        sign_numbers = list(args.signs)
    sign_numbers = sorted(set(sign_numbers))

    LOGGER.info("=== 定向重译英文签文启动 ===")
    LOGGER.info("待重译签号 %d 个：%s", len(sign_numbers), sign_numbers)
    LOGGER.info("每批 %d 条", args.batch_size)

    # 1. 加载 API key
    api_key = load_api_key()
    LOGGER.info("API key 已加载（前 6 位：%s...）", api_key[:6])

    # 2. 加载系统提示词
    system_prompt = load_system_prompt()
    LOGGER.info("系统提示词已加载（%d 字符）", len(system_prompt))

    # 3. 从数据库提取完整中文签文（9 字段）
    signs = fetch_signs_by_numbers(sign_numbers)
    if not signs:
        LOGGER.error("未能从数据库提取签文，退出")
        raise SystemExit(1)

    # 验证提取的签号与请求一致
    fetched_numbers = {s["sign_number"] for s in signs}
    missing = set(sign_numbers) - fetched_numbers
    if missing:
        LOGGER.warning("以下签号在数据库中未找到：%s", sorted(missing))

    LOGGER.info("成功提取 %d 条签文", len(signs))

    # 4. 分批翻译
    all_translations = []
    all_source_signs = []
    failed_signs = []
    total_batches = (len(signs) + args.batch_size - 1) // args.batch_size
    start_time = time.time()

    for batch_idx in range(total_batches):
        batch_start = batch_idx * args.batch_size
        batch_end = min(batch_start + args.batch_size, len(signs))
        batch_signs = signs[batch_start:batch_end]
        batch_num = batch_idx + 1
        sn_range = "{}-{}".format(
            batch_signs[0]["sign_number"], batch_signs[-1]["sign_number"]
        )

        LOGGER.info(
            "--- 批次 %d/%d（签号 %s，%d 条）---",
            batch_num, total_batches, sn_range, len(batch_signs)
        )

        user_message = build_translate_message(batch_signs)

        try:
            batch_start_time = time.time()
            content = call_deepseek(api_key, system_prompt, user_message)
            batch_translations = parse_translation_response(content, len(batch_signs))
            all_translations.extend(batch_translations)
            all_source_signs.extend(batch_signs)
            for s in batch_signs:
                append_run_log(s["sign_number"], "success")
            elapsed = time.time() - batch_start_time
            LOGGER.info(
                "批次 %d 完成（%d 条，耗时 %.1f 秒）",
                batch_num, len(batch_translations), elapsed
            )
        except Exception as e:
            LOGGER.error("批次 %d 失败：%s", batch_num, e)
            failed_signs.extend([s["sign_number"] for s in batch_signs])
            for s in batch_signs:
                append_run_log(s["sign_number"], "failed", str(e))

        # 批次间小延迟，避免 API 限流
        if batch_idx < total_batches - 1:
            time.sleep(2)

    elapsed_total = time.time() - start_time
    LOGGER.info("全部批次完成，总耗时 %.1f 秒", elapsed_total)

    # 5. 写入输出（合并覆盖到 oracle_signs_en.json）
    if all_translations:
        write_output(all_translations, all_source_signs)
    else:
        LOGGER.warning("无成功翻译，不写入文件")

    LOGGER.info("=== 重译流程结束 ===")
    LOGGER.info("输出文件：data/content/oracle_signs_en.json")
    LOGGER.info("日志文件：data/content/_review_log/translate_log.jsonl")
    LOGGER.info("成功 %d 条，失败 %d 条", len(all_translations), len(failed_signs))
    if failed_signs:
        LOGGER.warning("失败的签号：%s", failed_signs)
        LOGGER.info("可重新运行本脚本重试失败的签号")
    else:
        LOGGER.info("下一步：用网页版 Gemini 审核重译后的内容")


if __name__ == "__main__":
    main()
