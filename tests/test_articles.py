from __future__ import annotations

import json
from datetime import date

import pytest
from bs4 import BeautifulSoup

from app import create_app
from zhugeshensuan import content as content_module
from zhugeshensuan.content import (
    ArticleContentError,
    ArticleRepository,
    parse_article_text,
    serialize_public_article,
)


def article_text(
    slug: str = "reading-oracle-signs",
    *,
    title: str = "How to Read Oracle Signs",
    description: str = "A cultural guide to reading oracle signs with care and context.",
    published_at: str = "2026-07-15",
    updated_at: str | None = None,
    status: str = "published",
    tags: tuple[str, ...] = ("oracle signs", "culture"),
    source_notes: str = "Based on publicly available cultural references.",
    body: str = "## Read in context\n\nUse the text as a prompt for reflection.",
) -> str:
    lines = [
        "+++",
        f'slug = "{slug}"',
        f'title = "{title}"',
        f'description = "{description}"',
        f'published_at = "{published_at}"',
    ]
    if updated_at is not None:
        lines.append(f'updated_at = "{updated_at}"')
    lines.extend(
        [
            f'status = "{status}"',
            "tags = [" + ", ".join(f'"{tag}"' for tag in tags) + "]",
            f'source_notes = "{source_notes}"',
            "+++",
            body,
            "",
        ]
    )
    return "\n".join(lines)


def write_article(directory, slug: str, **overrides):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{slug}.md"
    path.write_text(article_text(slug, **overrides), encoding="utf-8")
    return path


def create_article_app(article_path, tmp_path, reference_db):
    return create_app(
        {
            "TESTING": True,
            "SITE_BASE_URL": "https://getwiseoracle.com",
            "CONTACT_EMAIL": "5siwei@gmail.com",
            "AI_API_KEY": "",
            "AI_GLOBAL_DAILY_LIMIT": 100,
            "REFERENCE_DB_PATH": reference_db,
            "RUNTIME_DB_PATH": tmp_path / "runtime.db",
            "ARTICLES_PATH": article_path,
        }
    )


def test_parse_article_text_returns_validated_article_and_safe_html():
    article = parse_article_text(
        article_text(
            body=(
                "## Read in context\n\n"
                "See [this site](https://example.org/guide) and "
                "[our oracle](/ask-oracle)."
            )
        ),
        source_name="reading-oracle-signs.md",
    )

    assert article.slug == "reading-oracle-signs"
    assert article.published_at == date(2026, 7, 15)
    assert article.updated_at is None
    assert article.tags == ("oracle signs", "culture")
    assert "<h2>Read in context</h2>" in article.body_html
    assert 'href="https://example.org/guide"' in article.body_html
    assert 'rel="nofollow noopener noreferrer"' in article.body_html
    assert '<a href="/ask-oracle">our oracle</a>' in article.body_html


def test_serialize_public_article_round_trips_through_shared_validation():
    serialized = serialize_public_article(
        slug="safe-public-article",
        title='A Quoted "Oracle" Title',
        description="A concise description for a safe public article.",
        published_at="2026-07-15",
        updated_at="2026-07-16",
        status="published",
        tags=("culture", "self-reflection"),
        source_notes="A public source note.",
        body_markdown="## Heading\n\nA body with **emphasis**.",
    )

    article = parse_article_text(serialized, source_name="safe-public-article.md")

    assert article.title == 'A Quoted "Oracle" Title'
    assert article.updated_at == date(2026, 7, 16)
    assert article.status == "published"
    assert "<strong>emphasis</strong>" in article.body_html
    assert "private" not in serialized.lower()


