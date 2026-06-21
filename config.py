import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


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


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    JSON_AS_ASCII = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 1024 * 1024))
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_DEBUG = _as_bool(os.getenv("APP_DEBUG"), False)
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Shanghai")

    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
    AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
    AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_DAILY_LIMIT = int(os.getenv("AI_DAILY_LIMIT", "3"))
    AI_RATE_LIMIT_PER_MINUTE = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "3"))
    AI_MAX_CONCURRENT = int(os.getenv("AI_MAX_CONCURRENT", "4"))
    AI_GLOBAL_DAILY_LIMIT = _optional_int("AI_GLOBAL_DAILY_LIMIT")

    REFERENCE_DB_PATH = _path_from_env("REFERENCE_DB_PATH", "database/reference.db")
    RUNTIME_DB_PATH = _path_from_env("RUNTIME_DB_PATH", "instance/runtime.db")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    AI_API_KEY = ""
    AI_GLOBAL_DAILY_LIMIT = 100
