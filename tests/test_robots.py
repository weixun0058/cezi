def test_robots_is_plain_text_and_points_to_production_sitemap(client):
    response = client.get("/robots.txt", headers={"Host": "attacker.example"})
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "User-agent: *" in body
    assert "Allow: /" in body
    assert "Disallow: /api/" in body
    assert "Disallow: /healthz" in body
    assert "Disallow: /readyz" in body
    assert body.count("Sitemap: https://getwiseoracle.com/sitemap.xml") == 1
    assert "attacker.example" not in body


def test_robots_does_not_block_rendering_assets_or_disclose_secrets(client):
    body = client.get("/robots.txt").get_data(as_text=True)

    assert "Disallow: /static" not in body
    assert "SECRET_KEY" not in body
    assert "AI_API_KEY" not in body
