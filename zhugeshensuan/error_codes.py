"""错误码模块。

定义所有 API 错误码的稳定 code 常量、中英文消息映射、HTTP status 对应关系。
依据：docs/business/wise-oracle-error-code-strategy.md（W1.2 定稿）

设计原则：
1. code 优先于 message：前端按 error.code 做差异化处理
2. code 稳定不变：一旦定义，code 字符串不随 message 文案调整而改变
3. 中英文双语：每个 code 同时有中文和英文消息
4. HTTP status 与 code 对应：同一 code 对应固定 status

使用方式：
    # 英文 API（推荐）
    from .error_codes import failure_with_code, ErrorCode
    return failure_with_code(ErrorCode.INVALID_ORACLE_NUMBER, "en")

    # 中文 API（现有调用保持不变）
    from .api_utils import failure
    return failure("INVALID_ORACLE_NUMBER", "Each number must be between 0 and 999.", 400)
"""

from __future__ import annotations

from typing import Optional

from .api_utils import failure


class ErrorCode:
    """错误码常量。

    依据 wise-oracle-error-code-strategy.md 第二节（现有 21 个）+ 第三节（英文版新增 6 个）。
    """

    # 通用错误（app.py）
    NOT_READY = "NOT_READY"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    NOT_FOUND = "NOT_FOUND"

    # 黄历 API（huangli_api.py）
    INVALID_DATE = "INVALID_DATE"
    INVALID_SCENARIO = "INVALID_SCENARIO"
    HUANGLI_NOT_FOUND = "HUANGLI_NOT_FOUND"
    INVALID_TEXT = "INVALID_TEXT"
    EXPLANATION_NOT_FOUND = "EXPLANATION_NOT_FOUND"

    # 算事 API（divination.py，中文版现有）
    INVALID_JSON = "INVALID_JSON"
    INVALID_CHARACTER = "INVALID_CHARACTER"
    STROKE_NOT_FOUND = "STROKE_NOT_FOUND"
    INVALID_STROKES = "INVALID_STROKES"
    INVALID_SIGN = "INVALID_SIGN"
    SIGN_NOT_FOUND = "SIGN_NOT_FOUND"

    # 论命 API（lunming_api.py + ai_usage.py）
    INVALID_BIRTH_DATA = "INVALID_BIRTH_DATA"
    MODEL_NOT_CONFIGURED = "MODEL_NOT_CONFIGURED"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    AI_DAILY_QUOTA_EXHAUSTED = "AI_DAILY_QUOTA_EXHAUSTED"
    AI_GLOBAL_QUOTA_EXHAUSTED = "AI_GLOBAL_QUOTA_EXHAUSTED"
    AI_RATE_LIMITED = "AI_RATE_LIMITED"
    AI_CONCURRENCY_LIMITED = "AI_CONCURRENCY_LIMITED"

    # 英文版新增（W4/W6 专用）
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_ORACLE_MODE = "INVALID_ORACLE_MODE"
    ORACLE_WORDS_INSUFFICIENT = "ORACLE_WORDS_INSUFFICIENT"
    INVALID_ORACLE_NUMBER = "INVALID_ORACLE_NUMBER"
    ORACLE_NUMBERS_ALL_ZERO = "ORACLE_NUMBERS_ALL_ZERO"
    CONTENT_NOT_FOUND = "CONTENT_NOT_FOUND"


