"""英文页面路由。

URL 结构（D2 已确认：/ 作为英文首页，旧中文路由保持 301）：
  /                         → 英文首页
  /ask-oracle               → 英文算事页
  /daily-almanac            → 英文黄历页
  /birth-chart-reading      → 英文论命页
  /articles                 → 英文文章列表
  /articles/<slug>          → 英文文章详情
  /privacy                  → 隐私政策
  /terms                    → 使用条款
  /disclaimer               → 免责声明
  /about                    → 关于
  /contact                  → 联系

英文 API 走 /api/en/* 前缀（D12 已确认），由各 API 蓝图处理（W4/W5/W6 实施）。

W3 阶段：路由 + 占位模板（最小可渲染）。
W7 阶段：完整前端实现。
"""

from flask import Blueprint, g, render_template

pages_en_bp = Blueprint("pages_en", __name__)


def _render_en(template_name: str, **context):
    """渲染英文模板，统一注入 current_lang='en' 和 html_lang='en'。

    输入：
        template_name: 英文模板名（如 "index.html"）
        context: 额外模板变量
    输出：
        Flask 渲染响应
    """
    g.lang = "en"
    return render_template(
        f"en/{template_name}",
        current_lang="en",
        html_lang="en",
        **context,
    )


@pages_en_bp.get("/")
def en_index():
    """英文首页"""
    return _render_en("index.html")


@pages_en_bp.get("/ask-oracle")
def en_ask_oracle():
    """英文算事页（Ask the Oracle）"""
    return _render_en("ask_oracle.html")


@pages_en_bp.get("/daily-almanac")
def en_daily_almanac():
    """英文黄历页（Daily Chinese Almanac）"""
    return _render_en("daily_almanac.html")


@pages_en_bp.get("/birth-chart-reading")
def en_birth_chart():
    """英文论命页（Birth Chart Reading）"""
    return _render_en("birth_chart.html")


@pages_en_bp.get("/articles")
def en_articles():
    """英文文章列表"""
    return _render_en("articles.html")


@pages_en_bp.get("/articles/<slug>")
def en_article_detail(slug: str):
    """英文文章详情

    输入：
        slug: 文章 URL 标识（如 "what-is-bazi"）
    """
    # W3 阶段：占位，W8 阶段实现文章系统
    return _render_en("article_detail.html", slug=slug)


@pages_en_bp.get("/privacy")
def en_privacy():
    """隐私政策"""
    return _render_en("privacy.html")


@pages_en_bp.get("/terms")
def en_terms():
    """使用条款"""
    return _render_en("terms.html")


@pages_en_bp.get("/disclaimer")
def en_disclaimer():
    """免责声明"""
    return _render_en("disclaimer.html")


@pages_en_bp.get("/about")
def en_about():
    """关于"""
    return _render_en("about.html")


@pages_en_bp.get("/contact")
def en_contact():
    """联系"""
    return _render_en("contact.html")
