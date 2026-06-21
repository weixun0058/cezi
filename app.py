import logging
import time
from pathlib import Path

from flask import Flask, g, request

from api_utils import failure, success
from blueprints import ALL_BLUEPRINTS
from config import Config
from database import Database
from huangli import HuangLi
from logging_config import configure_logging
from lunming import LunMing

LOGGER = logging.getLogger(__name__)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
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
    app.extensions["pzbj"] = app.extensions["database"].load_pzbj()

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    @app.before_request
    def start_request_timer():
        g.request_started = time.monotonic()

    @app.after_request
    def add_security_headers(response):
        duration_ms = (time.monotonic() - getattr(g, "request_started", time.monotonic())) * 1000
        LOGGER.info(
            "%s %s %s %.1fms", request.method, request.path, response.status_code, duration_ms
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response

    @app.get("/healthz")
    def healthcheck():
        return success({"status": "ok", "version": "4.1"})

    @app.errorhandler(413)
    def request_too_large(_error):
        return failure("PAYLOAD_TOO_LARGE", "请求内容过大", 413)

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return failure("NOT_FOUND", "接口不存在", 404)
        return _error

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["APP_DEBUG"],
    )
