"""Validated, read-only article content loading and safe Markdown rendering."""

from __future__ import annotations

import json
import os
import re
import threading
import tomllib
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from markdown_it import MarkdownIt
from markdown_it.token import Token

MAX_FRONT_MATTER_BYTES = 16 * 1024
MAX_BODY_BYTES = 256 * 1024
MAX_TITLE_LENGTH = 120
MAX_DESCRIPTION_LENGTH = 300
MAX_TAGS = 8
MAX_TAG_LENGTH = 40
MAX_SOURCE_NOTES_LENGTH = 2_000
MAX_UPLOAD_BYTES = 512 * 1024
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DANGEROUS_MARKDOWN_LINK_PATTERN = re.compile(
    r"!?\[[^\]]*\]\(\s*<?\s*(?:javascript|data)\s*:", re.IGNORECASE
)
REQUIRED_FIELDS = {
    "slug",
    "title",
    "description",
    "published_at",
    "status",
    "tags",
}
OPTIONAL_FIELDS = {"updated_at", "source_notes"}
ALLOWED_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


class ArticleContentError(ValueError):
    """Raised when an article file violates the public content contract."""


class ArticleExistsError(ArticleContentError):
    """Raised when an upload would replace an article without confirmation."""


@dataclass(frozen=True)
class Article:
    slug: str
    title: str
    description: str
    published_at: date
    updated_at: date | None
    status: str
    tags: tuple[str, ...]
    source_notes: str
    body_markdown: str
    body_html: str


def _external_link_open(tokens: list[Token], index: int, options: dict, env: dict) -> str:
    token = tokens[index]
    href = token.attrGet("href") or ""
    parsed = urlsplit(href)
    if parsed.scheme in {"http", "https", "mailto"} or parsed.netloc:
        token.attrSet("rel", "nofollow noopener noreferrer")
    return MARKDOWN.renderer.renderToken(tokens, index, options, env)


MARKDOWN = MarkdownIt("js-default", {"linkify": False, "typographer": False})
MARKDOWN.disable("image")
MARKDOWN.renderer.rules["link_open"] = _external_link_open
VALIDATION_MARKDOWN = MarkdownIt("js-default", {"linkify": False, "typographer": False})
HTML_DETECTOR = MarkdownIt("commonmark")


def _walk_tokens(tokens: list[Token]):
    for token in tokens:
        yield token
        if token.children:
            yield from _walk_tokens(token.children)


def _reject_control_characters(value: str, label: str) -> None:
    if any(
        unicodedata.category(character) == "Cc" and character not in {"\t", "\n", "\r"}
        for character in value
    ):
        raise ArticleContentError(f"{label} contains an unacceptable control character")


def _required_string(metadata: dict, field: str, maximum: int) -> str:
    value = metadata.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ArticleContentError(f"{field} must be a non-empty string")
    value = value.strip()
    _reject_control_characters(value, field)
    if len(value) > maximum:
        raise ArticleContentError(f"{field} exceeds the {maximum}-character limit")
    return value


