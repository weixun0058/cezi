"""英文黄历服务。

职责：
1. 启动时从 ``data/content/huangli_terms_en.json`` 加载英文黄历词表（活动类别+神煞+命名空间映射）
2. 从 ``data/content/huangli_scenarios_en.json`` 加载首发场景定义
3. 将中文 ``HuangLi.get_daily_huangli()`` 返回的中文 record 翻译为结构化英文 record
4. 遵循 D6 文化表达指南：神煞"Auspicious/Inauspicious Spirits"（不用 evil spirits）
5. 未审核词隐藏并记录 translation_missing（默认不暴露，``?debug=1`` 可返回 ``_missing`` 字段）
6. 不泄漏中文原词到英文 API 响应

依赖：
- ``huangli.HuangLi`` 提供中文基准数据（不修改，只读取 record）
- ``data/content/huangli_terms_en.json`` 提供英文词表
- ``data/content/huangli_scenarios_en.json`` 提供场景定义

依据：
- D6 文化表达指南（``docs/business/wise-oracle-cultural-expression-guide.md``）
- D16 卦属/吉凶不展示
- W5.1 英文黄历后端实现计划（``.trae/documents/W5.1-english-huangli-backend.md``）
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

LOGGER = logging.getLogger(__name__)

# CJK 检测：覆盖中日韩统一表意文字基本区（用于验证无中文泄漏）
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

# 固定免责声明（W0.4 responsible-use 底线）
RESPONSIBLE_USE_TEXT = (
    "For entertainment, cultural exploration, and self-reflection only. "
    "Not medical, legal, financial, psychological, or life-critical advice."
)

# 天干拼音（clash_pillar / peng_zu 需要，terms.stems 是阴阳五行非拼音）
GAN_PINYIN: dict[str, str] = {
    "甲": "Jia",
    "乙": "Yi",
    "丙": "Bing",
    "丁": "Ding",
    "戊": "Wu",
    "己": "Ji",
    "庚": "Geng",
    "辛": "Xin",
    "壬": "Ren",
    "癸": "Gui",
}

# 地支→生肖中文（terms 无 branch_to_zodiac，本地定义用于 chong_sha clashes_with）
BRANCH_TO_ZODIAC_CN: dict[str, str] = {
    "子": "鼠",
    "丑": "牛",
    "寅": "虎",
    "卯": "兔",
    "辰": "龙",
    "巳": "蛇",
    "午": "马",
    "未": "羊",
    "申": "猴",
    "酉": "鸡",
    "戌": "狗",
    "亥": "猪",
}

# 中文数字 → int 映射（用于 lunar_date 解析）
CHINESE_DIGITS: dict[str, int] = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}

# 干支后缀中文 → 英文
GAN_ZHI_SUFFIX_MAP: dict[str, str] = {
    "年": "Year",
    "月": "Month",
    "日": "Day",
    "时": "Hour",
}

# 节日类型中文 → 英文
FESTIVAL_TYPE_MAP: dict[str, str] = {
    "农历节日": "Lunar Festival",
    "阳历节日": "Solar Festival",
}

# 冲煞正则：冲午(庚)煞南
CHONG_SHA_RE = re.compile(r"冲(.+?)\((.+?)\)煞(.+)")

# 方位正则：西南(坤)
POSITION_RE = re.compile(r"(.+?)\((.+?)\)")


# ============================================================
# S2: 词表加载函数 + 反向索引
# ============================================================


def load_huangli_terms(json_path: Path) -> dict:
    """加载英文黄历词表 JSON。

    输入：json_path - huangli_terms_en.json 路径
    输出：词表 dict（含 activity_categories/excluded_activities/special_rules/各命名空间映射）
    异常：文件不存在或 JSON 格式错误抛异常（由 app.py 捕获）
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("黄历词表 JSON 必须是对象")
    LOGGER.info("Loaded huangli terms from %s", json_path)
    return data


