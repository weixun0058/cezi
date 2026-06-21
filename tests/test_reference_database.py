import sqlite3
from contextlib import closing
from pathlib import Path

from scripts.build_reference_db import build_reference_database

ROOT = Path(__file__).resolve().parents[1]


def test_build_reference_database_contains_all_sources(tmp_path):
    output = tmp_path / "reference.db"

    counts = build_reference_database(
        output,
        ROOT / "database" / "kanxi_dict.db",
        ROOT / "database" / "zhugeshenshuan_jq.xlsx",
        ROOT / "database" / "pzbj.json",
    )

    assert counts["hanzi"] >= 18000
    assert counts["gua"] == 383
    assert counts["pzbj"] == 120
    with closing(sqlite3.connect(output)) as connection:
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM gua").fetchone()[0] == 383


def test_reference_database_build_is_deterministic(tmp_path):
    first = tmp_path / "first.db"
    second = tmp_path / "second.db"
    sources = (
        ROOT / "database" / "kanxi_dict.db",
        ROOT / "database" / "zhugeshenshuan_jq.xlsx",
        ROOT / "database" / "pzbj.json",
    )

    build_reference_database(first, *sources)
    build_reference_database(second, *sources)

    assert first.read_bytes() == second.read_bytes()
