"""
将 reference.db 中的 gua 和 pzbj 表内容繁体化，写入新表 gua_hant 和 pzbj_hant。

策略：
  - 读取 gua 表全部记录
  - 用 OpenCC s2t 转换 10 个文本字段
  - sign_number 保持不变
  - 写入 gua_hant 表（结构与 gua 相同）
  - pzbj 同理

用法：
  python scripts/build_hant_db.py
"""
import sqlite3
from pathlib import Path

from opencc import OpenCC

DB_PATH = Path('data/reference/reference.db')

# gua 表需要繁体化的文本字段（sign_number 是整数主键，不转换）
GUA_TEXT_FIELDS = [
    'fortune', 'gua_type', 'sign_text', 'interpretation1',
    'career', 'wealth', 'love', 'health', 'study', 'general',
]


def build_hant_tables(db_path: Path) -> dict:
    """在 reference.db 中创建 gua_hant 和 pzbj_hant 表"""
    converter = OpenCC('s2t')  # 简体转繁体（通用配置）
    conn = sqlite3.connect(db_path)
    try:
        # 创建 gua_hant 表（结构与 gua 完全相同）
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS gua_hant (
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
            )
            """
        )
        # 清空旧数据（保证幂等）
        conn.execute('DELETE FROM gua_hant')

        # 读取 gua 全部记录并转换
        rows = conn.execute(
            'SELECT sign_number, fortune, gua_type, sign_text, interpretation1, '
            'career, wealth, love, health, study, general FROM gua'
        ).fetchall()

        hant_rows = []
        for row in rows:
            sign_number = row[0]
            # 转换后 10 个文本字段
            hant_texts = [converter.convert(row[i + 1]) for i in range(len(GUA_TEXT_FIELDS))]
            hant_rows.append((sign_number, *hant_texts))

        conn.executemany(
            'INSERT INTO gua_hant VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            hant_rows,
        )

        # 创建 pzbj_hant 表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pzbj_hant (
                text TEXT PRIMARY KEY,
                explanation TEXT NOT NULL
            ) WITHOUT ROWID
            """
        )
        conn.execute('DELETE FROM pzbj_hant')

        pzbj_rows = conn.execute('SELECT text, explanation FROM pzbj').fetchall()
        hant_pzbj = [
            (converter.convert(text), converter.convert(explanation))
            for text, explanation in pzbj_rows
        ]
        conn.executemany('INSERT INTO pzbj_hant VALUES (?, ?)', hant_pzbj)

        conn.commit()
        return {'gua_hant': len(hant_rows), 'pzbj_hant': len(hant_pzbj)}
    finally:
        conn.close()


def main():
    counts = build_hant_tables(DB_PATH)
    print('Built hant tables: ' + ', '.join(f'{k}={v}' for k, v in counts.items()))


if __name__ == '__main__':
    main()
