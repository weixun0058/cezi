import ipaddress
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
PUBLIC_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ARTICLE_ADMIN_PATH_PATTERN = re.compile(r"^\d{6}$")


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _path_from_env(name, default):
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else BASE_DIR / value


def _optional_int(name):
    value = os.getenv(name)
    return int(value) if value not in {None, ""} else None


def validate_config(config):
    if config.get("TESTING") or config.get("APP_ENV") != "production":
        return
    errors = []
    site_base_url = str(config.get("SITE_BASE_URL", ""))
    parsed_site_url = urlsplit(site_base_url)
    hostname = parsed_site_url.hostname or ""
    site_url_invalid = (
        parsed_site_url.scheme != "https"
        or not parsed_site_url.netloc
        or parsed_site_url.path not in {"", "/"}
        or bool(parsed_site_url.query)
        or bool(parsed_site_url.fragment)
        or parsed_site_url.username is not None
        or parsed_site_url.password is not None
        or hostname == "localhost"
        or hostname.endswith(".localhost")
        or hostname.endswith(".example")
    )
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        site_url_invalid = True
    if site_url_invalid:
        errors.append("SITE_BASE_URL must be a public HTTPS origin without a path")
    contact_email = str(config.get("CONTACT_EMAIL", "")).strip()
    contact_domain = contact_email.rpartition("@")[2].lower()
    if not PUBLIC_EMAIL_PATTERN.fullmatch(contact_email) or contact_domain.endswith(".example"):
        errors.append("CONTACT_EMAIL must be a valid public email address")
    secret_key = config.get("SECRET_KEY", "")
    if secret_key == "development-only-change-me" or len(secret_key) < 32:
        errors.append("SECRET_KEY must be a unique value of at least 32 characters")
    if not config.get("AI_API_KEY"):
        errors.append("AI_API_KEY must be configured")
    global_limit = config.get("AI_GLOBAL_DAILY_LIMIT")
    if not isinstance(global_limit, int) or global_limit < 1:
        errors.append("AI_GLOBAL_DAILY_LIMIT must be a positive integer")
    if config.get("APP_DEBUG"):
        errors.append("APP_DEBUG must be disabled")
    article_admin_path = str(config.get("ARTICLE_ADMIN_PATH", ""))
    if not ARTICLE_ADMIN_PATH_PATTERN.fullmatch(article_admin_path):
        errors.append("ARTICLE_ADMIN_PATH must contain exactly 6 digits")
    if errors:
        raise RuntimeError("Invalid production configuration: " + "; ".join(errors))


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    JSON_AS_ASCII = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 1024 * 1024))
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_DEBUG = _as_bool(os.getenv("APP_DEBUG"), False)
    TRUSTED_PROXY_HOPS = int(os.getenv("TRUSTED_PROXY_HOPS", "0"))
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Shanghai")
    SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://localhost:8000").rstrip("/")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "").strip()
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = APP_ENV == "production"
    SESSION_COOKIE_SAMESITE = "Strict"
    PERMANENT_SESSION_LIFETIME = 30 * 24 * 60 * 60
    ARTICLE_ADMIN_PATH = os.getenv("ARTICLE_ADMIN_PATH", "165131").strip().strip("/")
    ARTICLE_ADMIN_PASSWORD = os.getenv("ARTICLE_ADMIN_PASSWORD", "").strip()

    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
    AI_MODEL = os.getenv("AI_MODEL", "deepseek-v4-flash")
    AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_DAILY_LIMIT = int(os.getenv("AI_DAILY_LIMIT", "3"))
    AI_RATE_LIMIT_PER_MINUTE = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "3"))
    AI_MAX_CONCURRENT = int(os.getenv("AI_MAX_CONCURRENT", "4"))
    AI_GLOBAL_DAILY_LIMIT = _optional_int("AI_GLOBAL_DAILY_LIMIT")

    REFERENCE_DB_PATH = _path_from_env("REFERENCE_DB_PATH", "data/reference/reference.db")
    RUNTIME_DB_PATH = _path_from_env("RUNTIME_DB_PATH", "instance/runtime.db")
    # 简体签文（权威 JSON，运行时内存加载，不入数据库）
    SIGNS_SIMP_PATH = _path_from_env(
        "SIGNS_SIMP_PATH", "data/content/oracle_signs_reinterpreted.json"
    )
    # 繁体签文（由 scripts/build_hant_json.py 离线 OpenCC s2t 生成）
    SIGNS_HANT_PATH = _path_from_env(
        "SIGNS_HANT_PATH", "data/content/oracle_signs_reinterpreted_hant.json"
    )
    # 简体彭祖百忌
    PZBJ_SIMP_PATH = _path_from_env("PZBJ_SIMP_PATH", "data/reference/pzbj.json")
    # 繁体彭祖百忌（由 scripts/build_hant_json.py 离线 OpenCC s2t 生成）
    PZBJ_HANT_PATH = _path_from_env("PZBJ_HANT_PATH", "data/content/pzbj_hant.json")
    ENGLISH_SIGNS_PATH = _path_from_env("ENGLISH_SIGNS_PATH", "data/content/oracle_signs_en.json")
    HUANGLI_TERMS_EN_PATH = _path_from_env(
        "HUANGLI_TERMS_EN_PATH", "data/content/huangli_terms_en.json"
    )
    HUANGLI_SCENARIOS_EN_PATH = _path_from_env(
        "HUANGLI_SCENARIOS_EN_PATH", "data/content/huangli_scenarios_en.json"
    )
    ARTICLES_PATH = _path_from_env("ARTICLES_PATH", "instance/articles_en")
    # 英文八字 AI 提示词模板（Markdown 文件，启动时加载到内存）
    BIRTH_CHART_PROMPT_PATH = _path_from_env(
        "BIRTH_CHART_PROMPT_PATH", "prompts/birth_chart_en_prompt.md"
    )


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    AI_API_KEY = ""
    AI_GLOBAL_DAILY_LIMIT = 100
