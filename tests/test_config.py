import pytest

from app import create_app


def test_production_configuration_requires_secret_key():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(
            {
                "APP_ENV": "production",
                "TESTING": False,
                "SITE_BASE_URL": "https://getwiseoracle.com",
                "CONTACT_EMAIL": "5siwei@gmail.com",
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
                "SITE_BASE_URL": "https://getwiseoracle.com",
                "CONTACT_EMAIL": "5siwei@gmail.com",
                "SECRET_KEY": "a" * 32,
                "AI_API_KEY": "test-key",
                "AI_GLOBAL_DAILY_LIMIT": None,
            }
        )


@pytest.mark.parametrize(
    "site_base_url",
    [
        "",
        "http://getwiseoracle.com",
        "https://localhost:8000",
        "https://127.0.0.1",
        "https://wise-oracle.example",
        "https://getwiseoracle.com/path",
        "https://getwiseoracle.com?source=test",
        "https://getwiseoracle.com#fragment",
    ],
)
def test_production_configuration_requires_public_https_site_base_url(site_base_url):
    with pytest.raises(RuntimeError, match="SITE_BASE_URL"):
        create_app(
            {
                "APP_ENV": "production",
                "TESTING": False,
                "SITE_BASE_URL": site_base_url,
                "CONTACT_EMAIL": "5siwei@gmail.com",
                "SECRET_KEY": "a" * 32,
                "AI_API_KEY": "test-key",
                "AI_GLOBAL_DAILY_LIMIT": 10,
            }
        )


@pytest.mark.parametrize(
    "contact_email",
    ["", "not-an-email", "contact@wise-oracle.example"],
)
def test_production_configuration_requires_public_contact_email(contact_email):
    with pytest.raises(RuntimeError, match="CONTACT_EMAIL"):
        create_app(
            {
                "APP_ENV": "production",
                "TESTING": False,
                "SITE_BASE_URL": "https://getwiseoracle.com",
                "CONTACT_EMAIL": contact_email,
                "SECRET_KEY": "a" * 32,
                "AI_API_KEY": "test-key",
                "AI_GLOBAL_DAILY_LIMIT": 10,
            }
        )


@pytest.mark.parametrize("admin_path", ["", "12345", "1234567", "abcdef", "12/345"])
def test_production_configuration_requires_six_digit_article_admin_path(admin_path):
    with pytest.raises(RuntimeError, match="ARTICLE_ADMIN_PATH"):
        create_app(
            {
                "APP_ENV": "production",
                "TESTING": False,
                "SITE_BASE_URL": "https://getwiseoracle.com",
                "CONTACT_EMAIL": "5siwei@gmail.com",
                "SECRET_KEY": "a" * 32,
                "AI_API_KEY": "test-key",
                "AI_GLOBAL_DAILY_LIMIT": 10,
                "ARTICLE_ADMIN_PATH": admin_path,
            }
        )
