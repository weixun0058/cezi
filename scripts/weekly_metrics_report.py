import argparse
import json
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

METRIC_NAMES = ("almanac_results", "oracle_results")


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def _date_range(start_date, end_date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def _readonly_connection(path):
    resolved = Path(path).resolve().as_posix()
    connection = sqlite3.connect(f"file:{resolved}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def generate_report(runtime_db, start_date, end_date, articles_path, ai_unit_cost_usd):
    if start_date > end_date:
        raise ValueError("start date must not be after end date")
    try:
        unit_cost = Decimal(str(ai_unit_cost_usd))
    except InvalidOperation as exc:
        raise ValueError("AI unit cost must be numeric") from exc
    if unit_cost < 0:
        raise ValueError("AI unit cost must not be negative")

    daily = {
        day.isoformat(): {
            "date": day.isoformat(),
            "almanac_results": 0,
            "oracle_results": 0,
            "ai_requests_accepted": 0,
        }
        for day in _date_range(start_date, end_date)
    }

    with closing(_readonly_connection(runtime_db)) as connection:
        product_rows = connection.execute(
            """
            SELECT metric_date, metric_name, event_count
            FROM daily_product_metrics
            WHERE metric_date BETWEEN ? AND ?
            """,
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
        ai_rows = connection.execute(
            """
            SELECT usage_date, request_count
            FROM ai_daily_usage
            WHERE scope = 'global' AND subject = 'all'
              AND usage_date BETWEEN ? AND ?
            """,
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchall()

    for row in product_rows:
        if row["metric_name"] in METRIC_NAMES and row["metric_date"] in daily:
            daily[row["metric_date"]][row["metric_name"]] = row["event_count"]
    for row in ai_rows:
        if row["usage_date"] in daily:
            daily[row["usage_date"]]["ai_requests_accepted"] = row["request_count"]

    totals = {
        metric: sum(item[metric] for item in daily.values())
        for metric in (*METRIC_NAMES, "ai_requests_accepted")
    }
    totals["estimated_ai_cost_usd"] = str(
        (Decimal(totals["ai_requests_accepted"]) * unit_cost).quantize(Decimal("0.0001"))
    )
    article_root = Path(articles_path)
    published_articles = (
        sum(1 for path in article_root.rglob("*.md") if path.is_file())
        if article_root.is_dir()
        else 0
    )

    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "privacy_boundary": (
            "Aggregates only: no names, birth data, IP addresses, device IDs, "
            "questions, or result text."
        ),
        "published_articles_current": published_articles,
        "ai_unit_cost_usd": str(unit_cost),
        "daily": list(daily.values()),
        "totals": totals,
    }


def build_parser():
    parser = argparse.ArgumentParser(description="Export privacy-friendly weekly product metrics")
    parser.add_argument("--runtime-db", required=True)
    parser.add_argument("--articles-path", required=True)
    parser.add_argument("--start", required=True, type=_parse_date)
    parser.add_argument("--end", required=True, type=_parse_date)
    parser.add_argument("--ai-unit-cost-usd", default="0")
    parser.add_argument("--output", type=Path)
    return parser


def main():
    args = build_parser().parse_args()
    report = generate_report(
        args.runtime_db,
        args.start,
        args.end,
        args.articles_path,
        args.ai_unit_cost_usd,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
