from xml.etree import ElementTree

EXPECTED_URLS = {
    "https://getwiseoracle.com/",
    "https://getwiseoracle.com/ask-oracle",
    "https://getwiseoracle.com/daily-almanac",
    "https://getwiseoracle.com/birth-chart-reading",
    "https://getwiseoracle.com/about",
    "https://getwiseoracle.com/zh-hant",
    "https://getwiseoracle.com/zh-hant/divination",
    "https://getwiseoracle.com/zh-hant/almanac",
    "https://getwiseoracle.com/zh-hant/bazi",
}


def test_sitemap_is_valid_xml_with_exact_public_url_set(client):
    response = client.get("/sitemap.xml", headers={"Host": "attacker.example"})

    assert response.status_code == 200
    assert response.mimetype == "application/xml"

    root = ElementTree.fromstring(response.data)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = {node.text for node in root.findall("sm:url/sm:loc", namespace)}

    assert root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
    assert locations == EXPECTED_URLS
    assert len(root.findall("sm:url", namespace)) == len(EXPECTED_URLS)


def test_sitemap_excludes_non_public_and_placeholder_routes(client):
    body = client.get("/sitemap.xml").get_data(as_text=True)

    for forbidden in (
        "attacker.example",
        ".example",
        "/api/",
        "/healthz",
        "/readyz",
        "/huangli",
        "/suanshi",
        "/lunming",
        "/zh-hans",
        "/articles",
    ):
        assert forbidden not in body

    assert "<lastmod>" not in body
