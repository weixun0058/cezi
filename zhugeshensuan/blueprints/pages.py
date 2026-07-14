"""页面路由（含语言前缀与 SEO 友好 URL）。

URL 结构（D2 已确认：/ 作为英文首页，由 pages_en.py 处理）：
  /                         → 英文首页（由 pages_en_bp 处理，不在本蓝图）
  /huangli                  → 301 → /zh-hant/almanac
  /suanshi                  → 301 → /zh-hant/divination
  /lunming                  → 301 → /zh-hant/bazi
  /<lang>/almanac           → 黄历页面
  /<lang>/divination        → 算事页面
  /<lang>/bazi              → 论命页面

其中 <lang> ∈ {zh-hans, zh-hant}。
"""

from flask import Blueprint, abort, g, redirect, render_template, request

from ..i18n_utils import (
    DEFAULT_CHINESE_UI_LANG,
    LANGS,
    PAGE_TEMPLATES,
    PAGE_URL_NAMES,
    html_lang_for,
)

pages_bp = Blueprint("pages", __name__)


def _redirect_to_default(page: str = "almanac"):
    """301 重定向到公开中文入口（繁体）的对应页面。"""
    return redirect(f"/{DEFAULT_CHINESE_UI_LANG}/{page}", code=301)


@pages_bp.get("/<lang>")
def lang_index(lang: str):
    """简体/繁体中文首页。"""
    if lang not in LANGS:
        abort(404)
    g.lang = lang
    g.page = "index"
    return render_template(
        "index.html",
        current_lang=lang,
        html_lang=html_lang_for(lang),
    )


@pages_bp.get("/huangli")
def old_huangli():
    return _redirect_to_default("almanac")


@pages_bp.get("/suanshi")
def old_suanshi():
    return _redirect_to_default("divination")


@pages_bp.get("/lunming")
def old_lunming():
    return _redirect_to_default("bazi")


@pages_bp.get("/<lang>/almanac")
@pages_bp.get("/<lang>/divination")
@pages_bp.get("/<lang>/bazi")
def lang_page(lang: str):
    """语言前缀 + SEO 友好路径的页面路由"""
    if lang not in LANGS:
        abort(404)
    # request.path 形如 /zh-hans/almanac，取末段作为页面 URL 名
    url_name = request.path.rsplit("/", 1)[-1]
    page = PAGE_URL_NAMES.get(url_name)
    if not page:
        abort(404)
    g.lang = lang
    g.page = page
    template = PAGE_TEMPLATES[page]
    return render_template(template, current_lang=lang, html_lang=html_lang_for(lang))
