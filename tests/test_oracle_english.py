"""W4 Ask the Oracle 后端测试。

覆盖：
- W4.1 三词算法：确定性、范围、边界、LOVE/WORK/FATE→Sign #88、0→1 规则
- W4.1a 英文签文加载：字段数=9、CJK fallback、空字段 fallback、384 全覆盖
- W4.2 三数字算法：最小/最大/全零/非法/确定性、314|159|265→Sign #33
- W4.3 英文算事 API：同三词同签号、模式不互收、未译 fallback、错误码

依据：``docs/plans/2026-06-27-english-site-execution-plan.md`` W4.1/W4.1a/W4.2/W4.3
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zhugeshensuan.oracle_algorithm import (
    compose_english_three_number_seed,
    compose_three_character_number,
    english_three_numbers_to_start_index,
    reduce_to_start_index,
    stroke_digit,
    three_words_to_start_index,
    word_to_letter_sum,
    word_to_stroke_digit,
    word_transform,
)
from zhugeshensuan.oracle_english import (
    ENGLISH_SIGN_FIELDS,
    FALLBACK_TEXT,
    _needs_fallback,
    _sanitize_record,
    ask_with_numbers,
    ask_with_words,
    load_english_signs,
)


# ============================================================
# W4.1 三词算法
# ============================================================


class TestStrokeDigit:
    """源书"笔画取个位"规则。"""

    def test_basic_modulo(self):
        assert stroke_digit(7) == 7
        assert stroke_digit(12) == 2
        assert stroke_digit(54) == 4

    def test_zero_remainder_returns_one(self):
        """对 10 取模余 0 时返回 1（0→1 规则）。"""
        assert stroke_digit(10) == 1
        assert stroke_digit(20) == 1
        assert stroke_digit(50) == 1
        assert stroke_digit(60) == 1
        assert stroke_digit(70) == 1

    def test_rejects_non_positive(self):
        with pytest.raises(ValueError):
            stroke_digit(0)
        with pytest.raises(ValueError):
            stroke_digit(-5)


class TestComposeThreeCharacterNumber:
    def test_composition(self):
        assert compose_three_character_number([7, 9, 12]) == 792
        assert compose_three_character_number([4, 7, 2]) == 472

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            compose_three_character_number([1, 2])
        with pytest.raises(ValueError):
            compose_three_character_number([1, 2, 3, 4])


class TestReduceToStartIndex:
    def test_range_1_to_384(self):
        assert reduce_to_start_index(1) == 1
        assert reduce_to_start_index(384) == 384
        assert reduce_to_start_index(768) == 384
        assert reduce_to_start_index(472) == 88

    def test_rejects_non_positive(self):
        with pytest.raises(ValueError):
            reduce_to_start_index(0)


class TestWordToLetterSum:
    def test_love_work_fate(self):
        """A=1..Z=26 字母求和。"""
        assert word_to_letter_sum("LOVE") == 54  # 12+15+22+5
        assert word_to_letter_sum("WORK") == 67  # 23+15+18+11
        assert word_to_letter_sum("FATE") == 32  # 6+1+20+5

    def test_case_insensitive(self):
        assert word_to_letter_sum("love") == 54
        assert word_to_letter_sum("Love") == 54

    def test_strips_non_letters(self):
        """非字母字符剔除。"""
        assert word_to_letter_sum("LOVE!") == 54
        assert word_to_letter_sum("L-O-V-E") == 54
        assert word_to_letter_sum("LOVE123") == 54

    def test_single_letter(self):
        assert word_to_letter_sum("A") == 1
        assert word_to_letter_sum("Z") == 26

    def test_rejects_empty_after_strip(self):
        with pytest.raises(ValueError):
            word_to_letter_sum("")
        with pytest.raises(ValueError):
            word_to_letter_sum("123")
        with pytest.raises(ValueError):
            word_to_letter_sum("!@#")


class TestWordToStrokeDigit:
    def test_love_work_fate_digits(self):
        """字母和 → stroke_digit：54→4, 67→7, 32→2。"""
        assert word_to_stroke_digit("LOVE") == 4
        assert word_to_stroke_digit("WORK") == 7
        assert word_to_stroke_digit("FATE") == 2

    def test_zero_remainder_rule(self):
        """字母和为 10 的倍数时返回 1。"""
        # BEAD: 2+5+1+4 = 12 → 2
        # 找一个和为 50 的词：JUBILEE? J=10,U=21,B=2,I=9,L=12,E=5,E=5 = 64 → 4
        # 用单字母构造：和为 50 的组合，例如 "AAAA..." 不便；直接测函数行为
        # 字母和 50: EEEE...(10个E=50) → 0→1
        assert word_to_stroke_digit("E" * 10) == 1  # 10*5=50, 50%10=0→1


class TestThreeWordsToStartIndex:
    def test_love_work_fate_to_sign_88(self):
        """D4 定稿示例：LOVE/WORK/FATE → Sign #88。"""
        assert three_words_to_start_index(["LOVE", "WORK", "FATE"]) == 88

    def test_case_insensitive(self):
        assert three_words_to_start_index(["love", "work", "fate"]) == 88

    def test_deterministic(self):
        """同一组词多次计算返回同一签号。"""
        words = ["hope", "dream", "journey"]
        first = three_words_to_start_index(words)
        for _ in range(5):
            assert three_words_to_start_index(words) == first

    def test_range_always_1_to_384(self):
        """任意三词结果必在 1..384。"""
        test_words = [
            ["a", "b", "c"],
            ["z", "z", "z"],
            ["hope", "dream", "journey"],
            ["LOVE", "WORK", "FATE"],
            ["test", "word", "here"],
        ]
        for words in test_words:
            result = three_words_to_start_index(words)
            assert 1 <= result <= 384, f"{words} -> {result} 超出 1..384"

    def test_rejects_wrong_word_count(self):
        with pytest.raises(ValueError):
            three_words_to_start_index(["a", "b"])
        with pytest.raises(ValueError):
            three_words_to_start_index(["a", "b", "c", "d"])

    def test_rejects_word_without_letters(self):
        with pytest.raises(ValueError):
            three_words_to_start_index(["love", "123", "fate"])
        with pytest.raises(ValueError):
            three_words_to_start_index(["love", "", "fate"])


