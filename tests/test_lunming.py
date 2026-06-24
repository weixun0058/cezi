import json
from types import SimpleNamespace

import pytest

from zhugeshensuan.lunming import LunMing

REPORT = {
    "summary": "整体气象平稳，做事重视根基与节奏。",
    "keywords": ["稳健", "务实", "耐心"],
    "sections": [
        {
            "id": "five_elements",
            "points": [{"label": "观察", "text": "五行之间有生有制，宜关注长期平衡。"}],
        },
        {
            "id": "temperament",
            "points": [{"label": "倾向", "text": "处事审慎，遇到变化时通常先观察再行动。"}],
        },
        {
            "id": "career_learning",
            "points": [{"label": "方向", "text": "适合在清晰目标下持续积累专业能力。"}],
        },
        {
            "id": "relationships",
            "points": [{"label": "相处", "text": "沟通时明确表达需求，有助于减少误解。"}],
        },
        {
            "id": "luck_cycles",
            "points": [{"label": "当下", "text": "当前阶段宜稳步推进，不必追求短期定论。"}],
        },
    ],
    "actions": [{"title": "日常取向", "text": "保持规律作息并按阶段复盘目标。"}],
    "closing": "知其势，守其度。",
}


class FakeCompletions:
    last_kwargs = None

    @classmethod
    def create(cls, **kwargs):
        cls.last_kwargs = kwargs
        content = json.dumps(REPORT, ensure_ascii=False)
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


def test_full_analysis_consumes_json_stream_into_structured_result():
    service = LunMing(client=FakeClient())
    result = service.analyze_bazi(
        {"name": "测试", "gender": "男", "birth_date": "1990-01-01", "birth_time": "未知"}
    )

    assert result["report"]["summary"] == REPORT["summary"]
    assert result["report"]["sections"][0]["title"] == "五行气象"
    assert result["chart"]["pillars"]["time"] is None
    assert result["disclaimer"]
    assert FakeCompletions.last_kwargs["model"] == "deepseek-v4-flash"
    assert FakeCompletions.last_kwargs["response_format"] == {"type": "json_object"}
    assert FakeCompletions.last_kwargs["stream"] is True


def test_stream_emits_structured_report_sections():
    service = LunMing(client=FakeClient())
    events = list(
        service.analyze_bazi_stream(
            {"name": "测试", "gender": "女", "birth_date": "1990-01-01", "birth_time": "未知"}
        )
    )

    assert events[0]["type"] == "chart"
    assert events[1]["type"] == "report_start"
    assert [event["section"]["id"] for event in events if event["type"] == "report_section"] == [
        "five_elements",
        "temperament",
        "career_learning",
        "relationships",
        "luck_cycles",
    ]
    assert events[-1]["type"] == "report_end"


def test_invalid_model_json_is_rejected():
    service = LunMing(client=FakeClient())
    with pytest.raises(ValueError, match="有效的结构化解读"):
        service._parse_report("not json")
