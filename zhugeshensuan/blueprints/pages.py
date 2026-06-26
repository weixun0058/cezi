"""页面路由（含语言前缀与 SEO 友好 URL）。

URL 结构：
  /                         → 301 → /zh-hans/almanac
  /huangli                  → 301 → /zh-hans/almanac
  /suanshi                  → 301 → /zh-hans/divination
  /lunming                  → 301 → /zh-hans/bazi
  /<lang>/almanac           → 黄历页面
  /<lang>/divination        → 算事页面
  /<lang>/bazi              → 论命页面

其中 <lang> ∈ {zh-hans, zh-hant}。
"""
from flask import Blueprint, abort, g, redirect, render_template, request

from ..i18n_utils import DEFAULT_LANG, LANGS, PAGE_TEMPLATES, PAGE_URL_NAMES, html_lang_for

pages_bp = Blueprint("pages", __name__)


def _redirect_to_default(page: str = "almanac"):
    """301 重定向到默认语言的对应页面"""
    return redirect(f"/{DEFAULT_LANG}/{page}", code=301)


@pages_bp.get("/")
def index_redirect():
    return _redirect_to_default("almanac")


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
