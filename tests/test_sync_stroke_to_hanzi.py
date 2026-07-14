import csv
import sqlite3
from contextlib import closing

from scripts.sync_stroke_to_hanzi import (
    read_discovered_rows,
    sync_reference,
    sync_supplement,
)


def _create_reference(path):
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            "CREATE TABLE hanzi ("
            "character TEXT PRIMARY KEY, "
            "simplified_strokes INTEGER, "
            "traditional_strokes INTEGER, "
            "kangxi_strokes INTEGER)"
        )
        connection.execute("INSERT INTO hanzi VALUES ('你', 0, 0, 7)")
        connection.commit()


def _create_runtime(path):
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            "CREATE TABLE stroke_cache (" "character TEXT PRIMARY KEY, kangxi_strokes INTEGER)"
        )
        connection.execute("INSERT INTO stroke_cache VALUES ('新', 13)")
        connection.commit()


def test_sync_preserves_discovered_rows_in_authoritative_supplement(tmp_path):
    reference = tmp_path / "reference.db"
    runtime = tmp_path / "runtime.db"
    supplement = tmp_path / "hanzi_strokes_zdic.csv"
    _create_reference(reference)
    _create_runtime(runtime)

    rows = read_discovered_rows(runtime, reference)
    assert rows == {"你": 7, "新": 13}
    assert sync_supplement(rows, supplement) == (2, 0)
    assert sync_reference(rows, reference) == 1

    with supplement.open(encoding="utf-8", newline="") as file:
        saved = list(csv.DictReader(file))
    assert saved == [
        {"character": "你", "kangxi_strokes": "7", "source": "zdic.net"},
        {"character": "新", "kangxi_strokes": "13", "source": "zdic.net"},
    ]
    with closing(sqlite3.connect(reference)) as connection:
        assert connection.execute(
            "SELECT kangxi_strokes FROM hanzi WHERE character = '新'"
        ).fetchone() == (13,)
