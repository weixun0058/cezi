import pytest

from scripts.derive_original_oracle_signs import (
    compose_english_three_number_seed,
    compose_three_character_number,
    derive_sign,
    english_three_numbers_to_start_index,
    reduce_to_start_index,
    stroke_digit,
)


def make_record(index, value, status="accepted"):
    return {
        "global_index": index,
        "value": value,
        "status": status,
        "confidence": 1.0,
        "file": "source.jpg",
        "page_range": "1-100",
        "column": 1,
        "row": 1,
        "cell_id": "101",
    }


def test_source_book_stroke_rule_and_reduction():
    assert stroke_digit(7) == 7
    assert stroke_digit(12) == 2
    assert stroke_digit(10) == 1
    assert stroke_digit(20) == 1
    assert compose_three_character_number([7, 9, 12]) == 792
    assert reduce_to_start_index(792) == 24
    assert reduce_to_start_index(384) == 384
    assert reduce_to_start_index(768) == 384


def test_english_three_number_adaptation_covers_all_start_indices():
    assert compose_english_three_number_seed([314, 159, 265]) == 314_159_265
    assert compose_english_three_number_seed([1, 2, 3]) == 1_002_003
    assert english_three_numbers_to_start_index([314, 159, 265]) == 33
    assert english_three_numbers_to_start_index([0, 0, 384]) == 384

    reachable = {english_three_numbers_to_start_index([0, 0, number]) for number in range(1, 385)}
    assert reachable == set(range(1, 385))


@pytest.mark.parametrize(
    "numbers",
    ([0, 0, 0], [1, 2], [-1, 2, 3], [1, 2, 1000], [True, 2, 3], [1.5, 2, 3]),
)
def test_english_three_number_adaptation_rejects_invalid_input(numbers):
    with pytest.raises(ValueError):
        compose_english_three_number_seed(numbers)


def test_source_book_wealth_example():
    values = {
        24: "○",
        408: "意",
        792: "孜",
        1176: "孜",
        1560: "心",
        1944: "戚",
        2328: "戚",
        2712: "要",
        3096: "平",
        3480: "安",
        3864: "防",
        4248: "出",
        4632: "入",
        5016: "○",
    }
    by_index = {index: make_record(index, value) for index, value in values.items()}

    sign = derive_sign(by_index, sign_number=24, max_index=5016)

    assert sign["raw_text"] == "意孜孜心戚戚要平安防出入"
    assert sign["leading_placeholder_count"] == 1
    assert sign["first_character_index"] == 408
    assert sign["termination_index"] == 5016
    assert sign["termination_reason"] == "placeholder"


def test_dictionary_end_is_an_explicit_termination_reason():
    by_index = {
        1: make_record(1, "甲"),
        385: make_record(385, "乙", status="low_confidence"),
    }

    sign = derive_sign(by_index, sign_number=1, max_index=385)

    assert sign["raw_text"] == "甲乙"
    assert sign["termination_index"] is None
    assert sign["termination_reason"] == "dictionary_end"
    assert sign["needs_source_review"] is True
    assert sign["review_positions"] == [385]
