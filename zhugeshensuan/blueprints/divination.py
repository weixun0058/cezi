from flask import Blueprint, current_app, request

from ..api_utils import failure, success
from ..utils import cale_character_count

divination_bp = Blueprint("divination", __name__)


@divination_bp.post("/get_strokes")
def get_strokes():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return failure("INVALID_JSON", "请求体必须是 JSON 对象")
    character = payload.get("character")
    if not isinstance(character, str) or len(character) != 1:
        return failure("INVALID_CHARACTER", "请输入一个汉字")

    strokes = current_app.extensions["database"].get_stroke_count(character)
    if strokes is None:
        return failure("STROKE_NOT_FOUND", "暂时无法查询该字笔画", 404)
    return success({"strokes": strokes}, strokes=strokes)


@divination_bp.post("/calculate_sign")
def calculate_sign():
    payload = request.get_json(silent=True)
    strokes = payload.get("strokes") if isinstance(payload, dict) else None
    if (
        not isinstance(strokes, list)
        or len(strokes) != 3
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > 100
            for value in strokes
        )
    ):
        return failure("INVALID_STROKES", "笔画必须是三个 1 到 100 的整数")
    sign_number = cale_character_count(*strokes)
    return success({"sign_number": sign_number}, sign_number=sign_number)


@divination_bp.post("/get_gua_info")
def get_gua_info():
    payload = request.get_json(silent=True)
    sign_number = payload.get("sign_number") if isinstance(payload, dict) else None
    if (
        isinstance(sign_number, bool)
        or not isinstance(sign_number, int)
        or not 1 <= sign_number <= 383
    ):
        return failure("INVALID_SIGN", "签号必须是 1 到 383 的整数")
    # g.lang 由 before_request 钩子根据 URL/Header 设置
    result = current_app.extensions["database"].get_gua_info(sign_number)
    if result is None:
        return failure("SIGN_NOT_FOUND", "未找到对应签文", 404)
    return success(result, **result)
