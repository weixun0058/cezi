from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def test_divination_result_keeps_global_navigation_available():
    script = (ROOT / "static" / "js" / "main.js").read_text(encoding="utf-8")

    assert "document.querySelectorAll('.ancient-btn')" not in script
    assert "document.querySelectorAll('.ancient-btn:not(.nav-btn)')" not in script
    assert "document.querySelectorAll('.result-section .ancient-btn')" in script


def test_low_value_result_actions_are_not_rendered():
    templates = ("huangli.html", "suanshi.html", "lunming.html")
    removed_labels = {"简版", "切换简版", "复制", "分享", "打印"}

    for template_name in templates:
        markup = (ROOT / "templates" / template_name).read_text(encoding="utf-8")
        soup = BeautifulSoup(markup, "html.parser")
        button_labels = {button.get_text(strip=True) for button in soup.find_all("button")}
        assert button_labels.isdisjoint(removed_labels), template_name


def test_huangli_extension_is_collapsed_and_owns_scenario_filter():
    markup = (ROOT / "templates" / "huangli.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(markup, "html.parser")
    toggle = soup.find(id="weekHuangliToggle")
    panel = soup.find(id="weekHuangliPanel")
    scenario = soup.find(id="scenarioFilter")

    assert toggle["aria-label"] == "九天黄历"
    assert toggle["aria-expanded"] == "false"
    assert "hidden" in panel.get("class", [])
    assert scenario.find_parent(id="weekHuangliPanel") is panel
    assert scenario["aria-label"] == "择事"
    assert [option.get_text(strip=True) for option in scenario.find_all("option")] == [
        "诸事",
        "婚嫁",
        "搬迁",
        "开市",
        "出行",
        "签约",
        "理发",
    ]
    assert panel.find("h3") is None

    button_labels = {button.get_text(strip=True) for button in soup.find_all("button")}
    assert button_labels.isdisjoint({"收藏", "导出收藏", "清空收藏"})


def test_huangli_week_data_loads_only_from_extension_interactions():
    script = (ROOT / "static" / "js" / "huangli.js").read_text(encoding="utf-8")

    assert script.count("fetchAndDisplayNineDaysHuangliData();") == 2
    assert "fetch(`/api/huangli?date=${encodeURIComponent(date)}`)" in script
    assert "HUANGLI_FAVORITES_KEY" not in script
    assert "status !== '未载'" in script
