"""国际化工具模块。

集中管理：
  - 支持的语言代码列表
  - 默认语言
  - 页面 URL 名 ↔ 页面标识 ↔ 模板文件 的映射
  - 当前请求语言的获取（从 g.lang 读取，由 pages_bp 设置）
  - OpenCC 简繁转换工具（用于 lunar_python 输出的运行时转换）

设计原则：
  - 所有语言相关的常量在此定义，避免分散在各文件
  - URL 名采用 SEO 友好的英文（almanac/divination/bazi）
  - 页面标识（page key）用于内部逻辑，与 URL 名解耦
"""
from flask import g
from opencc import OpenCC

# 支持的语言代码（按 BCP 47 规范：zh-hans 简体，zh-hant 繁体）
LANGS = ("zh-hans", "zh-hant")

# 默认语言（无语言前缀的旧 URL 重定向到此语言）
DEFAULT_LANG = "zh-hans"

# OpenCC 简转繁转换器（模块级单例，避免重复初始化）
_S2T_CONVERTER = OpenCC('s2t')

# 页面标识 → SEO 友好的 URL 名
PAGE_URL_NAMES = {
    "almanac": "huangli",
    "divination": "suanshi",
    "bazi": "lunming",
}

# 页面标识 → 模板文件名
PAGE_TEMPLATES = {
    "huangli": "huangli.html",
    "suanshi": "suanshi.html",
    "lunming": "lunming.html",
}


def get_current_lang() -> str:
    """获取当前请求的语言代码。

    优先从 g.lang 读取（由 pages_bp 在路由处理时设置）；
    若未设置（如 API 请求），返回默认语言。
    """
    return getattr(g, "lang", None) or DEFAULT_LANG


def to_hant_if_needed(text: str, lang: str | None = None) -> str:
    """根据语言将简体文本转换为繁体。

    用于 lunar_python 等不支持 i18n 的库的输出转换。
    简体模式下原样返回，繁体模式下用 OpenCC s2t 转换。

    Args:
        text: 待转换的简体文本
        lang: 语言代码，None 时使用当前请求语言

    Returns:
        简体模式下原文本，繁体模式下转换后的繁体文本
    """
    if not text:
        return text
    effective = lang or get_current_lang()
    if effective != "zh-hant":
        return text
    return _S2T_CONVERTER.convert(text)


def to_hant_recursive(obj, lang: str | None = None):
    """递归地对字典/列表/字符串做繁体转换。

    用于整个 chart 等嵌套结构的批量转换。
    非字符串类型（int/float/bool/None）原样返回。

    Args:
        obj: 待转换的任意对象
        lang: 语言代码，None 时使用当前请求语言

    Returns:
        转换后的对象（结构相同，字符串字段已繁体化）
    """
    effective = lang or get_current_lang()
    if effective != "zh-hant":
        return obj
    if isinstance(obj, str):
        return _S2T_CONVERTER.convert(obj)
    if isinstance(obj, dict):
        return {k: to_hant_recursive(v, effective) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_hant_recursive(item, effective) for item in obj]
    return obj


def get_gua_table_name(lang: str | None = None) -> str:
    """根据语言返回签文表名。

    Args:
        lang: 语言代码，None 时使用当前请求语言

    Returns:
        'gua'（简体）或 'gua_hant'（繁体）
    """
    effective = lang or get_current_lang()
    return "gua_hant" if effective == "zh-hant" else "gua"


def get_pzbj_table_name(lang: str | None = None) -> str:
    """根据语言返回彭祖百忌表名。

    Args:
        lang: 语言代码，None 时使用当前请求语言

    Returns:
        'pzbj'（简体）或 'pzbj_hant'（繁体）
    """
    effective = lang or get_current_lang()
    return "pzbj_hant" if effective == "zh-hant" else "pzbj"


# 论命免责声明（简/繁）
DISCLAIMER = {
    "zh-hans": "传统文化娱乐参考，不构成医疗、投资或人生决策建议。",
    "zh-hant": "傳統文化娛樂參考，不構成醫療、投資或人生決策建議。",
}


def get_disclaimer(lang: str | None = None) -> str:
    """根据语言返回免责声明文本"""
    effective = lang or get_current_lang()
    return DISCLAIMER.get(effective, DISCLAIMER["zh-hans"])


# 论命报告章节标题（简/繁）
REPORT_SECTION_TITLES = {
    "zh-hans": {
        "five_elements": "五行气象",
        "temperament": "性情禀赋",
        "career_learning": "事业与学业",
        "relationships": "人际相处",
        "luck_cycles": "大运流转",
    },
    "zh-hant": {
        "five_elements": "五行氣象",
        "temperament": "性情稟賦",
        "career_learning": "事業與學業",
        "relationships": "人際相處",
        "luck_cycles": "大運流轉",
    },
}


def get_report_section_titles(lang: str | None = None) -> dict:
    """根据语言返回论命报告章节标题字典"""
    effective = lang or get_current_lang()
    return REPORT_SECTION_TITLES.get(effective, REPORT_SECTION_TITLES["zh-hans"])
