import logging
import re
import sqlite3
import time
import uuid
from pathlib import Path

from flask import Flask, g, request
from werkzeug.middleware.proxy_fix import ProxyFix

from .ai_usage import AIUsagePolicy
from .api_utils import failure, success
from .birth_chart_english import BirthChartEnglish
from .blueprints import ALL_BLUEPRINTS
from .blueprints.article_admin import create_article_admin_blueprint
from .config import Config, validate_config
from .content import ArticleRepository
from .database import Database
from .huangli import HuangLi
from .huangli_english import (
    HuangLiEnglish,
    load_huangli_scenarios_safe,
    load_huangli_terms_safe,
)
from .i18n_utils import DEFAULT_LANG, LANGS
from .logging_config import configure_logging
from .lunming import LunMing
from .metrics import ENDPOINT_METRICS, DailyMetricsStore
from .oracle_english import load_english_signs_safe

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
CSP = "; ".join(
    (
        "default-src 'self'",
        "script-src 'self' https://static.cloudflareinsights.com",
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


def _resolve_request_lang() -> str:
    """从当前请求解析语言代码。

    解析优先级：
      1. URL 路径前缀（/zh-hans/..., /zh-hant/...）
      2. 查询参数 lang（?lang=zh-hant）
      3. 请求头 X-Lang
      4. 默认语言 zh-hans
    """
    path = request.path
    for lang in LANGS:
        if path == f"/{lang}" or path.startswith(f"/{lang}/"):
            return lang
    query_lang = request.args.get("lang", "").strip()
    if query_lang in LANGS:
        return query_lang
    header_lang = request.headers.get("X-Lang", "").strip()
    if header_lang in LANGS:
        return header_lang
    return DEFAULT_LANG


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

    app.extensions["articles"] = ArticleRepository(app.config["ARTICLES_PATH"])

    app.extensions["database"] = Database(
        reference_db=app.config["REFERENCE_DB_PATH"],
        runtime_db=app.config["RUNTIME_DB_PATH"],
        signs_simp_path=app.config["SIGNS_SIMP_PATH"],
        signs_hant_path=app.config["SIGNS_HANT_PATH"],
        pzbj_simp_path=app.config["PZBJ_SIMP_PATH"],
        pzbj_hant_path=app.config["PZBJ_HANT_PATH"],
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
    app.extensions["daily_metrics"] = DailyMetricsStore(app.config["RUNTIME_DB_PATH"])
    # 英文签文内存字典（D15：JSON 内存加载，不入数据库）
    # 用户用其他 Agent 更新 JSON 文件后，重启服务器即生效（无缝切换）
    app.extensions["english_signs"] = load_english_signs_safe(app.config["ENGLISH_SIGNS_PATH"])
    huangli_terms_en = load_huangli_terms_safe(app.config["HUANGLI_TERMS_EN_PATH"])
    huangli_scenarios_en = load_huangli_scenarios_safe(app.config["HUANGLI_SCENARIOS_EN_PATH"])
    app.extensions["huangli_terms_en"] = huangli_terms_en
    app.extensions["huangli_scenarios_en"] = huangli_scenarios_en
    app.extensions["huangli_en"] = HuangLiEnglish(huangli_terms_en, huangli_scenarios_en)
    # 英文 Birth Chart Reading 服务（W6）
    # 复用 lunming 实例的 OpenAI client（配置统一，避免重复创建）
    app.extensions["birth_chart_en"] = BirthChartEnglish(
        app.extensions["lunming"],
        default_timezone=app.config["DEFAULT_TIMEZONE"],
        prompt_path=app.config["BIRTH_CHART_PROMPT_PATH"],
    )

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)
    app.register_blueprint(
        create_article_admin_blueprint(),
        url_prefix=f"/{app.config['ARTICLE_ADMIN_PATH']}",
    )

    @app.before_request
    def start_request_timer():
        g.request_started = time.monotonic()
        supplied_request_id = request.headers.get("X-Request-ID", "")
        g.request_id = (
            supplied_request_id
            if REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
            else uuid.uuid4().hex
        )
        # 解析当前请求语言（URL 路径前缀 > 查询参数 > Header > 默认）
        g.lang = _resolve_request_lang()

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
        metric_name = ENDPOINT_METRICS.get((request.endpoint, request.method))
        if metric_name and 200 <= response.status_code < 300:
            try:
                app.extensions["daily_metrics"].increment(metric_name)
            except (OSError, sqlite3.Error, ValueError):
                LOGGER.exception("Failed to record aggregate product metric")
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
        if not app.extensions["articles"].check_ready():
            failures.append("ARTICLE_CONTENT")
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