class TestWordTransform:
    def test_structure(self):
        t = word_transform("LOVE")
        assert t == {"word": "LOVE", "letter_sum": 54, "digit": 4}

    def test_preserves_original_word(self):
        t = word_transform("love")
        assert t["word"] == "love"
        assert t["letter_sum"] == 54


# ============================================================
# W4.2 三数字算法
# ============================================================


class TestComposeEnglishThreeNumberSeed:
    def test_composition(self):
        assert compose_english_three_number_seed([314, 159, 265]) == 314_159_265
        assert compose_english_three_number_seed([1, 2, 3]) == 1_002_003
        assert compose_english_three_number_seed([0, 0, 1]) == 1

    def test_minimal_nonzero(self):
        assert compose_english_three_number_seed([0, 0, 1]) == 1

    def test_max(self):
        assert compose_english_three_number_seed([999, 999, 999]) == 999_999_999

    def test_rejects_all_zero(self):
        with pytest.raises(ValueError):
            compose_english_three_number_seed([0, 0, 0])

    def test_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            compose_english_three_number_seed([-1, 0, 0])
        with pytest.raises(ValueError):
            compose_english_three_number_seed([1000, 0, 0])

    def test_rejects_bool(self):
        """bool 是 int 子类，必须显式拒绝。"""
        with pytest.raises(ValueError):
            compose_english_three_number_seed([True, 0, 0])

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            compose_english_three_number_seed([1, 2])
        with pytest.raises(ValueError):
            compose_english_three_number_seed([1, 2, 3, 4])


class TestEnglishThreeNumbersToStartIndex:
    def test_314_159_265_to_sign_33(self):
        """W0.2 文档示例：314|159|265 → Sign #33。"""
        assert english_three_numbers_to_start_index([314, 159, 265]) == 33

    def test_minimal(self):
        """最小非零：(0,0,1) → seed=1 → r=1。"""
        assert english_three_numbers_to_start_index([0, 0, 1]) == 1

    def test_max(self):
        """最大：(999,999,999) → r 必在 1..384。"""
        result = english_three_numbers_to_start_index([999, 999, 999])
        assert 1 <= result <= 384

    def test_deterministic(self):
        numbers = [123, 456, 789]
        first = english_three_numbers_to_start_index(numbers)
        for _ in range(5):
            assert english_three_numbers_to_start_index(numbers) == first

    def test_rejects_all_zero(self):
        with pytest.raises(ValueError):
            english_three_numbers_to_start_index([0, 0, 0])


