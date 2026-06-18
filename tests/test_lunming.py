from types import SimpleNamespace

from lunming import LunMing


class FakeCompletions:
    @staticmethod
    def create(**_kwargs):
        return [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="第一段"))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="第二段"))]),
        ]


class FakeClient:
    chat = SimpleNamespace(completions=FakeCompletions())


def test_full_analysis_consumes_stream_into_structured_result():
    service = LunMing(client=FakeClient())
    result = service.analyze_bazi(
        {"name": "测试", "gender": "男", "birth_date": "1990-01-01", "birth_time": "未知"}
    )
    assert result["analysis"] == "第一段第二段"
    assert result["chart"]["pillars"]["time"] is None
    assert result["disclaimer"]