def load_huangli_terms_safe(json_path: Path) -> dict:
    """安全加载词表：文件缺失或异常时返回空字典并记 warning。

    用于 app.py 启动期，避免缺数据文件导致整个服务启动失败。
    """
    try:
        return load_huangli_terms(json_path)
    except FileNotFoundError:
        LOGGER.warning("Huangli terms file not found: %s", json_path)
        return {}
    except (json.JSONDecodeError, ValueError) as exc:
        LOGGER.warning("Failed to load huangli terms from %s: %s", json_path, exc)
        return {}


def load_huangli_scenarios(json_path: Path) -> dict:
    """加载英文黄历场景定义 JSON。

    输入：json_path - huangli_scenarios_en.json 路径
    输出：场景 dict（含 scenarios 命名空间）
    异常：文件不存在或 JSON 格式错误抛异常
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("黄历场景 JSON 必须是对象")
    LOGGER.info("Loaded huangli scenarios from %s", json_path)
    return data


def load_huangli_scenarios_safe(json_path: Path) -> dict:
    """安全加载场景：文件缺失或异常时返回空字典并记 warning。"""
    try:
        return load_huangli_scenarios(json_path)
    except FileNotFoundError:
        LOGGER.warning("Huangli scenarios file not found: %s", json_path)
        return {}
    except (json.JSONDecodeError, ValueError) as exc:
        LOGGER.warning("Failed to load huangli scenarios from %s: %s", json_path, exc)
        return {}


def build_word_to_category(terms: dict) -> dict[str, str]:
    """构建 {中文原词: 类别key} 反向索引。

    输入：terms 词表（含 activity_categories）
    输出：{中文原词: category_key}，如 {"祭祀": "honoring_ancestors", "嫁娶": "wedding"}
    """
    index: dict[str, str] = {}
    for cat_key, cat in terms.get("activity_categories", {}).items():
        for src in cat.get("sources", []):
            index[src] = cat_key
    return index


# ============================================================
# S3: 纯函数转换层（字段翻译）
# ============================================================


def chinese_to_int(s: str) -> int:
    """中文数字转 int。支持 一..九、十/廿/卅 组合。

    输入：s - 中文数字字符串（如 "五"、"十七"、"廿三"、"初九"、"三十"）
    输出：对应整数（无法解析返回 0）
    """
    if not s:
        return 0
    # 初X（初九）
    if s.startswith("初"):
        return CHINESE_DIGITS.get(s[1:], 0)
    # 十X（十一..十九）/ 十
    if s.startswith("十"):
        rest = s[1:]
        return 10 + (CHINESE_DIGITS.get(rest, 0) if rest else 0)
    # 廿X（廿一..廿九）/ 廿
    if s.startswith("廿"):
        rest = s[1:]
        return 20 + (CHINESE_DIGITS.get(rest, 0) if rest else 0)
    # 三十
    if s == "三十":
        return 30
    # 单字（一..九）
    return CHINESE_DIGITS.get(s, 0)


def _ordinal_suffix(n: int) -> str:
    """返回英文序数后缀（1st/2nd/3rd/th）。"""
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def translate_lunar_date(raw: str, terms: dict, missing: dict) -> str | None:
    """农历日期中文 → 英文。

    输入：raw - 中文农历日期（如 "五月十七"、"闰六月廿三"、"十一月初九"）
    输出：英文日期（如 "5th Lunar Month, Day 17"、"Leap 6th Lunar Month, Day 23"）
    """
    if not raw:
        return None
    # 检测闰月
    is_leap = raw.startswith("闰")
    if is_leap:
        raw = raw[1:]
    # 拆分月和日
    parts = raw.split("月")
    if len(parts) != 2:
        missing.setdefault("lunar_date", []).append(raw)
        return None
    month_str, day_str = parts
    month = chinese_to_int(month_str)
    day = chinese_to_int(day_str)
    if month == 0 or day == 0:
        missing.setdefault("lunar_date", []).append(raw)
        return None
    prefix = "Leap " if is_leap else ""
    return f"{prefix}{month}{_ordinal_suffix(month)} Lunar Month, Day {day}"


def translate_gan_zhi(raw: str, terms: dict, missing: dict) -> str | None:
    """干支中文 → 英文（阴阳五行+生肖+后缀）。

    输入：raw - 中文干支（如 "丙午年"、"甲午月"、"辛卯日"、"戊戌时"）
    输出：英文干支（如 "Yang Fire Horse Year"）
    """
    if not raw:
        return None
    # 提取后缀
    suffix_en = ""
    raw_core = raw
    for cn_suffix, en_suffix in GAN_ZHI_SUFFIX_MAP.items():
        if raw.endswith(cn_suffix):
            suffix_en = en_suffix
            raw_core = raw[: -len(cn_suffix)]
            break
    # 查 sexagenary
    sexagenary = terms.get("sexagenary", {})
    en_val = sexagenary.get(raw_core)
    if en_val:
        return f"{en_val} {suffix_en}".strip()
    missing.setdefault("gan_zhi", []).append(raw)
    return None


def translate_zodiac(raw: str, terms: dict, missing: dict) -> str | None:
    """生肖中文 → 英文。

    输入：raw - 中文生肖（如 "马年"）
    输出：英文生肖（如 "Year of the Horse"）
    """
    if not raw:
        return None
    zodiac_map = terms.get("zodiac", {})
    if raw.endswith("年"):
        zodiac_cn = raw[:-1]
        zodiac_en = zodiac_map.get(zodiac_cn)
        if zodiac_en:
            return f"Year of the {zodiac_en}"
        missing.setdefault("zodiac", []).append(raw)
    return None


def translate_solar_term_info(record: dict, terms: dict, missing: dict) -> dict:
    """节气信息结构化翻译。

    输入：record - 中文 record（含 solar_term/prev_solar_term/next_solar_term 等字段）
    输出：包含 current、previous 和 next 三个节气位置的结构化对象。
    """
    solar_terms = terms.get("solar_terms", {})
    result = {"current": None, "previous": None, "next": None}

    # 当前节气
    current_cn = record.get("solar_term", "")
    if current_cn and current_cn != "无":
        en = solar_terms.get(current_cn)
        if en:
            result["current"] = {"name": en}
        else:
            missing.setdefault("solar_term", []).append(current_cn)

    # 上一节气
    prev_cn = record.get("prev_solar_term", "")
    prev_days = record.get("prev_solar_term_days", 0)
    if prev_cn:
        en = solar_terms.get(prev_cn)
        if en:
            result["previous"] = {"name": en, "days_ago": prev_days}
        else:
            missing.setdefault("solar_term", []).append(prev_cn)

    # 下一节气
    next_cn = record.get("next_solar_term", "")
    next_days = record.get("next_solar_term_days", 0)
    if next_cn:
        en = solar_terms.get(next_cn)
        if en:
            result["next"] = {"name": en, "days_ahead": next_days}
        else:
            missing.setdefault("solar_term", []).append(next_cn)

    return result


def translate_chong_sha(raw: str, terms: dict, missing: dict) -> dict | None:
    """冲煞中文 → 结构化英文。

    输入：raw - 中文冲煞（如 "冲午(庚)煞南"）
    输出：{"clashes_with": "Horse", "clash_pillar": "Geng-Wu", "inauspicious_direction": "South"}
    """
    if not raw:
        return None
    m = CHONG_SHA_RE.match(raw)
    if not m:
        missing.setdefault("chong_sha", []).append(raw)
        return None
    zhi_cn = m.group(1)  # 地支（午）
    gan_cn = m.group(2)  # 天干（庚）
    direction_cn = m.group(3)  # 方位（南）

    # clashes_with: 地支→生肖
    zodiac_cn = BRANCH_TO_ZODIAC_CN.get(zhi_cn)
    zodiac_en = terms.get("zodiac", {}).get(zodiac_cn) if zodiac_cn else None
    # clash_pillar: 天干+地支拼音
    gan_py = GAN_PINYIN.get(gan_cn, gan_cn)
    zhi_py = terms.get("branches", {}).get(zhi_cn, zhi_cn)
    # inauspicious_direction: 方位
    direction_en = terms.get("directions", {}).get(direction_cn)

    if zodiac_en and direction_en:
        return {
            "clashes_with": zodiac_en,
            "clash_pillar": f"{gan_py}-{zhi_py}",
            "inauspicious_direction": direction_en,
        }
    missing.setdefault("chong_sha", []).append(raw)
    return None


def translate_position(raw: str, terms: dict, missing: dict) -> dict | None:
    """方位中文 → 结构化英文。

    输入：raw - 中文方位（如 "西南(坤)"）
    输出：{"direction": "Southwest", "trigram": "Kun"}
    """
    if not raw:
        return None
    m = POSITION_RE.match(raw)
    if not m:
        missing.setdefault("position", []).append(raw)
        return None
    direction_cn = m.group(1)
    trigram_cn = m.group(2)
    direction_en = terms.get("directions", {}).get(direction_cn)
    trigram_en = terms.get("trigrams", {}).get(trigram_cn, trigram_cn)
    if direction_en:
        return {"direction": direction_en, "trigram": trigram_en}
    missing.setdefault("position", []).append(raw)
    return None


def translate_festivals(raw, terms: dict, missing: dict) -> list:
    """节日中文 → 英文列表。

    输入：raw - 中文节日列表（[{"name": "春节", "type": "农历节日"}] 或 JSON 字符串）
    输出：英文节日列表（[{"name": "Lunar New Year", "type": "Lunar Festival"}]）
    """
    if not raw:
        return []
    # 容错：db 读取时 festivals 可能是 JSON 字符串
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            missing.setdefault("festivals", []).append(raw)
            return []
    if not isinstance(raw, list):
        return []
    festivals_map = terms.get("festivals", {})
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name_cn = item.get("name", "")
        type_cn = item.get("type", "")
        name_en = festivals_map.get(name_cn)
        type_en = FESTIVAL_TYPE_MAP.get(type_cn, type_cn)
        if name_en:
            result.append({"name": name_en, "type": type_en})
        else:
            missing.setdefault("festivals", []).append(name_cn)
    return result


def translate_spirits(raw: str, terms: dict, spirit_type: str, missing: dict) -> list:
    """神煞中文 → 英文列表（D-W5-1 方案 C：命中 gods 输出译名，未命中隐藏+missing）。

    输入：
        raw - 中文神煞（如 "天恩、母仓、不将" 或 "无"）
        terms - 词表（含 gods 命名空间）
        spirit_type - "auspicious" 或 "inauspicious"
        missing - 缺失记录字典
    输出：[{name, pinyin, explanation}, ...]（仅含 gods 词表中审校过的神煞）
    """
    gods = terms.get("gods", {})
    result = []
    for name in split_activities(raw):
        if name in gods:
            entry = gods[name]
            result.append(
                {
                    "name": entry.get("name", ""),
                    "pinyin": entry.get("pinyin", ""),
                    "explanation": entry.get("explanation", ""),
                }
            )
        else:
            missing.setdefault("spirits", []).append({"name": name, "type": spirit_type})
    return result


# ============================================================
# S4: 活动流水线（核心，curated _meta.policy）
# ============================================================


def split_activities(raw: str) -> list[str]:
    """按"、"拆分活动原词；空串/"无"→[]。

    输入：raw - 中文活动串（如 "祭祀、祈福、嫁娶" 或 "无"）
    输出：原词列表（如 ["祭祀", "祈福", "嫁娶"]）
    """
    if not raw or raw == "无":
        return []
    return [w.strip() for w in raw.split("、") if w.strip()]


def filter_excluded(words: list[str], excluded: dict) -> list[str]:
    """剔除 excluded_activities 中的词。

    输入：
        words - 原词列表
        excluded - excluded_activities 字典（{原词: 剔除原因}）
    输出：剔除后的原词列表
    """
    return [w for w in words if w not in excluded]


def extract_special(words: list[str], special: dict) -> tuple[list[str], list[dict]]:
    """提取馀事勿取等特殊规则词。

    输入：
        words - 原词列表
        special - special_rules 字典（如 {"馀事勿取": {type, label, description}}）
    输出：(remaining_words, special_indications)
    """
    special_indications = []
    remaining = []
    for w in words:
        if w in special:
            rule = special[w]
            special_indications.append(
                {
                    "type": rule.get("type", ""),
                    "label": rule.get("label", ""),
                    "description": rule.get("description", ""),
                }
            )
        else:
            remaining.append(w)
    return remaining, special_indications


def merge_to_categories(
    words: list[str], word_to_category: dict, terms: dict, missing: dict
) -> list[dict]:
    """中文原词→类别合并（不输出中文原词，仅输出 {category, label}）。

    输入：
        words - 原词列表
        word_to_category - {中文原词: 类别key} 反向索引
        terms - 词表（含 activity_categories）
        missing - 缺失记录字典
    输出：[{category, label}, ...]（去重，未命中的原词记入 missing）
    """
    categories = terms.get("activity_categories", {})
    merged: dict[str, dict] = {}
    unmerged = []
    for w in words:
        cat_key = word_to_category.get(w)
        if cat_key and cat_key in categories:
            if cat_key not in merged:
                cat = categories[cat_key]
                merged[cat_key] = {
                    "category": cat_key,
                    "label": cat.get("label", ""),
                }
        else:
            unmerged.append(w)
    if unmerged:
        missing.setdefault("activities", []).extend(unmerged)
    return list(merged.values())


def process_activities(
    suitable_raw: str,
    unsuitable_raw: str,
    terms: dict,
    word_to_category: dict,
    missing: dict,
) -> dict:
    """活动流水线主函数。

    流程：原词匹配 → 剔除检查 → 特殊规则提取 → 类别合并 → 冲突处理（同类别两侧移 mixed）→ 去重

    输入：
        suitable_raw - 中文宜活动串
        unsuitable_raw - 中文忌活动串
        terms - 词表
        word_to_category - 反向索引
        missing - 缺失记录字典
    输出：{favorable_activities, unfavorable_activities, mixed_activities, special_indications}
    """
    excluded = terms.get("excluded_activities", {})
    special = terms.get("special_rules", {})

    # 处理宜
    suitable_words = split_activities(suitable_raw)
    suitable_words = filter_excluded(suitable_words, excluded)
    suitable_words, special_indications = extract_special(suitable_words, special)
    favorable = merge_to_categories(suitable_words, word_to_category, terms, missing)

    # 处理忌
    unsuitable_words = split_activities(unsuitable_raw)
    unsuitable_words = filter_excluded(unsuitable_words, excluded)
    unfavorable = merge_to_categories(unsuitable_words, word_to_category, terms, missing)

    # 冲突处理：同类别在两侧 → 移到 mixed
    favorable_keys = {item["category"] for item in favorable}
    unfavorable_keys = {item["category"] for item in unfavorable}
    mixed_keys = favorable_keys & unfavorable_keys

    mixed = []
    for key in mixed_keys:
        cat = terms.get("activity_categories", {}).get(key, {})
        mixed.append({"category": key, "label": cat.get("label", "")})

    new_favorable = [item for item in favorable if item["category"] not in mixed_keys]
    new_unfavorable = [item for item in unfavorable if item["category"] not in mixed_keys]

    return {
        "favorable_activities": new_favorable,
        "unfavorable_activities": new_unfavorable,
        "mixed_activities": mixed,
        "special_indications": special_indications,
    }


# ============================================================
# S5: 场景判断（对齐中文 _scenario_result 三级匹配）
# ============================================================


def assess_scenario(record: dict, scenario_key: str, scenario_map: dict) -> dict | None:
    """场景判断（用中文原词判断，不使用合并后的英文类别）。

    三级匹配：
    1. suitable 命中 → favored
    2. unsuitable 命中 → avoided
    3. peng_zu_bai_ji "不X" 命中 → avoided
    4. 否则 → not_loaded

    输入：
        record - 中文 record
        scenario_key - 场景 key（如 "wedding"）
        scenario_map - 场景映射（{scenario_key: {label, match_words, category}}）
    输出：{scenario, label, status_code, status_label, source_code, matched_activities}
    """
    if not scenario_key or scenario_key not in scenario_map:
        return None
    scenario = scenario_map[scenario_key]
    match_words = scenario.get("match_words", [])
    suitable = record.get("suitable", "")
    unsuitable = record.get("unsuitable", "")

    suitable_matches = [w for w in match_words if w in suitable]
    unsuitable_matches = [w for w in match_words if w in unsuitable]

    if suitable_matches:
        status_code = "favored"
        status_label = "Traditionally Favored"
        source_code = "yi_ji"
        matched = suitable_matches
    elif unsuitable_matches:
        status_code = "avoided"
        status_label = "Traditionally Avoided"
        source_code = "yi_ji"
        matched = unsuitable_matches
    else:
        # 三级：彭祖百忌 "不X" 命中 → avoided
        peng_zu = record.get("peng_zu_bai_ji", "")
        peng_zu_matches = [w for w in match_words if f"不{w}" in peng_zu]
        if peng_zu_matches:
            status_code = "avoided"
            status_label = "Traditionally Avoided"
            source_code = "pengzu"
            matched = peng_zu_matches
        else:
            status_code = "not_loaded"
            status_label = "Not Loaded"
            source_code = "none"
            matched = []

    matched_activities = []
    if matched:
        matched_activities.append(
            {
                "category": scenario.get("category", ""),
                "label": scenario.get("label", ""),
            }
        )

    return {
        "scenario": scenario_key,
        "label": scenario.get("label", ""),
        "status_code": status_code,
        "status_label": status_label,
        "source_code": source_code,
        # 原始匹配词是中文，仅用于内部判断；英文响应只暴露审校后的类别。
        "matched_activities": matched_activities,
    }


def find_next_favored_date(
    huangli, start_date: str, scenario_key: str, scenario_map: dict, max_days: int = 120
) -> dict | None:
    """择日：从 start_date（含当天）向后查找第一个场景 favored 的日子。

    输入：
        huangli - HuangLi 实例（提供 get_daily_huangli）
        start_date - 起算日期 'YYYY-MM-DD'（含当天）
        scenario_key - 场景 key（如 "travel"）
        scenario_map - 场景映射（self._scenario_map）
        max_days - 最多向后查多少天（默认 120）
    输出：
        命中时返回 {date, days_ahead}；未命中返回 None
    """
    from datetime import datetime, timedelta

    try:
        base = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return None

    for offset in range(max_days):
        check_date = (base + timedelta(days=offset)).strftime("%Y-%m-%d")
        record = huangli.get_daily_huangli(check_date)
        if not record:
            continue
        assessment = assess_scenario(record, scenario_key, scenario_map)
        if assessment and assessment.get("status_code") == "favored":
            return {
                "date": check_date,
                "days_ahead": offset,
            }
    return None


# ============================================================
# S6: HuangLiEnglish 类 + translate_daily/translate_week 组装
# ============================================================


class HuangLiEnglish:
    """英文黄历服务：持有 terms/scenarios 词表，提供中文 record → 英文 record 转换。

    转换逻辑用模块级纯函数（可独立单测），类只持有词表。
    """

    def __init__(self, terms: dict, scenarios: dict):
        """初始化。

        输入：
            terms - 英文黄历词表（from huangli_terms_en.json）
            scenarios - 场景定义（from huangli_scenarios_en.json）
        """
        self.terms = terms
        self.scenarios = scenarios
        self._word_to_category = build_word_to_category(terms)
        self._scenario_map = scenarios.get("scenarios", {})

    def translate_daily(self, record: dict, scenario: str = "", debug: bool = False) -> dict:
        """中文 record → 英文 record（端到端组装）。

        输入：
            record - 中文 HuangLi.get_daily_huangli() 返回的 record
            scenario - 可选场景 key（如 "wedding"）
            debug - True 时在结果中附加 _missing 字段
        输出：英文 record dict（含 responsible_use/source_language/footer_disclaimer）
        """
        missing: dict = {}

        lunar_date = translate_lunar_date(record.get("lunar_date", ""), self.terms, missing)
        gan_zhi = {
            "year": translate_gan_zhi(record.get("gan_zhi_year", ""), self.terms, missing),
            "month": translate_gan_zhi(record.get("gan_zhi_month", ""), self.terms, missing),
            "day": translate_gan_zhi(record.get("gan_zhi_day", ""), self.terms, missing),
            "hour": translate_gan_zhi(record.get("gan_zhi_hour", ""), self.terms, missing),
        }
        zodiac = translate_zodiac(record.get("zodiac", ""), self.terms, missing)
        solar_term = translate_solar_term_info(record, self.terms, missing)
        chong_sha = translate_chong_sha(record.get("chong_sha", ""), self.terms, missing)

        activities = process_activities(
            record.get("suitable", ""),
            record.get("unsuitable", ""),
            self.terms,
            self._word_to_category,
            missing,
        )

        auspicious_spirits = translate_spirits(
            record.get("ji_shen", ""), self.terms, "auspicious", missing
        )
        inauspicious_spirits = translate_spirits(
            record.get("xiong_shen", ""), self.terms, "inauspicious", missing
        )

        directions = {
            "joy": translate_position(record.get("xi_shen", ""), self.terms, missing),
            "fortune": translate_position(record.get("fu_shen", ""), self.terms, missing),
            "wealth": translate_position(record.get("cai_shen", ""), self.terms, missing),
        }

        festivals = translate_festivals(record.get("festivals", []), self.terms, missing)
        scenario_assessment = assess_scenario(record, scenario, self._scenario_map)

        result = {
            "date": record.get("date", ""),
            "lunar_date": lunar_date,
            "gan_zhi": gan_zhi,
            "zodiac": zodiac,
            "solar_term": solar_term,
            "favorable_activities": activities["favorable_activities"],
            "unfavorable_activities": activities["unfavorable_activities"],
            "mixed_activities": activities["mixed_activities"],
            "special_indications": activities["special_indications"],
            "auspicious_spirits": auspicious_spirits,
            "inauspicious_spirits": inauspicious_spirits,
            "directions": directions,
            "conflict_clash": chong_sha,
            "festivals": festivals,
            "scenario_assessment": scenario_assessment,
            "responsible_use": RESPONSIBLE_USE_TEXT,
            "source_language": "zh-Hans",
            "footer_disclaimer": self.terms.get("display_wording", {}).get("footer_disclaimer", ""),
        }

        if debug:
            result["_missing"] = missing

        return result

    def translate_week(self, records: list, scenario: str = "", debug: bool = False) -> list:
        """一周 records → 英文 records（字段精简，对齐中文 get_week_huangli 的 fields 子集）。

        输入：
            records - 中文 record 列表
            scenario - 可选场景 key
            debug - True 时每条记录附加 _missing 字段
        输出：精简英文 record 列表
        """
        results = []
        for record in records:
            daily = self.translate_daily(record, scenario, debug)
            slim = {
                "date": daily["date"],
                "lunar_date": daily["lunar_date"],
                "gan_zhi": {
                    "day": daily["gan_zhi"].get("day"),
                    "hour": daily["gan_zhi"].get("hour"),
                },
                "favorable_activities": daily["favorable_activities"],
                "unfavorable_activities": daily["unfavorable_activities"],
                "conflict_clash": daily["conflict_clash"],
                "directions": daily["directions"],
                "solar_term": daily["solar_term"],
                "scenario_assessment": daily["scenario_assessment"],
            }
            if debug:
                slim["_missing"] = daily.get("_missing", {})
            results.append(slim)
        return results