# ============================================================
# W4.1a 英文签文加载
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENGLISH_SIGNS_PATH = PROJECT_ROOT / "data" / "content" / "oracle_signs_en.json"


@pytest.fixture(scope="module")
def english_signs() -> dict:
    """加载真实英文签文数据；文件缺失时 skip。"""
    if not ENGLISH_SIGNS_PATH.exists():
        pytest.skip(f"英文签文数据文件不存在：{ENGLISH_SIGNS_PATH}")
    return load_english_signs(ENGLISH_SIGNS_PATH)


class TestNeedsFallback:
    def test_empty_string(self):
        assert _needs_fallback("") is True
        assert _needs_fallback("   ") is True

    def test_none(self):
        assert _needs_fallback(None) is True

    def test_non_string(self):
        assert _needs_fallback(123) is True

    def test_pure_english(self):
        assert _needs_fallback("This is English.") is False

    def test_cjk_residue(self):
        assert _needs_fallback("Some 中文 residue") is True
        assert _needs_fallback("签文") is True


class TestSanitizeRecord:
    def test_removes_fortune_and_gua_type(self):
        """D14：加载时剔除 fortune/gua_type。"""
        raw = {
            "sign_number": 1,
            "fortune": "Supremely Favorable",
            "gua_type": "Qian Palace",
            "sign_text": "Some text",
            "interpretation1": "Some interpretation",
            "career": "career text",
            "wealth": "wealth text",
            "love": "love text",
            "health": "health text",
            "study": "study text",
            "general": "general text",
        }
        result = _sanitize_record(raw)
        assert "fortune" not in result
        assert "gua_type" not in result

    def test_keeps_nine_required_fields(self):
        """D13：保留 9 必填字段。"""
        raw = {field: f"value-{field}" for field in ENGLISH_SIGN_FIELDS}
        raw["sign_number"] = 1
        result = _sanitize_record(raw)
        for field in ENGLISH_SIGN_FIELDS:
            assert field in result

    def test_cjk_field_gets_fallback(self):
        """CJK 残留字段触发 fallback。"""
        raw = {
            "sign_number": 1,
            "sign_text": "Some 中文 text",
            "interpretation1": "clean",
            "career": "clean",
            "wealth": "clean",
            "love": "clean",
            "health": "clean",
            "study": "clean",
            "general": "clean",
        }
        result = _sanitize_record(raw)
        assert result["sign_text"] == FALLBACK_TEXT
        assert result["interpretation1"] == "clean"

    def test_empty_field_gets_fallback(self):
        """空字段触发 fallback。"""
        raw = {
            "sign_number": 1,
            "sign_text": "",
            "interpretation1": "   ",
            "career": "clean",
            "wealth": "clean",
            "love": "clean",
            "health": "clean",
            "study": "clean",
            "general": "clean",
        }
        result = _sanitize_record(raw)
        assert result["sign_text"] == FALLBACK_TEXT
        assert result["interpretation1"] == FALLBACK_TEXT

    def test_preserves_responsible_use_when_valid(self):
        raw = {
            "sign_number": 1,
            "sign_text": "t",
            "interpretation1": "t",
            "career": "t",
            "wealth": "t",
            "love": "t",
            "health": "t",
            "study": "t",
            "general": "t",
            "responsible_use": "Reflect on how this resonates.",
        }
        result = _sanitize_record(raw)
        assert result["responsible_use"] == "Reflect on how this resonates."

    def test_drops_responsible_use_when_cjk(self):
        raw = {
            "sign_number": 1,
            "sign_text": "t",
            "interpretation1": "t",
            "career": "t",
            "wealth": "t",
            "love": "t",
            "health": "t",
            "study": "t",
            "general": "t",
            "responsible_use": "中文 responsible use",
        }
        result = _sanitize_record(raw)
        assert "responsible_use" not in result


