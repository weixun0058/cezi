"""验证数据库 gua_hant 异体字保留与关键签内容。"""
import sqlite3

conn = sqlite3.connect("data/reference/reference.db")
checks = [4, 14, 25, 26, 41, 85, 96, 142, 167, 211, 213, 216, 256, 260, 313, 373, 380]
for sn in checks:
    row = conn.execute(
        "SELECT sign_text FROM gua_hant WHERE sign_number=?", (sn,)
    ).fetchone()
    print(f"第{sn:>3}签: {row[0] if row else '[无]'}")

# 验证异体字存在
print("\n=== 异体字抽检 ===")
variant_checks = [
    (85, "盃"), (142, "啣"), (211, "啣"), (260, "廻"),
    (96, "旣"), (1, "掛"), (8, "嚦"), (41, "凟"),
    (27, "疴"), (313, "軛"), (63, "兎"),
]
for sn, ch in variant_checks:
    row = conn.execute(
        "SELECT sign_text FROM gua_hant WHERE sign_number=?", (sn,)
    ).fetchone()
    text = row[0] if row else ""
    ok = "✓" if ch in text else "✗"
    print(f"  第{sn:>3}签 含「{ch}」: {ok}")

conn.close()
