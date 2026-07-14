"""批量从 zdic.net 获取缺失汉字的康熙笔画，写入 reference.db hanzi 表。

背景：reference.db hanzi 表缺失部分常用简体字（如"你""为""简"等）。
      本脚本从 zdic.net 批量查询缺失字的康熙笔画，直接写入 reference.db。

模式：
  1. 补全模式（默认）：扫描 GB2312 一级常用字，补全缺失字到 hanzi 表
  2. 指定补全（--chars）：补全指定字到 hanzi 表（已存在则跳过）
  3. 纯查询（--query）：查询单个或多个字的笔画，不写入数据库，显示来源
  4. 远程查询（--remote）：只从 zdic.net 查询，不查本地数据库，不写入
  5. 复查模式（--recheck）：重新查询之前用错误逻辑（查总笔画）写入的字，
     用正确的康熙笔画覆盖。特征：simplified_strokes=0 AND traditional_strokes=0
     AND kangxi_strokes>0

用法：
  python scripts/backfill_hanzi_strokes.py                      # 补全 GB2312 一级常用字
  python scripts/backfill_hanzi_strokes.py --chars 你为简        # 补全指定字
  python scripts/backfill_hanzi_strokes.py --query 你            # 查询单个字笔画
  python scripts/backfill_hanzi_strokes.py --query 波你科        # 查询多个字笔画
  python scripts/backfill_hanzi_strokes.py --remote 你           # 只从 zdic.net 查询
  python scripts/backfill_hanzi_strokes.py --recheck
      # 复查错误写入的字（用康熙笔画覆盖）
  python scripts/backfill_hanzi_strokes.py --delay 2             # 每次查询间隔2秒（避免被封）
"""

import argparse
import sqlite3
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from zhugeshensuan.database import Database  # noqa: E402

REFERENCE_DB = PROJECT / "data" / "reference" / "reference.db"


def generate_gb2312_level1():
    """生成 GB2312 一级常用汉字（3755字）"""
    chars = []
    for high in range(0xB0, 0xD8):
        for low in range(0xA1, 0xFF):
            try:
                ch = bytes([high, low]).decode("gb2312")
                chars.append(ch)
            except (UnicodeDecodeError, LookupError):
                continue
    return chars


def find_missing_chars(ref_conn):
    """找出 hanzi 表中缺失的 GB2312 一级常用字"""
    all_chars = generate_gb2312_level1()
    missing = []
    for ch in all_chars:
        row = ref_conn.execute(
            "SELECT kangxi_strokes FROM hanzi WHERE character=?", (ch,)
        ).fetchone()
        if row is None:
            missing.append(ch)
    return missing


def query_chars(chars, db, ref_conn, delay):
    """纯查询模式：查询字的笔画，不写入数据库，显示来源。

    查询优先级：reference.db hanzi → runtime.db stroke_cache → zdic.net（只查不写）
    """
    print(f"查询 {len(chars)} 字: {' '.join(chars)}")
    print("-" * 40)
    for i, ch in enumerate(chars, 1):
        source = ""
        strokes = None

        # 1. 查 reference.db hanzi 表
        row = ref_conn.execute(
            "SELECT kangxi_strokes FROM hanzi WHERE character=?", (ch,)
        ).fetchone()
        if row and row[0] > 0:
            strokes = row[0]
            source = "reference.db"
        else:
            # 2. 查 runtime.db stroke_cache（直接查，不走 get_stroke_count 避免触发追加）
            with sqlite3.connect(PROJECT / "instance" / "runtime.db") as runtime_conn:
                cache_row = runtime_conn.execute(
                    "SELECT kangxi_strokes FROM stroke_cache WHERE character=?", (ch,)
                ).fetchone()
            if cache_row and cache_row[0] > 0:
                strokes = cache_row[0]
                source = "runtime.db(stroke_cache)"
            else:
                # 3. 从 zdic.net 查询（只查不写）
                strokes = db.get_stroke_count_by_hd(ch)
                source = "zdic.net(未入库)"

        if strokes:
            print(f"[{i}/{len(chars)}] {ch} = {strokes}画 (来源: {source})")
        else:
            print(f"[{i}/{len(chars)}] {ch} = 查询失败")

        if i < len(chars):
            time.sleep(delay)
    print("-" * 40)


def remote_query_chars(chars, db, delay):
    """远程查询模式：只从 zdic.net 查询，不查本地数据库，不写入。

    用于验证 zdic.net 接口可用性或对比本地数据差异。
    """
    print(f"远程查询 {len(chars)} 字: {' '.join(chars)}")
    print("-" * 40)
    for i, ch in enumerate(chars, 1):
        strokes = db.get_stroke_count_by_hd(ch)
        if strokes:
            print(f"[{i}/{len(chars)}] {ch} = {strokes}画 (来源: zdic.net)")
        else:
            print(f"[{i}/{len(chars)}] {ch} = zdic.net 查询失败")

        if i < len(chars):
            time.sleep(delay)
    print("-" * 40)


