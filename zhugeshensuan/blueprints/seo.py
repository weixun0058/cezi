"""Crawler-facing sitemap and robots endpoints."""

from flask import Blueprint, Response, current_app, render_template

from ..seo import absolute_public_url, build_sitemap_urls

seo_bp = Blueprint("seo", __name__)


@seo_bp.get("/sitemap.xml")
def sitemap():
    article_slugs = tuple(
        article.slug for article in current_app.extensions["articles"].list_public()
    )
    urls = build_sitemap_urls(current_app.config["SITE_BASE_URL"], article_slugs=article_slugs)
    return Response(
        render_template("sitemap.xml", urls=urls),
        content_type="application/xml; charset=utf-8",
    )


@seo_bp.get("/robots.txt")
def robots():
    sitemap_url = absolute_public_url(current_app.config["SITE_BASE_URL"], "/sitemap.xml")
    return Response(
        render_template("robots.txt", sitemap_url=sitemap_url),
        content_type="text/plain; charset=utf-8",
    )