class TestLoadEnglishSigns:
    def test_loads_384_signs(self, english_signs):
        """384 条签文全部加载。"""
        assert len(english_signs) == 384

    def test_sign_numbers_1_to_384(self, english_signs):
        """签号 1..384 全覆盖。"""
        assert set(english_signs.keys()) == set(range(1, 385))

    def test_all_records_have_nine_fields(self, english_signs):
        """每条记录必有 9 字段（不含 fortune/gua_type）。"""
        for sign_number, record in english_signs.items():
            for field in ENGLISH_SIGN_FIELDS:
                assert field in record, f"Sign #{sign_number} 缺字段 {field}"

    def test_no_fortune_or_gua_type(self, english_signs):
        """D14 硬约束：fortune/gua_type 必须剔除。"""
        for sign_number, record in english_signs.items():
            assert "fortune" not in record, f"Sign #{sign_number} 仍有 fortune"
            assert "gua_type" not in record, f"Sign #{sign_number} 仍有 gua_type"

    def test_no_cjk_in_loaded_fields(self, english_signs):
        """加载后字段不应含 CJK（残留应被 fallback 替换）。"""
        from zhugeshensuan.oracle_english import CJK_RE

        for sign_number, record in english_signs.items():
            for field in ENGLISH_SIGN_FIELDS:
                if field == "sign_number":
                    continue
                value = record[field]
                assert not CJK_RE.search(value), (
                    f"Sign #{sign_number} field={field} 仍有 CJK: {value[:50]}"
                )

    def test_known_empty_general_gets_fallback(self, english_signs):
        """已知质量遗留：sign #197-200 的 general 为空 → 应触发 fallback。"""
        for sign_number in (197, 198, 199, 200):
            assert english_signs[sign_number]["general"] == FALLBACK_TEXT


# ============================================================
# W4.3 服务层（ask_with_words / ask_with_numbers）
# ============================================================


class TestAskWithWords:
    def test_love_work_fate(self, english_signs):
        result = ask_with_words(["LOVE", "WORK", "FATE"], english_signs)
        assert result["mode"] == "words"
        assert result["sign_number"] == 88
        assert result["sign"] is not None
        assert result["sign"]["sign_number"] == 88

    def test_transform_structure(self, english_signs):
        result = ask_with_words(["LOVE", "WORK", "FATE"], english_signs)
        transform = result["transform"]
        assert len(transform) == 3
        assert transform[0] == {"word": "LOVE", "letter_sum": 54, "digit": 4}
        assert transform[1] == {"word": "WORK", "letter_sum": 67, "digit": 7}
        assert transform[2] == {"word": "FATE", "letter_sum": 32, "digit": 2}

    def test_sign_has_nine_fields(self, english_signs):
        result = ask_with_words(["LOVE", "WORK", "FATE"], english_signs)
        sign = result["sign"]
        for field in ENGLISH_SIGN_FIELDS:
            assert field in sign

    def test_deterministic(self, english_signs):
        words = ["hope", "dream", "journey"]
        first = ask_with_words(words, english_signs)
        for _ in range(3):
            r = ask_with_words(words, english_signs)
            assert r["sign_number"] == first["sign_number"]


class TestAskWithNumbers:
    def test_314_159_265(self, english_signs):
        result = ask_with_numbers([314, 159, 265], english_signs)
        assert result["mode"] == "numbers"
        assert result["sign_number"] == 33
        assert result["sign"] is not None

    def test_minimal(self, english_signs):
        result = ask_with_numbers([0, 0, 1], english_signs)
        assert result["sign_number"] == 1

    def test_deterministic(self, english_signs):
        numbers = [123, 456, 789]
        first = ask_with_numbers(numbers, english_signs)
        for _ in range(3):
            r = ask_with_numbers(numbers, english_signs)
            assert r["sign_number"] == first["sign_number"]

    def test_sign_has_nine_fields(self, english_signs):
        result = ask_with_numbers([314, 159, 265], english_signs)
        sign = result["sign"]
        for field in ENGLISH_SIGN_FIELDS:
            assert field in sign


# ============================================================
# W4.3 API 层（POST /api/en/oracle/ask）
# ============================================================


@pytest.fixture(scope="module")
def has_english_data():
    """是否加载了真实英文签文数据。"""
    return ENGLISH_SIGNS_PATH.exists()


