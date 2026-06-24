import json
import logging

from flask import Blueprint, Response, current_app, make_response, request, stream_with_context

from ..ai_usage import DEVICE_COOKIE, UsageLimitError
from ..api_utils import failure, success
from ..bazi_service import BaziInputError
from ..lunming import ModelConfigurationError

LOGGER = logging.getLogger(__name__)
lunming_bp = Blueprint("lunming_api", __name__)


def _payload_from_request():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise BaziInputError("请求体必须是 JSON 对象")
    if (
        not isinstance(payload.get("name"), str)
        or not payload["name"].strip()
        or len(payload["name"]) > 30
    ):
        raise BaziInputError("姓名不能为空且不能超过 30 字")
    if not isinstance(payload.get("birth_date"), str):
        raise BaziInputError("请提供出生日期")
    birth_time = payload.get("birth_time")
    if birth_time is not None and not isinstance(birth_time, str):
        raise BaziInputError("出生时间格式无效")
    return payload


def _sse(payload):
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _acquire_usage():
    policy = current_app.extensions["ai_usage"]
    client_id, signed_client_id = policy.resolve_client(request.cookies.get(DEVICE_COOKIE))
    grant = policy.acquire(client_id, request.remote_addr or "unknown")
    return policy, grant, signed_client_id


def _set_device_cookie(response, signed_client_id):
    response.set_cookie(
        DEVICE_COOKIE,
        signed_client_id,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        secure=request.is_secure,
        samesite="Lax",
    )
    return response


def _limit_response(error, signed_client_id=None):
    response = make_response(failure(error.code, error.message, 429))
    response.headers["Retry-After"] = str(error.retry_after)
    if signed_client_id:
        _set_device_cookie(response, signed_client_id)
    return response


@lunming_bp.post("/api/lunming/analyze")
def analyze_bazi():
    policy = None
    grant = None
    signed_client_id = None
    try:
        payload = _payload_from_request()
        service = current_app.extensions["lunming"]
        service.build_chart(payload)
        policy, grant, signed_client_id = _acquire_usage()
        result = service.analyze_bazi(payload)
        return _set_device_cookie(make_response(success(result)), signed_client_id)
    except BaziInputError as exc:
        return failure("INVALID_BIRTH_DATA", str(exc))
    except UsageLimitError as exc:
        return _limit_response(exc, signed_client_id)
    except ModelConfigurationError as exc:
        response = make_response(failure("MODEL_NOT_CONFIGURED", str(exc), 503))
        return _set_device_cookie(response, signed_client_id) if signed_client_id else response
    except Exception:
        LOGGER.exception("Bazi analysis failed")
        response = make_response(failure("ANALYSIS_FAILED", "分析服务暂时不可用", 502))
        return _set_device_cookie(response, signed_client_id) if signed_client_id else response
    finally:
        if policy and grant:
            policy.release(grant.lease_id)


@lunming_bp.post("/api/lunming/stream")
def stream_bazi_analysis():
    signed_client_id = None
    try:
        payload = _payload_from_request()
        service = current_app.extensions["lunming"]
        service.build_chart(payload)
        policy, grant, signed_client_id = _acquire_usage()
    except BaziInputError as exc:
        return failure("INVALID_BIRTH_DATA", str(exc))
    except UsageLimitError as exc:
        return _limit_response(exc, signed_client_id)

    @stream_with_context
    def generate():
        try:
            for event in service.analyze_bazi_stream(payload):
                yield _sse(event)
            yield _sse({"type": "done", "done": True})
        except ModelConfigurationError as exc:
            yield _sse({"type": "error", "error": str(exc)})
            yield _sse({"type": "done", "done": True})
        except GeneratorExit:
            LOGGER.info("Client closed bazi stream")
        except Exception:
            LOGGER.exception("Bazi stream failed")
            yield _sse({"type": "error", "error": "分析流意外中断，请重试"})
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
