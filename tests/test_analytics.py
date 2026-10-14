from datetime import date

from bs4 import BeautifulSoup

from zhugeshensuan.analytics import CloudflareAnalyticsClient, SearchConsoleClient


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"status={self.status_code}")

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def cloudflare_payload():
    return {
        "data": {
            "viewer": {
                "zones": [
                    {
                        "daily": [
                            {
                                "count": 3,
                                "sum": {"visits": 2, "edgeResponseBytes": 100},
                                "dimensions": {"datetimeHour": "2026-08-31T16:00:00Z"},
                            },
                            {
                                "count": 4,
                                "sum": {"visits": 3, "edgeResponseBytes": 120},
                                "dimensions": {"datetimeHour": "2026-09-01T16:00:00Z"},
                            },
                        ],
                        "pages": [
                            {
                                "count": 4,
                                "sum": {"visits": 3, "edgeResponseBytes": 120},
                                "dimensions": {"clientRequestPath": "/"},
                            },
                            {
                                "count": 2,
                                "sum": {"visits": 1, "edgeResponseBytes": 20},
                                "dimensions": {"clientRequestPath": "/static/site.css"},
                            },
                            {
                                "count": 1,
                                "sum": {"visits": 1, "edgeResponseBytes": 30},
                                "dimensions": {"clientRequestPath": "/articles"},
                            },
                        ],
                        "referrers": [
                            {
                                "count": 3,
                                "sum": {"visits": 2},
                                "dimensions": {"clientRefererHost": "google.com"},
                            },
                            {
                                "count": 1,
                                "sum": {"visits": 1},
                                "dimensions": {"clientRefererHost": None},
                            },
                        ],
                        "countries": [
                            {
                                "count": 4,
                                "sum": {"visits": 3},
                                "dimensions": {"clientCountryName": "US"},
                            }
                        ],
                    }
                ]
            }
        }
    }


def cloudflare_core_payload():
    payload = cloudflare_payload()
    del payload["data"]["viewer"]["zones"][0]["referrers"]
    return payload


def cloudflare_referrers_payload():
    payload = cloudflare_payload()
    zone = payload["data"]["viewer"]["zones"][0]
    return {"data": {"viewer": {"zones": [{"referrers": zone["referrers"]}]}}}


def unlock(client):
    page = client.get("/165131")
    token = BeautifulSoup(page.get_data(as_text=True), "html.parser").select_one(
        'input[name="csrf_token"]'
    )["value"]
    return client.post(
        "/165131/unlock",
        data={"csrf_token": token, "password": "test-owner-password"},
        follow_redirects=False,
    )


def test_cloudflare_overview_normalises_daily_pages_and_sources():
    session = FakeSession(
        [
            FakeResponse(cloudflare_core_payload()),
            FakeResponse(cloudflare_referrers_payload()),
            FakeResponse(cloudflare_core_payload()),
            FakeResponse(cloudflare_referrers_payload()),
        ]
    )
    provider = CloudflareAnalyticsClient(
        token="token",
        zone_id="zone",
        hostname="getwiseoracle.com",
        session=session,
    )

    result = provider.overview(date(2026, 9, 1), date(2026, 9, 3))

    assert result["totals"] == {"requests": 7, "visits": 5, "bytes": 220}
    assert [item["date"] for item in result["daily"]] == ["2026-09-01", "2026-09-02"]
    assert [item["value"] for item in result["pages"]] == ["/", "/articles"]
    assert result["referrers"][0]["value"] == "google.com"
    assert result["referrers"][1]["value"] == "(direct or hidden)"
    assert result["countries"][0]["value"] == "US"
    assert "requestSource" in session.calls[0][1]["json"]["query"]
    assert len(session.calls) == 4