class TestOracleAskApi:
    """英文算事 API 契约测试。"""

    def test_words_mode_success(self, client, has_english_data):
        if not has_english_data:
            pytest.skip("英文签文数据文件不存在")
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "words": ["LOVE", "WORK", "FATE"]},
        )
        assert resp.status_code == 200
        data = resp.json["data"]
        assert data["mode"] == "words"
        assert data["sign_number"] == 88
        assert data["sign"]["sign_number"] == 88
        assert len(data["transform"]) == 3

    def test_numbers_mode_success(self, client, has_english_data):
        if not has_english_data:
            pytest.skip("英文签文数据文件不存在")
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "numbers": [314, 159, 265]},
        )
        assert resp.status_code == 200
        data = resp.json["data"]
        assert data["mode"] == "numbers"
        assert data["sign_number"] == 33

    def test_words_mode_deterministic(self, client, has_english_data):
        if not has_english_data:
            pytest.skip("英文签文数据文件不存在")
        payload = {"mode": "words", "words": ["hope", "dream", "journey"]}
        first = client.post("/api/en/oracle/ask", json=payload).json["data"]["sign_number"]
        for _ in range(3):
            r = client.post("/api/en/oracle/ask", json=payload)
            assert r.json["data"]["sign_number"] == first

    def test_invalid_json(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            data="not-json",
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_JSON"

    def test_invalid_oracle_mode(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "unknown", "words": ["a", "b", "c"]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_ORACLE_MODE"

    def test_words_insufficient_wrong_count(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "words": ["a", "b"]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "ORACLE_WORDS_INSUFFICIENT"

    def test_words_insufficient_non_string(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "words": ["a", "b", 123]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "ORACLE_WORDS_INSUFFICIENT"

    def test_words_insufficient_no_letters(self, client):
        """某词剔除非字母后无字母。"""
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "words": ["love", "123", "fate"]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "ORACLE_WORDS_INSUFFICIENT"

    def test_numbers_invalid_type(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "numbers": ["a", "b", "c"]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_ORACLE_NUMBER"

    def test_numbers_bool_rejected(self, client):
        """bool 是 int 子类，必须拒绝。"""
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "numbers": [True, 0, 0]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_ORACLE_NUMBER"

    def test_numbers_out_of_range(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "numbers": [-1, 0, 0]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_ORACLE_NUMBER"

    def test_numbers_out_of_range_high(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "numbers": [1000, 0, 0]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_ORACLE_NUMBER"

    def test_numbers_all_zero(self, client):
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "numbers": [0, 0, 0]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "ORACLE_NUMBERS_ALL_ZERO"

    def test_words_mode_rejects_numbers_payload(self, client):
        """模式不互收：words 模式收到 numbers payload 应报错。"""
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "numbers": [1, 2, 3]},
        )
        assert resp.status_code == 400
        # words 字段缺失/类型错 → ORACLE_WORDS_INSUFFICIENT
        assert resp.json["error"]["code"] == "ORACLE_WORDS_INSUFFICIENT"

    def test_numbers_mode_rejects_words_payload(self, client):
        """模式不互收：numbers 模式收到 words payload 应报错。"""
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "numbers", "words": ["a", "b", "c"]},
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_ORACLE_NUMBER"

    def test_sign_has_no_fortune_or_gua_type(self, client, has_english_data):
        """D14：API 响应不含 fortune/gua_type。"""
        if not has_english_data:
            pytest.skip("英文签文数据文件不存在")
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "words": ["LOVE", "WORK", "FATE"]},
        )
        sign = resp.json["data"]["sign"]
        assert "fortune" not in sign
        assert "gua_type" not in sign

    def test_sign_has_no_old_fields(self, client, has_english_data):
        """契约：不出现 oracle_title/message/guidance_summary/caution 旧字段名。"""
        if not has_english_data:
            pytest.skip("英文签文数据文件不存在")
        resp = client.post(
            "/api/en/oracle/ask",
            json={"mode": "words", "words": ["LOVE", "WORK", "FATE"]},
        )
        sign = resp.json["data"]["sign"]
        for forbidden in ("oracle_title", "message", "guidance_summary", "caution"):
            assert forbidden not in sign
