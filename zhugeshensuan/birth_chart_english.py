"""Birth Chart Reading 英文服务。

职责：
1. 复用 ``bazi_service.calculate_bazi`` 生成基础盘，再英文化（zodiac/wu_xing/gan_zhi）
2. 设计英文 AI prompt（引用 ``docs/business/wise-oracle-ai-prompt-boundaries.md`` W0.3 红线）
3. 调用 AI 生成 reflection_points / cautions（cultural self-reflection，非预测）
4. 返回结构：chart_summary / element_balance / reflection_points / cautions / responsible_use
5. SSE 流保留错误事件和结束事件

依赖：
- ``bazi_service.calculate_bazi`` 提供中文基础盘
- ``lunming.LunMing`` 提供 OpenAI client（复用配置，避免重复）
- ``error_codes`` 提供错误码

依据：
- W0.3 AI prompt 边界（``docs/business/wise-oracle-ai-prompt-boundaries.md``）
- W6.2 英文论命后端边界（``docs/plans/2026-06-27-english-site-execution-plan.md``）
- D11（保留完整入口）、D12（/api/en/* 前缀）、D17（interpretation 非 prediction）
"""

from __future__ import annotations

import json
import logging
from typing import Any, Iterator, Optional

from .bazi_service import BaziInputError, calculate_bazi
from .lunming import ModelConfigurationError

LOGGER = logging.getLogger(__name__)

# 固定免责声明（W0.3 第 1.5 节）
RESPONSIBLE_USE_TEXT = (
    "This reading is for entertainment, cultural exploration, and self-reflection only. "
    "Different traditions offer different interpretations; consider this one perspective among many. "
    "Not medical, legal, financial, psychological, or life-critical advice."
)

# 生肖中文 → 英文
ZODIAC_EN: dict[str, str] = {
    "鼠": "Rat", "牛": "Ox", "虎": "Tiger", "兔": "Rabbit",
    "龙": "Dragon", "蛇": "Snake", "马": "Horse", "羊": "Goat",
    "猴": "Monkey", "鸡": "Rooster", "狗": "Dog", "猪": "Pig",
}

# 天干中文 → 英文（拼音）
GAN_EN: dict[str, str] = {
    "甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding", "戊": "Wu",
    "己": "Ji", "庚": "Geng", "辛": "Xin", "壬": "Ren", "癸": "Gui",
}

# 地支中文 → 英文（拼音）
ZHI_EN: dict[str, str] = {
    "子": "Zi", "丑": "Chou", "寅": "Yin", "卯": "Mao", "辰": "Chen",
    "巳": "Si", "午": "Wu", "未": "Wei", "申": "Shen", "酉": "You",
    "戌": "Xu", "亥": "Hai",
}

# 五行中文 → 英文
ELEMENT_EN: dict[str, str] = {
    "金": "Metal", "木": "Wood", "水": "Water", "火": "Fire", "土": "Earth",
}

# 英文性别 → 中文（bazi_service 要求中文）
GENDER_ZH: dict[str, str] = {
    "male": "男", "female": "女",
    # 兼容中文直接传入
    "男": "男", "女": "女",
}


def _pillar_to_english(pillar: Optional[str]) -> Optional[str]:
    """四柱中文 → 英文。如 "甲子" → "Jia-Zi"。"""
    if not pillar or len(pillar) != 2:
        return None
    gan, zhi = pillar[0], pillar[1]
    return f"{GAN_EN.get(gan, gan)}-{ZHI_EN.get(zhi, zhi)}"


def _gan_to_english(gan: Optional[str]) -> Optional[str]:
    """天干中文 → 英文。"""
    if not gan or len(gan) != 1:
        return None
    return GAN_EN.get(gan, gan)


def _wu_xing_to_english(value: Optional[str]) -> Optional[str]:
    """五行组合中文 → 英文。如 "金木" → "Metal-Wood"。"""
    if not value:
        return None
    parts = [ELEMENT_EN.get(ch, ch) for ch in value if ch in ELEMENT_EN]
    return "-".join(parts) if parts else None


def _normalize_gender(gender: Any) -> str:
    """英文性别归一化为 bazi_service 要求的中文。"""
    if not isinstance(gender, str):
        return "男"
    key = gender.strip().lower()
    return GENDER_ZH.get(key, GENDER_ZH.get(gender.strip(), "男"))


def _normalize_payload(payload: dict) -> dict:
    """英文 payload 归一化：gender 英文→中文，birth_time_unknown 处理。"""
    normalized = dict(payload)
    # gender 英文 → 中文
    normalized["gender"] = _normalize_gender(payload.get("gender"))
    # birth_time_unknown=True 时清空 birth_time
    if payload.get("birth_time_unknown"):
        normalized["birth_time"] = ""
    return normalized


