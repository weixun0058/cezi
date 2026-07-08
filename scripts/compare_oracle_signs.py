"""比对 xlsx 简体签文与 csv 考据繁体签文，并分析标点。

数据源：
  - data/reference/zhugeshenshuan_jq.xlsx  简体，有标点（旧版）
  - data/reference/original_oracle_signs.csv  繁体，无标点（考据版）

比对策略（双重比对，过滤异体字噪音）：
  1. 繁体层：xlsx 去标点 → s2t → 与 csv 繁体比对（含异体字差异）
  2. 简体层：csv 去标点 → t2s → 与 xlsx 去标点简体比对（过滤异体字）
  分类：
  - 完全一致：两层都一致
  - 仅异体字：繁体不一致但简体一致
  - 真正差异：简体也不一致（需人工裁定）

标点分析（仅对文字一致的签）：
  - 提取标点位置，统计分段字数
  - 判断是否符合诗句节奏（五言/七言）
"""
import csv
import openpyxl
from opencc import OpenCC
from pathlib import Path
from collections import Counter

XLSX_PATH = Path("data/reference/zhugeshenshuan_jq.xlsx")
CSV_PATH = Path("data/reference/original_oracle_signs.csv")
OUTPUT_PATH = Path("data/reference/signs_comparison.csv")

PUNCTUATION = set('，。、；：""''""''！？·…—（）()[]【】《》〈〉「」『』 \n\r\t.,;:!?\'"')


def strip_punct(text: str) -> str:
    return "".join(c for c in text if c not in PUNCTUATION)


def load_xlsx_signs() -> dict[int, str]:
    """从 xlsx 读取签文（第 4 列）。"""
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True)
    ws = wb["Sheet1"]
    signs = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        sn, text = row[0], row[3]
        if sn is not None and text is not None:
            signs[int(sn)] = str(text).strip()
    wb.close()
    return signs


def load_csv_signs() -> dict[int, str]:
    """从 csv 读取考据签文（raw_text 字段）。"""
    signs = {}
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            signs[int(row["sign_number"])] = row["raw_text"].strip()
    return signs


def find_diffs(a: str, b: str) -> list[str]:
    """逐字比对，返回差异位置列表。"""
    diffs = []
    max_len = max(len(a), len(b))
    for j in range(max_len):
        ca = a[j] if j < len(a) else "<无>"
        cb = b[j] if j < len(b) else "<无>"
        if ca != cb:
            ctx_a = a[max(0, j - 3):j + 4]
            ctx_b = b[max(0, j - 3):j + 4]
            diffs.append(f"pos{j}: xlsx={ca}({ctx_a}) csv={cb}({ctx_b})")
    return diffs


def analyze_punctuation(text: str) -> dict:
    """分析签文标点模式。

    输入：xlsx 原始签文（含标点）
    输出：{segments: [每段字数], punct_positions: [标点位置], punct_types: [标点类型]}
    """
    segments = []
    current_len = 0
    punct_positions = []
    punct_types = []
    for i, c in enumerate(text):
        if c in PUNCTUATION:
            if current_len > 0:
                segments.append(current_len)
            punct_positions.append(i)
            punct_types.append(c)
            current_len = 0
        else:
            current_len += 1
    if current_len > 0:
        segments.append(current_len)
    return {
        "segments": segments,
        "punct_count": len(punct_positions),
        "punct_types": punct_types,
    }


def main():
    xlsx_signs = load_xlsx_signs()
    csv_signs = load_csv_signs()
    s2t = OpenCC("s2t")
    t2s = OpenCC("t2s")

    print(f"xlsx 签数: {len(xlsx_signs)}")
    print(f"csv  签数: {len(csv_signs)}")

    all_sns = sorted(set(xlsx_signs) | set(csv_signs))
    results = []
    real_diffs = []      # 真正文字差异
    variant_diffs = []   # 仅异体字差异

    for sn in all_sns:
        xlsx_text = xlsx_signs.get(sn, "")
        csv_text = csv_signs.get(sn, "")

        xlsx_no_punct = strip_punct(xlsx_text)
        csv_no_punct = strip_punct(csv_text)

        # 繁体层：xlsx 简体→繁体
        xlsx_trad = s2t.convert(xlsx_no_punct)
        trad_match = xlsx_trad == csv_no_punct

        # 简体层：csv 繁体→简体
        csv_simp = t2s.convert(csv_no_punct)
        simp_match = xlsx_no_punct == csv_simp

        # 分类
        if simp_match and trad_match:
            category = "完全一致"
        elif simp_match and not trad_match:
            category = "仅异体字"
            variant_diffs.append(sn)
        else:
            category = "真正差异"
            real_diffs.append(sn)

        diff_detail = "" if simp_match else "; ".join(find_diffs(xlsx_no_punct, csv_simp))

        # 标点分析
        punct_info = analyze_punctuation(xlsx_text)

        results.append({
            "sign_number": sn,
            "category": category,
            "xlsx_text": xlsx_text,
            "csv_text": csv_text,
            "xlsx_simp_no_punct": xlsx_no_punct,
            "csv_simp_no_punct": csv_simp,
            "simp_match": simp_match,
            "trad_match": trad_match,
            "diff_detail": diff_detail,
            "punct_segments": str(punct_info["segments"]),
            "punct_count": punct_info["punct_count"],
        })

    # 写 CSV
    with open(OUTPUT_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sign_number", "category", "simp_match", "trad_match",
            "xlsx_text", "csv_text",
            "xlsx_simp_no_punct", "csv_simp_no_punct",
            "diff_detail", "punct_segments", "punct_count"
        ])
        writer.writeheader()
        writer.writerows(results)

    # 统计
    fully = sum(1 for r in results if r["category"] == "完全一致")
    variant = sum(1 for r in results if r["category"] == "仅异体字")
    real = sum(1 for r in results if r["category"] == "真正差异")
    print(f"\n=== 比对统计 ===")
    print(f"完全一致:   {fully}")
    print(f"仅异体字:   {variant}（繁体字形差异，非真正错误）")
    print(f"真正差异:   {real}（需人工裁定）")
    print(f"全量比对表: {OUTPUT_PATH}")

    # 真正差异详情
    if real_diffs:
        print(f"\n=== 真正文字差异（{len(real_diffs)} 签）===")
        for sn in real_diffs:
            r = next(x for x in results if x["sign_number"] == sn)
            print(f"\n第 {sn} 签:")
            print(f"  xlsx(简): {r['xlsx_simp_no_punct']}")
            print(f"  csv (简): {r['csv_simp_no_punct']}")
            print(f"  差异: {r['diff_detail']}")

    # 标点分析
    print(f"\n=== 标点分析（文字一致的签）===")
    consistent = [r for r in results if r["category"] == "完全一致"]
    seg_patterns = Counter()
    punct_counts = Counter()
    for r in consistent:
        segs = eval(r["punct_segments"])
        seg_patterns[tuple(segs)] += 1
        punct_counts[r["punct_count"]] += 1

    print(f"分析样本: {len(consistent)} 签")
    print(f"\n标点数量分布:")
    for cnt, num in sorted(punct_counts.items()):
        print(f"  {cnt} 个标点: {num} 签")

    print(f"\n分段字数模式（前 15 常见）:")
    for pattern, num in seg_patterns.most_common(15):
        print(f"  {list(pattern)}: {num} 签")


if __name__ == "__main__":
    main()
