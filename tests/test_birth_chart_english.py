"""W6 Birth Chart English 后端测试。

覆盖：
- W6.1 基础盘英文化：映射表、四柱/日主/生肖/五行映射、birth_time_unknown、gender 归一化
- W6.2 AI prompt：W0.3 红线规则、命盘数据、不要求 responsible_use 字段
- W6.3 AI 报告解析：合法/带代码栅栏/非法/不完整、cautions 支持 str 与 dict、上限
- W6.4 服务层（mock AI）：analyze 返回结构、无 fortune/gua_type、stream 事件序列
- W6.5 API 契约：输入校验错误码、无 key → MODEL_NOT_CONFIGURED、stream SSE、mock AI 完整响应

依据：docs/plans/2026-06-27-english-site-execution-plan.md W6.1-W6.5
      docs/business/wise-oracle-ai-prompt-boundaries.md（W0.3 红线）
      D14（加载时剔除 fortune/gua_type）、D16（不展示吉凶/卦属）、
      D17（interpretation 非 prediction）
"""

from __future__ import annotations

import json
import re
from types import SimpleNamespace

import pytest

from zhugeshensuan.bazi_service import BaziInputError
from zhugeshensuan.birth_chart_english import (
    ELEMENT_EN,
    GAN_ELEMENT,
    GAN_YIN_YANG,
    RESPONSIBLE_USE_TEXT,
    ZHI_TO_ZODIAC,
    ZODIAC_EN,
    BirthChartEnglish,
    _normalize_gender,
    _normalize_payload,
    _parse_ai_report,
    _pillar_to_english,
    build_english_chart_summary,
    build_english_prompt,
)
from zhugeshensuan.lunming import LunMing

# ============================================================
# 测试用 AI 报告（mock 返回）
# ============================================================

REPORT_EN = {
    "chart_summary": "This chart presents a cultural pattern of steady accumulation.",
    "element_balance": "Metal and Fire are prominent, inviting reflection on focus.",
    "reflection_points": [
        {
            "label": "Career",
            "text": "For career, this pattern suggests considering long-term foundations.",
        },
        {
            "label": "Relationships",
            "text": "In relationships, this pattern invites reflection on clear communication.",
        },
        {
            "label": "Personal Growth",
            "text": "This pattern is traditionally associated with patient self-development.",
        },
    ],
    "cautions": [
        "This pattern invites reflection on patience rather than expecting quick results.",
    ],
}


class FakeCompletions:
    """模拟 OpenAI 流式响应，返回 REPORT_EN 的 JSON 分两块。"""

    last_kwargs = None

    @classmethod
    def create(cls, **kwargs):
        cls.last_kwargs = kwargs
        content = json.dumps(REPORT_EN, ensure_ascii=False)
        midpoint = len(content) // 2
        return [
            SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=content[:midpoint]))]
            ),
            SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=content[midpoint:]))]
            ),
        ]


class FakeClient:
    chat = SimpleNamespace(completions=FakeCompletions())


def _make_service() -> BirthChartEnglish:
    """构造注入 mock AI client 的 BirthChartEnglish 实例。"""
    return BirthChartEnglish(LunMing(client=FakeClient()))


# ============================================================
# W6.1 基础盘英文化
# ============================================================


class TestMappingTables:
    """映射表完整性。"""

    def test_zodiac_complete(self):
        assert len(ZODIAC_EN) == 12
        assert ZODIAC_EN["鼠"] == "Rat"
        assert ZODIAC_EN["猪"] == "Pig"

    def test_gan_yin_yang_and_element_complete(self):
        assert len(GAN_YIN_YANG) == 10
        assert len(GAN_ELEMENT) == 10
        assert GAN_YIN_YANG["甲"] == "Yang"
        assert GAN_YIN_YANG["癸"] == "Yin"
        assert GAN_ELEMENT["庚"] == "Metal"

    def test_zhi_zodiac_complete(self):
        assert len(ZHI_TO_ZODIAC) == 12
        assert ZHI_TO_ZODIAC["子"] == "Rat"
        assert ZHI_TO_ZODIAC["亥"] == "Pig"

    def test_element_complete(self):
        assert len(ELEMENT_EN) == 5
        assert ELEMENT_EN["金"] == "Metal"


