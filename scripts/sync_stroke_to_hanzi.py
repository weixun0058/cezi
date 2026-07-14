"""把运行时查到的笔画同步到权威补充源和 reference.db。

容器部署时 reference.db 只读，汉典查到的字先写入 runtime.db。
本脚本在本地开发环境运行，把新增记录纳入可审查、可重建的 CSV
权威补充源，并同步当前 reference.db。

操作：
  1. 读取 reference.db 中既有的运行时新增记录和 runtime.db 缓存
  2. 将权威源尚未收录的字写入 hanzi_strokes_zdic.csv
  3. 将新增记录同步到 reference.db 并输出统计

用法：
  python scripts/sync_stroke_to_hanzi.py
"""

import csv
import sqlite3
from contextlib import closing
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUNTIME_DB = PROJECT / "instance" / "runtime.db"
REFERENCE_DB = PROJECT / "data" / "reference" / "reference.db"
SUPPLEMENT_SOURCE = PROJECT / "data" / "reference" / "hanzi_strokes_zdic.csv"


def read_discovered_rows(runtime_db, reference_db):
    """读取线上缓存和派生库中由汉典补充的记录。"""
    rows = {}
    if runtime_db.exists():
        with closing(sqlite3.connect(runtime_db)) as connection:
            for character, strokes in connection.execute(
                "SELECT character, kangxi_strokes FROM stroke_cache " "WHERE kangxi_strokes > 0"
            ):
                rows[character] = strokes
    if reference_db.exists():
        with closing(sqlite3.connect(reference_db)) as connection:
            for character, strokes in connection.execute(
                "SELECT character, kangxi_strokes FROM hanzi "
                "WHERE simplified_strokes = 0 AND traditional_strokes = 0 "
                "AND kangxi_strokes > 0"
            ):
                # 已经进入参考库的人工确认记录优先于运行缓存。
                rows[character] = strokes
    return rows


def sync_supplement(rows, supplement_source):
    """只新增权威补充源尚未收录的字；冲突保留权威源现值。"""
    existing = {}
    if supplement_source.exists():
        with supplement_source.open(encoding="utf-8-sig", newline="") as file:
            for item in csv.DictReader(file):
                character = (item.get("character") or "").strip()
                if character:
                    existing[character] = {
                        "character": character,
                        "kangxi_strokes": int(item["kangxi_strokes"]),
                        "source": item.get("source") or "zdic.net",
                    }

    inserted = 0
    conflicts = 0
    for character, strokes in rows.items():
        current = existing.get(character)
        if current is None:
            existing[character] = {
                "character": character,
                "kangxi_strokes": strokes,
                "source": "zdic.net",
            }
            inserted += 1
        elif current["kangxi_strokes"] != strokes:
            conflicts += 1

    supplement_source.parent.mkdir(parents=True, exist_ok=True)
    with supplement_source.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=("character", "kangxi_strokes", "source"),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(existing[key] for key in sorted(existing))
    return inserted, conflicts


def sync_reference(rows, reference_db):
    """把缺失记录写入当前派生库，不覆盖库内已有权威值。"""
    inserted = 0
    with closing(sqlite3.connect(reference_db)) as connection:
        for character, strokes in rows.items():
            existing = connection.execute(
                "SELECT 1 FROM hanzi WHERE character = ?", (character,)
            ).fetchone()
            if existing is None:
                connection.execute(
                    "INSERT INTO hanzi "
                    "(character, simplified_strokes, traditional_strokes, kangxi_strokes) "
                    "VALUES (?, 0, 0, ?)",
                    (character, strokes),
                )
                inserted += 1
        connection.commit()
    return inserted


def main():
    rows = read_discovered_rows(RUNTIME_DB, REFERENCE_DB)
    print(f"待同步的汉典补充记录: {len(rows)} 条")
    if not rows:
        print("无数据可同步")
        return

    source_inserted, conflicts = sync_supplement(rows, SUPPLEMENT_SOURCE)
    reference_inserted = sync_reference(rows, REFERENCE_DB)
    print(
        "同步完成: "
        f"权威补充源新增 {source_inserted} 字, "
        f"reference.db 新增 {reference_inserted} 字, "
        f"待人工核对冲突 {conflicts} 字"
    )
    print("请重新构建 reference.db，并提交权威补充源")


if __name__ == "__main__":
    main()
