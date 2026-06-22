import pytest

from app import create_app


def test_production_configuration_requires_secret_key():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(
            {
                "APP_ENV": "production",
                "TESTING": False,
                "SECRET_KEY": "development-only-change-me",
                "AI_API_KEY": "test-key",
                "AI_GLOBAL_DAILY_LIMIT": 10,
            }
        )


def test_production_configuration_requires_global_ai_limit():
    with pytest.raises(RuntimeError, match="AI_GLOBAL_DAILY_LIMIT"):
        create_app(
            {
                "APP_ENV": "production",
                "TESTING": False,
                "SECRET_KEY": "a" * 32,
                "AI_API_KEY": "test-key",
                "AI_GLOBAL_DAILY_LIMIT": None,
            }
        )
