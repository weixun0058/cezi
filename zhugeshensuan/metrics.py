import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from .database import sqlite_connection

SHANGHAI = ZoneInfo("Asia/Shanghai")
ALLOWED_METRICS = frozenset(
    {
        "almanac_results",
        "oracle_results",
    }
)

ENDPOINT_METRICS = {
    ("divination.get_gua_info", "POST"): "oracle_results",
    ("oracle_en_api.ask", "POST"): "oracle_results",
    ("huangli_api.get_huangli", "GET"): "almanac_results",
    ("huangli_api.get_week_huangli", "GET"): "almanac_results",
    ("huangli_en_api.daily_almanac", "GET"): "almanac_results",
    ("huangli_en_api.week_almanac", "GET"): "almanac_results",
}


class DailyMetricsStore:
    """Store daily aggregate product counters without request or user data."""

    def __init__(self, runtime_db):
        self.runtime_db = runtime_db
        self._init_db()

    def _init_db(self):
        with sqlite_connection(self.runtime_db) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS daily_product_metrics (
                    metric_date TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    event_count INTEGER NOT NULL DEFAULT 0 CHECK(event_count >= 0),
                    PRIMARY KEY (metric_date, metric_name)
                )
                """)

    def increment(self, metric_name, *, count=1, now=None):
        if metric_name not in ALLOWED_METRICS:
            raise ValueError(f"unsupported aggregate metric: {metric_name}")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError("metric count must be a positive integer")
        metric_date = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI).date().isoformat()
        with sqlite_connection(self.runtime_db) as connection:
            connection.execute(
                """
                INSERT INTO daily_product_metrics (metric_date, metric_name, event_count)
                VALUES (?, ?, ?)
                ON CONFLICT(metric_date, metric_name)
                DO UPDATE SET event_count=event_count + excluded.event_count
                """,
                (metric_date, metric_name, count),
            )

    def check_ready(self):
        try:
            with sqlite_connection(self.runtime_db) as connection:
                connection.execute("SELECT 1 FROM daily_product_metrics LIMIT 1").fetchone()
            return True
        except sqlite3.Error:
            return False
