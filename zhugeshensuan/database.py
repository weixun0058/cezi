import json
import logging
import re
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .i18n_utils import get_gua_table_name, get_pzbj_table_name

LOGGER = logging.getLogger(__name__)


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
        self,
        reference_db="data/reference/reference.db",
        runtime_db="instance/runtime.db",
        signs_simp_path="data/content/oracle_signs_reinterpreted.json",
        signs_hant_path="data/content/oracle_signs_reinterpreted_hant.json",
        pzbj_simp_path="data/reference/pzbj.json",
        pzbj_hant_path="data/content/pzbj_hant.json",
    ):
        self.reference_db = Path(reference_db)
        self.runtime_db = Path(runtime_db)
        self._stroke_failure_cache = {}
        self._stroke_failure_ttl = 300
        self._init_runtime_db()
        # 签文和彭祖百忌从 JSON 内存加载（权威数据源，不入数据库）
        self.gua_index = self._load_signs_from_json(signs_simp_path)
        self.gua_hant_index = self._load_signs_from_json(signs_hant_path)
        self.pzbj = self._load_pzbj_from_json(pzbj_simp_path)
        self.pzbj_hant = self._load_pzbj_from_json(pzbj_hant_path)

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

    def _load_signs_from_json(self, json_path):
        """从签文 JSON 加载全部记录到内存索引。

        输入：json_path - oracle_signs_reinterpreted(_hant).json 路径
        输出：{sign_number: {sign_number, sign_text, interpretation1, ...}}
        """
        path = Path(json_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        index = {item["sign_number"]: item for item in data}
        LOGGER.info("Loaded %d signs from %s", len(index), path.name)
        return index

    def _load_pzbj_from_json(self, json_path):
        """从彭祖百忌 JSON 加载到内存字典。

        输入：json_path - pzbj(_hant).json 路径
        输出：{text: explanation}
        """
        path = Path(json_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        LOGGER.info("Loaded %d pzbj entries from %s", len(data), path.name)
        return data

    def get_gua_info(self, sign_number, lang: str | None = None):
        """根据语言返回签文信息。

        Args:
            sign_number: 签号 1-383
            lang: 语言代码，None 时使用当前请求语言
        """
        index = self.gua_hant_index if get_gua_table_name(lang) == "gua_hant" else self.gua_index
        try:
            return index.get(int(sign_number))
        except (TypeError, ValueError):
            return None

    def get_pzbj(self, lang: str | None = None):
        """根据语言返回彭祖百忌字典"""
        return self.pzbj_hant if get_pzbj_table_name(lang) == "pzbj_hant" else self.pzbj

    def get_stroke_count_by_hd(self, character):
        """Return a remote stroke count, or None when the lookup is inconclusive.

        适配 zdic.net 改版后的页面结构。提取顺序：
        1. 新版结构：`<span class="meta-badge">总笔画</span><span class="meta-value">N</span>`
        2. 正则兜底：`总笔画</span>...<span class="meta-value...">N</span>`
        3. 旧版结构（已失效，保留以防回滚）：`div.kxzd span.res_d a` / `td.z_bs2 p`
        """
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

            # 1. 新版结构：找文本为"总笔画"的 meta-badge，取其后的 meta-value
            badge = soup.find("span", class_="meta-badge", string="总笔画")
            if badge:
                value_node = badge.find_next_sibling(
                    "span", class_=lambda c: c and "meta-value" in c.split()
                )
                if value_node:
                    return int(value_node.get_text(strip=True))

            # 2. 正则兜底：从原始 HTML 提取，防止 BeautifulSoup 解析差异
            match = re.search(
                r"总笔画</span>\s*<span[^>]*class=\"[^\"]*meta-value[^\"]*\"[^>]*>\s*(\d+)\s*</span>",
                response.text,
            )
            if match:
                return int(match.group(1))

            # 3. 旧版结构兜底（zdic.net 若回滚则仍可用）
            kx_path = soup.select("div.kxzd span.res_d a")
            if kx_path:
                return int(kx_path[-1].get_text(strip=True))

            for node in soup.select("td.z_bs2 p"):
                if "总笔画" in node.get_text():
                    return int(node.get_text().split()[-1])

            LOGGER.warning("zdic.net page structure unrecognized for character: %s", character)
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
