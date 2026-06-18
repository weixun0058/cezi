def test_healthcheck(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["data"]["status"] == "ok"


def test_rejects_invalid_json(client):
    response = client.post("/get_strokes", data="not-json", content_type="application/json")
    assert response.status_code == 400
    assert response.json["error"]["code"] == "INVALID_JSON"


def test_rejects_oversized_payload(client):
    response = client.post(
        "/get_strokes",
        data='{"character":"' + ("字" * 600000) + '"}',
        content_type="application/json",
    )
    assert response.status_code == 413
    assert response.json["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_gua_response_uses_named_fields(client):
    response = client.post("/get_gua_info", json={"sign_number": 1})
    assert response.status_code == 200
    assert response.json["data"]["sign_number"] == 1
    assert "sign_text" in response.json["data"]


def test_invalid_date_and_scenario(client):
    assert client.get("/api/huangli?date=2026-99-99").status_code == 400
    assert client.get("/api/huangli?scenario=不存在").status_code == 400


def test_pzbj_explanation(client):
    response = client.get(
        "/api/pzbj_explanation", query_string={"text": "甲不开仓财物耗散，子不问卜自惹祸殃"}
    )
    assert response.status_code == 200
    assert response.json["data"]["explanation"]


def test_model_not_configured_returns_503(client):
    response = client.post(
        "/api/lunming/analyze",
        json={"name": "测试", "gender": "男", "birth_date": "1990-01-01", "birth_time": "未知"},
    )
    assert response.status_code == 503
    assert response.json["error"]["code"] == "MODEL_NOT_CONFIGURED"


def test_post_stream_and_deprecated_get_headers(app, client):
    class FakeLunming:
        @staticmethod
        def build_chart(_payload):
            return {"pillars": {"year": "己巳"}}

        @staticmethod
        def analyze_bazi_stream(_payload):
            yield {"type": "chart", "chart": {"pillars": {"year": "己巳"}}}
            yield {"type": "text", "text": "测试文本块"}

    app.extensions["lunming"] = FakeLunming()
    payload = {"name": "测试", "gender": "男", "birth_date": "1990-01-01", "birth_time": "未知"}
    response = client.post("/api/lunming/stream", json=payload)
    assert response.status_code == 200
    assert "测试文本块" in response.get_data(as_text=True)

    legacy = client.get("/api/lunming/stream", query_string=payload)
    assert legacy.headers["Deprecation"] == "true"


def test_stream_interruption_returns_safe_error_event(app, client):
    class BrokenLunming:
        @staticmethod
        def build_chart(_payload):
            return {"pillars": {"year": "己巳"}}

        @staticmethod
        def analyze_bazi_stream(_payload):
            yield {"type": "chart", "chart": {"pillars": {"year": "己巳"}}}
            raise RuntimeError("provider details must not leak")

    app.extensions["lunming"] = BrokenLunming()
    response = client.post(
        "/api/lunming/stream",
        json={"name": "测试", "gender": "男", "birth_date": "1990-01-01", "birth_time": "未知"},
    )
    body = response.get_data(as_text=True)
    assert "分析流意外中断，请重试" in body
    assert "provider details must not leak" not in body
