from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from bs4 import BeautifulSoup

from app import create_app
from zhugeshensuan.content import ArticleRepository

ROOT = Path(__file__).resolve().parents[1]


def article_text(
    slug="portable-article",
    *,
    title="A Portable Article",
    status="published",
    body="## Published anywhere\n\nThis article was uploaded from another device.",
):
    return "\n".join(
        (
            "+++",
            f'slug = "{slug}"',
            f'title = "{title}"',
            'description = "A valid article uploaded through the private owner page."',
            'published_at = "2026-07-16"',
            f'status = "{status}"',
            'tags = ["culture"]',
            'source_notes = "Public source note."',
            "+++",
            body,
            "",
        )
    )


@pytest.fixture()
def admin_app(tmp_path, reference_db):
    articles_path = tmp_path / "articles"
    app = create_app(
        {
            "TESTING": True,
            "SITE_BASE_URL": "https://getwiseoracle.com",
            "CONTACT_EMAIL": "5siwei@gmail.com",
            "SECRET_KEY": "article-admin-test-secret-key",
            "SESSION_COOKIE_SECURE": False,
            "AI_API_KEY": "",
            "AI_GLOBAL_DAILY_LIMIT": 100,
            "REFERENCE_DB_PATH": reference_db,
            "RUNTIME_DB_PATH": tmp_path / "runtime.db",
            "ARTICLES_PATH": articles_path,
            "ARTICLE_ADMIN_PATH": "165131",
            "ARTICLE_ADMIN_PASSWORD": "simple-owner-password",
        }
    )
    return app


@pytest.fixture()
def admin_client(admin_app):
    with admin_app.test_client() as client:
        yield client


def csrf_from(response):
    soup = BeautifulSoup(response.get_data(as_text=True), "html.parser")
    return soup.select_one('input[name="csrf_token"]')["value"]


def close_test_upload(response):
    response.get_data()
    request_stream = response.request.environ.get("wsgi.input")
    if request_stream is not None:
        request_stream.close()
    response.request.close()
    response.close()
    return response


def unlock(client, password="simple-owner-password"):
    page = client.get("/165131")
    return client.post(
        "/165131/unlock",
        data={"csrf_token": csrf_from(page), "password": password},
        follow_redirects=False,
    )


def upload(client, text, filename, *, overwrite=False, csrf_token=None):
    if csrf_token is None:
        csrf_token = csrf_from(client.get("/165131"))
    stream = BytesIO(text.encode("utf-8"))
    try:
        data = {
            "csrf_token": csrf_token,
            "article": (stream, filename),
        }
        if overwrite:
            data["overwrite"] = "yes"
        response = client.post(
            "/165131/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=False,
            buffered=True,
        )
        return close_test_upload(response)
    finally:
        stream.close()


def test_private_page_is_unlinked_uncached_and_not_indexable(admin_client):
    response = admin_client.get("/165131")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "输入访问密码" in body
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "165131" not in admin_client.get("/sitemap.xml").get_data(as_text=True)
    assert "165131" not in admin_client.get("/robots.txt").get_data(as_text=True)


def test_password_is_checked_by_server_and_privileged_routes_hide_when_locked(admin_client):
    wrong = unlock(admin_client, "wrong-password")

    assert wrong.status_code == 403
    assert "密码不正确" in wrong.get_data(as_text=True)
    assert admin_client.get("/165131/articles.zip").status_code == 404
    assert (
        admin_client.post(
            "/165131/upload",
            data={"csrf_token": "anything"},
        ).status_code
        == 404
    )

    correct = unlock(admin_client)
    assert correct.status_code == 303
    assert correct.headers["Location"].endswith("/165131")
    assert "上传 Markdown 文章" in admin_client.get("/165131").get_data(as_text=True)


def test_upload_publishes_immediately_without_git_or_restart(admin_app, admin_client):
    unlock(admin_client)
    response = upload(admin_client, article_text(), "portable-article.md")

    assert response.status_code == 303
    assert response.headers["Location"].endswith("/165131?uploaded=portable-article")
    stored = admin_app.config["ARTICLES_PATH"] / "portable-article.md"
    assert stored.read_text(encoding="utf-8") == article_text()
    assert admin_client.get("/articles/portable-article").status_code == 200
    assert "A Portable Article" in admin_client.get("/articles").get_data(as_text=True)
    assert "portable-article" in admin_client.get("/sitemap.xml").get_data(as_text=True)


def test_other_repository_instance_detects_uploaded_file_on_next_request(tmp_path):
    articles_path = tmp_path / "articles"
    first_worker = ArticleRepository(articles_path)
    second_worker = ArticleRepository(articles_path)

    first_worker.publish_upload(
        filename="portable-article.md",
        text=article_text(),
        overwrite=False,
    )

    assert second_worker.get_public("portable-article") is not None


@pytest.mark.parametrize(
    ("filename", "text", "expected"),
    [
        ("article.txt", article_text(), "只接受 .md"),
        ("wrong-name.md", article_text(), "filename"),
        ("draft.md", article_text("draft", status="draft"), "published"),
        (
            "unsafe.md",
            article_text("unsafe", body="<script>alert(1)</script>"),
            "raw HTML",
        ),
    ],
)
def test_invalid_uploads_are_rejected_without_writing(
    admin_app, admin_client, filename, text, expected
):
    unlock(admin_client)
    response = upload(admin_client, text, filename)

    assert response.status_code == 400
    assert expected in response.get_data(as_text=True)
    assert list(admin_app.config["ARTICLES_PATH"].glob("*.md")) == []


