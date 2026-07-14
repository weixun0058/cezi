import json
import logging

from openai import OpenAI

from .bazi_service import calculate_bazi
from .i18n_utils import DEFAULT_LANG, get_disclaimer, get_report_section_titles

LOGGER = logging.getLogger(__name__)


class ModelConfigurationError(RuntimeError):
    pass


class LunMing:
    def __init__(
        self,
        api_key="",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
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
        chart = calculate_bazi(payload, self.default_timezone)
        return chart

    def generate_prompt(self, payload, chart, *, lang=DEFAULT_LANG):
        time_note = "时辰未知，不得推断时柱相关内容。" if chart["time_unknown"] else ""
        if lang == "zh-hant":
            output_lang_note = "请使用繁体中文输出所有内容。"
        else:
            output_lang_note = "请使用简体中文输出所有内容。"
        return (
            "请基于下列由历法程序确定计算的结构化命盘，进行传统文化解读，并只返回 JSON 对象。"
            "不得重新计算或修改四柱；使用可能性表达，不得作确定性的医疗、投资、婚姻、寿命或灾祸结论。"
            "健康内容只能给出一般生活方式建议并提示咨询专业人士。"
            "避免重复罗列命盘基础数据，避免使用 Markdown、星号、标题符号和编号。"
            "语言应平实、具体、易读，每个要点控制在 60 至 120 个汉字。"
            f"{output_lang_note}"
            "JSON 必须严格采用以下结构："
            '{"summary":"总览文字","keywords":["关键词一","关键词二","关键词三"],'
            '"sections":['
            '{"id":"five_elements","points":[{"label":"观察","text":"内容"}]},'
            '{"id":"temperament","points":[{"label":"倾向","text":"内容"}]},'
            '{"id":"career_learning","points":[{"label":"方向","text":"内容"}]},'
            '{"id":"relationships","points":[{"label":"相处","text":"内容"}]},'
            '{"id":"luck_cycles","points":[{"label":"当下","text":"内容"}]}],'
            '"actions":[{"title":"日常取向","text":"可执行建议"}],'
            '"closing":"简短收束语"}。'
            "sections 中五个 id 必须全部出现且顺序不变，"
            "每节给出 1 至 3 个 points；actions 给出 2 至 4 项。"
            f"{time_note}\n性别：{payload.get('gender', '男')}\n"
            f"命盘数据：{json.dumps(chart, ensure_ascii=False)}"
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
            response_format={"type": "json_object"},
            stream=True,
        )
        for chunk in stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            content = getattr(choices[0].delta, "content", None)
            if content:
                yield content

    @staticmethod
    def _text(value, fallback=""):
        return value.strip() if isinstance(value, str) and value.strip() else fallback

    def _parse_report(self, raw_response, *, lang=DEFAULT_LANG):
        text = raw_response.strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```")
            text = text.removesuffix("```").strip()
        try:
            payload = json.loads(text)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("模型未返回有效的结构化解读") from exc
        if not isinstance(payload, dict):
            raise ValueError("模型解读格式无效")

        keywords = [self._text(item) for item in payload.get("keywords", [])]
        keywords = [item for item in keywords if item][:4]
        section_titles = get_report_section_titles(lang)
        source_sections = {
            item.get("id"): item
            for item in payload.get("sections", [])
            if isinstance(item, dict) and item.get("id") in section_titles
        }
        sections = []
        for section_id, title in section_titles.items():
            source = source_sections.get(section_id, {})
            points = []
            for point in source.get("points", []):
                if not isinstance(point, dict):
                    continue
                point_text = self._text(point.get("text"))
                if point_text:
                    points.append(
                        {
                            "label": self._text(point.get("label"), "解读"),
                            "text": point_text,
                        }
                    )
            if points:
                sections.append({"id": section_id, "title": title, "points": points[:3]})

        actions = []
        for action in payload.get("actions", []):
            if not isinstance(action, dict):
                continue
            action_text = self._text(action.get("text"))
            if action_text:
                actions.append(
                    {
                        "title": self._text(action.get("title"), "行事参考"),
                        "text": action_text,
                    }
                )
        summary = self._text(payload.get("summary"))
        if not summary or not sections:
            raise ValueError("模型解读内容不完整")
        return {
            "summary": summary,
            "keywords": keywords,
            "sections": sections,
            "actions": actions[:4],
            "closing": self._text(payload.get("closing")),
        }

    def _generate_report(self, prompt, *, lang=DEFAULT_LANG):
        return self._parse_report("".join(self._completion_stream(prompt)), lang=lang)

    def analyze_bazi_stream(self, payload, *, lang=DEFAULT_LANG):
        chart = self.build_chart(payload)
        prompt = self.generate_prompt(payload, chart, lang=lang)
        LOGGER.info("Starting bazi interpretation with model %s", self.model)
        yield {"type": "chart", "chart": chart, "disclaimer": get_disclaimer(lang)}
        report = self._generate_report(prompt, lang=lang)
        yield {
            "type": "report_start",
            "summary": report["summary"],
            "keywords": report["keywords"],
        }
        for section in report["sections"]:
            yield {"type": "report_section", "section": section}
        yield {
            "type": "report_end",
            "actions": report["actions"],
            "closing": report["closing"],
        }

    def analyze_bazi(self, payload, *, lang=DEFAULT_LANG):
        chart = self.build_chart(payload)
        prompt = self.generate_prompt(payload, chart, lang=lang)
        report = self._generate_report(prompt, lang=lang)
        return {"chart": chart, "report": report, "disclaimer": get_disclaimer(lang)}
