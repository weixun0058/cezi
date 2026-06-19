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
