import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from lunar_python import Solar

from database import sqlite_connection

LOGGER = logging.getLogger(__name__)


class HuangLi:
    ALGORITHM_VERSION = 2
    MIN_DATE = date(1900, 1, 1)
    MAX_DATE = date(2100, 12, 31)
    COLUMNS = {
        "date": "TEXT UNIQUE",
        "lunar_date": "TEXT",
        "gan_zhi_year": "TEXT",
        "gan_zhi_month": "TEXT",
        "gan_zhi_day": "TEXT",
        "gan_zhi_hour": "TEXT",
        "zodiac": "TEXT",
        "suitable": "TEXT",
        "unsuitable": "TEXT",
        "chong_sha": "TEXT",
        "ji_shen": "TEXT",
        "xiong_shen": "TEXT",
        "peng_zu_bai_ji": "TEXT",
        "xi_shen": "TEXT",
        "fu_shen": "TEXT",
        "cai_shen": "TEXT",
        "solar_term": "TEXT",
        "prev_solar_term": "TEXT",
        "prev_solar_term_days": "INTEGER",
        "next_solar_term": "TEXT",
        "next_solar_term_days": "INTEGER",
        "formatted_solar_term_info": "TEXT",
        "festivals": "TEXT",
        "cache_version": "INTEGER NOT NULL DEFAULT 1",
        "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }

    def __init__(self, db_path="instance/huangli.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        definitions = ", ".join(f"{name} {definition}" for name, definition in self.COLUMNS.items())
        with sqlite_connection(self.db_path) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            create_table_sql = (
                "CREATE TABLE IF NOT EXISTS huangli_daily "
                f"(id INTEGER PRIMARY KEY AUTOINCREMENT, {definitions})"
            )
            connection.execute(create_table_sql)
            existing = {row[1] for row in connection.execute("PRAGMA table_info(huangli_daily)")}
            for name, definition in self.COLUMNS.items():
                if name not in existing:
                    connection.execute(f"ALTER TABLE huangli_daily ADD COLUMN {name} {definition}")

    def get_daily_huangli(self, date=None):
        date = date or datetime.now().strftime("%Y-%m-%d")
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        if not self.MIN_DATE <= parsed_date <= self.MAX_DATE:
            raise ValueError("日期必须在 1900-01-01 到 2100-12-31 之间")
        with sqlite_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM huangli_daily WHERE date = ? AND cache_version = ?",
                (date, self.ALGORITHM_VERSION),
            ).fetchone()
            if row:
                LOGGER.debug("Huangli cache hit for %s", date)
                return dict(row)

        record = self._generate_huangli_data(date)
        if record:
            record["cache_version"] = self.ALGORITHM_VERSION
            self._save_huangli_to_db(record)
        return record

    @staticmethod
    def _solar_term_data(lunar, date_text, solar_term):
        current = datetime.strptime(date_text, "%Y-%m-%d")
        previous = lunar.getPrevJieQi()
        following = lunar.getNextJieQi()

        def to_datetime(jie_qi):
            solar = jie_qi.getSolar()
            return datetime(solar.getYear(), solar.getMonth(), solar.getDay())

        next_date = to_datetime(following)
        if solar_term and next_date == current:
            future = Solar.fromYmd(current.year, current.month, current.day).next(1).getLunar()
            following = future.getNextJieQi()
            next_date = to_datetime(following)

        previous_days = (current - to_datetime(previous)).days
        next_days = (next_date - current).days
        current_label = f"{solar_term}(今日)" if solar_term else "无"
        return {
            "prev_solar_term": previous.getName(),
            "prev_solar_term_days": previous_days,
            "next_solar_term": following.getName(),
            "next_solar_term_days": next_days,
            "formatted_solar_term_info": (
                f"{previous.getName()}({previous_days}天前) --- {current_label} --- "
                f"{following.getName()}(还有{next_days}天)"
            ),
        }

    def _generate_huangli_data(self, date_text):
        try:
            year, month, day = map(int, date_text.split("-"))
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            solar_term = lunar.getJieQi() or ""
            festivals = [
                *({"name": item, "type": "农历节日"} for item in (lunar.getFestivals() or [])),
                *({"name": item, "type": "阳历节日"} for item in (solar.getFestivals() or [])),
            ]
            record = {
                "date": date_text,
                "lunar_date": f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
                "gan_zhi_year": f"{lunar.getYearInGanZhi()}年",
                "gan_zhi_month": f"{lunar.getMonthInGanZhi()}月",
                "gan_zhi_day": f"{lunar.getDayInGanZhi()}日",
                "gan_zhi_hour": f"{lunar.getTimeInGanZhi()}时",
                "zodiac": f"{lunar.getYearShengXiao()}年",
                "suitable": "、".join(lunar.getDayYi() or []) or "无",
                "unsuitable": "、".join(lunar.getDayJi() or []) or "无",
                "chong_sha": f"冲{lunar.getChong()}({lunar.getChongGan()})煞{lunar.getSha()}",
                "ji_shen": "、".join(lunar.getDayJiShen() or []) or "无",
                "xiong_shen": "、".join(lunar.getDayXiongSha() or []) or "无",
                "peng_zu_bai_ji": f"{lunar.getPengZuGan()}，{lunar.getPengZuZhi()}",
                "xi_shen": f"{lunar.getDayPositionXiDesc()}({lunar.getDayPositionXi()})",
                "fu_shen": f"{lunar.getDayPositionFuDesc()}({lunar.getDayPositionFu()})",
                "cai_shen": f"{lunar.getDayPositionCaiDesc()}({lunar.getDayPositionCai()})",
                "solar_term": solar_term or "无",
                "festivals": festivals,
            }
            record.update(self._solar_term_data(lunar, date_text, solar_term))
            return record
        except (AttributeError, TypeError, ValueError):
            LOGGER.exception("Could not generate huangli data for %s", date_text)
            return None

    def _save_huangli_to_db(self, record):
        values = dict(record)
        values["festivals"] = json.dumps(values.get("festivals", []), ensure_ascii=False)
        values["updated_at"] = datetime.now().isoformat(timespec="seconds")
        columns = list(self.COLUMNS)
        placeholders = ", ".join("?" for _ in columns)
        updates = ", ".join(f"{name}=excluded.{name}" for name in columns if name != "date")
        with sqlite_connection(self.db_path) as connection:
            connection.execute(
                f"INSERT INTO huangli_daily ({', '.join(columns)}) VALUES ({placeholders}) "
                f"ON CONFLICT(date) DO UPDATE SET {updates}",
                [values.get(name) for name in columns],
            )

    def get_week_huangli(self, base_date=None):
        center = base_date or datetime.now()
        fields = (
            "date",
            "lunar_date",
            "gan_zhi_day",
            "gan_zhi_hour",
            "suitable",
            "unsuitable",
            "chong_sha",
            "peng_zu_bai_ji",
            "xi_shen",
            "fu_shen",
            "cai_shen",
            "solar_term",
        )
        records = []
        for offset in range(-2, 7):
            date_text = (center + timedelta(days=offset)).strftime("%Y-%m-%d")
            record = self.get_daily_huangli(date_text)
            if record:
                records.append({field: record.get(field, "") for field in fields})
        return records
