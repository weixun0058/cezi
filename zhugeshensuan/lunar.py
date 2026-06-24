"""Command-line example for daily lunar-calendar data."""

import json

from .huangli import HuangLi


def get_lunar_day(date_text):
    service = HuangLi("instance/huangli.db")
    return service.get_daily_huangli(date_text)


if __name__ == "__main__":
    print(json.dumps(get_lunar_day("2026-06-18"), ensure_ascii=False, indent=2))
