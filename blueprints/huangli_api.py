import json
from datetime import datetime

from flask import Blueprint, current_app, request

from api_utils import failure, success

huangli_bp = Blueprint("huangli_api", __name__)
SCENARIOS = {
    "结婚": ("嫁娶", "结婚"),
    "搬家": ("移徙", "入宅", "搬家"),
    "开业": ("开市", "开业"),
    "出行": ("出行",),
    "签约": ("立券", "交易", "签约"),
    "理发": ("剃头", "理发"),
}


def _normalize_huangli(record):
    if isinstance(record.get("festivals"), str):
        try:
            record["festivals"] = json.loads(record["festivals"])
        except json.JSONDecodeError:
            record["festivals"] = []
    return record


def _scenario_result(record, scenario):
    if not scenario:
        return record
    keywords = SCENARIOS[scenario]
    suitable = record.get("suitable", "")
    unsuitable = record.get("unsuitable", "")
    suitable_matches = [word for word in keywords if word in suitable]
    unsuitable_matches = [word for word in keywords if word in unsuitable]
    status = "宜" if suitable_matches else "忌" if unsuitable_matches else "未载"
    record["scenario_assessment"] = {
        "scenario": scenario,
        "status": status,
        "suitable_matches": suitable_matches,
        "unsuitable_matches": unsuitable_matches,
    }
    return record


def _get_scenario():
    scenario = request.args.get("scenario", "")
    if scenario and scenario not in SCENARIOS:
        return None
    return scenario


@huangli_bp.get("/api/huangli")
def get_huangli():
    date_text = request.args.get("date") or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return failure("INVALID_DATE", "日期格式无效，请使用 YYYY-MM-DD")
    scenario = _get_scenario()
    if scenario is None:
        return failure("INVALID_SCENARIO", "不支持的场景筛选")
    record = current_app.extensions["huangli"].get_daily_huangli(date_text)
    if not record:
        return failure("HUANGLI_NOT_FOUND", "无法获取黄历数据", 404)
    return success(_scenario_result(_normalize_huangli(record), scenario))


@huangli_bp.get("/api/week_huangli")
def get_week_huangli():
    scenario = _get_scenario()
    if scenario is None:
        return failure("INVALID_SCENARIO", "不支持的场景筛选")
    records = current_app.extensions["huangli"].get_week_huangli()
    data = [_scenario_result(_normalize_huangli(item), scenario) for item in records]
    return success(data)


@huangli_bp.get("/api/pzbj_explanation")
def get_pzbj_explanation():
    text = request.args.get("text", "").strip()
    if not text or len(text) > 100:
        return failure("INVALID_TEXT", "彭祖百忌文本不能为空且不能超过 100 字")
    explanation = current_app.extensions["pzbj"].get(text)
    if explanation is None:
        return failure("EXPLANATION_NOT_FOUND", "未找到对应解释", 404)
    return success({"text": text, "explanation": explanation})
