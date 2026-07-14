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
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .bazi_service import calculate_bazi

LOGGER = logging.getLogger(__name__)

# 按模板绝对路径缓存；服务实例通过构造函数注入路径，不依赖 Flask 全局状态。
_PROMPT_TEMPLATE_CACHE: dict[Path, str] = {}

# 固定免责声明（W0.3 第 1.5 节）
RESPONSIBLE_USE_TEXT = (
    "This reading is for entertainment, cultural exploration, and self-reflection only. "
    "Different traditions offer different interpretations; consider this one perspective "
    "among many. "
    "Not medical, legal, financial, psychological, or life-critical advice."
)

# 生肖中文 → 英文
ZODIAC_EN: dict[str, str] = {
    "鼠": "Rat",
    "牛": "Ox",
    "虎": "Tiger",
    "兔": "Rabbit",
    "龙": "Dragon",
    "蛇": "Snake",
    "马": "Horse",
    "羊": "Goat",
    "猴": "Monkey",
    "鸡": "Rooster",
    "狗": "Dog",
    "猪": "Pig",
}

# 天干中文 → 英文（拼音）
# 天干 → 阴阳 + 五行（用于 pillar 描述式翻译）
GAN_YIN_YANG: dict[str, str] = {
    "甲": "Yang",
    "丙": "Yang",
    "戊": "Yang",
    "庚": "Yang",
    "壬": "Yang",
    "乙": "Yin",
    "丁": "Yin",
    "己": "Yin",
    "辛": "Yin",
    "癸": "Yin",
}
GAN_ELEMENT: dict[str, str] = {
    "甲": "Wood",
    "乙": "Wood",
    "丙": "Fire",
    "丁": "Fire",
    "戊": "Earth",
    "己": "Earth",
    "庚": "Metal",
    "辛": "Metal",
    "壬": "Water",
    "癸": "Water",
}

# 地支 → 生肖英文（用于 pillar 描述式翻译，与黄历一致）
ZHI_TO_ZODIAC: dict[str, str] = {
    "子": "Rat",
    "丑": "Ox",
    "寅": "Tiger",
    "卯": "Rabbit",
    "辰": "Dragon",
    "巳": "Snake",
    "午": "Horse",
    "未": "Goat",
    "申": "Monkey",
    "酉": "Rooster",
    "戌": "Dog",
    "亥": "Pig",
}

# 五行中文 → 英文
ELEMENT_EN: dict[str, str] = {
    "金": "Metal",
    "木": "Wood",
    "水": "Water",
    "火": "Fire",
    "土": "Earth",
}

# 英文性别 → 中文（bazi_service 要求中文）
GENDER_ZH: dict[str, str] = {
    "male": "男",
    "female": "女",
    # 兼容中文直接传入
    "男": "男",
    "女": "女",
}

CHINESE_DIGIT_EN = {
    "〇": "0",
    "零": "0",
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
}
LUNAR_DATE_RE = re.compile(r"(?P<year>.+?)年(?P<leap>闰?)(?P<month>.+?)月(?P<day>.+)$")


def _chinese_calendar_number(value: str) -> int | None:
    value = value.removeprefix("初")
    if value in CHINESE_DIGIT_EN:
        return int(CHINESE_DIGIT_EN[value])
    if value == "十":
        return 10
    if value.startswith("十"):
        tail = CHINESE_DIGIT_EN.get(value[1:])
        return 10 + int(tail) if tail else None
    if value.startswith("廿"):
        tail = CHINESE_DIGIT_EN.get(value[1:], "0")
        return 20 + int(tail)
    if value.startswith("三十"):
        tail = CHINESE_DIGIT_EN.get(value[2:], "0")
        return 30 + int(tail)
    return None


def _lunar_date_to_english(value: str) -> str | None:
    match = LUNAR_DATE_RE.fullmatch(value or "")
    if not match:
        return None
    year_digits = "".join(CHINESE_DIGIT_EN.get(char, "") for char in match["year"])
    month = _chinese_calendar_number(match["month"])
    day = _chinese_calendar_number(match["day"])
    if len(year_digits) != 4 or month is None or day is None:
        return None
    leap = "Leap " if match["leap"] else ""
    return f"Lunar Year {year_digits}, {leap}Month {month}, Day {day}"


