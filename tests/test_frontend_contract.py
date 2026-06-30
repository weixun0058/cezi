from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def test_divination_result_keeps_global_navigation_available():
    script = (ROOT / "frontend" / "static" / "js" / "main.js").read_text(encoding="utf-8")

    assert "document.querySelectorAll('.ancient-btn')" not in script
    assert "document.querySelectorAll('.ancient-btn:not(.nav-btn)')" not in script
    assert "document.querySelectorAll('.result-section .ancient-btn')" in script


def test_low_value_result_actions_are_not_rendered():
    templates = ("huangli.html", "suanshi.html", "lunming.html")
    removed_labels = {"简版", "切换简版", "复制", "分享", "打印"}

    for template_name in templates:
        markup = (ROOT / "frontend" / "templates" / template_name).read_text(encoding="utf-8")
        soup = BeautifulSoup(markup, "html.parser")
        button_labels = {button.get_text(strip=True) for button in soup.find_all("button")}
        assert button_labels.isdisjoint(removed_labels), template_name


def test_suanshi_does_not_store_or_render_local_history():
    markup = (ROOT / "frontend" / "templates" / "suanshi.html").read_text(encoding="utf-8")
    script = (ROOT / "frontend" / "static" / "js" / "main.js").read_text(encoding="utf-8")

    assert "本地起卦记录" not in markup
    assert "divinationHistory" not in markup
    assert "zhugeshen.divination.history" not in script
    assert "saveHistory(" not in script


def test_suanshi_starts_from_three_characters_without_question_confirmation():
    markup = (ROOT / "frontend" / "templates" / "suanshi.html").read_text(encoding="utf-8")
    script = (ROOT / "frontend" / "static" / "js" / "main.js").read_text(encoding="utf-8")

    assert "questionSummary" not in markup
    assert "questionConfirmation" not in markup
    assert "repeatWarning" not in markup
    assert "confirmQuestionBtn" not in script
    assert "getHistory()" not in script
    assert "calculateBtn.addEventListener('click', async function()" in script


def test_suanshi_uses_chunked_typewriter_rendering():
    script = (ROOT / "frontend" / "static" / "js" / "main.js").read_text(encoding="utf-8")

    assert "chunkSize = 3, interval = 45" in script
    assert "end += chunkSize" in script
    assert "setTimeout(resolve, interval)" in script
    assert "prefers-reduced-motion: reduce" in script


def test_lunming_does_not_store_or_render_local_reports():
    markup = (ROOT / "frontend" / "templates" / "lunming.html").read_text(encoding="utf-8")
    script = (ROOT / "frontend" / "static" / "js" / "lunming.js").read_text(encoding="utf-8")

    assert "本地报告" not in markup
    assert "report-history" not in markup
    assert "REPORT_STORAGE_KEY" not in script
    assert "localStorage" not in script
    assert "saveReport(" not in script


def test_huangli_extension_is_collapsed_and_owns_scenario_filter():
    markup = (ROOT / "frontend" / "templates" / "huangli.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(markup, "html.parser")
    toggle = soup.find(id="weekHuangliToggle")
    panel = soup.find(id="weekHuangliPanel")
    scenario = soup.find(id="scenarioFilter")

    assert toggle["aria-label"] == "九天黄历"
    assert toggle["aria-expanded"] == "false"
    assert "hidden" in panel.get("class", [])
    assert scenario.find_parent(id="weekHuangliPanel") is panel
    assert scenario["role"] == "group"
    assert scenario["aria-label"] == "择事"
    scenario_buttons = scenario.find_all("button")
    assert [button.get_text(strip=True) for button in scenario_buttons] == [
        "婚嫁",
        "搬迁",
        "开市",
        "出行",
        "签约",
        "理发",
    ]
    assert scenario_buttons[0]["aria-pressed"] == "true"
    assert all(button["aria-pressed"] == "false" for button in scenario_buttons[1:])
    assert panel.find("h3") is None

    button_labels = {button.get_text(strip=True) for button in soup.find_all("button")}
    assert button_labels.isdisjoint({"收藏", "导出收藏", "清空收藏"})


def test_huangli_week_data_loads_only_from_extension_interactions():
    script = (ROOT / "frontend" / "static" / "js" / "huangli.js").read_text(encoding="utf-8")

    assert script.count("fetchAndDisplayNineDaysHuangliData();") == 2
    assert "fetch(i18n.apiUrl(`/api/huangli?date=${encodeURIComponent(date)}`))" in script
    assert "HUANGLI_FAVORITES_KEY" not in script
    assert "status_code !== 'not_loaded'" in script
    assert "scenarioNames" not in script


def test_language_prefixed_pages_render_matching_html_lang(client):
    zh_hans = client.get("/zh-hans/almanac")
    zh_hant = client.get("/zh-hant/almanac")

    assert zh_hans.status_code == 200
    assert zh_hant.status_code == 200
    assert b'<html lang="zh-Hans">' in zh_hans.data
    assert b'<html lang="zh-Hant">' in zh_hant.data


def test_language_prefixed_homepages_render_matching_html_lang(client):
    zh_hans = client.get("/zh-hans")
    zh_hant = client.get("/zh-hant")

    assert zh_hans.status_code == 200
    assert zh_hant.status_code == 200
    assert b'<html lang="zh-Hans">' in zh_hans.data
    assert b'<html lang="zh-Hant">' in zh_hant.data


def test_shared_language_switcher_supports_english_and_page_mapping():
    script = (
        ROOT / "frontend" / "static" / "js" / "lang" / "lang_switcher.js"
    ).read_text(encoding="utf-8")

    assert "{ code: 'en', label: 'EN' }" in script
    assert "'/ask-oracle': 'divination'" in script
    assert "'/daily-almanac': 'almanac'" in script
    assert "'/birth-chart-reading': 'bazi'" in script


def test_i18n_uses_url_language_prefix_before_local_storage():
    script = (ROOT / "frontend" / "static" / "js" / "lang" / "i18n.js").read_text(
        encoding="utf-8"
    )

    assert "function languageFromPath()" in script
    assert "URL 语言前缀优先" in script
    assert "localStorage.setItem(STORAGE_KEY, pathLang)" in script


def test_lunar_date_handlers_use_project_formatters_not_lunar_to_string():
    # 共享模块 lunar-format.js 应承载项目的汉字化逻辑
    shared = (ROOT / "frontend" / "static" / "js" / "lang" / "lunar-format.js").read_text(encoding="utf-8")
    assert "calendar.month_prefix_leap" in shared
    assert "month.toString()" not in shared
    assert "chineseDigits" not in shared

    # 两个 handler 必须通过 LunarFormat 引用共享模块，不得自行实现汉字化逻辑
    handlers = (
        ROOT / "frontend" / "static" / "js" / "huangli_lunar_handler.js",
        ROOT / "frontend" / "static" / "js" / "lunar_date_handler.js",
    )
    for handler in handlers:
        script = handler.read_text(encoding="utf-8")
        assert "LunarFormat" in script, f"{handler.name} 必须引用 LunarFormat 共享模块"
        assert "calendar.month_prefix_leap" not in script, (
            f"{handler.name} 不应再定义 calendar.month_prefix_leap，已迁移到 lunar-format.js"
        )
        assert "month.toString()" not in script
        assert "chineseDigits" not in script
