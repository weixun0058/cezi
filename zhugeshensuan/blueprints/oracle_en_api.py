"""英文算事 API（D12 统一 ``/api/en/*`` 前缀）。

接口：
    POST /api/en/oracle/ask

Payload：
    {"mode": "words", "words": ["love","work","fate"]}
    {"mode": "numbers", "numbers": [123, 45, 678]}

成功响应：
    {"success": true, "data": {"mode":..., "sign_number":..., "transform":[...], "sign":{...}}}

失败响应：
    {"success": false, "error": {"code": "...", "message": "..."}}

错误码（依据 ``docs/business/wise-oracle-error-code-strategy.md``）：
    INVALID_JSON / INVALID_ORACLE_MODE / ORACLE_WORDS_INSUFFICIENT
    INVALID_ORACLE_NUMBER / ORACLE_NUMBERS_ALL_ZERO / CONTENT_NOT_FOUND
"""

from __future__ import annotations

from flask import Blueprint, current_app, request

from ..api_utils import success
from ..error_codes import ErrorCode, failure_with_code
from ..oracle_english import ask_with_numbers, ask_with_words

oracle_en_api_bp = Blueprint("oracle_en_api", __name__, url_prefix="/api/en/oracle")


@oracle_en_api_bp.post("/ask")
def ask():
    """英文算事主接口。"""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return failure_with_code(ErrorCode.INVALID_JSON, "en")

    mode = payload.get("mode")
    signs = current_app.extensions.get("english_signs") or {}

    if mode == "words":
        return _handle_words(payload, signs)
    if mode == "numbers":
        return _handle_numbers(payload, signs)
    return failure_with_code(ErrorCode.INVALID_ORACLE_MODE, "en")


def _handle_words(payload: dict, signs: dict) -> tuple:
    """处理三词模式。"""
    words = payload.get("words")
    if (
        not isinstance(words, list)
        or len(words) != 3
        or any(not isinstance(w, str) for w in words)
    ):
        return failure_with_code(ErrorCode.ORACLE_WORDS_INSUFFICIENT, "en")
    try:
        result = ask_with_words(words, signs)
    except ValueError:
        # 某个词剔除非字母后无字母
        return failure_with_code(ErrorCode.ORACLE_WORDS_INSUFFICIENT, "en")
    if result.get("sign") is None:
        return failure_with_code(ErrorCode.CONTENT_NOT_FOUND, "en")
    return success(result)


def _handle_numbers(payload: dict, signs: dict) -> tuple:
    """处理三数字模式。"""
    numbers = payload.get("numbers")
    if (
        not isinstance(numbers, list)
        or len(numbers) != 3
        or any(isinstance(v, bool) or not isinstance(v, int) for v in numbers)
    ):
        return failure_with_code(ErrorCode.INVALID_ORACLE_NUMBER, "en")
    if any(not 0 <= v <= 999 for v in numbers):
        return failure_with_code(ErrorCode.INVALID_ORACLE_NUMBER, "en")
    if all(v == 0 for v in numbers):
        return failure_with_code(ErrorCode.ORACLE_NUMBERS_ALL_ZERO, "en")
    try:
        result = ask_with_numbers(numbers, signs)
    except ValueError:
        # 理论上前置校验已覆盖，兜底
        return failure_with_code(ErrorCode.INVALID_ORACLE_NUMBER, "en")
    if result.get("sign") is None:
        return failure_with_code(ErrorCode.CONTENT_NOT_FOUND, "en")
    return success(result)