def _pillar_to_english(pillar: str | None) -> str | None:
    """四柱中文 → 英文描述式。如 "丙午" → "Yang Fire Horse"。

    格式：阴阳 + 五行（天干） + 生肖（地支），与黄历页面干支显示保持一致。
    """
    if not pillar or len(pillar) != 2:
        return None
    gan, zhi = pillar[0], pillar[1]
    yin_yang = GAN_YIN_YANG.get(gan, "")
    element = GAN_ELEMENT.get(gan, "")
    zodiac = ZHI_TO_ZODIAC.get(zhi, "")
    if yin_yang and element and zodiac:
        return f"{yin_yang} {element} {zodiac}"
    return None


def _gan_to_english(gan: str | None) -> str | None:
    """天干中文 → 英文描述式。如 "丁" → "Yin Fire"。

    格式：阴阳 + 五行，与 pillar 显示风格一致。
    """
    if not gan or len(gan) != 1:
        return None
    yin_yang = GAN_YIN_YANG.get(gan, "")
    element = GAN_ELEMENT.get(gan, "")
    if yin_yang and element:
        return f"{yin_yang} {element}"
    return None


def _wu_xing_to_english(value: str | None) -> str | None:
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

    counts_zh = chart["wu_xing_counts"]
    element_balance = {ELEMENT_EN.get(elem, elem): count for elem, count in counts_zh.items()}

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
            "lunar_date": _lunar_date_to_english(chart.get("calendar", {}).get("lunar_date", "")),
            "time_unknown": chart.get("time_unknown", False),
        },
        "element_balance": element_balance,
        "limitations": (
            ["Birth time is unknown, so the time pillar and dependent details are omitted."]
            if chart.get("time_unknown", False)
            else []
        ),
        # 保留中文基础盘供 AI prompt 使用（不暴露给前端）
        "_raw_chart": chart,
    }


# ============================================================
# AI prompt（从 prompts/birth_chart_en_prompt.md 加载，引用 W0.3 红线）
# ============================================================


def _load_prompt_template(prompt_path: str | Path | None = None) -> str:
    """加载提示词模板。

    优先从 config.BIRTH_CHART_PROMPT_PATH 读取 Markdown 文件；
    文件缺失时回退到代码内置的最小模板（保证服务可用）。

    模板中使用占位符：
    - {chart_data_json} — 命盘数据 JSON 字符串
    - {name} — 用户姓名
    - {gender} — 用户性别

    用 str.replace 替换（非 str.format），避免 JSON 中的花括号被误解析。
    """
    if prompt_path:
        template_path = Path(prompt_path).resolve()
        cached = _PROMPT_TEMPLATE_CACHE.get(template_path)
        if cached is not None:
            return cached
        try:
            template = template_path.read_text(encoding="utf-8")
            _PROMPT_TEMPLATE_CACHE[template_path] = template
            LOGGER.info("Loaded birth chart prompt template from %s", template_path)
            return template
        except (OSError, UnicodeDecodeError) as exc:
            LOGGER.warning("Failed to load prompt template from %s: %s", template_path, exc)

    # 回退：代码内置最小模板
    LOGGER.warning("Using fallback inline prompt template")
    return (
        "You are a cultural interpreter for traditional Chinese BaZi (Four Pillars) astrology. "
        "Your role is to offer cultural self-reflection prompts, NOT predictions or advice.\n\n"
        "LANGUAGE: You MUST respond entirely in English. "
        "Do NOT output any Chinese characters in your response. "
        "Translate all Chinese terms in the input data to English.\n\n"
        "RED LINES:\n"
        "- Do NOT output medical, legal, financial, psychological, fertility, death, "
        "or disaster statements.\n"
        "- Do NOT use 'will' for life predictions.\n"
        "- Do NOT assign fortune grades or hexagram types.\n"
        "- Use 'traditionally suggests' / 'invites reflection on' / 'one cultural reading is'.\n"
        "- Keep each point concise (40-80 words).\n\n"
        "Return ONLY a JSON object with this exact structure:\n"
        "{\n"
        '  "chart_summary": "One-paragraph cultural overview of the chart (60-120 words)",\n'
        '  "element_balance": "Brief note on the five-element pattern (40-80 words)",\n'
        '  "reflection_points": [\n'
        '    {"label": "Career", "text": "..."},\n'
        '    {"label": "Relationships", "text": "..."},\n'
        '    {"label": "Personal Growth", "text": "..."}\n'
        "  ],\n"
        '  "cautions": [\n'
        '    "Cultural caution 1 (not prediction)",\n'
        '    "Cultural caution 2"\n'
        "  ]\n"
        "}\n\n"
        "reflection_points must have 2-4 items. "
        "cautions must be cultural reflections, NOT predictions. "
        "Do NOT include a responsible_use field.\n\n"
        "Birth chart data (Chinese terms preserved for accuracy, "
        "but you MUST translate them to English in your response):\n"
        "{chart_data_json}\n"
        "Name: {name}\nGender: {gender}\n"
    )


