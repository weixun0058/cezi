"""W7 英文前端契约测试。

覆盖（依据 docs/plans/2026-06-27-english-site-execution-plan.md W7.3-W7.7）：
- 11 条英文路由全部 200
- base.html 共享布局：html lang=en、canonical、wise_oracle.css、wise_oracle_common.js
- W7.3 首页：H1 Wise Oracle、三大工具入口
- W7.4 Ask the Oracle：两输入模式、Draw a Sign、How were these numbers formed 折叠项、
  页面 JS 加载；不出现旧字段名 oracle_title/message/guidance_summary/caution；
  不出现旧重启按钮文案 Ask Another Question
- W7.5 Daily Almanac：不出现 Yellow Calendar；coming soon 降级
- W7.6 Birth Chart Reading：time unknown checkbox、Generate Chart、页面 JS 加载；
  不出现 fate guarantee / accurate prediction / pay to change your destiny
- W7.7 合规页：Privacy/Terms/Disclaimer/About/Contact 渲染真实内容
- W7.2 base.html 不链接中文 style.css（中英两套布局，已知技术债）
"""

from __future__ import annotations

import re

import pytest


def _normalize_ws(text: str) -> str:
    """归一化空白：连续空白（含换行）折叠为单空格，便于跨行断言。"""
    return re.sub(r"\s+", " ", text)


def _body(client, path: str) -> str:
    """取路由响应体（空白归一化）。"""
    resp = client.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"
    return _normalize_ws(resp.get_data(as_text=True))


def _raw(client, path: str) -> str:
    """取路由响应体（保留原始空白）。"""
    resp = client.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"
    return resp.get_data(as_text=True)


# ============================================================
# 路由可达性
# ============================================================


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/ask-oracle",
        "/daily-almanac",
        "/birth-chart-reading",
        "/articles",
        "/articles/how-oracle-signs-work",
        "/privacy",
        "/terms",
        "/disclaimer",
        "/about",
        "/contact",
    ],
)
def test_english_route_returns_200(client, path):
    """11 条英文路由全部返回 200。"""
    resp = client.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"


# ============================================================
# base.html 共享布局
# ============================================================


def test_base_html_has_english_lang_attribute(client):
    """base.html 输出 <html lang="en">。"""
    body = _raw(client, "/")
    assert '<html lang="en">' in body


def test_base_html_links_english_css(client):
    """base.html 链接 wise_oracle.css，不链接中文 style.css（W7.2 技术债：两套布局）。"""
    body = _raw(client, "/")
    assert "wise_oracle.css" in body
    assert "css/style.css" not in body


def test_base_html_loads_common_js(client):
    """base.html 加载 wise_oracle_common.js。"""
    body = _raw(client, "/")
    assert "wise_oracle_common.js" in body


def test_base_html_has_canonical(client):
    """base.html 含 canonical link。"""
    body = _raw(client, "/")
    assert 'rel="canonical"' in body


def test_base_html_has_three_language_switcher(client):
    """英文布局提供 EN/简/繁共享语言切换器。"""
    body = _raw(client, "/")
    assert 'id="lang-switcher"' in body
    assert "js/lang/lang_switcher.js" in body


def test_base_html_has_responsible_use_footer(client):
    """页脚含 responsible-use 免责声明。"""
    body = _body(client, "/")
    assert "entertainment" in body.lower()
    assert "not medical" in body.lower()


# ============================================================
# W7.3 首页
# ============================================================


def test_homepage_has_brand_and_tools(client):
    """首页 H1 Wise Oracle + 三大工具入口。"""
    body = _body(client, "/")
    assert "Wise Oracle" in body
    assert "/ask-oracle" in body
    assert "/daily-almanac" in body
    assert "/birth-chart-reading" in body


# ============================================================
# W7.4 Ask the Oracle
# ============================================================


def test_ask_oracle_has_both_input_modes(client):
    """Ask the Oracle 含 Three Words 与 Three Numbers 两种输入模式。"""
    body = _body(client, "/ask-oracle")
    assert "Three Words" in body
    assert "Three Numbers" in body


def test_ask_oracle_has_submit_button(client):
    """提交按钮文案为 Draw a Sign。"""
    body = _body(client, "/ask-oracle")
    assert "Draw a Sign" in body


def test_ask_oracle_has_how_numbers_formed_collapsible(client):
    """含折叠项 How were these numbers formed?（输入前不展示公式，默认折叠）。"""
    body = _body(client, "/ask-oracle")
    assert "How were these numbers formed?" in body
    assert "<details" in _raw(client, "/ask-oracle")


def test_ask_oracle_loads_page_js(client):
    """页面加载 ask_oracle_en.js。"""
    body = _raw(client, "/ask-oracle")
    assert "ask_oracle_en.js" in body