# 中文消息映射（zh-hans）
MESSAGES_ZH: dict[str, str] = {
    # 通用
    ErrorCode.NOT_READY: "服务尚未就绪",
    ErrorCode.PAYLOAD_TOO_LARGE: "请求内容过大",
    ErrorCode.NOT_FOUND: "接口不存在",
    # 黄历
    ErrorCode.INVALID_DATE: "日期格式无效，请使用 YYYY-MM-DD",
    ErrorCode.INVALID_SCENARIO: "不支持的场景筛选",
    ErrorCode.HUANGLI_NOT_FOUND: "无法获取黄历数据",
    ErrorCode.INVALID_TEXT: "彭祖百忌文本不能为空且不能超过 100 字",
    ErrorCode.EXPLANATION_NOT_FOUND: "未找到对应解释",
    # 算事
    ErrorCode.INVALID_JSON: "请求体必须是 JSON 对象",
    ErrorCode.INVALID_CHARACTER: "请输入一个汉字",
    ErrorCode.STROKE_NOT_FOUND: "暂时无法查询该字笔画",
    ErrorCode.INVALID_STROKES: "笔画必须是三个 1 到 100 的整数",
    ErrorCode.INVALID_SIGN: "签号必须是 1 到 383 的整数",
    ErrorCode.SIGN_NOT_FOUND: "未找到对应签文",
    # 论命
    ErrorCode.INVALID_BIRTH_DATA: "出生信息格式错误，请检查后重试",
    ErrorCode.MODEL_NOT_CONFIGURED: "分析服务未配置，请联系管理员",
    ErrorCode.ANALYSIS_FAILED: "分析服务暂时不可用",
    ErrorCode.AI_DAILY_QUOTA_EXHAUSTED: "今日免费论命次数已用完",
    ErrorCode.AI_GLOBAL_QUOTA_EXHAUSTED: "今日分析服务额度已用完",
    ErrorCode.AI_RATE_LIMITED: "请求过于频繁，请稍后再试",
    ErrorCode.AI_CONCURRENCY_LIMITED: "分析服务繁忙，请稍后再试",
    # 英文版新增（中文版一般不触发，提供兜底中文消息）
    ErrorCode.INVALID_INPUT: "部分字段缺失或无效，请检查后重试",
    ErrorCode.INVALID_ORACLE_MODE: "输入模式无效，请选择三词或三数字",
    ErrorCode.ORACLE_WORDS_INSUFFICIENT: "请输入恰好三个英文单词",
    ErrorCode.INVALID_ORACLE_NUMBER: "每个数字必须在 0 到 999 之间",
    ErrorCode.ORACLE_NUMBERS_ALL_ZERO: "三组数字不能全为 0",
    ErrorCode.CONTENT_NOT_FOUND: "请求的内容不存在",
}

# 英文消息映射（en）
MESSAGES_EN: dict[str, str] = {
    # 通用
    ErrorCode.NOT_READY: "The service is not ready yet. Please try again later.",
    ErrorCode.PAYLOAD_TOO_LARGE: "The request payload is too large.",
    ErrorCode.NOT_FOUND: "The requested API endpoint does not exist.",
    # 黄历
    ErrorCode.INVALID_DATE: "The date provided was invalid. Please use YYYY-MM-DD.",
    ErrorCode.INVALID_SCENARIO: "The selected scenario is not supported.",
    ErrorCode.HUANGLI_NOT_FOUND: "Could not retrieve almanac data for this date.",
    ErrorCode.INVALID_TEXT: "The text must not be empty and must not exceed 100 characters.",
    ErrorCode.EXPLANATION_NOT_FOUND: "No explanation was found for this item.",
    # 算事
    ErrorCode.INVALID_JSON: "The request body must be a JSON object.",
    ErrorCode.INVALID_CHARACTER: "Please enter a single Chinese character.",
    ErrorCode.STROKE_NOT_FOUND: "Could not determine the stroke count. Please try a different character.",
    ErrorCode.INVALID_STROKES: "Strokes must be three integers between 1 and 100.",
    ErrorCode.INVALID_SIGN: "The sign number must be an integer between 1 and 383.",
    ErrorCode.SIGN_NOT_FOUND: "This oracle sign could not be found.",
    # 论命
    ErrorCode.INVALID_BIRTH_DATA: "The birth data provided was invalid. Please check and try again.",
    ErrorCode.MODEL_NOT_CONFIGURED: "The analysis service is not configured. Please contact support.",
    ErrorCode.ANALYSIS_FAILED: "The analysis service is temporarily unavailable. Please try again later.",
    ErrorCode.AI_DAILY_QUOTA_EXHAUSTED: "Your daily free analysis quota has been used up. Please try again tomorrow.",
    ErrorCode.AI_GLOBAL_QUOTA_EXHAUSTED: "The analysis service quota has been exhausted today. Please try again tomorrow.",
    ErrorCode.AI_RATE_LIMITED: "Too many requests. Please slow down.",
    ErrorCode.AI_CONCURRENCY_LIMITED: "The analysis service is busy. Please try again shortly.",
    # 英文版新增
    ErrorCode.INVALID_INPUT: "Some fields were missing or invalid. Please check and try again.",
    ErrorCode.INVALID_ORACLE_MODE: "Invalid input mode. Choose 'three words' or 'three numbers'.",
    ErrorCode.ORACLE_WORDS_INSUFFICIENT: "Please enter exactly three words.",
    ErrorCode.INVALID_ORACLE_NUMBER: "Each number must be between 0 and 999.",
    ErrorCode.ORACLE_NUMBERS_ALL_ZERO: "The three numbers cannot all be zero.",
    ErrorCode.CONTENT_NOT_FOUND: "The requested content is not available.",
}

