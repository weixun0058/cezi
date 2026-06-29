"""Derive the 384 original oracle texts from the corrected 12,700-cell dictionary."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

STEP = 384
SIGN_COUNT = 384
PLACEHOLDER = "○"
TRUSTED_STATUSES = {"accepted", "corrected"}


def stroke_digit(strokes: int) -> int:
    """Apply the source book's one-digit stroke rule."""
    if strokes < 1:
        raise ValueError("笔画数必须为正整数")
    remainder = strokes % 10
    return remainder if remainder else 1


def compose_three_character_number(strokes: list[int] | tuple[int, int, int]) -> int:
    """Compose the hundreds/tens/units number from three stroke counts."""
    if len(strokes) != 3:
        raise ValueError("占法要求恰好三个字")
    first, second, third = (stroke_digit(value) for value in strokes)
    return 100 * first + 10 * second + third


def reduce_to_start_index(number: int) -> int:
    """Reduce a positive number to the source book's 1..384 start index."""
    if number < 1:
        raise ValueError("起数必须为正整数")
    return (number - 1) % STEP + 1


# English product adaptation; this rule is not part of the source-book method.
def compose_english_three_number_seed(
    numbers: list[int] | tuple[int, int, int],
) -> int:
    """Join three 000..999 number groups into one fixed-width nine-digit seed."""
    if len(numbers) != 3:
        raise ValueError("英文数字起签要求恰好三组数字")
    if any(
        isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 999
        for value in numbers
    ):
        raise ValueError("每组数字必须是 000 到 999 之间的整数")

    first, second, third = numbers
    seed = first * 1_000_000 + second * 1_000 + third
    if seed == 0:
        raise ValueError("三组数字不能全为 000")
    return seed


def english_three_numbers_to_start_index(
    numbers: list[int] | tuple[int, int, int],
) -> int:
    """Map three English-mode number groups deterministically to 1..384."""
    return reduce_to_start_index(compose_english_three_number_seed(numbers))


def load_dictionary(source_path: Path) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    records = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError("字典 JSON 必须是非空数组")

    by_index: dict[int, dict[str, Any]] = {}
    for record in records:
        index = record.get("global_index")
        value = record.get("value")
        if not isinstance(index, int):
            raise ValueError(f"global_index 非整数：{index!r}")
        if index in by_index:
            raise ValueError(f"global_index 重复：{index}")
        if not isinstance(value, str) or len(value) != 1:
            raise ValueError(f"第 {index} 位不是单字符：{value!r}")
        by_index[index] = record

    expected_indices = set(range(1, len(records) + 1))
    actual_indices = set(by_index)
    if actual_indices != expected_indices:
        missing = sorted(expected_indices - actual_indices)[:10]
        extra = sorted(actual_indices - expected_indices)[:10]
        raise ValueError(f"global_index 不连续；缺失={missing}，多余={extra}")
    if len(records) < SIGN_COUNT:
        raise ValueError(f"字典仅有 {len(records)} 格，无法推导 {SIGN_COUNT} 签")

    return records, by_index


def evidence_row(
    record: dict[str, Any], sign_number: int, role: str, character_order: int | None
) -> dict[str, Any]:
    status = str(record.get("status", ""))
    return {
        "sign_number": sign_number,
        "character_order": character_order,
        "global_index": record["global_index"],
        "value": record["value"],
        "role": role,
        "status": status,
        "confidence": record.get("confidence"),
        "file": record.get("file", ""),
        "page_range": record.get("page_range", ""),
        "column": record.get("column"),
        "row": record.get("row"),
        "cell_id": record.get("cell_id", ""),
        "needs_review": role == "character" and status not in TRUSTED_STATUSES,
    }


def derive_sign(
    by_index: dict[int, dict[str, Any]], sign_number: int, max_index: int
) -> dict[str, Any]:
    if not 1 <= sign_number <= SIGN_COUNT:
        raise ValueError(f"签号必须在 1..{SIGN_COUNT}：{sign_number}")

    characters: list[str] = []
    positions: list[int] = []
    evidence: list[dict[str, Any]] = []
    leading_placeholders = 0
    termination_index: int | None = None
    termination_reason = "dictionary_end"

    for index in range(sign_number, max_index + 1, STEP):
        record = by_index[index]
        value = record["value"]
        if value == PLACEHOLDER:
            if not characters:
                leading_placeholders += 1
                evidence.append(evidence_row(record, sign_number, "leading_placeholder", None))
                continue
            termination_index = index
            termination_reason = "placeholder"
            evidence.append(evidence_row(record, sign_number, "terminator", None))
            break

        characters.append(value)
        positions.append(index)
        evidence.append(evidence_row(record, sign_number, "character", len(characters)))

    if not characters:
        raise ValueError(f"第 {sign_number} 签没有查得任何实字")

    character_evidence = [item for item in evidence if item["role"] == "character"]
    status_counts = Counter(item["status"] for item in character_evidence)
    review_positions = [item["global_index"] for item in character_evidence if item["needs_review"]]
    return {
        "sign_number": sign_number,
        "raw_text": "".join(characters),
        "character_count": len(characters),
        "start_index": sign_number,
        "first_character_index": positions[0],
        "leading_placeholder_count": leading_placeholders,
        "termination_index": termination_index,
        "termination_reason": termination_reason,
        "positions": positions,
        "source_status_counts": dict(sorted(status_counts.items())),
        "needs_source_review": bool(review_positions),
        "review_positions": review_positions,
        "evidence": evidence,
    }


