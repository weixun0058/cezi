import pytest

from zhugeshensuan.seo import absolute_public_url


def test_absolute_public_url_normalizes_root_and_page_paths():
    base_url = "https://getwiseoracle.com"

    assert absolute_public_url(base_url, "/") == "https://getwiseoracle.com/"
    assert absolute_public_url(base_url, "/ask-oracle") == ("https://getwiseoracle.com/ask-oracle")


@pytest.mark.parametrize(
    "path",
    [
        "https://evil.example/x",
        "//evil.example/x",
        "/x?a=1",
        "/x#fragment",
        "/x\\y",
    ],
)
def test_absolute_public_url_rejects_untrusted_path_forms(path):
    with pytest.raises(ValueError):
        absolute_public_url("https://getwiseoracle.com", path)


def test_canonical_uses_configured_origin_not_request_host(client):
    response = client.get(
        "/ask-oracle",
        headers={
            "Host": "attacker.example",
            "X-Forwarded-Host": "forwarded-attacker.example",
        },
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'href="https://getwiseoracle.com/ask-oracle"' in body
    assert "attacker.example" not in body


def test_canonical_drops_request_query_string(client):
    response = client.get("/ask-oracle?utm_source=test&lang=en")
    body = response.get_data(as_text=True)

    assert 'href="https://getwiseoracle.com/ask-oracle"' in body
    assert "utm_source" not in body