class TestPillarToEnglish:
    """四柱中文 → 英文。"""

    def test_basic(self):
        assert _pillar_to_english("甲子") == "Yang Wood Rat"
        assert _pillar_to_english("庚午") == "Yang Metal Horse"
        assert _pillar_to_english("乙丑") == "Yin Wood Ox"

    def test_none_or_short(self):
        assert _pillar_to_english(None) is None
        assert _pillar_to_english("") is None
        assert _pillar_to_english("甲") is None  # 长度 != 2


class TestNormalizeGender:
    """英文性别归一化（bazi_service 要求中文"男"/"女"）。"""

    def test_english_to_chinese(self):
        assert _normalize_gender("male") == "男"
        assert _normalize_gender("female") == "女"

    def test_case_insensitive(self):
        assert _normalize_gender("MALE") == "男"
        assert _normalize_gender("Female") == "女"

    def test_chinese_passthrough(self):
        assert _normalize_gender("男") == "男"
        assert _normalize_gender("女") == "女"

    def test_invalid_defaults_male(self):
        assert _normalize_gender(None) == "男"
        assert _normalize_gender(123) == "男"
        assert _normalize_gender("unknown") == "男"


class TestNormalizePayload:
    """payload 归一化。"""

    def test_gender_normalized(self):
        result = _normalize_payload({"gender": "male", "birth_date": "1990-01-01"})
        assert result["gender"] == "男"

    def test_birth_time_unknown_clears_time(self):
        result = _normalize_payload(
            {
                "gender": "female",
                "birth_date": "1990-01-01",
                "birth_time": "14:30",
                "birth_time_unknown": True,
            }
        )
        assert result["birth_time"] == ""

    def test_birth_time_preserved_when_known(self):
        result = _normalize_payload(
            {
                "gender": "female",
                "birth_date": "1990-01-01",
                "birth_time": "14:30",
            }
        )
        assert result["birth_time"] == "14:30"


class TestBuildEnglishChartSummary:
    """英文基础盘摘要。"""

    PAYLOAD = {
        "name": "Alex",
        "gender": "male",
        "birth_date": "1990-05-01",
        "birth_time": "14:30",
    }

    def test_pillars_use_yin_yang_element_zodiac_format(self):
        result = build_english_chart_summary(self.PAYLOAD)
        summary = result["chart_summary"]
        pillar_pattern = re.compile(
            r"^(Yin|Yang) (Wood|Fire|Earth|Metal|Water) "
            r"(Rat|Ox|Tiger|Rabbit|Dragon|Snake|Horse|Goat|Monkey|Rooster|Dog|Pig)$"
        )
        assert summary["year_pillar"] == "Yang Metal Horse"  # 1990 庚午年
        assert pillar_pattern.fullmatch(summary["month_pillar"])
        assert pillar_pattern.fullmatch(summary["day_pillar"])
        assert summary["time_pillar"] is not None
        assert pillar_pattern.fullmatch(summary["time_pillar"])

    def test_zodiac_english(self):
        result = build_english_chart_summary(self.PAYLOAD)
        assert result["chart_summary"]["zodiac"] == "Horse"  # 1990 年马

    def test_day_master_english(self):
        result = build_english_chart_summary(self.PAYLOAD)
        dm = result["chart_summary"]["day_master"]
        assert re.fullmatch(r"(Yin|Yang) (Wood|Fire|Earth|Metal|Water)", dm)

    def test_time_known(self):
        result = build_english_chart_summary(self.PAYLOAD)
        assert result["chart_summary"]["time_unknown"] is False

    def test_birth_time_unknown(self):
        payload = {
            "name": "Sam",
            "gender": "female",
            "birth_date": "1990-05-01",
            "birth_time_unknown": True,
        }
        result = build_english_chart_summary(payload)
        summary = result["chart_summary"]
        assert summary["time_unknown"] is True
        assert summary["time_pillar"] is None
        assert len(result["limitations"]) > 0  # 含未知时辰提示
        assert result["limitations"] == [
            "Birth time is unknown, so the time pillar and dependent details are omitted."
        ]
        assert not re.search(r"[\u4e00-\u9fff]", result["chart_summary"]["lunar_date"])
        assert not re.search(r"[\u4e00-\u9fff]", result["limitations"][0])

    def test_lunar_date_is_english(self):
        result = build_english_chart_summary(self.PAYLOAD)
        assert result["chart_summary"]["lunar_date"] == ("Lunar Year 1990, Month 4, Day 7")

    def test_element_balance_english_keys(self):
        result = build_english_chart_summary(self.PAYLOAD)
        balance = result["element_balance"]
        for key in balance:
            assert key in ELEMENT_EN.values()
        assert sum(balance.values()) > 0

    def test_raw_chart_preserved_for_prompt(self):
        """_raw_chart 保留中文基础盘供 AI prompt 使用。"""
        result = build_english_chart_summary(self.PAYLOAD)
        assert "_raw_chart" in result
        assert "pillars" in result["_raw_chart"]
        assert "wu_xing" in result["_raw_chart"]


