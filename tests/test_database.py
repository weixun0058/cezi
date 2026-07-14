from shutil import copy2

import requests

from zhugeshensuan.database import Database, sqlite_connection
from zhugeshensuan.utils import cale_character_count


def test_sign_number_never_returns_zero():
    assert cale_character_count(3, 8, 4) == 383
    assert 1 <= cale_character_count(1, 1, 1) <= 383


def test_failed_remote_stroke_lookup_is_not_persisted(tmp_path, monkeypatch, reference_db):
    runtime_db = tmp_path / "runtime.db"
    database = Database(reference_db, runtime_db)

    def fail(*_args, **_kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(requests, "get", fail)
    assert database.get_stroke_count("🀄") is None
    with sqlite_connection(runtime_db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM stroke_cache").fetchone()[0] == 0


def test_remote_stroke_lookup_is_persisted_in_both_databases(tmp_path, monkeypatch, reference_db):
    local_reference = tmp_path / "reference.db"
    runtime_db = tmp_path / "runtime.db"
    copy2(reference_db, local_reference)
    with sqlite_connection(local_reference) as connection:
        connection.execute("DELETE FROM hanzi WHERE character = ?", ("你",))

    database = Database(local_reference, runtime_db)
    monkeypatch.setattr(database, "get_stroke_count_by_hd", lambda character: 7)

    assert database.get_stroke_count("你") == 7
    with sqlite_connection(runtime_db) as connection:
        row = connection.execute(
            "SELECT kangxi_strokes, source FROM stroke_cache WHERE character = ?", ("你",)
        ).fetchone()
        assert tuple(row) == (7, "zdic.net")
    with sqlite_connection(local_reference, readonly=True) as connection:
        row = connection.execute(
            "SELECT kangxi_strokes FROM hanzi WHERE character = ?", ("你",)
        ).fetchone()
        assert row["kangxi_strokes"] == 7
