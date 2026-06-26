import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _build_reference_database():
    pytest.importorskip("opencc")
    from scripts.build_reference_db import build_reference_database

    return build_reference_database


def test_packaged_reference_database_contains_runtime_tables():
    database = ROOT / "data" / "reference" / "reference.db"

    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM gua").fetchone()[0] == 383
        assert connection.execute("SELECT COUNT(*) FROM gua_hant").fetchone()[0] == 383
        assert connection.execute("SELECT COUNT(*) FROM pzbj").fetchone()[0] == 120
        assert connection.execute("SELECT COUNT(*) FROM pzbj_hant").fetchone()[0] == 120


def test_build_reference_database_contains_all_sources(tmp_path):
    build_reference_database = _build_reference_database()
    output = tmp_path / "reference.db"

    counts = build_reference_database(
        output,
        ROOT / "data" / "reference" / "kanxi_dict.db",
        ROOT / "data" / "reference" / "zhugeshenshuan_jq.xlsx",
        ROOT / "data" / "reference" / "pzbj.json",
    )

    assert counts["hanzi"] >= 18000
    assert counts["gua"] == 383
    assert counts["pzbj"] == 120
    with closing(sqlite3.connect(output)) as connection:
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM gua").fetchone()[0] == 383


def test_reference_database_build_is_deterministic(tmp_path):
    build_reference_database = _build_reference_database()
    first = tmp_path / "first.db"
    second = tmp_path / "second.db"
    sources = (
        ROOT / "data" / "reference" / "kanxi_dict.db",
        ROOT / "data" / "reference" / "zhugeshenshuan_jq.xlsx",
        ROOT / "data" / "reference" / "pzbj.json",
    )

    build_reference_database(first, *sources)
    build_reference_database(second, *sources)

    assert first.read_bytes() == second.read_bytes()
