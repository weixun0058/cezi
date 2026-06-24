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
    assert "fetch(`/api/huangli?date=${encodeURIComponent(date)}`)" in script
    assert "HUANGLI_FAVORITES_KEY" not in script
    assert "status !== '未载'" in script
