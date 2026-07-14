"""英文签文服务。

职责：
1. 启动时从 ``data/content/oracle_signs_en.json`` 加载 384 条签文到内存
   （D15：JSON 内存加载，不入数据库）
2. 加载时剔除 ``fortune``/``gua_type``（D14/D16 硬约束），保留 9 必填字段 + 可选 ``responsible_use``
3. CJK 残留或空字段触发 fallback 占位（项目硬约束：未译签文显示占位文案）
4. 运行期只读，不修改原 JSON 文件（用户用其他 Agent 更新数据后，重启服务器即生效）

依赖：
- ``oracle_algorithm.py`` 提供签号算法
- ``data/content/oracle_signs_en.json`` 提供 384 条英文签文

依据：
- D13/D14/D15/D16 决策
- ``docs/plans/2026-06-27-english-site-execution-plan.md`` W4.1a/W4.3
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Sequence
from pathlib import Path

from .oracle_algorithm import (
    english_three_numbers_to_start_index,
    three_words_to_start_index,
    words_transform,
)

LOGGER = logging.getLogger(__name__)

# CJK 检测：覆盖中日韩统一表意文字基本区
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

# 未译签文字段占位文案（项目硬约束）
FALLBACK_TEXT = "This sign's English translation is under review."

# 英文签文必填 9 字段（D13/D14：已剔除 fortune/gua_type）
ENGLISH_SIGN_FIELDS: tuple[str, ...] = (
    "sign_number",
    "sign_text",
    "interpretation1",
    "career",
    "wealth",
    "love",
    "health",
    "study",
    "general",
)

# 可选字段（有值才保留）
OPTIONAL_FIELDS: tuple[str, ...] = ("responsible_use",)


def _needs_fallback(value) -> bool:
    """字段是否需要 fallback：空字符串或含 CJK 残留。"""
    if not isinstance(value, str) or not value.strip():
        return True
    return bool(CJK_RE.search(value))


def _sanitize_record(raw: dict) -> dict:
    """剔除 fortune/gua_type，对问题字段填 fallback。

    输入：原始 JSON 记录（11+ 字段）
    输出：清洗后记录（9 必填字段 + 可选 responsible_use）
    """
    sanitized = {field: raw.get(field, "") for field in ENGLISH_SIGN_FIELDS}
    for field in ENGLISH_SIGN_FIELDS:
        if field == "sign_number":
            continue
        if _needs_fallback(sanitized[field]):
            sanitized[field] = FALLBACK_TEXT
    # 保留 responsible_use（仅当非空且无 CJK）
    ru = raw.get("responsible_use")
    if isinstance(ru, str) and ru.strip() and not CJK_RE.search(ru):
        sanitized["responsible_use"] = ru
    return sanitized


def load_english_signs(json_path: Path) -> dict[int, dict]:
    """加载英文签文 JSON 到内存字典。

    输入：json_path - oracle_signs_en.json 路径
    输出：{sign_number(int): sanitized_record(dict)}，键为 int
    异常：文件不存在或 JSON 格式错误抛异常（由 app.py 捕获）
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("英文签文 JSON 必须是数组")
    signs: dict[int, dict] = {}
    for record in data:
        if not isinstance(record, dict):
            continue
        sign_number = record.get("sign_number")
        if not isinstance(sign_number, int):
            continue
        signs[sign_number] = _sanitize_record(record)
    LOGGER.info("Loaded %d English oracle signs from %s", len(signs), json_path)
    return signs


def load_english_signs_safe(json_path: Path) -> dict[int, dict]:
    """安全加载：文件缺失或异常时返回空字典并记 warning。

    用于 app.py 启动期，避免缺数据文件导致整个服务启动失败。
    """
    try:
        return load_english_signs(json_path)
    except FileNotFoundError:
        LOGGER.warning("English oracle signs file not found: %s", json_path)
        return {}
    except (json.JSONDecodeError, ValueError) as exc:
        LOGGER.warning("Failed to load English oracle signs from %s: %s", json_path, exc)
        return {}


def get_english_sign(sign_number: int, signs: dict[int, dict]) -> dict | None:
    """按签号取英文签文。

    输入：sign_number 1..384，signs 内存字典
    输出：签文 dict 或 None（未找到）
    """
    return signs.get(sign_number)


def ask_with_words(words: Sequence[str], signs: dict[int, dict]) -> dict:
    """三词模式查询。

    输入：words 三个英文单词，signs 内存字典
    输出：{"mode":"words", "sign_number":int, "transform":[...], "sign":dict|None}
    异常：ValueError（词数/字母校验失败，由 API 层捕获转错误码）
    """
    sign_number = three_words_to_start_index(words)
    transform = words_transform(words)
    sign = get_english_sign(sign_number, signs)
    return {
        "mode": "words",
        "sign_number": sign_number,
        "transform": transform,
        "sign": sign,
    }


def ask_with_numbers(numbers: Sequence[int], signs: dict[int, dict]) -> dict:
    """三数字模式查询。

    输入：numbers 三个 0..999 整数，signs 内存字典
    输出：{"mode":"numbers", "sign_number":int, "sign":dict|None}
    异常：ValueError（范围/全零校验失败，由 API 层捕获转错误码）
    """
    sign_number = english_three_numbers_to_start_index(numbers)
    sign = get_english_sign(sign_number, signs)
    return {
        "mode": "numbers",
        "sign_number": sign_number,
        "sign": sign,
    }
