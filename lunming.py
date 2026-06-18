import json
import logging

from openai import OpenAI

from bazi_service import calculate_bazi

LOGGER = logging.getLogger(__name__)
DISCLAIMER = "传统文化娱乐参考，不构成医疗、投资或人生决策建议。"


class ModelConfigurationError(RuntimeError):
    pass


class LunMing:
    def __init__(
        self,
        api_key="",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        timeout=60,
        temperature=0.7,
        default_timezone="Asia/Shanghai",
        client=None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.default_timezone = default_timezone
        self._client = client

    @property
    def client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise ModelConfigurationError("AI 服务尚未配置，请联系管理员")
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        return self._client

    def build_chart(self, payload):
        return calculate_bazi(payload, self.default_timezone)

    def generate_prompt(self, payload, chart):
        time_note = "时辰未知，不得推断时柱相关内容。" if chart["time_unknown"] else ""
        return (
            "请基于下列由历法程序确定计算的结构化命盘，进行传统文化解读。"
            "不得重新计算或修改四柱；使用可能性表达，不得作确定性的医疗、投资、婚姻、寿命或灾祸结论。"
            "健康内容只能给出一般生活方式建议并提示咨询专业人士。"
            "请依次说明命盘基础、五行观察、性格倾向、事业与学习、人际关系、大运文化解读和可执行建议。"
            f"{time_note}\n性别：{payload.get('gender', '男')}\n"
            f"命盘数据：{json.dumps(chart, ensure_ascii=False)}\n"
            f"结尾必须原样附上：{DISCLAIMER}"
        )

    def _completion_stream(self, prompt):
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是传统历法文化解读助手。尊重事实边界，"
                        "不使用心理操纵话术，不制造恐惧。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            stream=True,
        )
        for chunk in stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            content = getattr(choices[0].delta, "content", None)
            if content:
                yield content

    def analyze_bazi_stream(self, payload):
        chart = self.build_chart(payload)
        prompt = self.generate_prompt(payload, chart)
        LOGGER.info("Starting bazi interpretation with model %s", self.model)
        yield {"type": "chart", "chart": chart, "disclaimer": DISCLAIMER}
        for text in self._completion_stream(prompt):
            yield {"type": "text", "text": text}

    def analyze_bazi(self, payload):
        chart = self.build_chart(payload)
        prompt = self.generate_prompt(payload, chart)
        analysis = "".join(self._completion_stream(prompt))
        return {"chart": chart, "analysis": analysis, "disclaimer": DISCLAIMER}
