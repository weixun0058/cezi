import sqlite3

import requests

from database import Database
from utils import cale_character_count


def test_sign_number_never_returns_zero():
    assert cale_character_count(3, 8, 4) == 383
    assert 1 <= cale_character_count(1, 1, 1) <= 383


def test_failed_remote_stroke_lookup_is_not_persisted(tmp_path, monkeypatch):
    db_path = tmp_path / "hanzi.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE hanzi (ID INTEGER PRIMARY KEY, 汉字 TEXT, "
            "简体字总笔画 INTEGER, 繁体字总笔画 INTEGER, 康熙字典笔画 INTEGER)"
        )
    database = Database.__new__(Database)
    database.hanzi_db = db_path
    database._stroke_failure_cache = {}
    database._stroke_failure_ttl = 300

    def fail(*_args, **_kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(requests, "get", fail)
    assert database.get_stroke_count("龘") is None
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM hanzi").fetchone()[0] == 0