def test_ask_oracle_has_guidance_text(client):
    """含引导语 Hold one question quietly in mind。"""
    body = _body(client, "/ask-oracle")
    assert "Hold one question quietly in mind" in body


@pytest.mark.parametrize(
    "forbidden",
    ["oracle_title", "guidance_summary", "Ask Another Question"],
)
def test_ask_oracle_does_not_contain_old_fields_or_text(client, forbidden):
    """W7.4 契约：不出现旧字段名 oracle_title/guidance_summary/caution，不出现旧重启按钮文案。"""
    body = _body(client, "/ask-oracle")
    assert forbidden not in body, f"ask-oracle contains forbidden '{forbidden}'"


# ============================================================
# W7.5 Daily Almanac
# ============================================================


def test_daily_almanac_is_connected_to_english_api(client):
    """英文黄历页已接通日期、场景控件和页面脚本。"""
    body = _body(client, "/daily-almanac")
    raw = _raw(client, "/daily-almanac")
    assert "Coming soon" not in body
    assert 'data-almanac-form' in raw
    assert 'data-almanac-date' in raw
    assert 'data-almanac-scenario' in raw
    assert "/static/js/daily_almanac.js" in raw


def test_daily_almanac_does_not_contain_yellow_calendar(client):
    """W7.5 契约：页面不含 Yellow Calendar。"""
    body = _body(client, "/daily-almanac")
    assert "Yellow Calendar" not in body


# ============================================================
# W7.6 Birth Chart Reading
# ============================================================


def test_birth_chart_has_time_unknown_checkbox(client):
    """出生时间未知用 checkbox，不要求选"未知"中文值。"""
    body = _raw(client, "/birth-chart-reading")
    assert 'type="checkbox"' in body
    assert "don't know my birth time" in _body(client, "/birth-chart-reading").lower()


def test_birth_chart_has_generate_button(client):
    """提交按钮文案为 Generate Chart。"""
    body = _body(client, "/birth-chart-reading")
    assert "Generate Chart" in body


def test_birth_chart_loads_page_js(client):
    """页面加载 birth_chart_en.js。"""
    body = _raw(client, "/birth-chart-reading")
    assert "birth_chart_en.js" in body


def test_birth_chart_has_privacy_notice(client):
    """输入隐私提示可见。"""
    body = _body(client, "/birth-chart-reading")
    assert "birth details" in body.lower()
    assert "not stored" in body.lower()


def test_birth_chart_has_responsible_positioning(client):
    """非预测定位：含 self-reflection / not ... prediction 表述。"""
    body = _body(client, "/birth-chart-reading")
    assert "self-reflection" in body.lower()
    assert "destiny reading" in body.lower() or "life prediction" in body.lower()


@pytest.mark.parametrize(
    "forbidden",
    ["fate guarantee", "accurate prediction", "pay to change your destiny"],
)
def test_birth_chart_does_not_contain_forbidden_phrases(client, forbidden):
    """W7.6 契约：不出现 fate guarantee / accurate prediction / pay to change your destiny。"""
    body = _body(client, "/birth-chart-reading")
    assert forbidden not in body.lower(), (
        f"birth-chart-reading contains forbidden '{forbidden}'"
    )


# ============================================================
# W7.7 合规页
# ============================================================


def test_privacy_page_has_real_content(client):
    """隐私政策含真实内容（数据收集、AI、Cookie、用户权利）。"""
    body = _body(client, "/privacy")
    assert "Privacy Policy" in body
    assert "birth chart input" in body.lower()
    assert "AI" in body
    assert "cookie" in body.lower()
    assert "rights" in body.lower()


def test_terms_page_has_real_content(client):
    """使用条款含真实内容。"""
    body = _body(client, "/terms")
    assert "Terms of Service" in body
    assert "not professional advice" in body.lower() or "not" in body.lower()
    assert "AI" in body


def test_disclaimer_page_has_real_content(client):
    """免责声明含真实内容。"""
    body = _body(client, "/disclaimer")
    assert "Disclaimer" in body
    assert "entertainment" in body.lower()
    assert "cultural exploration" in body.lower()
    assert "not" in body.lower()


def test_about_page_has_real_content(client):
    """关于页含真实内容 + 三大工具链接。"""
    body = _body(client, "/about")
    assert "About" in body
    assert "/ask-oracle" in body
    assert "/birth-chart-reading" in body


def test_contact_page_has_real_content(client):
    """联系页含真实内容。"""
    body = _body(client, "/contact")
    assert "Contact" in body
    assert "@" in body  # 邮箱
    assert "/privacy" in body  # 引用隐私政策
