"""诊断 OpenCC t2s 不识别的异体字。

遍历所有"简体字符数==CSV底本字符数"的签，逐字比对：
  若 t2s(csv字) != 简体字，记录 (csv字, 简体字, s2t(简体字), 签号列表)

输出供人工分类：
  - 异体字（csv字是简体字的繁体异体形式）→ 应保留 csv字，需加入补充映射
  - OCR错误（csv字与简体字无关的误认）→ 应使用 s2t(简体字) 修正
"""

import csv
from collections import defaultdict

from opencc import OpenCC

PUNCTUATION = set('，。、；：""' '""' "！？·…—（）()[]【】《》〈〉「」『』 \n\r\t.,;:!?'\"")


def strip_punct(text):
    return "".join(c for c in text if c not in PUNCTUATION)


def main():
    sc = {}
    with open("data/reference/oracle_signs_authoritative_sc.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sc[int(row["sign_number"])] = row["sign_text"]

    csv_raw = {}
    with open("data/reference/original_oracle_signs.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            csv_raw[int(row["sign_number"])] = row["raw_text"].strip()

    s2t = OpenCC("s2t")
    t2s = OpenCC("t2s")

    mismatches = defaultdict(list)  # (csv_char, sc_char) -> [sign_numbers]
    char_count_mismatch = []
    for sn in sorted(sc):
        sc_np = strip_punct(sc[sn])
        csv_np = csv_raw.get(sn, "")
        if len(sc_np) != len(csv_np):
            char_count_mismatch.append((sn, len(sc_np), len(csv_np)))
            continue
        for i, c in enumerate(sc_np):
            tc = csv_np[i]
            if t2s.convert(tc) != c:
                mismatches[(tc, c)].append(sn)

    print(f"字符数不一致的签: {len(char_count_mismatch)}")
    for sn, lsc, lcsv in char_count_mismatch:
        print(f"  第{sn}签: 简体{lsc}字 vs CSV底本{lcsv}字")

    print(f"\nt2s不匹配的字对数: {len(mismatches)}")
    print(f"\n{'csv字':<6}{'简体字':<6}{'s2t(简)':<8}{'出现签号':<40}")
    print("-" * 70)
    for (tc, c), sns in sorted(mismatches.items(), key=lambda x: -len(x[1])):
        s2t_c = s2t.convert(c)
        sns_str = ",".join(str(s) for s in sns[:8]) + (
            f"...(+{len(sns)-8})" if len(sns) > 8 else ""
        )
        print(f"{tc:<6}{c:<6}{s2t_c:<8}{sns_str}  (共{len(sns)}签)")


if __name__ == "__main__":
    main()