# 语言 → 消息映射
MESSAGES_BY_LANG: dict[str, dict[str, str]] = {
    "zh-hans": MESSAGES_ZH,
    "zh-hant": MESSAGES_ZH,  # 繁体暂复用简体消息（运行期繁体化由数据层处理）
    "en": MESSAGES_EN,
}

# code → 默认 HTTP status 映射
DEFAULT_HTTP_STATUS: dict[str, int] = {
    # 通用
    ErrorCode.NOT_READY: 503,
    ErrorCode.PAYLOAD_TOO_LARGE: 413,
    ErrorCode.NOT_FOUND: 404,
    # 黄历
    ErrorCode.INVALID_DATE: 400,
    ErrorCode.INVALID_SCENARIO: 400,
    ErrorCode.HUANGLI_NOT_FOUND: 404,
    ErrorCode.INVALID_TEXT: 400,
    ErrorCode.EXPLANATION_NOT_FOUND: 404,
    # 算事
    ErrorCode.INVALID_JSON: 400,
    ErrorCode.INVALID_CHARACTER: 400,
    ErrorCode.STROKE_NOT_FOUND: 404,
    ErrorCode.INVALID_STROKES: 400,
    ErrorCode.INVALID_SIGN: 400,
    ErrorCode.SIGN_NOT_FOUND: 404,
    # 论命
    ErrorCode.INVALID_BIRTH_DATA: 400,
    ErrorCode.MODEL_NOT_CONFIGURED: 503,
    ErrorCode.ANALYSIS_FAILED: 502,
    ErrorCode.AI_DAILY_QUOTA_EXHAUSTED: 429,
    ErrorCode.AI_GLOBAL_QUOTA_EXHAUSTED: 429,
    ErrorCode.AI_RATE_LIMITED: 429,
    ErrorCode.AI_CONCURRENCY_LIMITED: 429,
    # 英文版新增
    ErrorCode.INVALID_INPUT: 400,
    ErrorCode.INVALID_ORACLE_MODE: 400,
    ErrorCode.ORACLE_WORDS_INSUFFICIENT: 400,
    ErrorCode.INVALID_ORACLE_NUMBER: 400,
    ErrorCode.ORACLE_NUMBERS_ALL_ZERO: 400,
    ErrorCode.CONTENT_NOT_FOUND: 404,
}


def get_message(code: str, lang: str = "en") -> str:
    """返回指定语言的错误消息。

    输入：
        code: 错误码（如 ErrorCode.INVALID_DATE）
        lang: 语言代码（zh-hans / zh-hant / en）
    输出：
        错误消息字符串。若 code 未识别，返回 code 本身作为兜底。
    """
    messages = MESSAGES_BY_LANG.get(lang, MESSAGES_EN)
    return messages.get(code, code)


def get_http_status(code: str) -> int:
    """返回 code 对应的默认 HTTP status。若未识别，返回 400。"""
    return DEFAULT_HTTP_STATUS.get(code, 400)


def failure_with_code(
    code: str,
    lang: str = "en",
    status: Optional[int] = None,
    details: Optional[dict] = None,
    **legacy_fields,
):
    """封装 failure()，按 code 和 lang 自动取消息和 status。

    输入：
        code: 错误码（如 ErrorCode.INVALID_ORACLE_NUMBER）
        lang: 语言代码（zh-hans / zh-hant / en）
        status: 可选，覆盖默认 status
        details: 可选，附加详情
        **legacy_fields: 透传给 failure()
    输出：
        Flask JSON 响应
    """
    message = get_message(code, lang)
    http_status = status if status is not None else get_http_status(code)
    return failure(code, message, http_status, details, **legacy_fields)