def test_non_utf8_and_oversized_uploads_are_rejected(admin_app, admin_client):
    unlock(admin_client)
    csrf_token = csrf_from(admin_client.get("/165131"))
    with BytesIO(b"\xff\xfe\x00") as invalid_stream:
        invalid_utf8 = admin_client.post(
            "/165131/upload",
            data={
                "csrf_token": csrf_token,
                "article": (invalid_stream, "invalid.md"),
            },
            content_type="multipart/form-data",
            buffered=True,
        )
    with BytesIO(b"x" * (512 * 1024 + 1)) as oversized_stream:
        oversized = admin_client.post(
            "/165131/upload",
            data={
                "csrf_token": csrf_token,
                "article": (oversized_stream, "oversized.md"),
            },
            content_type="multipart/form-data",
            buffered=True,
        )
    close_test_upload(invalid_utf8)
    close_test_upload(oversized)

    assert invalid_utf8.status_code == 400
    assert "UTF-8" in invalid_utf8.get_data(as_text=True)
    assert oversized.status_code == 400
    assert "512 KiB" in oversized.get_data(as_text=True)
    assert list(admin_app.config["ARTICLES_PATH"].glob("*.md")) == []


def test_existing_article_requires_explicit_overwrite(admin_app, admin_client):
    unlock(admin_client)
    original = article_text(title="Original title")
    assert upload(admin_client, original, "portable-article.md").status_code == 303

    replacement = article_text(title="Replacement title")
    refused = upload(admin_client, replacement, "portable-article.md")
    assert refused.status_code == 409
    assert "勾选确认覆盖" in refused.get_data(as_text=True)
    assert "Original title" in (
        admin_app.config["ARTICLES_PATH"] / "portable-article.md"
    ).read_text(encoding="utf-8")

    accepted = upload(
        admin_client,
        replacement,
        "portable-article.md",
        overwrite=True,
    )
    assert accepted.status_code == 303
    assert "Replacement title" in admin_client.get("/articles/portable-article").get_data(
        as_text=True
    )


def test_download_button_exports_all_markdown_and_nothing_else(admin_client):
    unlock(admin_client)
    upload(admin_client, article_text("alpha", title="Alpha"), "alpha.md")
    upload(admin_client, article_text("beta", title="Beta"), "beta.md")

    response = admin_client.get("/165131/articles.zip")
    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    assert "attachment;" in response.headers["Content-Disposition"]
    with BytesIO(response.data) as archive_stream, ZipFile(archive_stream) as archive:
        assert archive.namelist() == ["alpha.md", "beta.md"]
        assert archive.read("alpha.md").decode("utf-8") == article_text("alpha", title="Alpha")
        assert all(not name.endswith((".db", ".env", ".log")) for name in archive.namelist())


def test_csrf_is_required_after_unlock(admin_client):
    unlock(admin_client)
    with BytesIO(article_text().encode()) as stream:
        response = admin_client.post(
            "/165131/upload",
            data={"article": (stream, "portable-article.md")},
            content_type="multipart/form-data",
            buffered=True,
        )
    close_test_upload(response)

    assert response.status_code == 400
    assert "表单已过期" in response.get_data(as_text=True)


def test_compose_uses_independent_persistent_article_volume_and_admin_env():
    compose = (ROOT / "deploy" / "compose.prod.yml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "deploy" / "Dockerfile").read_text(encoding="utf-8")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "ARTICLE_ADMIN_PATH" in compose
    assert "ARTICLE_ADMIN_PASSWORD" in compose
    assert "ARTICLES_PATH: /app/content/articles_en" in compose
    assert "article-content:/app/content" in compose
    assert "article-content:" in compose
    assert "/app/content/articles_en" in dockerfile
    assert 'VOLUME ["/app/instance", "/app/content"]' in dockerfile
    assert "ARTICLE_ADMIN_PATH=165131" in env_example
    assert "ARTICLE_ADMIN_PASSWORD=replace-with-owner-password" in env_example


def test_admin_path_can_be_rotated_with_configuration(tmp_path, reference_db):
    app = create_app(
        {
            "TESTING": True,
            "SITE_BASE_URL": "https://getwiseoracle.com",
            "CONTACT_EMAIL": "5siwei@gmail.com",
            "AI_API_KEY": "",
            "AI_GLOBAL_DAILY_LIMIT": 100,
            "REFERENCE_DB_PATH": reference_db,
            "RUNTIME_DB_PATH": tmp_path / "runtime.db",
            "ARTICLES_PATH": tmp_path / "articles",
            "ARTICLE_ADMIN_PATH": "654321",
            "ARTICLE_ADMIN_PASSWORD": "",
        }
    )
    client = app.test_client()

    assert client.get("/165131").status_code == 404
    assert client.get("/654321").status_code == 200
    assert "上传 Markdown 文章" in client.get("/654321").get_data(as_text=True)
