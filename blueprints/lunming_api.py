import json
import logging

from flask import Blueprint, Response, current_app, request, stream_with_context

from api_utils import failure, success
from bazi_service import BaziInputError
from lunming import ModelConfigurationError

LOGGER = logging.getLogger(__name__)
lunming_bp = Blueprint("lunming_api", __name__)


def _payload_from_request():
    payload = request.get_json(silent=True) if request.method == "POST" else request.args.to_dict()
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
    if request.method == "GET":
        payload["use_true_solar_time"] = (
            str(payload.get("use_true_solar_time", "false")).lower() == "true"
        )
    return payload


def _sse(payload):
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@lunming_bp.post("/api/lunming/analyze")
def analyze_bazi():
    try:
        payload = _payload_from_request()
        result = current_app.extensions["lunming"].analyze_bazi(payload)
        return success(result)
    except BaziInputError as exc:
        return failure("INVALID_BIRTH_DATA", str(exc))
    except ModelConfigurationError as exc:
        return failure("MODEL_NOT_CONFIGURED", str(exc), 503)
    except Exception:
        LOGGER.exception("Bazi analysis failed")
        return failure("ANALYSIS_FAILED", "分析服务暂时不可用", 502)


@lunming_bp.route("/api/lunming/stream", methods=["GET", "POST"])
def stream_bazi_analysis():
    try:
        payload = _payload_from_request()
        service = current_app.extensions["lunming"]
        service.build_chart(payload)
    except BaziInputError as exc:
        return failure("INVALID_BIRTH_DATA", str(exc))

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

    response = Response(generate(), mimetype="text/event-stream")
    response.headers.update(
        {
            "Cache-Control": "no-cache, no-store",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )
    if request.method == "GET":
        response.headers.update(
            {
                "Deprecation": "true",
                "Sunset": "Wed, 31 Dec 2026 23:59:59 GMT",
                "Link": '</api/lunming/stream>; rel="successor-version"',
            }
        )
    return response