def test_cloudflare_overview_survives_unavailable_referrers():
    session = FakeSession(
        [
            FakeResponse(cloudflare_core_payload()),
            FakeResponse({"errors": [{"message": "clientRefererHost unavailable"}]}),
            FakeResponse(cloudflare_core_payload()),
        ]
    )
    provider = CloudflareAnalyticsClient(
        token="token",
        zone_id="zone",
        hostname="getwiseoracle.com",
        session=session,
    )

    result = provider.overview(date(2026, 9, 1), date(2026, 9, 3))

    assert result["totals"] == {"requests": 7, "visits": 5, "bytes": 220}
    assert result["referrers"] == []
    assert any("来源网站字段" in note for note in result["notes"])
    assert len(session.calls) == 3


def test_cloudflare_overview_skips_dates_beyond_zone_retention():
    session = FakeSession(
        [
            FakeResponse(cloudflare_core_payload()),
            FakeResponse(cloudflare_referrers_payload()),
        ]
    )
    provider = CloudflareAnalyticsClient(
        token="token",
        zone_id="zone",
        hostname="getwiseoracle.com",
        max_lookback_days=1,
        session=session,
    )

    result = provider.overview(date(2026, 9, 1), date(2026, 9, 4))

    assert len(session.calls) == 2
    assert any("仅保留最近约 1 天" in note for note in result["notes"])


def test_analytics_status_requires_owner_session(client):
    response = client.get("/165131/analytics/status")
    assert response.status_code == 404

    unlock(client)
    response = client.get("/165131/analytics/status")
    assert response.status_code == 200
    assert response.json["data"]["cloudflare"]["configured"] is False
    assert response.json["data"]["search_console"]["configured"] is False


def test_analytics_dashboard_requires_owner_session(client):
    response = client.get("/165131/analytics")
    assert response.status_code == 404

    unlock(client)
    response = client.get("/165131/analytics")
    assert response.status_code == 200
    assert "网站统计" in response.get_data(as_text=True)


def test_analytics_overview_reports_missing_cloudflare_configuration(client):
    unlock(client)
    response = client.get("/165131/analytics/overview")
    assert response.status_code == 503
    assert response.json["error"]["code"] == "ANALYTICS_NOT_CONFIGURED"


def test_analytics_overview_returns_provider_data(app, client):
    session = FakeSession(
        [
            FakeResponse(cloudflare_core_payload()),
            FakeResponse(cloudflare_referrers_payload()),
            FakeResponse(cloudflare_core_payload()),
            FakeResponse(cloudflare_referrers_payload()),
        ]
    )
    app.extensions["cloudflare_analytics"] = CloudflareAnalyticsClient(
        token="token",
        zone_id="zone",
        hostname="getwiseoracle.com",
        session=session,
    )
    unlock(client)

    response = client.get("/165131/analytics/overview?from=2026-09-01&to=2026-09-02")

    assert response.status_code == 200
    assert response.json["data"]["range"] == {
        "from": "2026-09-01",
        "to": "2026-09-02",
        "timezone": "Asia/Shanghai",
    }
    assert response.json["data"]["totals"]["visits"] == 5


def test_search_console_refreshes_token_and_maps_rows():
    session = FakeSession(
        [
            FakeResponse({"access_token": "access", "expires_in": 3600}),
            FakeResponse(
                {
                    "rows": [
                        {
                            "keys": ["2026-09-01", "getwiseoracle.com/"],
                            "clicks": 3,
                            "impressions": 20,
                            "ctr": 0.15,
                            "position": 4.5,
                        }
                    ]
                }
            ),
        ]
    )
    provider = SearchConsoleClient(
        site_url="sc-domain:getwiseoracle.com",
        client_id="client",
        client_secret="secret",
        refresh_token="refresh",
        session=session,
    )

    result = provider.query(date(2026, 9, 1), date(2026, 9, 3), ["date", "page"], row_limit=10)

    assert result["rows"][0]["date"] == "2026-09-01"
    assert result["rows"][0]["page"] == "getwiseoracle.com/"
    assert result["rows"][0]["clicks"] == 3.0
    assert session.calls[1][1]["json"]["endDate"] == "2026-09-02"
