import json
from datetime import datetime, timedelta
from pathlib import Path

from zhugeshensuan.huangli_english import (
    CJK_RE,
    HuangLiEnglish,
    assess_scenario,
    build_activity_safety_notices,
    build_word_to_category,
    load_huangli_scenarios,
    load_huangli_terms,
    load_huangli_terms_safe,
    process_activities,
    translate_chong_sha,
    translate_lunar_date,
    translate_spirits,
)

ROOT = Path(__file__).resolve().parents[1]
TERMS_PATH = ROOT / "data" / "content" / "huangli_terms_en.json"
SCENARIOS_PATH = ROOT / "data" / "content" / "huangli_scenarios_en.json"


def _contains_cjk(value) -> bool:
    if isinstance(value, str):
        return bool(CJK_RE.search(value))
    if isinstance(value, dict):
        return any(_contains_cjk(key) or _contains_cjk(item) for key, item in value.items())
    if isinstance(value, list | tuple):
        return any(_contains_cjk(item) for item in value)
    return False


def test_terms_and_scenarios_load():
    terms = load_huangli_terms(TERMS_PATH)
    scenarios = load_huangli_scenarios(SCENARIOS_PATH)

    assert len(terms["zodiac"]) == 12
    assert len(terms["solar_terms"]) == 24
    assert len(terms["sexagenary"]) == 60
    assert len(terms["gods"]) == 20
    assert set(scenarios["scenarios"]) == {
        "wedding",
        "moving",
        "business_opening",
        "travel",
        "signing",
        "haircut",
    }


def test_safe_terms_loader_returns_empty_for_missing_file(tmp_path):
    assert load_huangli_terms_safe(tmp_path / "missing.json") == {}


def test_core_translation_functions_do_not_expose_chinese():
    terms = load_huangli_terms(TERMS_PATH)
    missing = {}

    assert translate_lunar_date("闰六月廿三", terms, missing) == ("Leap 6th Lunar Month, Day 23")
    assert translate_chong_sha("冲午(庚)煞南", terms, missing) == {
        "clashes_with": "Horse",
        "clash_pillar": "Geng-Wu",
        "inauspicious_direction": "South",
    }
    spirits = translate_spirits("天恩、未审校神煞", terms, "auspicious", missing)
    assert spirits[0]["name"] == "Heavenly Grace"
    assert not _contains_cjk(spirits)
    assert missing["spirits"] == [{"name": "未审校神煞", "type": "auspicious"}]


def test_activity_pipeline_filters_and_merges_categories():
    terms = load_huangli_terms(TERMS_PATH)
    missing = {}
    result = process_activities(
        "嫁娶、沐浴、馀事勿取",
        "嫁娶、出行",
        terms,
        build_word_to_category(terms),
        missing,
    )

    assert result["favorable_activities"] == []
    assert result["mixed_activities"] == [{"category": "wedding", "label": "Wedding"}]
    assert result["unfavorable_activities"] == [{"category": "travel", "label": "Travel"}]
    assert result["special_indications"]
    assert not _contains_cjk(result)


def test_medical_activity_category_is_not_published():
    terms = load_huangli_terms(TERMS_PATH)
    missing = {}
    result = process_activities(
        "求医、针灸",
        "",
        terms,
        build_word_to_category(terms),
        missing,
    )

    assert "medical_care" not in terms["activity_categories"]
    assert result["favorable_activities"] == []
    assert missing["activities"] == ["求医", "针灸"]

    translated = HuangLiEnglish(terms, {"scenarios": {}}).translate_daily(
        {"date": "2026-07-15", "suitable": "求医、针灸", "unsuitable": ""}
    )
    assert translated["favorable_activities"] == []
    assert translated["safety_notices"] == []