# ============================================================
# W6.2 AI prompt（引用 W0.3 红线）
# ============================================================


class TestBuildEnglishPrompt:
    """英文 AI prompt 构建。"""

    def test_contains_red_lines(self):
        prompt = build_english_prompt(
            {"pillars": {"year": "庚午"}}, {"name": "Alex", "gender": "male"}
        )
        low = prompt.lower()
        assert "red line" in low
        assert "medical" in low
        assert "fortune grades" in low or "hexagram" in low

    def test_contains_chart_data(self):
        prompt = build_english_prompt(
            {"pillars": {"year": "庚午"}}, {"name": "Alex", "gender": "male"}
        )
        assert "庚午" in prompt  # 中文命盘数据保留
        assert "Alex" in prompt

    def test_requests_json_structure(self):
        prompt = build_english_prompt({}, {"name": "Alex", "gender": "male"})
        assert "JSON" in prompt
        assert "reflection_points" in prompt
        assert "cautions" in prompt

    def test_excludes_responsible_use_from_ai_output(self):
        """prompt 应要求 AI 不返回 responsible_use（由系统追加）。"""
        prompt = build_english_prompt({}, {"name": "Alex", "gender": "male"})
        assert "responsible_use" in prompt.lower()

    def test_uses_injected_prompt_path(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(
            "Custom template {chart_data_json} / {name} / {gender}",
            encoding="utf-8",
        )

        prompt = build_english_prompt(
            {"pillars": {"year": "庚午"}},
            {"name": "Alex", "gender": "male"},
            prompt_path=prompt_path,
        )

        assert "Custom template" in prompt
        assert "庚午" in prompt
        assert "Alex / male" in prompt


# ============================================================
# W6.3 AI 报告解析
# ============================================================


class TestParseAiReport:
    """解析 AI 返回的 JSON 报告。"""

    def test_parse_valid_json(self):
        result = _parse_ai_report(json.dumps(REPORT_EN))
        assert result["chart_summary"] == REPORT_EN["chart_summary"]
        assert len(result["reflection_points"]) == 3
        assert result["reflection_points"][0]["label"] == "Career"
        assert len(result["cautions"]) == 1

    def test_parse_with_code_fence(self):
        raw = f"```json\n{json.dumps(REPORT_EN)}\n```"
        result = _parse_ai_report(raw)
        assert result["chart_summary"] == REPORT_EN["chart_summary"]

    def test_parse_invalid_json_raises(self):
        with pytest.raises(ValueError, match="not valid JSON"):
            _parse_ai_report("not json at all")

    def test_parse_non_dict_raises(self):
        with pytest.raises(ValueError, match="format invalid"):
            _parse_ai_report("[1, 2, 3]")

    def test_parse_missing_chart_summary_raises(self):
        incomplete = {"element_balance": "...", "reflection_points": [{"label": "X", "text": "Y"}]}
        with pytest.raises(ValueError, match="incomplete"):
            _parse_ai_report(json.dumps(incomplete))

    def test_parse_missing_reflection_points_raises(self):
        incomplete = {"chart_summary": "...", "element_balance": "..."}
        with pytest.raises(ValueError, match="incomplete"):
            _parse_ai_report(json.dumps(incomplete))

    def test_parse_caution_as_string(self):
        raw = json.dumps(
            {
                "chart_summary": "Overview",
                "reflection_points": [{"label": "Career", "text": "Reflect on career."}],
                "cautions": ["Caution one", "Caution two"],
            }
        )
        result = _parse_ai_report(raw)
        assert result["cautions"] == ["Caution one", "Caution two"]

    def test_parse_caution_as_dict_with_text(self):
        raw = json.dumps(
            {
                "chart_summary": "Overview",
                "reflection_points": [{"label": "Career", "text": "Reflect."}],
                "cautions": [{"text": "Dict caution"}],
            }
        )
        result = _parse_ai_report(raw)
        assert result["cautions"] == ["Dict caution"]

    def test_parse_limits_reflection_points_to_four(self):
        raw = json.dumps(
            {
                "chart_summary": "Overview",
                "reflection_points": [{"label": f"L{i}", "text": f"T{i}"} for i in range(6)],
                "cautions": [],
            }
        )
        result = _parse_ai_report(raw)
        assert len(result["reflection_points"]) == 4

    def test_parse_empty_reflection_text_skipped(self):
        raw = json.dumps(
            {
                "chart_summary": "Overview",
                "reflection_points": [
                    {"label": "Keep", "text": "Valid"},
                    {"label": "Skip", "text": ""},
                ],
                "cautions": [],
            }
        )
        result = _parse_ai_report(raw)
        assert len(result["reflection_points"]) == 1
        assert result["reflection_points"][0]["label"] == "Keep"


# ============================================================
# W6.4 服务层（mock AI）
# ============================================================


class TestBirthChartEnglishService:
    """BirthChartEnglish 服务层（注入 mock AI client）。"""

    PAYLOAD = {
        "name": "Alex",
        "gender": "male",
        "birth_date": "1990-05-01",
        "birth_time": "14:30",
    }

    def test_analyze_returns_responsible_use(self):
        result = _make_service().analyze(self.PAYLOAD)
        assert result["responsible_use"] == RESPONSIBLE_USE_TEXT

    def test_analyze_returns_chart_summary_dict(self):
        result = _make_service().analyze(self.PAYLOAD)
        assert isinstance(result["chart_summary"], dict)
        assert "year_pillar" in result["chart_summary"]
        assert "zodiac" in result["chart_summary"]

    def test_analyze_returns_reflection_points(self):
        result = _make_service().analyze(self.PAYLOAD)
        assert len(result["reflection_points"]) == 3
        assert all("label" in p and "text" in p for p in result["reflection_points"])

    def test_analyze_no_fortune_no_gua_type(self):
        """D14/D16：返回结构不含 fortune/gua_type。"""
        result = _make_service().analyze(self.PAYLOAD)
        assert "fortune" not in result
        assert "gua_type" not in result
        assert "fortune" not in result["chart_summary"]
        assert "gua_type" not in result["chart_summary"]

    def test_analyze_no_raw_chart_leak(self):
        """_raw_chart 不应泄露到最终返回。"""
        result = _make_service().analyze(self.PAYLOAD)
        assert "_raw_chart" not in result

    def test_analyze_stream_event_sequence(self):
        """流事件序列：chart → report → responsible_use（无 done，由 API 补）。"""
        events = list(_make_service().analyze_stream(self.PAYLOAD))
        types = [e["type"] for e in events]
        assert types == ["chart", "report", "responsible_use"]

    def test_analyze_stream_chart_event_english(self):
        events = list(_make_service().analyze_stream(self.PAYLOAD))
        chart = events[0]
        assert chart["type"] == "chart"
        assert chart["chart_summary"]["zodiac"] == "Horse"
        assert chart["chart_summary"]["year_pillar"] == "Yang Metal Horse"
        assert "Geng-Wu" not in chart["chart_summary"]["year_pillar"]

    def test_analyze_stream_responsible_use_event(self):
        events = list(_make_service().analyze_stream(self.PAYLOAD))
        assert events[-1]["type"] == "responsible_use"
        assert events[-1]["responsible_use"] == RESPONSIBLE_USE_TEXT

    def test_analyze_invalid_birth_data_raises(self):
        with pytest.raises(BaziInputError):
            _make_service().analyze(
                {
                    "name": "Alex",
                    "gender": "male",
                    "birth_date": "not-a-date",
                }
            )

    def test_ai_client_uses_json_object_response_format(self):
        """验证 AI 调用要求 json_object 响应格式且流式。"""
        _make_service().analyze(self.PAYLOAD)
        assert FakeCompletions.last_kwargs["response_format"] == {"type": "json_object"}
        assert FakeCompletions.last_kwargs["stream"] is True


# ============================================================
# W6.5 API 契约（使用 conftest 的 app/client fixture）
# ============================================================


class TestBirthChartEnApiContract:
    """英文 Birth Chart API 契约测试。

    测试环境无 AI_API_KEY：
    - 输入校验错误 → 400 INVALID_BIRTH_DATA
    - 合法输入 → 503 MODEL_NOT_CONFIGURED（AI 未配置）
    - stream 合法输入 → 200 SSE，chart 事件后 error + done
    """

    def test_analyze_missing_name(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "birth_date": "1990-05-01",
                "gender": "male",
            },
        )
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "INVALID_BIRTH_DATA"

    def test_analyze_empty_name(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "   ",
                "birth_date": "1990-05-01",
                "gender": "male",
            },
        )
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "INVALID_BIRTH_DATA"

    def test_analyze_name_too_long(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "x" * 31,
                "birth_date": "1990-05-01",
                "gender": "male",
            },
        )
        assert r.status_code == 400

    def test_analyze_missing_birth_date(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "gender": "male",
            },
        )
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "INVALID_BIRTH_DATA"

    def test_analyze_invalid_birth_time_type(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "gender": "male",
                "birth_time": 123,  # 非字符串
            },
        )
        assert r.status_code == 400

    def test_analyze_invalid_birth_time_unknown_type(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "gender": "male",
                "birth_time_unknown": "yes",  # 非布尔
            },
        )
        assert r.status_code == 400

    def test_analyze_non_json_body(self, client):
        r = client.post(
            "/api/en/birth-chart/analyze",
            data="not json",
            content_type="text/plain",
        )
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "INVALID_BIRTH_DATA"

    def test_analyze_invalid_birth_date(self, client):
        """非法日期格式 → 400（bazi_service 抛 BaziInputError）。"""
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "birth_date": "not-a-date",
                "gender": "male",
            },
        )
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "INVALID_BIRTH_DATA"

    def test_analyze_valid_payload_no_key(self, client):
        """合法载荷但无 AI key → 503 MODEL_NOT_CONFIGURED。"""
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "birth_time": "14:30",
                "gender": "male",
            },
        )
        assert r.status_code == 503
        assert r.get_json()["error"]["code"] == "MODEL_NOT_CONFIGURED"

    def test_stream_valid_payload_no_key(self, client):
        """stream 合法载荷无 key → 200 SSE，含 chart/error/done。"""
        r = client.post(
            "/api/en/birth-chart/stream",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "gender": "female",
            },
        )
        assert r.status_code == 200
        assert "text/event-stream" in r.headers["Content-Type"]
        text = r.data.decode("utf-8")
        assert '"type": "chart"' in text  # 基础盘先出（不需 AI）
        assert '"type": "error"' in text  # AI 失败
        assert '"type": "done"' in text  # 终止帧

    def test_stream_missing_name(self, client):
        r = client.post(
            "/api/en/birth-chart/stream",
            json={
                "birth_date": "1990-05-01",
            },
        )
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "INVALID_BIRTH_DATA"

    def test_stream_chart_event_english(self, client):
        """stream 的 chart 事件应为英文化基础盘。"""
        r = client.post(
            "/api/en/birth-chart/stream",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "gender": "male",
            },
        )
        text = r.data.decode("utf-8")
        assert "Horse" in text  # 英文生肖
        assert "Yang Metal Horse" in text  # 阴阳 + 五行 + 生肖
        assert "Geng-Wu" not in text  # 不再沿用旧拼音四柱契约
        assert '"zodiac": "马"' not in text  # 不含中文生肖

    def test_stream_no_fortune_no_gua_type(self, client):
        """D14/D16：流内容不含 fortune/gua_type。"""
        r = client.post(
            "/api/en/birth-chart/stream",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "gender": "male",
            },
        )
        text = r.data.decode("utf-8").lower()
        assert "fortune" not in text
        assert "gua_type" not in text


