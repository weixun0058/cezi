from datetime import date, timedelta

import pytest
from lunar_python import Solar

from zhugeshensuan.huangli_i18n import localize_huangli_record, localize_text


def test_localize_common_huangli_terms_to_traditional():
    assert localize_text("开光、进人口、纳财、交易、造畜稠、无", "zh-hant") == (
        "開光、進人口、納財、交易、造畜稠、無"
    )


# 2026 全年 lunar_python 输出反向扫描出的真实样本，确保补齐的字被覆盖。
# 每条 = (简体原文, 期望繁体)
REAL_LUNAR_PYTHON_SAMPLES = [
    # 宜忌 / 神煞 / 彭祖百忌中的真实片段
    ("四废", "四廢"),
    ("癸不词讼理弱敌强", "癸不詞訟理弱敵強"),
    ("五富、不将、福生", "五富、不將、福生"),
    ("小时", "小時"),
    ("时德", "時德"),
    ("大时", "大時"),
    ("五离", "五離"),
    ("四穷", "四窮"),
    ("触水龙", "觸水龍"),
    ("植千株不长", "植千株不長"),
    ("八风", "八風"),
    ("鸣吠", "鳴吠"),
    ("鸣吠对", "鳴吠對"),
    # 神煞专有名词"后"简繁同形，不得转成"後"
    ("天后", "天后"),
    ("益后", "益后"),
]


@pytest.mark.parametrize("src,expected", REAL_LUNAR_PYTHON_SAMPLES)
def test_localize_real_lunar_python_samples(src, expected):
    assert localize_text(src, "zh-hant") == expected


# 本轮补齐的 16 个简繁异形字；若转换后仍含这些字，说明映射有遗漏。
NEWLY_COVERED_CHARS = set("专将废强护摇敌时离穷触长难风鸣对")


def test_localize_2026_full_year_no_newly_covered_char_residual():
    """2026 全年 lunar_python 输出经 localize_text 后，本轮补齐的 16 个字不应有残留。

    这是对静态映射表覆盖度的回归保护：将来如果有人误删映射或 lunar_python
    升级引入新词，该测试会抓住"应转未转"的回归。
    """
    d = date(2026, 1, 1)
    end = date(2026, 12, 31)
    while d <= end:
        lunar = Solar.fromYmd(d.year, d.month, d.day).getLunar()
        texts = [
            "、".join(lunar.getDayYi() or []),
            "、".join(lunar.getDayJi() or []),
            "、".join(lunar.getDayJiShen() or []),
            "、".join(lunar.getDayXiongSha() or []),
            lunar.getPengZuGan(),
            lunar.getPengZuZhi(),
            lunar.getDayPositionXiDesc(),
            lunar.getDayPositionCaiDesc(),
            lunar.getDayPositionFuDesc(),
            str(lunar.getChong()) + lunar.getChongGan() + str(lunar.getSha()),
            lunar.getYearShengXiao(),
        ]
        for src in texts:
            converted = localize_text(src, "zh-hant")
            residual = NEWLY_COVERED_CHARS & set(converted)
            assert not residual, f"{d}: '{src}' 转换为 '{converted}' 后仍有简体残留 {residual}"
        d += timedelta(days=1)


def test_localize_huangli_record_keeps_source_record_unchanged():
    source = {
        "suitable": "嫁娶、开光、进人口、纳财、交易、立券、挂匾、造畜稠",
        "unsuitable": "无",
        "chong_sha": "冲狗(庚戌)煞南",
        "zodiac": "马年",
        "festivals": [{"name": "国庆节", "type": "阳历节日"}],
        "scenario_assessment": {
            "scenario": "结婚",
            "status": "未载",
            "status_code": "not_loaded",
            "source": None,
            "source_code": "none",
            "suitable_matches": [],
            "unsuitable_matches": [],
        },
    }

    localized = localize_huangli_record(source, "zh-hant")

    assert "开光" in source["suitable"]
    assert localized["suitable"] == "嫁娶、開光、進人口、納財、交易、立券、掛匾、造畜稠"
    assert localized["unsuitable"] == "無"
    assert localized["chong_sha"] == "沖狗(庚戌)煞南"
    assert localized["zodiac"] == "馬年"
    assert localized["festivals"][0]["name"] == "國慶節"
    assert localized["festivals"][0]["type"] == "陽曆節日"
    assert localized["scenario_assessment"]["status"] == "未載"
    assert localized["scenario_assessment"]["status_code"] == "not_loaded"