def test_legal_activity_emits_contextual_notice():
    terms = load_huangli_terms(TERMS_PATH)
    missing = {}
    result = process_activities(
        "词讼",
        "",
        terms,
        build_word_to_category(terms),
        missing,
    )
    notices = build_activity_safety_notices(result)

    assert result["favorable_activities"] == [
        {"category": "legal_matters", "label": "Legal Matters"}
    ]
    assert len(notices) == 1
    assert "not legal advice" in notices[0]["text"]
    assert "qualified legal professional" in notices[0]["text"]
    assert not _contains_cjk(notices)

    translated = HuangLiEnglish(terms, {"scenarios": {}}).translate_daily(
        {"date": "2026-07-15", "suitable": "词讼", "unsuitable": ""}
    )
    assert translated["safety_notices"] == notices


def test_scenario_assessment_keeps_source_words_internal():
    scenarios = load_huangli_scenarios(SCENARIOS_PATH)["scenarios"]
    assessment = assess_scenario(
        {"suitable": "嫁娶、祭祀", "unsuitable": "", "peng_zu_bai_ji": ""},
        "wedding",
        scenarios,
    )

    assert assessment["status_code"] == "favored"
    assert "matched_words" not in assessment
    assert assessment["matched_activities"] == [{"category": "wedding", "label": "Wedding"}]
    assert not _contains_cjk(assessment)


def test_daily_api_contract_and_no_chinese_leak(client):
    response = client.get("/api/en/daily-almanac?date=2026-07-01&scenario=wedding")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["date"] == "2026-07-01"
    assert data["scenario_assessment"]["scenario"] == "wedding"
    assert set(data["next_favored_date"]) == {"date", "days_ahead"}
    assert "safety_notices" in data
    assert not _contains_cjk(data)
    assert "fortune" not in data
    assert "gua_type" not in data


def test_daily_api_debug_exposes_missing_audit_only_when_requested(client):
    normal = client.get("/api/en/daily-almanac?date=2026-07-01").get_json()["data"]
    debug = client.get("/api/en/daily-almanac?date=2026-07-01&debug=1").get_json()["data"]

    assert "_missing" not in normal
    assert "_missing" in debug


def test_daily_api_rejects_invalid_inputs(client):
    invalid_date = client.get("/api/en/daily-almanac?date=2026-99-99")
    invalid_scenario = client.get("/api/en/daily-almanac?date=2026-07-01&scenario=unknown")

    assert invalid_date.status_code == 400
    assert invalid_date.get_json()["error"]["code"] == "INVALID_DATE"
    assert invalid_scenario.status_code == 400
    assert invalid_scenario.get_json()["error"]["code"] == "INVALID_SCENARIO"


def test_week_api_contract(client):
    response = client.get("/api/en/week-almanac?scenario=travel")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data) == 10
    dates = [record["date"] for record in data]
    assert dates == sorted(dates)
    assert len(set(dates)) == 10
    assert all(not _contains_cjk(record) for record in data)


def test_2026_full_year_no_chinese_leak(app):
    huangli = app.extensions["huangli"]
    translator: HuangLiEnglish = app.extensions["huangli_en"]
    scenarios = tuple(translator.scenarios["scenarios"])
    reviewed_spirit_seen = False
    hidden_spirit_seen = False
    day = datetime(2026, 1, 1)
    end = datetime(2027, 1, 1)

    while day < end:
        record = huangli.get_daily_huangli(day.strftime("%Y-%m-%d"))
        translated = translator.translate_daily(dict(record), scenario="wedding", debug=True)
        reviewed_spirit_seen |= bool(
            translated["auspicious_spirits"] or translated["inauspicious_spirits"]
        )
        hidden_spirit_seen |= bool(translated["_missing"].get("spirits"))
        translated.pop("_missing")
        assert not _contains_cjk(translated), json.dumps(translated, ensure_ascii=False, indent=2)
        assert "fortune" not in translated
        assert "gua_type" not in translated
        for scenario in scenarios:
            assessment = translator.translate_daily(dict(record), scenario=scenario)[
                "scenario_assessment"
            ]
            assert assessment["status_code"] in {"favored", "avoided", "not_loaded"}
            assert not _contains_cjk(assessment)
        day += timedelta(days=1)

    assert reviewed_spirit_seen
    assert hidden_spirit_seen