class TestBirthChartEnApiWithMockAi:
    """mock AI 后的完整 API 响应测试。"""

    def test_analyze_full_success(self, app, client, monkeypatch):
        """mock AI 返回，验证完整成功响应结构。"""
        service = app.extensions["birth_chart_en"]
        monkeypatch.setattr(
            service, "_generate_report", lambda prompt: _parse_ai_report(json.dumps(REPORT_EN))
        )
        r = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "birth_time": "14:30",
                "gender": "male",
            },
        )
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert "chart_summary" in data
        assert "element_balance" in data
        assert "reflection_points" in data
        assert "cautions" in data
        assert "responsible_use" in data
        assert "limitations" in data
        assert data["responsible_use"] == RESPONSIBLE_USE_TEXT
        assert "fortune" not in data
        assert "gua_type" not in data
        assert isinstance(data["chart_summary"], dict)
        assert data["chart_summary"]["zodiac"] == "Horse"

    def test_stream_full_success(self, app, client, monkeypatch):
        """mock AI 返回，验证 stream 完整事件序列。"""
        service = app.extensions["birth_chart_en"]
        monkeypatch.setattr(
            service, "_generate_report", lambda prompt: _parse_ai_report(json.dumps(REPORT_EN))
        )
        r = client.post(
            "/api/en/birth-chart/stream",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "birth_time": "14:30",
                "gender": "male",
            },
        )
        assert r.status_code == 200
        text = r.data.decode("utf-8")
        assert '"type": "chart"' in text
        assert '"type": "report"' in text
        assert '"type": "responsible_use"' in text
        assert '"type": "done"' in text
        assert RESPONSIBLE_USE_TEXT in text
        assert "fortune" not in text.lower()
        assert "gua_type" not in text.lower()

    def test_analyze_ai_timeout_returns_generic_502(self, app, client, monkeypatch):
        """上游超时不得泄漏异常细节，应返回稳定的通用错误。"""
        service = app.extensions["birth_chart_en"]

        def raise_timeout(_prompt):
            raise TimeoutError("upstream provider timeout with internal details")

        monkeypatch.setattr(service, "_generate_report", raise_timeout)
        response = client.post(
            "/api/en/birth-chart/analyze",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "birth_time": "14:30",
                "gender": "male",
            },
        )

        assert response.status_code == 502
        assert response.get_json()["error"]["code"] == "ANALYSIS_FAILED"
        assert "internal details" not in response.get_data(as_text=True)

    def test_stream_ai_timeout_ends_with_error_and_done(self, app, client, monkeypatch):
        """流式上游超时应保留基础盘，并用 error + done 正常结束。"""
        service = app.extensions["birth_chart_en"]

        def raise_timeout(_prompt):
            raise TimeoutError("upstream provider timeout with internal details")

        monkeypatch.setattr(service, "_generate_report", raise_timeout)
        response = client.post(
            "/api/en/birth-chart/stream",
            json={
                "name": "Alex",
                "birth_date": "1990-05-01",
                "birth_time": "14:30",
                "gender": "male",
            },
        )
        text = response.get_data(as_text=True)

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["Content-Type"]
        assert '"type": "chart"' in text
        assert '"error_code": "ANALYSIS_FAILED"' in text
        assert '"type": "done"' in text
        assert "internal details" not in text
