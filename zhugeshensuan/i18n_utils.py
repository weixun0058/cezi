"""国际化基础工具。

本模块只保留运行期必须使用的语言常量、路由映射和静态文案。
繁体签文、解签、彭祖百忌等内容应来自已生成的数据表；OpenCC 仅允许用于离线数据构建脚本。
"""
from flask import g, has_app_context

LANGS = ("zh-hans", "zh-hant")
DEFAULT_LANG = "zh-hans"

PAGE_URL_NAMES = {
    "almanac": "huangli",
    "divination": "suanshi",
    "bazi": "lunming",
}

PAGE_TEMPLATES = {
    "huangli": "huangli.html",
    "suanshi": "suanshi.html",
    "lunming": "lunming.html",
}


def get_current_lang() -> str:
    """返回当前请求语言；API 或后台调用未设置时使用默认简体。"""
    if not has_app_context():
        return DEFAULT_LANG
    return getattr(g, "lang", None) or DEFAULT_LANG


def html_lang_for(lang: str | None = None) -> str:
    """返回 HTML lang 属性使用的 BCP 47 语言标签。"""
    effective = lang or get_current_lang()
    return "zh-Hant" if effective == "zh-hant" else "zh-Hans"


def get_gua_table_name(lang: str | None = None) -> str:
    """根据语言返回签文表名。"""
    effective = lang or get_current_lang()
    return "gua_hant" if effective == "zh-hant" else "gua"


def get_pzbj_table_name(lang: str | None = None) -> str:
    """根据语言返回彭祖百忌表名。"""
    effective = lang or get_current_lang()
    return "pzbj_hant" if effective == "zh-hant" else "pzbj"


DISCLAIMER = {
    "zh-hans": "传统文化娱乐参考，不构成医疗、投资或人生决策建议。",
    "zh-hant": "傳統文化娛樂參考，不構成醫療、投資或人生決策建議。",
}


def get_disclaimer(lang: str | None = None) -> str:
    """根据语言返回免责声明。"""
    effective = lang or get_current_lang()
    return DISCLAIMER.get(effective, DISCLAIMER["zh-hans"])


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
    """根据语言返回论命报告章节标题。"""
    effective = lang or get_current_lang()
    return REPORT_SECTION_TITLES.get(effective, REPORT_SECTION_TITLES["zh-hans"])
