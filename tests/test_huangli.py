from datetime import datetime

from huangli import HuangLi


def test_cache_hit_does_not_regenerate(tmp_path, monkeypatch):
    service = HuangLi(tmp_path / "huangli.db")
    original = service._generate_huangli_data
    calls = 0

    def counted(date_text):
        nonlocal calls
        calls += 1
        return original(date_text)

    monkeypatch.setattr(service, "_generate_huangli_data", counted)
    first = service.get_daily_huangli("2026-06-18")
    second = service.get_daily_huangli("2026-06-18")
    assert first["date"] == second["date"]
    assert calls == 1


def test_solar_term_day_points_to_following_term(tmp_path):
    record = HuangLi(tmp_path / "huangli.db").get_daily_huangli("2026-06-21")
    assert record["solar_term"] == "夏至"
    assert record["next_solar_term"] == "小暑"
    assert record["next_solar_term_days"] > 0


def test_leap_lunar_month_is_preserved(tmp_path):
    record = HuangLi(tmp_path / "huangli.db").get_daily_huangli("2025-07-25")
    assert record["lunar_date"].startswith("闰六月")


def test_week_contains_nine_days(tmp_path):
    records = HuangLi(tmp_path / "huangli.db").get_week_huangli(datetime(2026, 6, 18))
    assert len(records) == 9