def build_english_chart_summary(payload: dict, default_timezone: str = "Asia/Shanghai") -> dict:
    """生成英文基础盘摘要。

    输入：payload（含 name/birth_date/birth_time/birth_time_unknown/gender/timezone）
    输出：英文基础盘 dict（chart_summary + element_balance）
    异常：BaziInputError（输入校验失败）
    """
    normalized = _normalize_payload(payload)
    chart = calculate_bazi(normalized, default_timezone)

    pillars_zh = chart["pillars"]
    pillars_en = {
        "year": _pillar_to_english(pillars_zh.get("year")),
        "month": _pillar_to_english(pillars_zh.get("month")),
        "day": _pillar_to_english(pillars_zh.get("day")),
        "time": _pillar_to_english(pillars_zh.get("time")),
    }

    wu_xing_zh = chart["wu_xing"]
    wu_xing_en = {
        key: _wu_xing_to_english(value) for key, value in wu_xing_zh.items()
    }

    counts_zh = chart["wu_xing_counts"]
    element_balance = {
        ELEMENT_EN.get(elem, elem): count for elem, count in counts_zh.items()
    }

    zodiac_zh = chart.get("zodiac", "")
    zodiac_en = ZODIAC_EN.get(zodiac_zh, zodiac_zh)

    day_master_zh = chart.get("day_master")
    day_master_en = _gan_to_english(day_master_zh)

    return {
        "chart_summary": {
            "year_pillar": pillars_en["year"],
            "month_pillar": pillars_en["month"],
            "day_pillar": pillars_en["day"],
            "time_pillar": pillars_en["time"],
            "day_master": day_master_en,
            "zodiac": zodiac_en,
            "lunar_date": chart.get("calendar", {}).get("lunar_date", ""),
            "time_unknown": chart.get("time_unknown", False),
        },
        "element_balance": element_balance,
        "limitations": chart.get("limitations", []),
        # 保留中文基础盘供 AI prompt 使用（不暴露给前端）
        "_raw_chart": chart,
    }


# ============================================================
# AI prompt（引用 W0.3 红线）
# ============================================================


def build_english_prompt(chart_data: dict, payload: dict) -> str:
    """构建英文 AI prompt。

    依据 W0.3 ``docs/business/wise-oracle-ai-prompt-boundaries.md``：
    - 定位 cultural self-reflection prompt，非 prediction
    - 禁止医疗/法律/财务/心理/生育/死亡/灾难/确定性未来/吉凶分级/卦属
    - 措辞用 "traditionally suggests" / "invites reflection on"
    - 末尾含 responsible-use 免责声明
    """
    name = payload.get("name", "")
    gender = payload.get("gender", "")
    return (
        "You are a cultural interpreter for traditional Chinese BaZi (Four Pillars) astrology. "
        "Your role is to offer cultural self-reflection prompts, NOT predictions or advice.\n\n"
        "RED LINES (must follow strictly):\n"
        "- Do NOT output medical, legal, financial, psychological, fertility, death, or disaster statements.\n"
        "- Do NOT use 'will' for life predictions.\n"
        "- Do NOT assign fortune grades or hexagram types.\n"
        "- Use 'traditionally suggests' / 'invites reflection on' / 'one cultural reading is'.\n"
        "- Keep each point concise (40-80 words).\n\n"
        "Return ONLY a JSON object with this exact structure:\n"
        "{\n"
        "  \"chart_summary\": \"One-paragraph cultural overview of the chart (60-120 words)\",\n"
        "  \"element_balance\": \"Brief note on the five-element pattern (40-80 words)\",\n"
        "  \"reflection_points\": [\n"
        "    {\"label\": \"Career\", \"text\": \"...\"},\n"
        "    {\"label\": \"Relationships\", \"text\": \"...\"},\n"
        "    {\"label\": \"Personal Growth\", \"text\": \"...\"}\n"
        "  ],\n"
        "  \"cautions\": [\n"
        "    \"Cultural caution 1 (not prediction)\",\n"
        "    \"Cultural caution 2\"\n"
        "  ]\n"
        "}\n\n"
        "reflection_points must have 2-4 items with labels like Career, Relationships, "
        "Personal Growth, or Energy Patterns. "
        "cautions must be cultural reflections, NOT predictions (e.g., 'This pattern invites "
        "reflection on patience' rather than 'You will face delays'). "
        "Do NOT include a responsible_use field; the system appends it automatically.\n\n"
        f"Birth chart data (Chinese terms preserved for accuracy): "
        f"{json.dumps(chart_data, ensure_ascii=False)}\n"
        f"Name: {name}\nGender: {gender}\n"
    )


