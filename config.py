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

    HUANGLI_DB_PATH = _path_from_env("HUANGLI_DB_PATH", "instance/huangli.db")
    HANZI_DB_PATH = _path_from_env("HANZI_DB_PATH", "database/kanxi_dict.db")
    GUA_DATA_PATH = _path_from_env("GUA_DATA_PATH", "database/zhugeshenshuan_jq.xlsx")
    PZBJ_DATA_PATH = _path_from_env("PZBJ_DATA_PATH", "database/pzbj.json")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    AI_API_KEY = ""
