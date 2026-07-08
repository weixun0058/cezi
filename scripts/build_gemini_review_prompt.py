"""生成 Gemini 翻译审核 prompt（批量入口）。

用途：
  1. 从权威 JSON 读取中文原文（reinterpreted.json）
  2. 从权威 JSON 读取对应英文翻译（en.json）
  3. 生成中英对照的审核 prompt，可直接粘贴到 Gemini Studio

数据源（硬约束）：
  - 中文：data/content/oracle_signs_reinterpreted.json（权威）
  - 英文：data/content/oracle_signs_en.json（权威）
  - 不读数据库（reference.db 是派生物，不可靠）

使用：
  python scripts/build_gemini_review_prompt.py
  python scripts/build_gemini_review_prompt.py --start 1 --limit 24
  python scripts/build_gemini_review_prompt.py --start 1 --limit 12  # 分批审核

输出：
  data/content/_review_log/gemini_review_prompt_signs_{start}-{end}.md

注意：基于 D16 硬约束，英文版不含 fortune/gua_type 字段，
      中文原文也只取 9 字段以保持对照一致，避免 Gemini 重复标记已废弃字段。
"""
import argparse

from pathlib import Path

# 确保能 import 同目录下的模块
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gemini_prompt_builder import (
    load_chinese_signs,
    load_english_signs,
    build_gemini_review_prompt,
)

# 输出路径
OUTPUT_DIR = Path("data/content/_review_log")


def main():
    parser = argparse.ArgumentParser(description="生成 Gemini 翻译审核 prompt（批量）")
    parser.add_argument("--start", type=int, default=1, help="起始签号（默认 1）")
    parser.add_argument("--limit", type=int, default=24, help="审核条数（默认 24）")
    args = parser.parse_args()

    end = args.start + args.limit - 1

    # 从权威 JSON 读取数据（不读数据库）
    cn_signs = load_chinese_signs(args.start, args.limit)
    en_signs = load_english_signs(args.start, args.limit)

    print(f"中文原文：{len(cn_signs)} 条（签号 {args.start}-{end}）")
    print(f"英文翻译：{len(en_signs)} 条")
    print(f"数据源：reinterpreted.json + en.json（权威 JSON）")

    missing_cn = set(s["sign_number"] for s in en_signs) - set(s["sign_number"] for s in cn_signs)
    missing_en = set(s["sign_number"] for s in cn_signs) - set(s["sign_number"] for s in en_signs)
    if missing_cn:
        print(f"⚠️ 缺少中文原文的签号：{sorted(missing_cn)}")
    if missing_en:
        print(f"⚠️ 缺少英文翻译的签号：{sorted(missing_en)}")

    # 构建审查 prompt
    prompt = build_gemini_review_prompt(cn_signs, en_signs)

    # 保存到文件
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"gemini_review_prompt_signs_{args.start}-{end}.md"
    output_file.write_text(prompt, encoding="utf-8")

    print(f"\n审核 prompt 已生成：{output_file}")
    print(f"文件大小：{len(prompt)} 字符")
    print(f"\n使用方法：")
    print(f"1. 打开 https://aistudio.google.com/")
    print(f"2. System instructions 填入：prompts/gemini_review_system_instructions.md 的内容")
    print(f"3. Prompt 填入：{output_file} 的内容")
    print(f"4. 运行 Gemini，获取审核结果")
    print(f"5. 结果存为：data/content/_review_log/gemini_review_result_signs_{args.start}-{end}.md")


if __name__ == "__main__":
    main()
