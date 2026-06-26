"""黄历动态数据本地化。

`lunar_python` 只提供简体中文词库。本模块在项目内维护运行期可控的本地化层，
避免修改 site-packages，也避免把 OpenCC 放回网站请求路径。
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .i18n_utils import get_current_lang

LOCALIZABLE_FIELDS = (
    "lunar_date",
    "gan_zhi_year",
    "gan_zhi_month",
    "gan_zhi_day",
    "gan_zhi_hour",
    "zodiac",
    "suitable",
    "unsuitable",
    "chong_sha",
    "ji_shen",
    "xiong_shen",
    "peng_zu_bai_ji",
    "xi_shen",
    "fu_shen",
    "cai_shen",
    "solar_term",
    "prev_solar_term",
    "next_solar_term",
    "formatted_solar_term_info",
)

PHRASE_REPLACEMENTS = {
    "黄历": "黃曆",
    "农历": "農曆",
    "阴历": "陰曆",
    "阳历": "陽曆",
    "闰": "閏",
    "开光": "開光",
    "齐醮": "齊醮",
    "斋醮": "齋醮",
    "造庙": "造廟",
    "谢土": "謝土",
    "订婚": "訂婚",
    "纳采": "納采",
    "问名": "問名",
    "纳婿": "納婿",
    "归宁": "歸寧",
    "合帐": "合帳",
    "订盟": "訂盟",
    "进人口": "進人口",
    "修坟": "修墳",
    "启钻": "啟鑽",
    "安葬": "安葬",
    "开生坟": "開生墳",
    "合寿木": "合壽木",
    "入殓": "入殮",
    "移柩": "移柩",
    "入宅": "入宅",
    "安门": "安門",
    "修造": "修造",
    "起基": "起基",
    "动土": "動土",
    "竖柱": "豎柱",
    "开井开池": "開井開池",
    "作陂放水": "作陂放水",
    "破屋": "破屋",
    "坏垣": "壞垣",
    "补垣": "補垣",
    "伐木做梁": "伐木做梁",
    "开柱眼": "開柱眼",
    "盖屋合脊": "蓋屋合脊",
    "开厕": "開廁",
    "造仓": "造倉",
    "平治道涂": "平治道塗",
    "造桥": "造橋",
    "作厕": "作廁",
    "筑堤": "築堤",
    "开池": "開池",
    "开渠": "開渠",
    "扫舍": "掃舍",
    "造屋": "造屋",
    "造畜稠": "造畜稠",
    "修饰垣墙": "修飾垣牆",
    "开市": "開市",
    "挂匾": "掛匾",
    "纳财": "納財",
    "求财": "求財",
    "开仓": "開倉",
    "买车": "買車",
    "置产": "置產",
    "雇佣": "僱傭",
    "出货财": "出貨財",
    "安机械": "安機械",
    "造车器": "造車器",
    "经络": "經絡",
    "酝酿": "醞釀",
    "鼓铸": "鼓鑄",
    "栽种": "栽種",
    "取渔": "取漁",
    "结网": "結網",
    "牧养": "牧養",
    "习艺": "習藝",
    "入学": "入學",
    "理发": "理髮",
    "见贵": "見貴",
    "针灸": "針灸",
    "剃头": "剃頭",
    "整手足甲": "整手足甲",
    "纳畜": "納畜",
    "畋猎": "畋獵",
    "教牛马": "教牛馬",
    "会亲友": "會親友",
    "求医": "求醫",
    "治病": "治病",
    "词讼": "詞訟",
    "起基动土": "起基動土",
    "破屋坏垣": "破屋壞垣",
    "造仓库": "造倉庫",
    "立券交易": "立券交易",
    "求医疗病": "求醫療病",
    "诸事不宜": "諸事不宜",
    "馀事勿取": "餘事勿取",
    "行丧": "行喪",
    "断蚁": "斷蟻",
    "青龙": "青龍",
    "金匮": "金匱",
    "勾陈": "勾陳",
    "东北": "東北",
    "东南": "東南",
    "正东": "正東",
    "惊蛰": "驚蟄",
    "处暑": "處暑",
    "立春": "立春",
    "雨水": "雨水",
    "春分": "春分",
    "清明": "清明",
    "谷雨": "穀雨",
    "立夏": "立夏",
    "小满": "小滿",
    "芒种": "芒種",
    "夏至": "夏至",
    "小暑": "小暑",
    "大暑": "大暑",
    "立秋": "立秋",
    "白露": "白露",
    "秋分": "秋分",
    "寒露": "寒露",
    "霜降": "霜降",
    "立冬": "立冬",
    "小雪": "小雪",
    "大雪": "大雪",
    "冬至": "冬至",
    "小寒": "小寒",
    "大寒": "大寒",
    "马年": "馬年",
    "龙年": "龍年",
    "鸡年": "雞年",
    "猪年": "豬年",
    "今日": "今日",
    "天前": "天前",
    "还有": "還有",
    "无": "無",
}

CHAR_REPLACEMENTS = str.maketrans(
    {
        "历": "曆",
        "农": "農",
        "阴": "陰",
        "阳": "陽",
        "闰": "閏",
        "冲": "沖",
        "岁": "歲",
        "龙": "龍",
        "马": "馬",
        "鸡": "雞",
        "猪": "豬",
        "东": "東",
        "开": "開",
        "关": "關",
        "进": "進",
        "纳": "納",
        "财": "財",
        "订": "訂",
        "归": "歸",
        "宁": "寧",
        "齐": "齊",
        "斋": "齋",
        "庙": "廟",
        "谢": "謝",
        "问": "問",
        "寿": "壽",
        "殓": "殮",
        "坟": "墳",
        "启": "啟",
        "钻": "鑽",
        "门": "門",
        "动": "動",
        "竖": "豎",
        "坏": "壞",
        "补": "補",
        "盖": "蓋",
        "厕": "廁",
        "仓": "倉",
        "涂": "塗",
        "桥": "橋",
        "筑": "築",
        "扫": "掃",
        "饰": "飾",
        "墙": "牆",
        "挂": "掛",
        "买": "買",
        "车": "車",
        "产": "產",
        "佣": "傭",
        "货": "貨",
        "机": "機",
        "经": "經",
        "络": "絡",
        "酝": "醞",
        "酿": "釀",
        "铸": "鑄",
        "种": "種",
        "渔": "漁",
        "网": "網",
        "养": "養",
        "艺": "藝",
        "学": "學",
        "发": "發",
        "头": "頭",
        "见": "見",
        "贵": "貴",
        "针": "針",
        "猎": "獵",
        "会": "會",
        "亲": "親",
        "医": "醫",
        "疗": "療",
        "词": "詞",
        "讼": "訟",
        "诸": "諸",
        "余": "餘",
        "丧": "喪",
        "断": "斷",
        "匮": "匱",
        "陈": "陳",
        "惊": "驚",
        "蛰": "蟄",
        "处": "處",
        "谷": "穀",
        "满": "滿",
        "国": "國",
        "庆": "慶",
        "节": "節",
        "还": "還",
        "祸": "禍",
        "带": "帶",
        "乡": "鄉",
        "尝": "嘗",
        "远": "遠",
        "药": "藥",
        "气": "氣",
        "肠": "腸",
        "颠": "顛",
        "张": "張",
        "灾": "災",
        # 以下为 2026 全年 lunar_python 输出反向扫描补齐的字
        # 注意："后" 不在此列 —— lunar_python 输出中"后"只出现在神煞专有名词
        # （天后、益后）中，简繁同形，不应转成"後"。
        "专": "專",
        "将": "將",
        "废": "廢",
        "强": "強",
        "护": "護",
        "摇": "搖",
        "敌": "敵",
        "时": "時",
        "离": "離",
        "穷": "窮",
        "触": "觸",
        "长": "長",
        "难": "難",
        "风": "風",
        "鸣": "鳴",
        "对": "對",
    }
)

STATUS_TEXT = {
    "zh-hans": {"suitable": "宜", "unsuitable": "忌", "not_loaded": "未载"},
    "zh-hant": {"suitable": "宜", "unsuitable": "忌", "not_loaded": "未載"},
}

SOURCE_TEXT = {
    "zh-hans": {"yi_ji": "宜忌", "pengzu": "彭祖百忌", "none": None},
    "zh-hant": {"yi_ji": "宜忌", "pengzu": "彭祖百忌", "none": None},
}


def localize_text(value: str, lang: str | None = None) -> str:
    """把 lunar_python 的简体输出转为当前语言文案。"""
    effective = lang or get_current_lang()
    if effective != "zh-hant" or not value:
        return value

    text = value
    for source, target in sorted(PHRASE_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    return text.translate(CHAR_REPLACEMENTS)


def _localize_list(values: list[Any], lang: str) -> list[Any]:
    return [localize_text(item, lang) if isinstance(item, str) else item for item in values]


def _ensure_scenario_codes(assessment: dict[str, Any]) -> dict[str, Any]:
    if "status_code" not in assessment:
        status = assessment.get("status")
        if status == "宜":
            assessment["status_code"] = "suitable"
        elif status == "忌":
            assessment["status_code"] = "unsuitable"
        else:
            assessment["status_code"] = "not_loaded"
    if "source_code" not in assessment:
        source = assessment.get("source")
        if source == "宜忌":
            assessment["source_code"] = "yi_ji"
        elif source == "彭祖百忌":
            assessment["source_code"] = "pengzu"
        else:
            assessment["source_code"] = "none"
    return assessment


def localize_huangli_record(record: dict[str, Any], lang: str | None = None) -> dict[str, Any]:
    """返回本地化后的黄历记录副本，不修改缓存中的简体基准数据。"""
    effective = lang or get_current_lang()
    localized = deepcopy(record)

    for field in LOCALIZABLE_FIELDS:
        value = localized.get(field)
        if isinstance(value, str):
            localized[field] = localize_text(value, effective)

    festivals = localized.get("festivals")
    if isinstance(festivals, list):
        for festival in festivals:
            if isinstance(festival, dict):
                for key in ("name", "type"):
                    if isinstance(festival.get(key), str):
                        festival[key] = localize_text(festival[key], effective)

    assessment = localized.get("scenario_assessment")
    if isinstance(assessment, dict):
        _ensure_scenario_codes(assessment)
        status_code = assessment["status_code"]
        source_code = assessment["source_code"]
        assessment["status"] = STATUS_TEXT.get(effective, STATUS_TEXT["zh-hans"]).get(
            status_code, assessment.get("status")
        )
        assessment["source"] = SOURCE_TEXT.get(effective, SOURCE_TEXT["zh-hans"]).get(
            source_code, assessment.get("source")
        )
        if isinstance(assessment.get("scenario"), str):
            assessment["scenario"] = localize_text(assessment["scenario"], effective)
        for key in ("suitable_matches", "unsuitable_matches"):
            if isinstance(assessment.get(key), list):
                assessment[key] = _localize_list(assessment[key], effective)

    return localized
