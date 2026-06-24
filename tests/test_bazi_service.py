import pytest

from zhugeshensuan.bazi_service import BaziInputError, calculate_bazi


def test_calculates_deterministic_pillars_and_luck_cycles():
    chart = calculate_bazi(
        {
            "gender": "男",
            "birth_date": "1990-01-01",
            "birth_time": "12:30",
            "timezone": "Asia/Shanghai",
        }
    )
    assert chart["pillars"] == {"year": "己巳", "month": "丙子", "day": "丙寅", "time": "甲午"}
    assert len(chart["luck_cycles"]["cycles"]) == 8


def test_unknown_birth_time_omits_time_pillar():
    chart = calculate_bazi({"gender": "女", "birth_date": "1990-01-01", "birth_time": "未知"})
    assert chart["pillars"]["time"] is None
    assert chart["limitations"]


def test_true_solar_time_requires_known_time_and_longitude():
    with pytest.raises(BaziInputError):
        calculate_bazi(
            {
                "gender": "男",
                "birth_date": "1990-01-01",
                "birth_time": "未知",
                "use_true_solar_time": True,
                "longitude": 116.4,
            }
        )


def test_true_solar_correction_is_bounded_for_beijing():
    chart = calculate_bazi(
        {
            "gender": "男",
            "birth_date": "1990-01-01",
            "birth_time": "12:30",
            "use_true_solar_time": True,
            "longitude": 116.4,
        }
    )
    assert -30 < chart["calendar"]["correction_minutes"] < 0