def build_english_prompt(
    chart_data: dict,
    payload: dict,
    prompt_path: str | Path | None = None,
) -> str:
    """构建英文 AI prompt。

    从 ``prompts/birth_chart_en_prompt.md`` 加载模板，替换占位符：
    - {chart_data_json} — 命盘数据 JSON
    - {name} — 用户姓名
    - {gender} — 用户性别

    依据 W0.3 ``docs/business/wise-oracle-ai-prompt-boundaries.md``：
    - 定位 cultural self-reflection prompt，非 prediction
    - 禁止医疗/法律/财务/心理/生育/死亡/灾难/确定性未来/吉凶分级/卦属
    - 强制英文输出（输入数据含中文术语，AI 必须翻译为英文）
    """
    template = _load_prompt_template(prompt_path)
    chart_data_json = json.dumps(chart_data, ensure_ascii=False)
    # 用 replace 而非 format，避免 JSON 中的花括号被误解析
    return (
        template.replace("{chart_data_json}", chart_data_json)
        .replace("{name}", str(payload.get("name", "")))
        .replace("{gender}", str(payload.get("gender", "")))
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
        caution_text = (
            _clean(item)
            if isinstance(item, str)
            else _clean(item.get("text")) if isinstance(item, dict) else ""
        )
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

    def __init__(
        self,
        lunming,
        default_timezone: str = "Asia/Shanghai",
        prompt_path: str | Path | None = None,
    ):
        """初始化。

        输入：
            lunming: LunMing 实例（复用其 client/model/temperature）
            default_timezone: 默认时区
            prompt_path: 提示词模板路径；由应用工厂注入，服务不读取 Flask 全局状态
        """
        self.lunming = lunming
        self.default_timezone = default_timezone
        self.prompt_path = prompt_path

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
                        "You respect factual boundaries and do not use fear-based tactics. "
                        "You MUST respond entirely in English. "
                        "Do NOT output any Chinese characters in your response. "
                        "Translate all Chinese terms in the input data to English."
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

        输出：chart_summary、element_balance、reflection_points、cautions、
        responsible_use、limitations
        异常：BaziInputError / ModelConfigurationError / ValueError
        """
        chart_data = self.build_chart_summary(payload)
        raw_chart = chart_data.pop("_raw_chart", {})
        prompt = build_english_prompt(raw_chart, payload, self.prompt_path)
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
        - report：chart_summary、element_balance、reflection_points、cautions
        - {type: "responsible_use", responsible_use:...}

        终止帧 {type: "done", done: true} 由 ``birth_chart_en_api`` 在正常完成
        或异常分支后统一补发，避免重复 done。与 ``lunming.analyze_bazi_stream`` 对齐。
        """
        chart_data = self.build_chart_summary(payload)
        raw_chart = chart_data.pop("_raw_chart", {})
        prompt = build_english_prompt(raw_chart, payload, self.prompt_path)
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