def test_public_serializer_refuses_draft_output():
    with pytest.raises(ArticleContentError, match="published"):
        serialize_public_article(
            slug="local-draft",
            title="Local Draft",
            description="This draft must remain outside the public repository.",
            published_at="2026-07-15",
            updated_at=None,
            status="draft",
            tags=("culture",),
            source_notes="",
            body_markdown="Draft body.",
        )


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda text: text.replace('title = "How to Read Oracle Signs"\n', ""), "title"),
        (
            lambda text: text.replace('published_at = "2026-07-15"', 'published_at = "15/07/2026"'),
            "published_at",
        ),
        (lambda text: text.replace('status = "published"', 'status = "scheduled"'), "status"),
        (lambda text: text.replace('tags = ["oracle signs", "culture"]', "tags = []"), "tags"),
        (lambda text: text[: text.rfind("+++") + 3] + "\n   \n", "body"),
        (
            lambda text: text.replace(
                'source_notes = "Based on publicly available cultural references."',
                'source_notes = "Based on publicly available cultural references."\n'
                'private_notes = "do not publish"',
            ),
            "private_notes",
        ),
    ],
)
def test_invalid_required_metadata_and_empty_body_are_rejected(mutator, message):
    with pytest.raises(ArticleContentError, match=message):
        parse_article_text(mutator(article_text()), source_name="reading-oracle-signs.md")


def test_slug_must_be_safe_and_match_filename():
    with pytest.raises(ArticleContentError, match="slug"):
        parse_article_text(article_text(slug="../outside"), source_name="outside.md")

    with pytest.raises(ArticleContentError, match="filename"):
        parse_article_text(article_text(), source_name="different.md")


@pytest.mark.parametrize(
    "tags",
    [
        tuple(f"tag-{index}" for index in range(9)),
        ("x" * 41,),
        ("culture", "Culture"),
    ],
)
def test_tag_count_length_and_case_insensitive_duplicates_are_rejected(tags):
    with pytest.raises(ArticleContentError, match="tags"):
        parse_article_text(article_text(tags=tags), source_name="reading-oracle-signs.md")


@pytest.mark.parametrize(
    "body",
    [
        "<script>alert(1)</script>",
        "A raw <span>HTML fragment</span>.",
        "![remote tracking](https://example.org/tracker.gif)",
        "[unsafe](javascript:alert(1))",
        "[unsafe](data:text/html;base64,AAAA)",
    ],
)
def test_raw_html_images_and_dangerous_links_are_rejected(body):
    with pytest.raises(ArticleContentError):
        parse_article_text(article_text(body=body), source_name="reading-oracle-signs.md")


def test_control_characters_and_size_limits_are_rejected():
    with pytest.raises(ArticleContentError, match="control"):
        parse_article_text(
            article_text(body="unsafe\x00body"),
            source_name="reading-oracle-signs.md",
        )

    oversized_front_matter = article_text(title="x" * (16 * 1024))
    with pytest.raises(ArticleContentError, match="front matter"):
        parse_article_text(oversized_front_matter, source_name="reading-oracle-signs.md")

    oversized_body = article_text(body="x" * (256 * 1024 + 1))
    with pytest.raises(ArticleContentError, match="body"):
        parse_article_text(oversized_body, source_name="reading-oracle-signs.md")


def test_repository_filters_drafts_and_future_articles_and_sorts_stably(tmp_path):
    articles_path = tmp_path / "articles"
    write_article(articles_path, "alpha", published_at="2026-07-10")
    write_article(articles_path, "beta", published_at="2026-07-15")
    write_article(articles_path, "charlie", published_at="2026-07-15")
    write_article(articles_path, "draft-only", status="draft")
    write_article(articles_path, "future", published_at="2026-07-17")

    repository = ArticleRepository(articles_path, today=date(2026, 7, 16))

    assert [article.slug for article in repository.list_public()] == [
        "beta",
        "charlie",
        "alpha",
    ]
    assert repository.get_public("draft-only") is None
    assert repository.get_public("future") is None
    assert repository.get_public("../alpha") is None


def test_repository_rejects_invalid_file_without_leaking_article_body(tmp_path):
    articles_path = tmp_path / "articles"
    secret_body = "PRIVATE-BODY-MUST-NOT-APPEAR"
    write_article(articles_path, "broken", body=f"<script>{secret_body}</script>")

    with pytest.raises(ArticleContentError) as error:
        ArticleRepository(articles_path)

    assert "broken.md" in str(error.value)
    assert secret_body not in str(error.value)


