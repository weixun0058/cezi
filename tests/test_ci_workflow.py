from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_production_image_smoke_test_matches_required_runtime_contract():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    for required in (
        "docker volume create zhugeshensuan-ci-data",
        "docker volume create zhugeshensuan-ci-content",
        "-v zhugeshensuan-ci-data:/app/instance",
        "-v zhugeshensuan-ci-content:/app/content",
        "-e APP_ENV=production",
        "-e SITE_BASE_URL=https://getwiseoracle.com",
        "-e CONTACT_EMAIL=ci@getwiseoracle.com",
        "-e ARTICLE_ADMIN_PATH=165131",
        "-e ARTICLES_PATH=/app/content/articles_en",
        "-e AI_API_KEY=ci-readiness-placeholder",
        "-e AI_GLOBAL_DAILY_LIMIT=100",
    ):
        assert required in workflow

    assert "curl --fail --silent http://127.0.0.1:8000/healthz" in workflow
    assert "curl --fail --silent http://127.0.0.1:8000/readyz" in workflow
