"""比对并同步 gua_hant.sign_text 与权威繁体文本。

权威繁体文本由 generate_authoritative_signs.py 生成（CSV底本+标点转移法，
保留异体字、修正OCR错误）。本脚本直接读取权威繁体 CSV，覆盖数据库
gua_hant.sign_text，使数据库繁体与权威文本一致。

build_reference_db.py 用 OpenCC s2t 自动生成 gua_hant（会标准化异体字），
故重建数据库后必须运行本脚本恢复异体字。
"""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("data/reference/reference.db")
TC_CSV = Path("data/reference/oracle_signs_authoritative_tc.csv")


def load_tc_csv():
    """从权威繁体 CSV 读取签文。"""
    signs = {}
    with open(TC_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            signs[int(row["sign_number"])] = row["sign_text"]
    return signs


def load_db_hant():
    """从数据库读取 gua_hant.sign_text。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT sign_number, sign_text FROM gua_hant ORDER BY sign_number"
        ).fetchall()
        return {row[0]: row[1] for row in rows}
    finally:
        conn.close()


def sync_hant(tc_signs):
    """用权威繁体文本覆盖 gua_hant.sign_text。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        for sn, text in tc_signs.items():
            conn.execute(
                "UPDATE gua_hant SET sign_text = ? WHERE sign_number = ?",
                (text, sn),
            )
        conn.commit()
        return len(tc_signs)
    finally:
        conn.close()


def main():
    tc_signs = load_tc_csv()
    db_hant = load_db_hant()

    print(f"权威繁体签数: {len(tc_signs)}")
    print(f"数据库繁体签数: {len(db_hant)}")

    # 比对差异
    diffs = []
    for sn in sorted(tc_signs):
        if db_hant.get(sn, "") != tc_signs[sn]:
            diffs.append((sn, db_hant.get(sn, ""), tc_signs[sn]))

    print(f"\n差异签数: {len(diffs)}")
    if diffs:
        print("\n=== 差异详情（前20签）===")
        for sn, db_text, csv_text in diffs[:20]:
            print(f"\n第 {sn} 签:")
            print(f"  DB(旧): {db_text}")
            print(f"  权威TC: {csv_text}")
        if len(diffs) > 20:
            print(f"\n... 还有 {len(diffs) - 20} 签差异")

        print(f"\n同步 {len(tc_signs)} 签到 gua_hant...")
        count = sync_hant(tc_signs)
        print(f"已更新 {count} 签")

        # 验证
        db_hant_new = load_db_hant()
        remaining = sum(1 for sn in tc_signs if db_hant_new[sn] != tc_signs[sn])
        print(f"验证: 剩余差异 {remaining} 签")
    else:
        print("无差异，无需同步")


if __name__ == "__main__":
    main()