def derive_all_signs(
    records: list[dict[str, Any]], by_index: dict[int, dict[str, Any]]
) -> list[dict[str, Any]]:
    max_index = len(records)
    return [derive_sign(by_index, number, max_index) for number in range(1, SIGN_COUNT + 1)]


def build_document(source_path: Path) -> dict[str, Any]:
    records, by_index = load_dictionary(source_path)
    signs = derive_all_signs(records, by_index)
    wealth_example = signs[23]
    if (
        wealth_example["raw_text"] != "意孜孜心戚戚要平安防出入"
        or wealth_example["termination_index"] != 5016
    ):
        raise ValueError("第 24 签未能复现原稿“求财运”演式，请检查字表或算法")
    dictionary_status_counts = Counter(str(record.get("status", "")) for record in records)
    termination_counts = Counter(sign["termination_reason"] for sign in signs)
    review_signs = [sign["sign_number"] for sign in signs if sign["needs_source_review"]]
    character_counts = [sign["character_count"] for sign in signs]

    return {
        "metadata": {
            "title": "诸葛神算原始字表推导签文",
            "source_file": str(source_path),
            "algorithm": "起查位置 r=1..384；沿 r+384k 取字；跳过前导○；首字后遇○停止",
            "step": STEP,
            "sign_count": len(signs),
            "dictionary_cell_count": len(records),
            "dictionary_placeholder_count": sum(
                record["value"] == PLACEHOLDER for record in records
            ),
            "dictionary_status_counts": dict(sorted(dictionary_status_counts.items())),
            "termination_counts": dict(sorted(termination_counts.items())),
            "minimum_character_count": min(character_counts),
            "maximum_character_count": max(character_counts),
            "review_sign_count": len(review_signs),
            "review_sign_numbers": review_signs,
            "punctuation_policy": "仅保留字表取出的字符，不依据后世签本补标点",
        },
        "signs": signs,
    }


def write_json(document: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_csv(document: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sign_number",
        "raw_text",
        "character_count",
        "start_index",
        "first_character_index",
        "leading_placeholder_count",
        "termination_index",
        "termination_reason",
        "positions",
        "needs_source_review",
        "review_positions",
        "source_status_counts",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for sign in document["signs"]:
            writer.writerow(
                {
                    **{key: sign[key] for key in fieldnames if key in sign},
                    "positions": " ".join(str(value) for value in sign["positions"]),
                    "review_positions": " ".join(str(value) for value in sign["review_positions"]),
                    "source_status_counts": json.dumps(
                        sign["source_status_counts"], ensure_ascii=False, sort_keys=True
                    ),
                }
            )


def write_markdown(document: dict[str, Any], output_path: Path) -> None:
    metadata = document["metadata"]
    lines = [
        "# 诸葛神算原始字表推导签文",
        "",
        "> 由勘误后的 12,700 字表按 384 步长机械推导。正文不补后世标点；完整字位证据见 JSON。",
        "",
        f"- 签文总数：{metadata['sign_count']}",
        f"- 空位终止：{metadata['termination_counts'].get('placeholder', 0)}",
        f"- 字典末尾终止：{metadata['termination_counts'].get('dictionary_end', 0)}",
        f"- 涉及待复核来源状态的签文：{metadata['review_sign_count']}",
        "",
        "| 签号 | 字表推导原文 | 字数 | 首字位置 | 终止方式 | 待复核字位 |",
        "|---:|---|---:|---:|---|---|",
    ]
    for sign in document["signs"]:
        review_positions = "、".join(str(value) for value in sign["review_positions"]) or "—"
        termination = (
            f"○@{sign['termination_index']}"
            if sign["termination_reason"] == "placeholder"
            else "字典末尾"
        )
        lines.append(
            f"| {sign['sign_number']} | {sign['raw_text']} | {sign['character_count']} | "
            f"{sign['first_character_index']} | {termination} | {review_positions} |"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="勘误后的 final.json")
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--csv-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document = build_document(args.source.resolve())
    write_json(document, args.json_output)
    write_csv(document, args.csv_output)
    write_markdown(document, args.markdown_output)
    metadata = document["metadata"]
    print(
        f"generated={metadata['sign_count']} "
        f"placeholder_terminated={metadata['termination_counts'].get('placeholder', 0)} "
        f"dictionary_end_terminated={metadata['termination_counts'].get('dictionary_end', 0)} "
        f"review_signs={metadata['review_sign_count']}"
    )


if __name__ == "__main__":
    main()
