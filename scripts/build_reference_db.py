import argparse
import json
import os
import sqlite3
from pathlib import Path

from openpyxl import load_workbook

GUA_FIELDS = {
    "签号": "sign_number",
    "吉凶": "fortune",
    "卦属": "gua_type",
    "签文": "sign_text",
    "解签一": "interpretation1",
    "事业": "career",
    "财运": "wealth",
    "情感": "love",
    "健康": "health",
    "学业": "study",
    "泛泛": "general",
}


def _read_hanzi(source):
    connection = sqlite3.connect(source)
    try:
        rows = connection.execute(
            """
            SELECT 汉字, 简体字总笔画, 繁体字总笔画, 康熙字典笔画
            FROM hanzi
            WHERE 汉字 IS NOT NULL AND 汉字 != ''
            ORDER BY 汉字, ID
            """
        ).fetchall()
        unique = {}
        for row in rows:
            unique.setdefault(row[0], row)
        return list(unique.values())
    finally:
        connection.close()


def _read_gua(source):
    workbook = load_workbook(source, read_only=True, data_only=True)
    try:
        rows = workbook.active.iter_rows(values_only=True)
        headers = [str(value).strip() if value is not None else "" for value in next(rows)]
        records = []
        for values in rows:
            row = dict(zip(headers, values, strict=False))
            try:
                sign_number = int(row.get("签号"))
            except (TypeError, ValueError):
                continue
            records.append(
                tuple(
                    sign_number if field == "sign_number" else row.get(source_name) or ""
                    for source_name, field in GUA_FIELDS.items()
                )
            )
        return sorted(records, key=lambda item: item[0])
    finally:
        workbook.close()


def _read_pzbj(source):
    with open(source, encoding="utf-8") as file:
        return sorted(json.load(file).items())


def build_reference_database(output, hanzi_source, gua_source, pzbj_source):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.unlink(missing_ok=True)

    hanzi = _read_hanzi(hanzi_source)
    gua = _read_gua(gua_source)
    pzbj = _read_pzbj(pzbj_source)
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript(
            """
            PRAGMA page_size=4096;
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=FULL;
            CREATE TABLE hanzi (
                character TEXT PRIMARY KEY,
                simplified_strokes INTEGER,
                traditional_strokes INTEGER,
                kangxi_strokes INTEGER
            ) WITHOUT ROWID;
            CREATE TABLE gua (
                sign_number INTEGER PRIMARY KEY CHECK(sign_number BETWEEN 1 AND 383),
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
            CREATE TABLE pzbj (
                text TEXT PRIMARY KEY,
                explanation TEXT NOT NULL
            ) WITHOUT ROWID;
            """
        )
        connection.executemany("INSERT INTO hanzi VALUES (?, ?, ?, ?)", hanzi)
        connection.executemany("INSERT INTO gua VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", gua)
        connection.executemany("INSERT INTO pzbj VALUES (?, ?)", pzbj)
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()

    os.replace(temporary, output)
    return {"hanzi": len(hanzi), "gua": len(gua), "pzbj": len(pzbj)}


def main():
    parser = argparse.ArgumentParser(description="Build the production reference database")
    parser.add_argument("--output", default="database/reference.db")
    parser.add_argument("--hanzi", default="database/kanxi_dict.db")
    parser.add_argument("--gua", default="database/zhugeshenshuan_jq.xlsx")
    parser.add_argument("--pzbj", default="database/pzbj.json")
    arguments = parser.parse_args()
    counts = build_reference_database(
        arguments.output, arguments.hanzi, arguments.gua, arguments.pzbj
    )
    print("Built reference database: " + ", ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
