"""离线生成繁体签文和彭祖百忌 JSON 文件。

用途：
  生成繁体 JSON 供运行时内存加载。
  改签文后的流程：改简体 JSON → 跑本脚本同步繁体 → 重启即生效。

约束：
  OpenCC 只在离线构建脚本使用，运行时不依赖 OpenCC（项目硬约束）。

签文 sign_text 的特殊处理：
  CSV 权威繁体签文（oracle_signs_authoritative_tc.csv）包含异体字，
  不能用 OpenCC s2t 转换（会破坏异体字，如奥→奧、别→別、说→説）。
  因此 sign_text 必须从 CSV 读取，其他字段用 OpenCC s2t 转换。

输入：
  - data/content/oracle_signs_reinterpreted.json（简体签文，9 字段）
  - data/reference/oracle_signs_authoritative_tc.csv（权威繁体签文，仅 sign_text）
  - data/reference/pzbj.json（简体彭祖百忌，{text: explanation}）

输出：
  - data/content/oracle_signs_reinterpreted_hant.json（繁体签文）
  - data/content/pzbj_hant.json（繁体彭祖百忌）
"""

import csv
import json
from pathlib import Path

from opencc import OpenCC

PROJECT = Path(__file__).resolve().parent.parent
SIGNS_SIMP = PROJECT / "data" / "content" / "oracle_signs_reinterpreted.json"
SIGNS_HANT = PROJECT / "data" / "content" / "oracle_signs_reinterpreted_hant.json"
SIGNS_TC_CSV = PROJECT / "data" / "reference" / "oracle_signs_authoritative_tc.csv"
PZBJ_SIMP = PROJECT / "data" / "reference" / "pzbj.json"
PZBJ_HANT = PROJECT / "data" / "content" / "pzbj_hant.json"

# 解签字段用 OpenCC s2t 转换（sign_text 从 CSV 权威取，不转换）
INTERPRETATION_FIELDS = (
    "interpretation1",
    "career",
    "wealth",
    "love",
    "health",
    "study",
    "general",
)


def load_tc_sign_text() -> dict[int, str]:
    """从 CSV 读取权威繁体签文，返回 {sign_number: sign_text}。"""
    tc_text = {}
    with SIGNS_TC_CSV.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            tc_text[int(row["sign_number"])] = row["sign_text"]
    return tc_text


def build_signs_hant(converter: OpenCC) -> int:
    """生成繁体签文 JSON。

    sign_text 从 CSV 权威繁体取（保留异体字）；
    其他字段用 OpenCC s2t 从简体 JSON 转换。
    """
    data = json.loads(SIGNS_SIMP.read_text(encoding="utf-8"))
    tc_sign_text = load_tc_sign_text()
    hant_data = []
    missing_tc = []
    for sign in data:
        sn = sign["sign_number"]
        hant_sign = {"sign_number": sn}
        # sign_text 从 CSV 权威取
        if sn in tc_sign_text:
            hant_sign["sign_text"] = tc_sign_text[sn]
        else:
            hant_sign["sign_text"] = converter.convert(sign.get("sign_text", ""))
            missing_tc.append(sn)
        # 解签字段用 OpenCC s2t 转换
        for field in INTERPRETATION_FIELDS:
            hant_sign[field] = converter.convert(sign.get(field, ""))
        hant_data.append(hant_sign)
    if missing_tc:
        print(f"警告：{len(missing_tc)} 签在 CSV 中缺失，已用 OpenCC 转换: {missing_tc}")
    SIGNS_HANT.write_text(
        json.dumps(hant_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(hant_data)


def build_pzbj_hant(converter: OpenCC) -> int:
    """从简体彭祖百忌 JSON 生成繁体 JSON，返回条数。"""
    data = json.loads(PZBJ_SIMP.read_text(encoding="utf-8"))
    hant_data = {
        converter.convert(text): converter.convert(explanation)
        for text, explanation in data.items()
    }
    PZBJ_HANT.write_text(
        json.dumps(hant_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(hant_data)


def main():
    converter = OpenCC("s2t")
    signs_count = build_signs_hant(converter)
    print(f"已生成繁体签文: {SIGNS_HANT} ({signs_count} 签)")
    pzbj_count = build_pzbj_hant(converter)
    print(f"已生成繁体彭祖百忌: {PZBJ_HANT} ({pzbj_count} 条)")


if __name__ == "__main__":
    main()