def _parse_date(metadata: dict, field: str, required: bool) -> date | None:
    value = metadata.get(field)
    if value is None and not required:
        return None
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        raise ArticleContentError(f"{field} must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ArticleContentError(f"{field} must be a real calendar date") from exc


def _validate_tags(metadata: dict) -> tuple[str, ...]:
    value = metadata.get("tags")
    if not isinstance(value, list) or not value:
        raise ArticleContentError("tags must be a non-empty TOML array")
    if len(value) > MAX_TAGS:
        raise ArticleContentError(f"tags may contain no more than {MAX_TAGS} values")
    normalized = []
    seen = set()
    for tag in value:
        if not isinstance(tag, str) or not tag.strip():
            raise ArticleContentError("tags must contain non-empty strings")
        tag = tag.strip()
        _reject_control_characters(tag, "tags")
        if len(tag) > MAX_TAG_LENGTH:
            raise ArticleContentError(f"tags may not exceed {MAX_TAG_LENGTH} characters each")
        folded = tag.casefold()
        if folded in seen:
            raise ArticleContentError("tags must not contain duplicates")
        seen.add(folded)
        normalized.append(tag)
    return tuple(normalized)


def _validate_markdown(body_markdown: str) -> str:
    if DANGEROUS_MARKDOWN_LINK_PATTERN.search(body_markdown):
        raise ArticleContentError("body contains a dangerous link scheme")

    html_tokens = list(_walk_tokens(HTML_DETECTOR.parse(body_markdown)))
    if any(token.type in {"html_block", "html_inline"} for token in html_tokens):
        raise ArticleContentError("body contains raw HTML")

    validation_tokens = list(_walk_tokens(VALIDATION_MARKDOWN.parse(body_markdown)))
    if any(token.type == "image" for token in validation_tokens):
        raise ArticleContentError("body images are not allowed")
    for token in validation_tokens:
        if token.type != "link_open":
            continue
        href = token.attrGet("href") or ""
        parsed = urlsplit(href)
        if parsed.scheme and parsed.scheme not in {"http", "https", "mailto"}:
            raise ArticleContentError("body contains an unsupported link scheme")

    rendered = MARKDOWN.render(body_markdown)
    lowered = rendered.casefold()
    if "javascript:" in lowered or "data:" in lowered:
        raise ArticleContentError("rendered body contains a dangerous link scheme")
    return rendered


def parse_article_text(text: str, *, source_name: str) -> Article:
    """Parse and validate one article using the same contract as production."""
    if not isinstance(text, str):
        raise ArticleContentError("article content must be text")
    _reject_control_characters(text, "article")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "+++":
        raise ArticleContentError("article must start with +++ TOML front matter")
    try:
        closing_index = lines.index("+++", 1)
    except ValueError as exc:
        raise ArticleContentError("article front matter is not closed") from exc

    front_matter = "\n".join(lines[1:closing_index])
    if len(front_matter.encode("utf-8")) > MAX_FRONT_MATTER_BYTES:
        raise ArticleContentError("article front matter exceeds 16 KiB")
    body_markdown = "\n".join(lines[closing_index + 1 :]).strip()
    if not body_markdown:
        raise ArticleContentError("article body must not be empty")
    if len(body_markdown.encode("utf-8")) > MAX_BODY_BYTES:
        raise ArticleContentError("article body exceeds 256 KiB")

    try:
        metadata = tomllib.loads(front_matter)
    except tomllib.TOMLDecodeError as exc:
        raise ArticleContentError("article front matter is invalid TOML") from exc
    unknown_fields = sorted(set(metadata) - ALLOWED_FIELDS)
    if unknown_fields:
        raise ArticleContentError(f"unknown article metadata field: {unknown_fields[0]}")
    missing_fields = sorted(REQUIRED_FIELDS - set(metadata))
    if missing_fields:
        raise ArticleContentError(f"missing article metadata field: {missing_fields[0]}")

    slug = _required_string(metadata, "slug", 80)
    if not SLUG_PATTERN.fullmatch(slug):
        raise ArticleContentError("slug must contain lowercase letters, numbers, and hyphens")
    filename = Path(source_name).name
    if filename != f"{slug}.md":
        raise ArticleContentError("article filename must exactly match its slug")

    title = _required_string(metadata, "title", MAX_TITLE_LENGTH)
    description = _required_string(metadata, "description", MAX_DESCRIPTION_LENGTH)
    published_at = _parse_date(metadata, "published_at", required=True)
    updated_at = _parse_date(metadata, "updated_at", required=False)
    if updated_at is not None and updated_at < published_at:
        raise ArticleContentError("updated_at must not be earlier than published_at")
    status = metadata.get("status")
    if status not in {"draft", "published"}:
        raise ArticleContentError("status must be draft or published")
    tags = _validate_tags(metadata)
    source_notes = metadata.get("source_notes", "")
    if not isinstance(source_notes, str):
        raise ArticleContentError("source_notes must be a string")
    source_notes = source_notes.strip()
    _reject_control_characters(source_notes, "source_notes")
    if len(source_notes) > MAX_SOURCE_NOTES_LENGTH:
        raise ArticleContentError(
            f"source_notes exceeds the {MAX_SOURCE_NOTES_LENGTH}-character limit"
        )

    return Article(
        slug=slug,
        title=title,
        description=description,
        published_at=published_at,
        updated_at=updated_at,
        status=status,
        tags=tags,
        source_notes=source_notes,
        body_markdown=body_markdown,
        body_html=_validate_markdown(body_markdown),
    )


def render_markdown(body_markdown: str) -> str:
    """Validate and render Markdown for production pages and editor previews."""
    if not isinstance(body_markdown, str) or not body_markdown.strip():
        raise ArticleContentError("article body must not be empty")
    _reject_control_characters(body_markdown, "body")
    if len(body_markdown.encode("utf-8")) > MAX_BODY_BYTES:
        raise ArticleContentError("article body exceeds 256 KiB")
    return _validate_markdown(body_markdown.strip())


def serialize_article(
    *,
    slug: str,
    title: str,
    description: str,
    published_at: str,
    updated_at: str | None,
    status: str,
    tags: tuple[str, ...] | list[str],
    source_notes: str,
    body_markdown: str,
) -> str:
    """Serialize editor fields, then validate them through the production parser."""
    if not isinstance(tags, tuple | list):
        raise ArticleContentError("tags must be a list or tuple")

    def string(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    lines = [
        "+++",
        f"slug = {string(slug)}",
        f"title = {string(title)}",
        f"description = {string(description)}",
        f"published_at = {string(published_at)}",
    ]
    if updated_at:
        lines.append(f"updated_at = {string(updated_at)}")
    lines.extend(
        [
            f"status = {string(status)}",
            "tags = [" + ", ".join(string(tag) for tag in tags) + "]",
            f"source_notes = {string(source_notes)}",
            "+++",
            body_markdown.strip(),
            "",
        ]
    )
    serialized = "\n".join(lines)
    parse_article_text(serialized, source_name=f"{slug}.md")
    return serialized


def serialize_public_article(**fields) -> str:
    """Serialize a publishable file; draft output is deliberately refused."""
    if fields.get("status") != "published":
        raise ArticleContentError("public article status must be published")
    return serialize_article(**fields)


class ArticleRepository:
    """Validate, atomically update, and expose the persistent article directory."""

    def __init__(self, root: str | Path, *, today: date | None = None):
        self.root = Path(root).resolve()
        if self.root.exists() and not self.root.is_dir():
            raise ArticleContentError(f"article path is not a directory: {self.root}")
        try:
            self.root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ArticleContentError(f"article directory cannot be created: {self.root}") from exc
        self._today = today
        self._lock = threading.RLock()
        self._fingerprint: tuple[tuple[str, int, int], ...] | None = None
        self._public_articles: tuple[Article, ...] = ()
        self._public_by_slug: dict[str, Article] = {}
        self.reload()

    def _directory_fingerprint(self) -> tuple[tuple[str, int, int], ...]:
        try:
            fingerprint = []
            for path in sorted(self.root.glob("*.md"), key=lambda value: value.name):
                stat = path.stat()
                fingerprint.append((path.name, stat.st_mtime_ns, stat.st_size))
            return tuple(fingerprint)
        except OSError as exc:
            raise ArticleContentError("article directory cannot be inspected") from exc

    def _load_locked(self) -> None:
        loaded: dict[str, Article] = {}
        for path in sorted(self.root.glob("*.md"), key=lambda value: value.name):
            resolved_path = path.resolve()
            if resolved_path.parent != self.root:
                raise ArticleContentError(
                    f"article file resolves outside the article directory: {path.name}"
                )
            try:
                article = parse_article_text(
                    path.read_text(encoding="utf-8"), source_name=path.name
                )
            except (OSError, UnicodeError, ArticleContentError) as exc:
                raise ArticleContentError(f"invalid article file {path.name}: {exc}") from exc
            if article.slug in loaded:
                raise ArticleContentError(f"duplicate article slug: {article.slug}")
            loaded[article.slug] = article

        current_date = self._today or date.today()
        public = [
            article
            for article in loaded.values()
            if article.status == "published" and article.published_at <= current_date
        ]
        self._public_articles = tuple(
            sorted(public, key=lambda item: (-item.published_at.toordinal(), item.slug))
        )
        self._public_by_slug = {article.slug: article for article in self._public_articles}
        self._fingerprint = self._directory_fingerprint()

    def reload(self) -> None:
        with self._lock:
            self._load_locked()

    def _refresh_if_changed(self) -> None:
        fingerprint = self._directory_fingerprint()
        if fingerprint == self._fingerprint:
            return
        with self._lock:
            if self._directory_fingerprint() != self._fingerprint:
                self._load_locked()

    def list_public(self) -> tuple[Article, ...]:
        self._refresh_if_changed()
        return self._public_articles

    def get_public(self, slug: str) -> Article | None:
        if not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug):
            return None
        self._refresh_if_changed()
        return self._public_by_slug.get(slug)

    def publish_upload(self, *, filename: str, text: str, overwrite: bool) -> Article:
        if (
            not isinstance(filename, str)
            or "/" in filename
            or "\\" in filename
            or Path(filename).name != filename
        ):
            raise ArticleContentError("upload filename must not contain a path")
        if not filename.lower().endswith(".md"):
            raise ArticleContentError("only .md article files are accepted")
        encoded = text.encode("utf-8")
        if len(encoded) > MAX_UPLOAD_BYTES:
            raise ArticleContentError("article upload exceeds 512 KiB")
        article = parse_article_text(text, source_name=filename)
        if article.status != "published":
            raise ArticleContentError("uploaded article status must be published")

        target = (self.root / filename).resolve()
        if target.parent != self.root:
            raise ArticleContentError("article target is outside the content directory")

        with self._lock:
            previous = target.read_bytes() if target.exists() else None
            if previous is not None and not overwrite:
                raise ArticleExistsError("article already exists; confirm overwrite to replace it")
            temporary = self.root / f".upload-{uuid.uuid4().hex}.tmp"
            replaced = False
            try:
                with temporary.open("xb") as handle:
                    handle.write(encoded)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, target)
                replaced = True
                self._load_locked()
            except Exception:
                if replaced:
                    if previous is None:
                        target.unlink(missing_ok=True)
                    else:
                        restore = self.root / f".restore-{uuid.uuid4().hex}.tmp"
                        try:
                            with restore.open("xb") as handle:
                                handle.write(previous)
                                handle.flush()
                                os.fsync(handle.fileno())
                            os.replace(restore, target)
                        finally:
                            restore.unlink(missing_ok=True)
                    self._load_locked()
                raise
            finally:
                temporary.unlink(missing_ok=True)
        return article

    def export_markdown_files(self) -> tuple[tuple[str, bytes], ...]:
        self._refresh_if_changed()
        with self._lock:
            return tuple(
                (path.name, path.read_bytes())
                for path in sorted(self.root.glob("*.md"), key=lambda value: value.name)
            )

    def check_ready(self) -> bool:
        return self.root.is_dir()
