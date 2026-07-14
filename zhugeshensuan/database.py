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
            connection.execute("""
                CREATE TABLE IF NOT EXISTS stroke_cache (
                    character TEXT PRIMARY KEY,
                    kangxi_strokes INTEGER NOT NULL CHECK(kangxi_strokes > 0),
                    source TEXT NOT NULL,
                    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """)

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
        """从 zdic.net 查询汉字笔画数。

        查询顺序（优先康熙笔画，逐级回退）：
        1. 当前字康熙笔画（section#kxzd 下所有 p.dict-ancient__ref，
           正则提取"康熙笔画：N"）。简化字若康熙字典未收录，会给出
           参考繁体字的康熙笔画（如"为"→参考"爲"=12画）。
        2. 繁体字页面康熙笔画（meta-badge "繁体" 下的链接，二次请求）。
        3. 繁体字页面总笔画（meta-badge "总笔画"）。
        4. 当前字总笔画（康熙字典未收录且无繁体字时的最后回退，
           如化学元素字"氖""氟"等后起字）。

        输入：character - 单个汉字
        输出：笔画数（int）或 None
        """
        cached_until = self._stroke_failure_cache.get(character, 0)
        if cached_until > time.monotonic():
            return None

        try:
            soup = self._fetch_zdic_soup(character)
            if not soup:
                return None

            # 1. 当前字康熙笔画
            kangxi = self._extract_kangxi_strokes(soup)
            if kangxi:
                return kangxi

            # 2. 康熙笔画没有，查繁体字页面
            traditional_char = self._extract_traditional_char(soup)
            if traditional_char and traditional_char != character:
                trad_soup = self._fetch_zdic_soup(traditional_char)
                if trad_soup:
                    # 2.1 繁体字康熙笔画
                    kangxi = self._extract_kangxi_strokes(trad_soup)
                    if kangxi:
                        return kangxi
                    # 2.2 繁体字总笔画
                    total = self._extract_total_strokes(trad_soup)
                    if total:
                        return total

            # 3. 当前字总笔画（康熙字典未收录且无繁体字的最后回退）
            total = self._extract_total_strokes(soup)
            if total:
                return total

            LOGGER.warning("zdic.net page structure unrecognized for character: %s", character)
        except (requests.RequestException, TypeError, ValueError) as exc:
            LOGGER.warning("Remote stroke lookup failed for one character: %s", type(exc).__name__)

        self._stroke_failure_cache[character] = time.monotonic() + self._stroke_failure_ttl
        return None

    def _fetch_zdic_soup(self, character):
        """请求 zdic.net 汉字页面，返回 BeautifulSoup 对象。

        输入：character - 单个汉字
        输出：BeautifulSoup 对象或 None（请求失败时）
        """
        response = requests.get(
            f"https://www.zdic.net/hans/{character}",
            headers={"User-Agent": "ZhugeshenSuan/4.1 (+stroke lookup)"},
            timeout=(3.05, 5),
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        return BeautifulSoup(response.text, "html.parser")

    def _extract_kangxi_strokes(self, soup):
        """从 zdic.net 页面提取康熙笔画。

        DOM 路径：section#kxzd div.dict-ancient p.dict-ancient__ref
        文本格式：'【巳集上】【水字部】 康熙笔画：9 部外笔画：5'
        简化字可能有多条 ref（首条为"未收录"提示，后续为参考字笔画），
        遍历所有 ref 取第一个匹配。

        输入：soup - BeautifulSoup 对象
        输出：康熙笔画数（int）或 None
        """
        kxzd = soup.find("section", id="kxzd")
        if not kxzd:
            return None
        pattern = re.compile(r"康熙笔画[：:]\s*(\d+)")
        for ref in kxzd.find_all("p", class_="dict-ancient__ref"):
            match = pattern.search(ref.get_text(strip=True))
            if match:
                return int(match.group(1))
        return None

    def _extract_total_strokes(self, soup):
        """从 zdic.net 页面提取总笔画。

        DOM：span.meta-badge（文本"总笔画"）的下一个 span.meta-value。

        输入：soup - BeautifulSoup 对象
        输出：总笔画数（int）或 None
        """
        for badge in soup.find_all("span", class_="meta-badge"):
            if badge.get_text(strip=True) == "总笔画":
                value_node = badge.find_next_sibling(
                    "span", class_=lambda c: c and "meta-value" in c.split()
                )
                if value_node:
                    try:
                        return int(value_node.get_text(strip=True))
                    except ValueError:
                        return None
        return None

    def _extract_traditional_char(self, soup):
        """从 zdic.net 页面提取第一个繁体字。

        DOM：span.meta-badge（文本"繁体"）父元素下 a.variant-link 的 title 属性。
        简繁同形的字无此 badge。

        输入：soup - BeautifulSoup 对象
        输出：繁体字（str）或 None
        """
        for badge in soup.find_all("span", class_="meta-badge"):
            if badge.get_text(strip=True) == "繁体":
                parent = badge.parent
                if parent:
                    link = parent.find("a", class_="variant-link")
                    if link:
                        return link.get("title") or None
                break
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
            # 缓存命中，但 reference.db hanzi 表可能缺失，尝试回写（使字典库永久增长）
            self._append_to_hanzi(character, row["kangxi_strokes"])
            return row["kangxi_strokes"]

        stroke_count = self.get_stroke_count_by_hd(character)
        if not stroke_count or stroke_count < 1:
            return None

        # 1. 写入 runtime.db stroke_cache（运行时缓存，容器内可写）
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
            LOGGER.exception("Could not cache a remote stroke count in runtime.db")

        # 2. 写入 reference.db hanzi 表（永久字典）
        self._append_to_hanzi(character, stroke_count)

        return stroke_count

    def _append_to_hanzi(self, character, kangxi_strokes):
        """把字追加到 reference.db hanzi 表，使字典库永久增长。

        本地开发时 reference.db 可写，追加成功；
        容器中 reference.db 只读，静默降级（不影响功能）。
        """
        try:
            with sqlite_connection(self.reference_db) as connection:
                connection.execute(
                    """
                    INSERT INTO hanzi (
                        character,
                        simplified_strokes,
                        traditional_strokes,
                        kangxi_strokes
                    )
                    VALUES (?, 0, 0, ?)
                    ON CONFLICT(character) DO UPDATE SET
                        kangxi_strokes=excluded.kangxi_strokes
                    """,
                    (character, kangxi_strokes),
                )
            LOGGER.info(
                "Appended character '%s' (kangxi_strokes=%d) to reference.db hanzi table",
                character,
                kangxi_strokes,
            )
        except sqlite3.Error:
            # 容器中 reference.db 只读，静默降级（只写 runtime.db）
            LOGGER.debug("Could not append to reference.db hanzi (likely read-only): %s", character)

    def check_ready(self):
        with sqlite_connection(self.reference_db, readonly=True) as connection:
            reference_ok = connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        with sqlite_connection(self.runtime_db) as connection:
            runtime_ok = connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        return reference_ok and runtime_ok
