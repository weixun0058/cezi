import json

import pytest
from bs4 import BeautifulSoup

CORE_PAGE_GROUPS = (
    (
        "/",
        {
            "en": "https://getwiseoracle.com/",
            "zh-Hans": "https://getwiseoracle.com/zh-hans",
            "zh-Hant": "https://getwiseoracle.com/zh-hant",
            "x-default": "https://getwiseoracle.com/",
        },
    ),
    (
        "/ask-oracle",
        {
            "en": "https://getwiseoracle.com/ask-oracle",
            "zh-Hans": "https://getwiseoracle.com/zh-hans/divination",
            "zh-Hant": "https://getwiseoracle.com/zh-hant/divination",
            "x-default": "https://getwiseoracle.com/ask-oracle",
        },
    ),
    (
        "/daily-almanac",
        {
            "en": "https://getwiseoracle.com/daily-almanac",
            "zh-Hans": "https://getwiseoracle.com/zh-hans/almanac",
            "zh-Hant": "https://getwiseoracle.com/zh-hant/almanac",
            "x-default": "https://getwiseoracle.com/daily-almanac",
        },
    ),
    (
        "/birth-chart-reading",
        {
            "en": "https://getwiseoracle.com/birth-chart-reading",
            "zh-Hans": "https://getwiseoracle.com/zh-hans/bazi",
            "zh-Hant": "https://getwiseoracle.com/zh-hant/bazi",
            "x-default": "https://getwiseoracle.com/birth-chart-reading",
        },
    ),
)

PAGE_CASES = (
    ("/", "https://getwiseoracle.com/", "index,follow"),
    ("/ask-oracle", "https://getwiseoracle.com/ask-oracle", "index,follow"),
    ("/daily-almanac", "https://getwiseoracle.com/daily-almanac", "index,follow"),
    (
        "/birth-chart-reading",
        "https://getwiseoracle.com/birth-chart-reading",
        "index,follow",
    ),
    ("/articles", "https://getwiseoracle.com/articles", "noindex,follow"),
    ("/privacy", "https://getwiseoracle.com/privacy", "index,follow"),
    ("/terms", "https://getwiseoracle.com/terms", "index,follow"),
    ("/disclaimer", "https://getwiseoracle.com/disclaimer", "index,follow"),
    ("/about", "https://getwiseoracle.com/about", "index,follow"),
    ("/contact", "https://getwiseoracle.com/contact", "index,follow"),
    ("/zh-hans", "https://getwiseoracle.com/zh-hans", "index,follow"),
    (
        "/zh-hans/divination",
        "https://getwiseoracle.com/zh-hans/divination",
        "index,follow",
    ),
    (
        "/zh-hans/almanac",
        "https://getwiseoracle.com/zh-hans/almanac",
        "index,follow",
    ),
    ("/zh-hans/bazi", "https://getwiseoracle.com/zh-hans/bazi", "index,follow"),
    ("/zh-hant", "https://getwiseoracle.com/zh-hant", "index,follow"),
    (
        "/zh-hant/divination",
        "https://getwiseoracle.com/zh-hant/divination",
        "index,follow",
    ),
    (
        "/zh-hant/almanac",
        "https://getwiseoracle.com/zh-hant/almanac",
        "index,follow",
    ),
    ("/zh-hant/bazi", "https://getwiseoracle.com/zh-hant/bazi", "index,follow"),
)


def _soup(client, path):
    response = client.get(path)
    assert response.status_code == 200, path
    return BeautifulSoup(response.get_data(as_text=True), "html.parser")


def _json_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from _json_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _json_keys(nested)


@pytest.mark.parametrize(("path", "canonical_url", "robots"), PAGE_CASES)
def test_public_page_has_one_server_rendered_metadata_set(client, path, canonical_url, robots):
    soup = _soup(client, path)

    assert len(soup.find_all("title")) == 1
    assert soup.title.get_text(strip=True)

    descriptions = soup.find_all("meta", attrs={"name": "description"})
    assert len(descriptions) == 1
    assert descriptions[0].get("content", "").strip()

    canonicals = soup.find_all("link", attrs={"rel": "canonical"})
    assert len(canonicals) == 1
    assert canonicals[0]["href"] == canonical_url

    robots_tags = soup.find_all("meta", attrs={"name": "robots"})
    assert len(robots_tags) == 1
    assert robots_tags[0]["content"] == robots