def recheck_chars(db, ref_conn, delay):
    """复查模式：重新查询之前用错误逻辑（查总笔画）写入的字，用正确康熙笔画覆盖。

    背景：旧版 get_stroke_count_by_hd 查的是"总笔画"而非"康熙笔画"，
    错误数据特征为 simplified_strokes=0 AND traditional_strokes=0 AND kangxi_strokes>0
    （backfill 脚本用 INSERT OR REPLACE 写入，s/t 字段固定为0）。

    本函数找出所有特征记录，用修复后的康熙笔画查询逻辑重新查询并覆盖。
    """
    rows = ref_conn.execute(
        "SELECT character, kangxi_strokes FROM hanzi "
        "WHERE simplified_strokes=0 AND traditional_strokes=0 AND kangxi_strokes>0 "
        "ORDER BY character"
    ).fetchall()
    print(f"需复查: {len(rows)} 字（特征: s=0, t=0, k>0）")
    print(f"查询间隔: {delay}秒")
    print()

    corrected = 0  # 新旧笔画不同，已修正
    consistent = 0  # 新旧笔画一致，无需改
    failed = 0  # 查询失败

    for i, (ch, old_strokes) in enumerate(rows, 1):
        new_strokes = db.get_stroke_count_by_hd(ch)
        if new_strokes and new_strokes > 0:
            if new_strokes != old_strokes:
                # 笔画不同，覆盖写入
                ref_conn.execute(
                    "UPDATE hanzi SET kangxi_strokes=? WHERE character=?",
                    (new_strokes, ch),
                )
                ref_conn.commit()
                print(f"[{i}/{len(rows)}] {ch} {old_strokes}→{new_strokes}画 ✓ 已修正")
                corrected += 1
            else:
                print(f"[{i}/{len(rows)}] {ch} {old_strokes}画 一致")
                consistent += 1
        else:
            print(f"[{i}/{len(rows)}] {ch} 原{old_strokes}画 查询失败 ✗ 保留原值")
            failed += 1

        if i < len(rows):
            time.sleep(delay)

    print()
    print("=== 复查完成 ===")
    print(f"已修正: {corrected} 字")
    print(f"原值一致: {consistent} 字")
    print(f"查询失败: {failed} 字（保留原值）")
    print(f"总计: {len(rows)} 字")


def main():
    parser = argparse.ArgumentParser(
        description="批量补全缺失汉字的康熙笔画 / 查询汉字笔画",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--chars", type=str, default="", help="指定要补全的字（如 '你为简'），写入数据库"
    )
    parser.add_argument(
        "--query", type=str, default="", help="查询字的笔画（如 '你' 或 '波你科'），不写入数据库"
    )
    parser.add_argument(
        "--remote",
        type=str,
        default="",
        help="只从 zdic.net 查询（如 '你' 或 '波你科'），不查本地不写入",
    )
    parser.add_argument(
        "--recheck",
        action="store_true",
        help="复查模式：重新查询之前用错误逻辑写入的字，用康熙笔画覆盖",
    )
    parser.add_argument("--delay", type=float, default=1.0, help="每次查询间隔秒数（默认1秒）")
    args = parser.parse_args()

    ref_conn = sqlite3.connect(REFERENCE_DB)

    # 初始化 Database 实例（用于调用 get_stroke_count_by_hd）
    db = Database(
        reference_db=str(REFERENCE_DB),
        runtime_db=str(PROJECT / "instance" / "runtime.db"),
    )

    # 复查模式（重新查询错误写入的字）
    if args.recheck:
        recheck_chars(db, ref_conn, args.delay)
        ref_conn.close()
        return

    # 远程查询模式（只查 zdic.net）
    if args.remote:
        remote_query_chars(list(args.remote), db, args.delay)
        ref_conn.close()
        return

    # 纯查询模式
    if args.query:
        query_chars(list(args.query), db, ref_conn, args.delay)
        ref_conn.close()
        return

    # 补全模式
    if args.chars:
        target_chars = list(args.chars)
        print(f"指定补全: {len(target_chars)} 字")
    else:
        target_chars = find_missing_chars(ref_conn)
        print(f"GB2312 一级常用字缺失: {len(target_chars)} 字")

    if not target_chars:
        print("无缺失字，无需补全")
        ref_conn.close()
        return

    print(f"缺失字: {' '.join(target_chars[:50])}{'...' if len(target_chars) > 50 else ''}")
    print(f"查询间隔: {args.delay}秒")
    print()

    # 初始化 Database 实例（用于调用 get_stroke_count_by_hd）
    db = Database(
        reference_db=str(REFERENCE_DB),
        runtime_db=str(PROJECT / "instance" / "runtime.db"),
    )

    success = 0
    failed = 0
    for i, ch in enumerate(target_chars, 1):
        # 先检查是否已存在（可能之前已补全）
        existing = ref_conn.execute(
            "SELECT kangxi_strokes FROM hanzi WHERE character=?", (ch,)
        ).fetchone()
        if existing and existing[0] > 0:
            print(f"[{i}/{len(target_chars)}] {ch} 已存在({existing[0]}画)，跳过")
            continue

        # 从 zdic.net 查询
        strokes = db.get_stroke_count_by_hd(ch)
        if strokes and strokes > 0:
            # 写入 reference.db
            ref_conn.execute(
                "INSERT OR REPLACE INTO hanzi "
                "(character, simplified_strokes, traditional_strokes, kangxi_strokes) "
                "VALUES (?, 0, 0, ?)",
                (ch, strokes),
            )
            ref_conn.commit()
            print(f"[{i}/{len(target_chars)}] {ch} = {strokes}画 ✓")
            success += 1
        else:
            print(f"[{i}/{len(target_chars)}] {ch} 查询失败 ✗")
            failed += 1

        if i < len(target_chars):
            time.sleep(args.delay)

    ref_conn.close()

    print("\n=== 补全完成 ===")
    print(f"成功: {success} 字")
    print(f"失败: {failed} 字")
    print(f"总计: {len(target_chars)} 字")
    if failed > 0:
        print("\n失败的字需要手动查询或更换数据源")


if __name__ == "__main__":
    main()