def _parse_ai_report(raw_response: str) -> dict:
    """解析 AI 返回的 JSON 报告。"""
    text = raw_response.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```")
        text = text.removesuffix("```").strip()
    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("AI report is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("AI report format invalid")

    def _clean(value, fallback=""):
        return value.strip() if isinstance(value, str) and value.strip() else fallback

    reflection_points = []
    for item in payload.get("reflection_points", []):
        if not isinstance(item, dict):
            continue
        point_text = _clean(item.get("text"))
        if point_text:
            reflection_points.append(
                {"label": _clean(item.get("label"), "Reflection"), "text": point_text}
            )

    cautions = []
    for item in payload.get("cautions", []):
        caution_text = _clean(item) if isinstance(item, str) else _clean(item.get("text")) if isinstance(item, dict) else ""
        if caution_text:
            cautions.append(caution_text)

    chart_summary = _clean(payload.get("chart_summary"))
    element_balance = _clean(payload.get("element_balance"))
    if not chart_summary or not reflection_points:
        raise ValueError("AI report content incomplete")

    return {
        "chart_summary": chart_summary,
        "element_balance": element_balance,
        "reflection_points": reflection_points[:4],
        "cautions": cautions[:3],
    }


class BirthChartEnglish:
    """英文 Birth Chart Reading 服务。

    复用 LunMing 的 OpenAI client（配置统一），独立实现英文 prompt 和返回结构。
    """

    def __init__(self, lunming, default_timezone: str = "Asia/Shanghai"):
        """初始化。

        输入：
            lunming: LunMing 实例（复用其 client/model/temperature）
            default_timezone: 默认时区
        """
        self.lunming = lunming
        self.default_timezone = default_timezone

    @property
    def client(self):
        """复用 lunming 的 OpenAI client。无 key 时抛 ModelConfigurationError。"""
        return self.lunming.client

    @property
    def model(self) -> str:
        return self.lunming.model

    @property
    def temperature(self) -> float:
        return self.lunming.temperature

    def build_chart_summary(self, payload: dict) -> dict:
        """生成英文基础盘摘要（不含 AI 解读）。"""
        return build_english_chart_summary(payload, self.default_timezone)

    def _stream_completion(self, prompt: str) -> Iterator[str]:
        """流式调用 AI，逐块返回文本。"""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a cultural interpreter for traditional Chinese BaZi astrology. "
                        "You offer cultural self-reflection, NOT predictions. "
                        "You respect factual boundaries and do not use fear-based tactics."
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

    def _generate_report(self, prompt: str) -> dict:
        """完整调用 AI 并解析报告。"""
        raw = "".join(self._stream_completion(prompt))
        return _parse_ai_report(raw)

    def analyze(self, payload: dict) -> dict:
        """完整分析：基础盘 + AI 报告。

        输出：{chart_summary, element_balance, reflection_points, cautions, responsible_use, limitations}
        异常：BaziInputError / ModelConfigurationError / ValueError
        """
        chart_data = self.build_chart_summary(payload)
        raw_chart = chart_data.pop("_raw_chart", {})
        prompt = build_english_prompt(raw_chart, payload)
        LOGGER.info("Starting English birth chart analysis with model %s", self.model)
        report = self._generate_report(prompt)
        return {
            "chart_summary": chart_data["chart_summary"],
            "element_balance": report["element_balance"] or self._element_balance_note(chart_data),
            "reflection_points": report["reflection_points"],
            "cautions": report["cautions"],
            "responsible_use": RESPONSIBLE_USE_TEXT,
            "limitations": chart_data["limitations"],
        }

    def analyze_stream(self, payload: dict) -> Iterator[dict]:
        """SSE 流式分析。

        事件序列（不含终止帧，由 API 层补 done）：
        - {type: "chart", chart_summary:..., element_balance:..., limitations:...}
        - {type: "report", chart_summary:..., element_balance:..., reflection_points:..., cautions:...}
        - {type: "responsible_use", responsible_use:...}

        终止帧 {type: "done", done: true} 由 ``birth_chart_en_api`` 在正常完成
        或异常分支后统一补发，避免重复 done。与 ``lunming.analyze_bazi_stream`` 对齐。
        """
        chart_data = self.build_chart_summary(payload)
        raw_chart = chart_data.pop("_raw_chart", {})
        prompt = build_english_prompt(raw_chart, payload)
        LOGGER.info("Starting English birth chart stream with model %s", self.model)
        yield {
            "type": "chart",
            "chart_summary": chart_data["chart_summary"],
            "element_balance": chart_data["element_balance"],
            "limitations": chart_data["limitations"],
        }
        report = self._generate_report(prompt)
        yield {
            "type": "report",
            "chart_summary": report["chart_summary"],
            "element_balance": report["element_balance"] or self._element_balance_note(chart_data),
            "reflection_points": report["reflection_points"],
            "cautions": report["cautions"],
        }
        yield {"type": "responsible_use", "responsible_use": RESPONSIBLE_USE_TEXT}

    @staticmethod
    def _element_balance_note(chart_data: dict) -> str:
        """AI 未返回 element_balance 时的兜底文案。"""
        balance = chart_data.get("element_balance", {})
        if not balance:
            return ""
        parts = [f"{elem}: {count}" for elem, count in balance.items() if count]
        return f"Element distribution — {', '.join(parts)}."
