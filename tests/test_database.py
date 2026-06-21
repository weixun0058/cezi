import requests

from database import Database
from utils import cale_character_count


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
    from database import sqlite_connection

    with sqlite_connection(runtime_db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM stroke_cache").fetchone()[0] == 0
