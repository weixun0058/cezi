import sqlite3
from contextlib import closing
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from scripts.weekly_metrics_report import generate_report
from zhugeshensuan.metrics import DailyMetricsStore


def test_daily_metrics_store_keeps_aggregate_counts_only(tmp_path):
    runtime_db = tmp_path / "runtime.db"
    store = DailyMetricsStore(runtime_db)
    now = datetime(2026, 7, 19, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

    store.increment("oracle_results", now=now)
    store.increment("oracle_results", count=2, now=now)
    store.increment("almanac_results", now=now)

    with closing(sqlite3.connect(runtime_db)) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(daily_product_metrics)")}
        rows = connection.execute(
            "SELECT metric_date, metric_name, event_count FROM daily_product_metrics "
            "ORDER BY metric_name"
        ).fetchall()

    assert columns == {"metric_date", "metric_name", "event_count"}
    assert rows == [
        ("2026-07-19", "almanac_results", 1),
        ("2026-07-19", "oracle_results", 3),
    ]


def test_daily_metrics_store_rejects_arbitrary_or_personal_fields(tmp_path):
    store = DailyMetricsStore(tmp_path / "runtime.db")

    with pytest.raises(ValueError, match="unsupported aggregate metric"):
        store.increment("birth_date")
    with pytest.raises(ValueError, match="positive integer"):
        store.increment("oracle_results", count=0)


def test_weekly_report_combines_product_and_ai_aggregates(tmp_path):
    runtime_db = tmp_path / "runtime.db"
    articles_path = tmp_path / "articles"
    articles_path.mkdir()
    (articles_path / "one.md").write_text("# One", encoding="utf-8")
    store = DailyMetricsStore(runtime_db)
    store.increment(
        "oracle_results",
        count=4,
        now=datetime(2026, 7, 19, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    with closing(sqlite3.connect(runtime_db)) as connection:
        connection.execute("""
            CREATE TABLE ai_daily_usage (
                scope TEXT NOT NULL,
                subject TEXT NOT NULL,
                usage_date TEXT NOT NULL,
                request_count INTEGER NOT NULL,
                PRIMARY KEY (scope, subject, usage_date)
            )
            """)
        connection.execute("INSERT INTO ai_daily_usage VALUES ('global', 'all', '2026-07-19', 3)")
        connection.commit()

    report = generate_report(
        runtime_db,
        date(2026, 7, 19),
        date(2026, 7, 20),
        articles_path,
        "0.0125",
    )

    assert report["published_articles_current"] == 1
    assert report["totals"] == {
        "almanac_results": 0,
        "oracle_results": 4,
        "ai_requests_accepted": 3,
        "estimated_ai_cost_usd": "0.0375",
    }
    assert {"name", "birth_date", "ip_address", "question"}.isdisjoint(report["daily"][0])


def test_successful_product_responses_increment_aggregate_metrics(app, client):
    assert client.post("/get_gua_info", json={"sign_number": 1}).status_code == 200
    assert client.post("/get_gua_info", json={"sign_number": 0}).status_code == 400
    assert client.get("/api/huangli?date=2026-07-19").status_code == 200
    assert client.get("/healthz").status_code == 200

    with closing(sqlite3.connect(app.config["RUNTIME_DB_PATH"])) as connection:
        rows = dict(
            connection.execute(
                "SELECT metric_name, SUM(event_count) FROM daily_product_metrics "
                "GROUP BY metric_name"
            ).fetchall()
        )

    assert rows == {"almanac_results": 1, "oracle_results": 1}
