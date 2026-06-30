"""英文 Birth Chart Reading API 蓝图（D12 统一 ``/api/en/*`` 前缀）。

接口：
    POST /api/en/birth-chart/analyze   同步分析（基础盘 + AI 报告）
    POST /api/en/birth-chart/stream    SSE 流式分析

Payload：
    {
        "name": "Alex",
        "birth_date": "1990-05-01",
        "birth_time": "14:30",          # 可选；birth_time_unknown=true 时忽略
        "birth_time_unknown": false,    # 可选
        "gender": "male",               # male / female
        "timezone": "Asia/Shanghai"     # 可选，默认 DEFAULT_TIMEZONE
    }

成功响应（analyze）：
    {
        "success": true,
        "data": {
            "chart_summary": {...},
            "element_balance": {...},
            "reflection_points": [...],
            "cautions": [...],
            "responsible_use": "...",
            "limitations": [...]
        }
    }

SSE 事件序列（stream）：
    data: {"type": "chart", ...}
    data: {"type": "report", ...}
    data: {"type": "responsible_use", ...}
    data: {"type": "done", "done": true}

错误码（依据 ``docs/business/wise-oracle-error-code-strategy.md``）：
    INVALID_JSON / INVALID_BIRTH_DATA / MODEL_NOT_CONFIGURED / ANALYSIS_FAILED
    AI_DAILY_QUOTA_EXHAUSTED / AI_GLOBAL_QUOTA_EXHAUSTED / AI_RATE_LIMITED / AI_CONCURRENCY_LIMITED

依据：
- W6.2 英文论命后端边界（``docs/plans/2026-06-27-english-site-execution-plan.md``）
- W0.3 AI prompt 边界（``docs/business/wise-oracle-ai-prompt-boundaries.md``）
- D12（``/api/en/*`` 前缀）、D17（interpretation 非 prediction）

注：stream 端点用 POST 而非 GET，与中文 ``lunming_api.py`` 一致，便于传递 JSON body。
执行计划原写 GET，此处修正为 POST（见执行计划变更日志）。
"""

from __future__ import annotations

import json
import logging

from flask import (
    Blueprint,
    Response,
    current_app,
    make_response,
    request,
    stream_with_context,
)

from ..ai_usage import DEVICE_COOKIE, UsageLimitError
from ..api_utils import success
from ..bazi_service import BaziInputError
from ..error_codes import ErrorCode, failure_with_code
from ..lunming import ModelConfigurationError

LOGGER = logging.getLogger(__name__)
birth_chart_en_api_bp = Blueprint(
    "birth_chart_en_api", __name__, url_prefix="/api/en/birth-chart"
)

LANG = "en"


def _payload_from_request() -> dict:
    """校验并返回英文 birth chart payload。

    输入：当前请求 JSON
    输出：payload dict
    异常：BaziInputError（字段缺失/无效）
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise BaziInputError("Request body must be a JSON object")
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 30:
        raise BaziInputError("Name must be a non-empty string of at most 30 characters")
    if not isinstance(payload.get("birth_date"), str):
        raise BaziInputError("Birth date is required")
    birth_time = payload.get("birth_time")
    if birth_time is not None and not isinstance(birth_time, str):
        raise BaziInputError("Birth time must be a string or null")
    if "birth_time_unknown" in payload and not isinstance(
        payload.get("birth_time_unknown"), bool
    ):
        raise BaziInputError("birth_time_unknown must be a boolean")
    return payload


def _sse(payload: dict) -> str:
    """格式化 SSE data 帧。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _acquire_usage():
    """获取 AI 用量配额。返回 (policy, grant, signed_client_id)。"""
    policy = current_app.extensions["ai_usage"]
    client_id, signed_client_id = policy.resolve_client(
        request.cookies.get(DEVICE_COOKIE)
    )
    grant = policy.acquire(client_id, request.remote_addr or "unknown")
    return policy, grant, signed_client_id


def _set_device_cookie(response, signed_client_id):
    """写入设备 Cookie（用于跨请求识别同一设备的用量）。"""
    response.set_cookie(
        DEVICE_COOKIE,
        signed_client_id,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        secure=request.is_secure,
        samesite="Lax",
    )
    return response


def _limit_response(error: UsageLimitError, signed_client_id=None):
    """构造用量超限响应（429 + Retry-After）。"""
    response = make_response(failure_with_code(error.code, LANG))
    response.headers["Retry-After"] = str(error.retry_after)
    if signed_client_id:
        _set_device_cookie(response, signed_client_id)
    return response


@birth_chart_en_api_bp.post("/analyze")
def analyze():
    """同步分析：基础盘 + AI 报告。"""
    policy = None
    grant = None
    signed_client_id = None
    try:
        payload = _payload_from_request()
        service = current_app.extensions["birth_chart_en"]
        # 先做基础盘校验，确保输入合法再消耗配额
        service.build_chart_summary(payload)
        policy, grant, signed_client_id = _acquire_usage()
        result = service.analyze(payload)
        return _set_device_cookie(make_response(success(result)), signed_client_id)
    except BaziInputError:
        return failure_with_code(ErrorCode.INVALID_BIRTH_DATA, LANG)
    except UsageLimitError as exc:
        return _limit_response(exc, signed_client_id)
    except ModelConfigurationError:
        return failure_with_code(ErrorCode.MODEL_NOT_CONFIGURED, LANG)
    except Exception:
        LOGGER.exception("English birth chart analysis failed")
        response = make_response(failure_with_code(ErrorCode.ANALYSIS_FAILED, LANG))
        return (
            _set_device_cookie(response, signed_client_id)
            if signed_client_id
            else response
        )
    finally:
        if policy and grant:
            policy.release(grant.lease_id)


@birth_chart_en_api_bp.post("/stream")
def stream():
    """SSE 流式分析。事件：chart → report → responsible_use → done。"""
    signed_client_id = None
    try:
        payload = _payload_from_request()
        service = current_app.extensions["birth_chart_en"]
        service.build_chart_summary(payload)
        policy, grant, signed_client_id = _acquire_usage()
    except BaziInputError:
        return failure_with_code(ErrorCode.INVALID_BIRTH_DATA, LANG)
    except UsageLimitError as exc:
        return _limit_response(exc, signed_client_id)

    @stream_with_context
    def generate():
        try:
            for event in service.analyze_stream(payload):
                yield _sse(event)
            yield _sse({"type": "done", "done": True})
        except ModelConfigurationError:
            yield _sse({"type": "error", "error_code": ErrorCode.MODEL_NOT_CONFIGURED})
            yield _sse({"type": "done", "done": True})
        except GeneratorExit:
            LOGGER.info("Client closed English birth chart stream")
        except Exception:
            LOGGER.exception("English birth chart stream failed")
            yield _sse({"type": "error", "error_code": ErrorCode.ANALYSIS_FAILED})
            yield _sse({"type": "done", "done": True})
        finally:
            policy.release(grant.lease_id)

    response = Response(generate(), mimetype="text/event-stream")
    response.headers.update(
        {
            "Cache-Control": "no-cache, no-store",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )
    return _set_device_cookie(response, signed_client_id)
