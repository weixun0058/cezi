"""English Chinese-almanac API."""

from datetime import datetime

from flask import Blueprint, current_app, request

from ..api_utils import success
from ..error_codes import ErrorCode, failure_with_code

huangli_en_api_bp = Blueprint("huangli_en_api", __name__, url_prefix="/api/en")
LANG = "en"


def _scenario():
    scenario = request.args.get("scenario", "").strip()
    supported = current_app.extensions["huangli_scenarios_en"].get("scenarios", {})
    if scenario and scenario not in supported:
        return None
    return scenario


def _debug_enabled() -> bool:
    return request.args.get("debug", "").strip().lower() in {"1", "true", "yes", "on"}


@huangli_en_api_bp.get("/daily-almanac")
def daily_almanac():
    date_text = request.args.get("date") or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return failure_with_code(ErrorCode.INVALID_DATE, LANG)

    scenario = _scenario()
    if scenario is None:
        return failure_with_code(ErrorCode.INVALID_SCENARIO, LANG)

    try:
        record = current_app.extensions["huangli"].get_daily_huangli(date_text)
    except ValueError:
        return failure_with_code(ErrorCode.INVALID_DATE, LANG)
    if not record:
        return failure_with_code(ErrorCode.HUANGLI_NOT_FOUND, LANG)

    data = current_app.extensions["huangli_en"].translate_daily(
        dict(record), scenario=scenario, debug=_debug_enabled()
    )
    return success(data)


@huangli_en_api_bp.get("/week-almanac")
def week_almanac():
    scenario = _scenario()
    if scenario is None:
        return failure_with_code(ErrorCode.INVALID_SCENARIO, LANG)

    records = current_app.extensions["huangli"].get_week_huangli()
    data = current_app.extensions["huangli_en"].translate_week(
        [dict(record) for record in records],
        scenario=scenario,
        debug=_debug_enabled(),
    )
    return success(data)
