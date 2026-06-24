import logging
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
GUA_COLUMNS = (
    "sign_number",
    "fortune",
    "gua_type",
    "sign_text",
    "interpretation1",
    "career",
    "wealth",
    "love",
    "health",
    "study",
    "general",
)


@contextmanager
def sqlite_connection(path, *, readonly=False):
    path = Path(path)
    if readonly:
        connection = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path, timeout=5)
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute("PRAGMA foreign_keys=ON")
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        if not readonly:
            connection.commit()
    except Exception:
        if not readonly:
            connection.rollback()
        raise
    finally:
        connection.close()


class Database:
    def __init__(
        self, reference_db="data/reference/reference.db", runtime_db="instance/runtime.db"
    ):
        self.reference_db = Path(reference_db)
        self.runtime_db = Path(runtime_db)
        self._stroke_failure_cache = {}
        self._stroke_failure_ttl = 300
        self._init_runtime_db()
        self.gua_index = self._load_gua_index()

    def _init_runtime_db(self):
        with sqlite_connection(self.runtime_db) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS stroke_cache (
                    character TEXT PRIMARY KEY,
                    kangxi_strokes INTEGER NOT NULL CHECK(kangxi_strokes > 0),
                    source TEXT NOT NULL,
                    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _load_gua_index(self):
        with sqlite_connection(self.reference_db, readonly=True) as connection:
            rows = connection.execute(f"SELECT {', '.join(GUA_COLUMNS)} FROM gua").fetchall()
        index = {row["sign_number"]: dict(row) for row in rows}
        LOGGER.info("Loaded %d divination records", len(index))
        return index

    def load_pzbj(self):
        with sqlite_connection(self.reference_db, readonly=True) as connection:
            rows = connection.execute("SELECT text, explanation FROM pzbj").fetchall()
        return {row["text"]: row["explanation"] for row in rows}

    def get_gua_info(self, sign_number):
        try:
            return self.gua_index.get(int(sign_number))
        except (TypeError, ValueError):
            return None

    def get_stroke_count_by_hd(self, character):
        """Return a remote stroke count, or None when the lookup is inconclusive."""
        cached_until = self._stroke_failure_cache.get(character, 0)
        if cached_until > time.monotonic():
            return None

        try:
            response = requests.get(
                f"https://www.zdic.net/hans/{character}",
                headers={"User-Agent": "ZhugeshenSuan/4.1 (+stroke lookup)"},
                timeout=(3.05, 5),
            )
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")

            kx_path = soup.select("div.kxzd span.res_d a")
            if kx_path:
                return int(kx_path[-1].get_text(strip=True))

            for node in soup.select("td.z_bs2 p"):
                if "总笔画" in node.get_text():
                    return int(node.get_text().split()[-1])
        except (requests.RequestException, TypeError, ValueError) as exc:
            LOGGER.warning("Remote stroke lookup failed for one character: %s", type(exc).__name__)

        self._stroke_failure_cache[character] = time.monotonic() + self._stroke_failure_ttl
        return None

    def get_stroke_count(self, character):
        if not isinstance(character, str) or len(character) != 1:
            return None

        with sqlite_connection(self.reference_db, readonly=True) as connection:
            row = connection.execute(
                """
                SELECT simplified_strokes, traditional_strokes, kangxi_strokes
                FROM hanzi WHERE character = ?
                """,
                (character,),
            ).fetchone()
        if row:
            for value in (
                row["kangxi_strokes"],
                row["traditional_strokes"],
                row["simplified_strokes"],
            ):
                if isinstance(value, int) and value > 0:
                    return value

        with sqlite_connection(self.runtime_db) as connection:
            row = connection.execute(
                "SELECT kangxi_strokes FROM stroke_cache WHERE character = ?", (character,)
            ).fetchone()
        if row:
            return row["kangxi_strokes"]

        stroke_count = self.get_stroke_count_by_hd(character)
        if not stroke_count or stroke_count < 1:
            return None

        try:
            with sqlite_connection(self.runtime_db) as connection:
                connection.execute(
                    """
                    INSERT INTO stroke_cache (character, kangxi_strokes, source)
                    VALUES (?, ?, 'zdic.net')
                    ON CONFLICT(character) DO UPDATE SET
                        kangxi_strokes=excluded.kangxi_strokes,
                        source=excluded.source,
                        fetched_at=CURRENT_TIMESTAMP
                    """,
                    (character, stroke_count),
                )
        except sqlite3.Error:
            LOGGER.exception("Could not cache a remote stroke count")
        return stroke_count

    def check_ready(self):
        with sqlite_connection(self.reference_db, readonly=True) as connection:
            reference_ok = connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        with sqlite_connection(self.runtime_db) as connection:
            runtime_ok = connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        return reference_ok and runtime_ok
