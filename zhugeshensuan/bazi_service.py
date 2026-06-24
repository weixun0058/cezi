import math
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from lunar_python import Solar

TIME_BRANCH_HOURS = {
    "子": 0,
    "丑": 2,
    "寅": 4,
    "卯": 6,
    "辰": 8,
    "巳": 10,
    "午": 12,
    "未": 14,
    "申": 16,
    "酉": 18,
    "戌": 20,
    "亥": 22,
}
ELEMENTS = "金木水火土"


class BaziInputError(ValueError):
    pass


def _parse_birth_datetime(birth_date, birth_time, timezone_name):
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise BaziInputError("不支持的时区") from exc

    unknown_time = birth_time in {None, "", "未知", "unknown"}
    if unknown_time:
        hour, minute = 12, 0
    elif birth_time in TIME_BRANCH_HOURS:
        hour, minute = TIME_BRANCH_HOURS[birth_time], 0
    else:
        try:
            parsed_time = datetime.strptime(birth_time, "%H:%M")
            hour, minute = parsed_time.hour, parsed_time.minute
        except (TypeError, ValueError) as exc:
            raise BaziInputError("出生时间应为 HH:MM、十二时辰或未知") from exc

    try:
        parsed_date = datetime.strptime(birth_date, "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise BaziInputError("出生日期应为 YYYY-MM-DD") from exc

    return parsed_date.replace(hour=hour, minute=minute, tzinfo=timezone), unknown_time


def true_solar_correction(local_dt, longitude):
    """Approximate apparent solar-time correction in minutes."""
    offset_hours = local_dt.utcoffset().total_seconds() / 3600
    standard_meridian = offset_hours * 15
    day_number = local_dt.timetuple().tm_yday
    angle = 2 * math.pi * (day_number - 81) / 364
    equation_of_time = 9.87 * math.sin(2 * angle) - 7.53 * math.cos(angle) - 1.5 * math.sin(angle)
    return 4 * (float(longitude) - standard_meridian) + equation_of_time


def _safe_call(target, method, default=""):
    function = getattr(target, method, None)
    if not function:
        return default
    try:
        return function()
    except (AttributeError, TypeError, ValueError):
        return default


def _build_luck_cycles(eight_char, gender):
    try:
        yun = eight_char.getYun(1 if gender == "男" else 0)
        cycles = []
        for item in yun.getDaYun()[1:9]:
            cycles.append(
                {
                    "gan_zhi": item.getGanZhi(),
                    "start_year": item.getStartYear(),
                    "end_year": item.getEndYear(),
                    "start_age": item.getStartAge(),
                    "end_age": item.getEndAge(),
                }
            )
        return {
            "start": {
                "years": yun.getStartYear(),
                "months": yun.getStartMonth(),
                "days": yun.getStartDay(),
            },
            "cycles": cycles,
        }
    except (AttributeError, TypeError, ValueError, IndexError):
        return {"start": None, "cycles": []}


def calculate_bazi(payload, default_timezone="Asia/Shanghai"):
    gender = payload.get("gender", "男")
    if gender not in {"男", "女"}:
        raise BaziInputError("性别应为男或女")

    timezone_name = payload.get("timezone") or default_timezone
    local_dt, unknown_time = _parse_birth_datetime(
        payload.get("birth_date"), payload.get("birth_time"), timezone_name
    )
    correction_minutes = 0.0
    use_true_solar_time = bool(payload.get("use_true_solar_time", False))
    longitude = payload.get("longitude")
    if use_true_solar_time:
        if unknown_time:
            raise BaziInputError("时辰未知时不能启用真太阳时")
        if longitude is None:
            raise BaziInputError("启用真太阳时必须提供经度")
        try:
            longitude = float(longitude)
        except (TypeError, ValueError) as exc:
            raise BaziInputError("经度必须是数字") from exc
        if not -180 <= longitude <= 180:
            raise BaziInputError("经度必须在 -180 到 180 之间")
        correction_minutes = true_solar_correction(local_dt, longitude)
        local_dt += timedelta(minutes=correction_minutes)

    solar = Solar.fromYmdHms(
        local_dt.year, local_dt.month, local_dt.day, local_dt.hour, local_dt.minute, local_dt.second
    )
    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()

    pillars = {
        "year": eight_char.getYear(),
        "month": eight_char.getMonth(),
        "day": eight_char.getDay(),
        "time": None if unknown_time else eight_char.getTime(),
    }
    wu_xing = {
        "year": _safe_call(eight_char, "getYearWuXing"),
        "month": _safe_call(eight_char, "getMonthWuXing"),
        "day": _safe_call(eight_char, "getDayWuXing"),
        "time": None if unknown_time else _safe_call(eight_char, "getTimeWuXing"),
    }
    counts = Counter(
        char for value in wu_xing.values() if value for char in value if char in ELEMENTS
    )
    na_yin = {
        "year": _safe_call(eight_char, "getYearNaYin"),
        "month": _safe_call(eight_char, "getMonthNaYin"),
        "day": _safe_call(eight_char, "getDayNaYin"),
        "time": None if unknown_time else _safe_call(eight_char, "getTimeNaYin"),
    }

    return {
        "calendar": {
            "local_datetime": local_dt.isoformat(),
            "timezone": timezone_name,
            "true_solar_time": use_true_solar_time,
            "longitude": longitude if use_true_solar_time else None,
            "birth_place": payload.get("birth_place", ""),
            "correction_minutes": round(correction_minutes, 2),
            "lunar_date": (
                f"{lunar.getYearInChinese()}年"
                f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
            ),
        },
        "pillars": pillars,
        "time_unknown": unknown_time,
        "zodiac": lunar.getYearShengXiao(),
        "wu_xing": wu_xing,
        "wu_xing_counts": {element: counts.get(element, 0) for element in ELEMENTS},
        "na_yin": na_yin,
        "day_master": eight_char.getDayGan(),
        "luck_cycles": _build_luck_cycles(eight_char, gender),
        "limitations": ["出生时辰未知，时柱及依赖时柱的内容未计算"] if unknown_time else [],
    }