@pytest.mark.parametrize(("path", "expected"), CORE_PAGE_GROUPS)
def test_core_page_hreflang_group_is_complete_and_absolute(client, path, expected):
    soup = _soup(client, path)
    alternates = {
        link["hreflang"]: link["href"] for link in soup.find_all("link", attrs={"rel": "alternate"})
    }

    assert alternates == expected


@pytest.mark.parametrize(
    ("path", "english_path"),
    [
        ("/zh-hans", "/"),
        ("/zh-hant", "/"),
        ("/zh-hans/divination", "/ask-oracle"),
        ("/zh-hant/divination", "/ask-oracle"),
        ("/zh-hans/almanac", "/daily-almanac"),
        ("/zh-hant/almanac", "/daily-almanac"),
        ("/zh-hans/bazi", "/birth-chart-reading"),
        ("/zh-hant/bazi", "/birth-chart-reading"),
    ],
)
def test_chinese_core_pages_return_same_hreflang_group(client, path, english_path):
    chinese_soup = _soup(client, path)
    english_soup = _soup(client, english_path)

    def alternates(soup):
        return {
            link["hreflang"]: link["href"]
            for link in soup.find_all("link", attrs={"rel": "alternate"})
        }

    assert alternates(chinese_soup) == alternates(english_soup)


@pytest.mark.parametrize(
    "path",
    ["/articles", "/privacy", "/terms", "/disclaimer", "/about", "/contact"],
)
def test_english_only_page_does_not_claim_untranslated_alternates(client, path):
    soup = _soup(client, path)
    assert soup.find_all("link", attrs={"rel": "alternate"}) == []


@pytest.mark.parametrize(
    ("path", "locale"),
    [(path, "en_US") for path, _, _ in PAGE_CASES if not path.startswith("/zh-")]
    + [(path, "zh_CN") for path, _, _ in PAGE_CASES if path.startswith("/zh-hans")]
    + [(path, "zh_TW") for path, _, _ in PAGE_CASES if path.startswith("/zh-hant")],
)
def test_open_graph_matches_page_metadata(client, path, locale):
    soup = _soup(client, path)
    canonical = soup.find("link", attrs={"rel": "canonical"})["href"]
    description = soup.find("meta", attrs={"name": "description"})["content"]

    assert soup.find("meta", property="og:title")["content"] == soup.title.get_text(strip=True)
    assert soup.find("meta", property="og:description")["content"] == description
    assert soup.find("meta", property="og:url")["content"] == canonical
    assert soup.find("meta", property="og:type")["content"] == "website"
    assert soup.find("meta", property="og:site_name")["content"] == "Wise Oracle"
    assert soup.find("meta", property="og:locale")["content"] == locale


@pytest.mark.parametrize(
    "path",
    [path for path, _, robots in PAGE_CASES if robots == "index,follow"],
)
def test_indexable_page_has_valid_conservative_json_ld(client, path):
    soup = _soup(client, path)
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    canonical = soup.find("link", attrs={"rel": "canonical"})["href"]

    assert scripts
    graphs = [json.loads(script.string) for script in scripts]
    graph_types = {graph["@type"] for graph in graphs}
    assert graph_types <= {"WebSite", "WebPage"}
    assert "WebPage" in graph_types
    assert any(graph.get("url") == canonical for graph in graphs)

    graph_keys = set(_json_keys(graphs))
    for forbidden_property in (
        "aggregateRating",
        "review",
        "offers",
        "price",
        "MedicalWebPage",
    ):
        assert forbidden_property not in graph_keys


def test_homepage_has_website_and_webpage_json_ld(client):
    soup = _soup(client, "/")
    graph_types = {
        json.loads(script.string)["@type"]
        for script in soup.find_all("script", attrs={"type": "application/ld+json"})
    }

    assert graph_types == {"WebSite", "WebPage"}


def test_json_ld_does_not_weaken_script_csp(client):
    response = client.get("/")
    directives = {
        part.strip().split(" ", 1)[0]: part.strip()
        for part in response.headers["Content-Security-Policy"].split(";")
        if part.strip()
    }

    assert directives["script-src"] == ("script-src 'self' https://static.cloudflareinsights.com")
    assert "'unsafe-inline'" not in directives["script-src"]
    assert "'unsafe-eval'" not in directives["script-src"]
    assert directives["connect-src"] == "connect-src 'self'"
