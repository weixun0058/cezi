import logging
import re
import time
import uuid
from pathlib import Path

from flask import Flask, g, request
from werkzeug.middleware.proxy_fix import ProxyFix

from .ai_usage import AIUsagePolicy
from .api_utils import failure, success
from .blueprints import ALL_BLUEPRINTS
from .config import Config, validate_config
from .database import Database
from .huangli import HuangLi
from .logging_config import configure_logging
from .lunming import LunMing

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
CSP = "; ".join(
    (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'self'",
    )
)


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_path=str(PROJECT_ROOT / "instance"),
        template_folder=str(FRONTEND_ROOT / "templates"),
        static_folder=str(FRONTEND_ROOT / "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    validate_config(app.config)
    proxy_hops = app.config["TRUSTED_PROXY_HOPS"]
    if proxy_hops:
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=proxy_hops, x_proto=proxy_hops, x_host=proxy_hops
        )
    configure_logging(app.config.get("APP_DEBUG", False))
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.extensions["database"] = Database(
        app.config["REFERENCE_DB_PATH"], app.config["RUNTIME_DB_PATH"]
    )
    app.extensions["huangli"] = HuangLi(app.config["RUNTIME_DB_PATH"])
    app.extensions["lunming"] = LunMing(
        api_key=app.config["AI_API_KEY"],
        base_url=app.config["AI_BASE_URL"],
        model=app.config["AI_MODEL"],
        timeout=app.config["AI_TIMEOUT_SECONDS"],
        temperature=app.config["AI_TEMPERATURE"],
        default_timezone=app.config["DEFAULT_TIMEZONE"],
    )
    app.extensions["ai_usage"] = AIUsagePolicy(
        runtime_db=app.config["RUNTIME_DB_PATH"],
        secret_key=app.config["SECRET_KEY"],
        global_daily_limit=app.config["AI_GLOBAL_DAILY_LIMIT"],
        daily_limit=app.config["AI_DAILY_LIMIT"],
        rate_limit=app.config["AI_RATE_LIMIT_PER_MINUTE"],
        max_concurrent=app.config["AI_MAX_CONCURRENT"],
        lease_seconds=int(app.config["AI_TIMEOUT_SECONDS"] + 30),
    )
    app.extensions["pzbj"] = app.extensions["database"].load_pzbj()

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    @app.before_request
    def start_request_timer():
        g.request_started = time.monotonic()
        supplied_request_id = request.headers.get("X-Request-ID", "")
        g.request_id = (
            supplied_request_id
            if REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
            else uuid.uuid4().hex
        )

    @app.after_request
    def add_security_headers(response):
        duration_ms = (time.monotonic() - getattr(g, "request_started", time.monotonic())) * 1000
        LOGGER.info(
            "%s %s %s %.1fms request_id=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            g.request_id,
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Content-Security-Policy", CSP)
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("X-Request-ID", g.request_id)
        return response

    @app.get("/healthz")
    def healthcheck():
        return success({"status": "ok", "version": "4.1"})

    @app.get("/readyz")
    def readinesscheck():
        failures = []
        if not app.config.get("AI_API_KEY"):
            failures.append("AI_API_KEY")
        if app.config.get("AI_GLOBAL_DAILY_LIMIT") is None:
            failures.append("AI_GLOBAL_DAILY_LIMIT")
        if not app.extensions["database"].check_ready():
            failures.append("REFERENCE_OR_RUNTIME_DB")
        if not app.extensions["ai_usage"].check_ready():
            failures.append("AI_USAGE_DB")
        if failures:
            return failure("NOT_READY", "服务尚未就绪", 503, details={"checks": failures})
        return success({"status": "ready", "version": "4.1"})

    @app.errorhandler(413)
    def request_too_large(_error):
        return failure("PAYLOAD_TOO_LARGE", "请求内容过大", 413)

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return failure("NOT_FOUND", "接口不存在", 404)
        return _error

    return app


if __name__ == "__main__":
    local_app = create_app()
    local_app.run(
        host=local_app.config["APP_HOST"],
        port=local_app.config["APP_PORT"],
        debug=local_app.config["APP_DEBUG"],
    )