def test_repository_defensively_rejects_duplicate_loaded_slugs(tmp_path, monkeypatch):
    articles_path = tmp_path / "articles"
    articles_path.mkdir()
    (articles_path / "first.md").write_text("placeholder", encoding="utf-8")
    (articles_path / "second.md").write_text("placeholder", encoding="utf-8")
    duplicate = parse_article_text(article_text(), source_name="reading-oracle-signs.md")
    monkeypatch.setattr(
        content_module,
        "parse_article_text",
        lambda _text, *, source_name: duplicate,
    )

    with pytest.raises(ArticleContentError, match="duplicate article slug"):
        ArticleRepository(articles_path)


def test_repository_creates_missing_directory_but_rejects_file_path(tmp_path):
    missing = tmp_path / "missing"
    repository = ArticleRepository(missing)

    assert missing.is_dir()
    assert repository.list_public() == ()

    file_path = tmp_path / "not-a-directory"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ArticleContentError, match="directory"):
        ArticleRepository(file_path)


def test_article_routes_render_published_content_and_dynamic_seo(tmp_path, reference_db):
    articles_path = tmp_path / "articles"
    write_article(
        articles_path,
        "reading-oracle-signs",
        updated_at="2026-07-16",
        body="## Read in context\n\nA **careful** interpretation.",
    )
    app = create_article_app(articles_path, tmp_path, reference_db)
    client = app.test_client()

    list_response = client.get("/articles")
    list_soup = BeautifulSoup(list_response.get_data(as_text=True), "html.parser")
    assert list_response.status_code == 200
    assert list_soup.find("meta", attrs={"name": "robots"})["content"] == "index,follow"
    assert list_soup.find("a", href="/articles/reading-oracle-signs")
    assert "How to Read Oracle Signs" in list_soup.get_text(" ", strip=True)

    detail_response = client.get("/articles/reading-oracle-signs")
    detail_soup = BeautifulSoup(detail_response.get_data(as_text=True), "html.parser")
    assert detail_response.status_code == 200
    assert detail_soup.find("link", rel="canonical")["href"] == (
        "https://getwiseoracle.com/articles/reading-oracle-signs"
    )
    assert detail_soup.find("meta", property="og:type")["content"] == "article"
    assert detail_soup.find("article").find("strong").get_text(strip=True) == "careful"
    graphs = [
        json.loads(script.string)
        for script in detail_soup.find_all("script", type="application/ld+json")
    ]
    assert {graph["@type"] for graph in graphs} == {"Article", "WebPage"}
    article_graph = next(graph for graph in graphs if graph["@type"] == "Article")
    assert article_graph["datePublished"] == "2026-07-15"
    assert article_graph["dateModified"] == "2026-07-16"

    sitemap = client.get("/sitemap.xml").get_data(as_text=True)
    assert "https://getwiseoracle.com/articles</loc>" in sitemap
    assert "https://getwiseoracle.com/articles/reading-oracle-signs</loc>" in sitemap


def test_draft_future_and_unknown_articles_stay_private(tmp_path, reference_db):
    articles_path = tmp_path / "articles"
    write_article(articles_path, "draft-only", status="draft")
    write_article(articles_path, "future", published_at="2999-01-01")
    app = create_article_app(articles_path, tmp_path, reference_db)
    client = app.test_client()

    list_response = client.get("/articles")
    list_soup = BeautifulSoup(list_response.get_data(as_text=True), "html.parser")
    assert list_soup.find("meta", attrs={"name": "robots"})["content"] == "noindex,follow"
    assert "Coming soon" in list_soup.get_text(" ", strip=True)
    assert client.get("/articles/draft-only").status_code == 404
    assert client.get("/articles/future").status_code == 404
    assert client.get("/articles/unknown").status_code == 404
    sitemap = client.get("/sitemap.xml").get_data(as_text=True)
    assert "/articles" not in sitemap


def test_application_detects_articles_added_after_startup(tmp_path, reference_db):
    articles_path = tmp_path / "articles"
    articles_path.mkdir()
    app = create_article_app(articles_path, tmp_path, reference_db)
    client = app.test_client()

    write_article(articles_path, "added-after-startup")

    assert client.get("/articles/added-after-startup").status_code == 200
    assert "added-after-startup" in client.get("/sitemap.xml").get_data(as_text=True)
