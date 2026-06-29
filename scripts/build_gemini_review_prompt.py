"""
生成 Gemini 翻译审核 prompt。

用途：
  1. 从数据库读取 24 条中文原文
  2. 从 oracle_signs_en_sample.json 读取对应英文翻译
  3. 生成中英对照的审核 prompt，可直接粘贴到 Gemini Studio

使用：
  python scripts/build_gemini_review_prompt.py
  python scripts/build_gemini_review_prompt.py --start 1 --limit 24
  python scripts/build_gemini_review_prompt.py --start 1 --limit 12  # 分批审核

输出：
  data/content/_review_log/gemini_review_prompt.md
"""
import argparse
import json
import sqlite3
from pathlib import Path

# 路径常量
DB_FILE = Path("data/reference/reference.db")
EN_FILE = Path("data/content/oracle_signs_en.json")
OUTPUT_FILE = Path("data/content/_review_log/gemini_review_prompt.md")

# 字段定义
FIELDS = [
    ("fortune", "吉凶等级"),
    ("gua_type", "卦属"),
    ("sign_text", "签文"),
    ("interpretation1", "整体解读"),
    ("career", "事业"),
    ("wealth", "财运"),
    ("love", "情感"),
    ("health", "健康"),
    ("study", "学业"),
    ("general", "泛泛"),
]

# 吉凶等级对照（用于审核参考）
FORTUNE_MAP = {
    "上上签": "Supremely Favorable",
    "上签": "Very Favorable",
    "中上签": "Moderately Favorable",
    "中签": "Neutral",
    "中下签": "Moderately Unfavorable",
    "下签": "Unfavorable",
    "下下签": "Supremely Unfavorable",
}


def fetch_chinese_signs(start: int, limit: int) -> list[dict]:
    """从数据库读取中文签文。"""
    conn = sqlite3.connect(DB_FILE)
    end = start + limit - 1
    rows = conn.execute(
        f"SELECT sign_number, fortune, gua_type, sign_text, interpretation1, "
        f"career, wealth, love, health, study, general "
        f"FROM gua WHERE sign_number BETWEEN ? AND ? ORDER BY sign_number",
        (start, end),
    ).fetchall()
    conn.close()

    keys = ["sign_number"] + [f[0] for f in FIELDS]
    return [dict(zip(keys, row)) for row in rows]


def fetch_english_signs(start: int, limit: int) -> list[dict]:
    """读取英文翻译。"""
    data = json.loads(EN_FILE.read_text(encoding="utf-8"))
    end = start + limit - 1
    return [d for d in data if start <= d["sign_number"] <= end]


def build_review_prompt(cn_signs: list[dict], en_signs: list[dict]) -> str:
    """构建审核 prompt。"""
    lines = []

    # 任务说明
    lines.append("# 翻译质量审核任务")
    lines.append("")
    lines.append("请审核以下诸葛神算签文的中英翻译质量。")
    lines.append(f"共 {len(cn_signs)} 条签文，按签号排列。")
    lines.append("")
    lines.append("## 审核要求")
    lines.append("")
    lines.append("1. 对每条签文，按 System Instructions 中定义的 5 个维度评分（A/B/C/D）")
    lines.append("2. 列出问题清单，按严重度排序（Critical > High > Medium > Low）")
    lines.append("3. 指出翻译亮点")
    lines.append("4. 对 Critical 和 High 问题给出具体修改建议")
    lines.append("5. 最后给出整体总结：24 条翻译的总体质量、共性问题、优先修改项")
    lines.append("")
    lines.append("## 吉凶等级对照（审核参考）")
    lines.append("")
    for cn, en in FORTUNE_MAP.items():
        lines.append(f"- {cn} → {en}")
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
            lines.append(f"⚠️ **缺少英文翻译**")
            lines.append("")
            lines.append("### 中文原文")
            lines.append("```json")
            lines.append(json.dumps(cn, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
        elif en and not cn:
            lines.append(f"⚠️ **缺少中文原文**")
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
    lines.append("1. **总体评分**：24 条翻译的平均质量（A/B/C/D）")
    lines.append("2. **共性问题**：多条签文反复出现的问题（如反思句重复、卦名拼写不一致等）")
    lines.append("3. **优先修改项**：必须修改的 Critical/High 问题清单（按签号排列）")
    lines.append("4. **可接受项**：虽有瑕疵但可接受的翻译，无需立即修改")
    lines.append("5. **建议重译项**：质量过差需要重新翻译的签号")
    lines.append("6. **改进建议**：对翻译提示词或流程的改进建议")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成 Gemini 翻译审核 prompt")
    parser.add_argument("--start", type=int, default=1, help="起始签号（默认 1）")
    parser.add_argument("--limit", type=int, default=24, help="审核条数（默认 24）")
    args = parser.parse_args()

    cn_signs = fetch_chinese_signs(args.start, args.limit)
    en_signs = fetch_english_signs(args.start, args.limit)

    print(f"中文原文：{len(cn_signs)} 条（签号 {args.start}-{args.start + args.limit - 1}）")
    print(f"英文翻译：{len(en_signs)} 条")

    missing_cn = set(s['sign_number'] for s in en_signs) - set(s['sign_number'] for s in cn_signs)
    missing_en = set(s['sign_number'] for s in cn_signs) - set(s['sign_number'] for s in en_signs)
    if missing_cn:
        print(f"⚠️ 缺少中文原文的签号：{sorted(missing_cn)}")
    if missing_en:
        print(f"⚠️ 缺少英文翻译的签号：{sorted(missing_en)}")

    prompt = build_review_prompt(cn_signs, en_signs)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(prompt, encoding="utf-8")

    print(f"\n审核 prompt 已生成：{OUTPUT_FILE}")
    print(f"文件大小：{len(prompt)} 字符")
    print(f"\n使用方法：")
    print(f"1. 打开 https://aistudio.google.com/")
    print(f"2. System instructions 填入：prompts/gemini_review_system_instructions.md 的内容")
    print(f"3. Prompt 填入：{OUTPUT_FILE} 的内容")
    print(f"4. 运行 Gemini，获取审核结果")


if __name__ == "__main__":
    main()
