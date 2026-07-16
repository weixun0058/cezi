"""Private, server-hosted Markdown upload and export page for the site owner."""

from __future__ import annotations

import hashlib
import hmac
import io
import secrets
import zipfile
from datetime import UTC, datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from ..content import MAX_UPLOAD_BYTES, ArticleContentError, ArticleExistsError


def _auth_fingerprint() -> str:
    payload = (
        f"{current_app.config['ARTICLE_ADMIN_PATH']}\0"
        f"{current_app.config['ARTICLE_ADMIN_PASSWORD']}"
    ).encode()
    return hmac.new(
        str(current_app.config["SECRET_KEY"]).encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()


def _is_authorized() -> bool:
    if not current_app.config["ARTICLE_ADMIN_PASSWORD"]:
        return True
    supplied = str(session.get("article_admin_authorized", ""))
    return bool(supplied) and hmac.compare_digest(supplied, _auth_fingerprint())


def _csrf_token() -> str:
    token = session.get("article_admin_csrf")
    if not isinstance(token, str) or len(token) < 32:
        token = secrets.token_urlsafe(32)
        session["article_admin_csrf"] = token
    return token


def _require_csrf() -> None:
    expected = _csrf_token()
    supplied = request.form.get("csrf_token", "")
    if not hmac.compare_digest(expected, supplied):
        abort(400, "表单已过期，请刷新页面后重试。")


def _render_page(*, error: str | None = None, status: int = 200):
    authorized = _is_authorized()
    articles = current_app.extensions["articles"].list_public() if authorized else ()
    return (
        render_template(
            "admin/articles.html",
            authorized=authorized,
            articles=articles,
            csrf_token=_csrf_token(),
            error=error,
            uploaded=request.args.get("uploaded", ""),
            max_upload_kib=MAX_UPLOAD_BYTES // 1024,
            password_enabled=bool(current_app.config["ARTICLE_ADMIN_PASSWORD"]),
        ),
        status,
    )


def create_article_admin_blueprint() -> Blueprint:
    blueprint = Blueprint("article_admin", __name__)

    @blueprint.after_request
    def protect_admin_response(response):
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @blueprint.get("")
    def index():
        return _render_page()

    @blueprint.post("/unlock")
    def unlock():
        _require_csrf()
        supplied = request.form.get("password", "")
        expected = str(current_app.config["ARTICLE_ADMIN_PASSWORD"])
        if not expected:
            return redirect(url_for("article_admin.index"), code=303)
        if not hmac.compare_digest(supplied, expected):
            return _render_page(error="访问密码不正确。", status=403)
        session.clear()
        session.permanent = True
        session["article_admin_authorized"] = _auth_fingerprint()
        _csrf_token()
        return redirect(url_for("article_admin.index"), code=303)

    @blueprint.post("/upload")
    def upload():
        if not _is_authorized():
            abort(404)
        _require_csrf()
        uploaded = request.files.get("article")
        if uploaded is None or not uploaded.filename:
            return _render_page(error="请选择一个 Markdown 文件。", status=400)
        filename = uploaded.filename
        if not filename.lower().endswith(".md"):
            return _render_page(error="只接受 .md 文件。", status=400)
        try:
            raw = uploaded.stream.read(MAX_UPLOAD_BYTES + 1)
        finally:
            uploaded.close()
        if len(raw) > MAX_UPLOAD_BYTES:
            return _render_page(error="单个文件不能超过 512 KiB。", status=400)
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return _render_page(error="文件必须使用 UTF-8 编码。", status=400)
        try:
            article = current_app.extensions["articles"].publish_upload(
                filename=filename,
                text=text,
                overwrite=request.form.get("overwrite") == "yes",
            )
        except ArticleExistsError:
            return _render_page(error="文章已存在，请勾选确认覆盖。", status=409)
        except ArticleContentError as exc:
            return _render_page(error=f"文章校验失败：{exc}", status=400)
        return redirect(
            url_for("article_admin.index", uploaded=article.slug),
            code=303,
        )

    @blueprint.get("/articles.zip")
    def download_articles():
        if not _is_authorized():
            abort(404)
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for filename, content in current_app.extensions["articles"].export_markdown_files():
                archive.writestr(filename, content)
        output.seek(0)
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%SZ")
        return send_file(
            output,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"getwiseoracle-articles-{timestamp}.zip",
            max_age=0,
        )

    @blueprint.post("/lock")
    def lock():
        if not _is_authorized():
            abort(404)
        _require_csrf()
        session.clear()
        return redirect(url_for("article_admin.index"), code=303)

    return blueprint
