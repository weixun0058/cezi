"""把新解签内容从 json 回填到 reference.db 的 gua 和 gua_hant 表。

背景：reinterpret_oracle_signs.py 生成的新解签目前只在
      oracle_signs_reinterpreted.json/md 里，数据库还是旧内容。
      本脚本把 384 签的新解签（7 个字段）更新到数据库。

操作：
  1. 从 json 读取 384 签新解签
  2. 更新 gua 表（简体）的 7 个解签字段
  3. 用 opencc s2t 转换，更新 gua_hant 表（繁体）的 7 个解签字段

注意：只更新解签字段（interpretation1/career/wealth/love/health/study/general），
      不动 fortune/gua_type/sign_text（这些字段由 build_reference_db.py 从权威 CSV 同步，本脚本不负责）。
"""

import json
import sqlite3
from pathlib import Path

from opencc import OpenCC

PROJECT = Path(__file__).resolve().parent.parent
JSON_FILE = PROJECT / "data" / "content" / "oracle_signs_reinterpreted.json"
DB_FILE = PROJECT / "data" / "reference" / "reference.db"

# 需要更新的 7 个解签字段
INTERPRETATION_FIELDS = [
    "interpretation1", "career", "wealth", "love", "health", "study", "general",
]


def main():
    # 1. 读取 json 新解签
    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    print(f"从 json 读取 {len(data)} 签新解签")

    # 2. 初始化 opencc
    converter = OpenCC("s2t")

    # 3. 更新数据库
    conn = sqlite3.connect(DB_FILE)
    try:
        # 检查 gua_hant 表的 CHECK 约束是否已是 1-384
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='gua_hant'"
        ).fetchone()[0]
        if "383" in schema:
            print("警告：gua_hant 表 CHECK 约束仍是 1-383，需要重建表。")
            # 重建 gua_hant 表（CHECK 1-384）
            conn.executescript("""
                CREATE TABLE gua_hant_new (
                    sign_number INTEGER PRIMARY KEY CHECK(sign_number BETWEEN 1 AND 384),
                    fortune TEXT NOT NULL,
                    gua_type TEXT NOT NULL,
                    sign_text TEXT NOT NULL,
                    interpretation1 TEXT NOT NULL,
                    career TEXT NOT NULL,
                    wealth TEXT NOT NULL,
                    love TEXT NOT NULL,
                    health TEXT NOT NULL,
                    study TEXT NOT NULL,
                    general TEXT NOT NULL
                );
                INSERT INTO gua_hant_new SELECT * FROM gua_hant;
                DROP TABLE gua_hant;
                ALTER TABLE gua_hant_new RENAME TO gua_hant;
            """)
            print("已重建 gua_hant 表（CHECK 约束: 1-384）")

        # 更新简体 gua 表
        simp_updated = 0
        for d in data:
            sn = d["sign_number"]
            set_clause = ", ".join(f"{f} = ?" for f in INTERPRETATION_FIELDS)
            values = [d[f] for f in INTERPRETATION_FIELDS] + [sn]
            conn.execute(
                f"UPDATE gua SET {set_clause} WHERE sign_number = ?",
                values,
            )
            simp_updated += 1

        # 更新繁体 gua_hant 表
        hant_updated = 0
        for d in data:
            sn = d["sign_number"]
            set_clause = ", ".join(f"{f} = ?" for f in INTERPRETATION_FIELDS)
            # 繁体转换
            hant_values = [converter.convert(d[f]) for f in INTERPRETATION_FIELDS] + [sn]
            conn.execute(
                f"UPDATE gua_hant SET {set_clause} WHERE sign_number = ?",
                hant_values,
            )
            hant_updated += 1

        conn.commit()
        print(f"已更新 gua 表: {simp_updated} 条")
        print(f"已更新 gua_hant 表: {hant_updated} 条")

        # 4. 验证
        print("\n验证第 1 签（简体）:")
        row = conn.execute(
            "SELECT interpretation1, career FROM gua WHERE sign_number=1"
        ).fetchone()
        print(f"  interpretation1: {row[0][:60]}...")
        print(f"  career: {row[1][:60]}...")

        print("\n验证第 1 签（繁体）:")
        row = conn.execute(
            "SELECT interpretation1, career FROM gua_hant WHERE sign_number=1"
        ).fetchone()
        print(f"  interpretation1: {row[0][:60]}...")
        print(f"  career: {row[1][:60]}...")

        print("\n验证第 384 签（简体）:")
        row = conn.execute(
            "SELECT interpretation1, career FROM gua WHERE sign_number=384"
        ).fetchone()
        print(f"  interpretation1: {row[0][:60]}...")
        print(f"  career: {row[1][:60]}...")

        print("\n验证第 384 签（繁体）:")
        row = conn.execute(
            "SELECT interpretation1, career FROM gua_hant WHERE sign_number=384"
        ).fetchone()
        print(f"  interpretation1: {row[0][:60]}...")
        print(f"  career: {row[1][:60]}...")

        # 统计
        count_simp = conn.execute("SELECT COUNT(*) FROM gua WHERE interpretation1 != ''").fetchone()[0]
        count_hant = conn.execute("SELECT COUNT(*) FROM gua_hant WHERE interpretation1 != ''").fetchone()[0]
        print(f"\n非空解签统计: gua {count_simp}/384, gua_hant {count_hant}/384")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
