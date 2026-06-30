"""诸葛神算签号算法（英文版运行期实现）。

复用 ``scripts/derive_original_oracle_signs.py`` 的核心算法，保持运行期与离线脚本一致。
本模块只放纯函数，无 Flask 依赖，便于独立测试。

函数分组：
- 源书方法（中文版也用）：``stroke_digit`` / ``compose_three_character_number`` / ``reduce_to_start_index``
- 英文三数字专用：``compose_english_three_number_seed`` / ``english_three_numbers_to_start_index``
- 英文三词专用：``word_to_stroke_digit`` / ``three_words_to_start_index``

设计原则：
1. 算法纯函数，无副作用，可独立测试
2. 输入校验抛 ``ValueError``，由上层 API 捕获转错误码
3. 与 ``scripts/derive_original_oracle_signs.py`` 保持算法一致

依据：
- D4 决策（2026-06-30 定稿）：三词 A=1..Z=26 字母求和 + stroke_digit + compose + reduce
- ``docs/plans/2026-06-27-english-site-execution-plan.md`` W4.1/W4.2
- ``scripts/derive_original_oracle_signs.py``（权威算法源，只读）
"""

from __future__ import annotations

from typing import Iterable, Sequence

STEP = 384


def stroke_digit(strokes: int) -> int:
    """源书"笔画取个位"规则：对 10 取模，余 0 取 1。

    输入：strokes 正整数
    输出：1..9 的个位数
    异常：ValueError（strokes < 1）
    """
    if strokes < 1:
        raise ValueError("笔画数必须为正整数")
    remainder = strokes % 10
    return remainder if remainder else 1


def compose_three_character_number(strokes: Sequence[int]) -> int:
    """三字笔画合成三位数：100×d1 + 10×d2 + d3。

    输入：三个正整数的序列
    输出：111..999 的三位数
    异常：ValueError（长度不是 3）
    """
    if len(strokes) != 3:
        raise ValueError("占法要求恰好三个字")
    first, second, third = (stroke_digit(value) for value in strokes)
    return 100 * first + 10 * second + third


def reduce_to_start_index(number: int) -> int:
    """正整数映射到 1..384 起查位置：((N-1) mod 384) + 1。

    输入：正整数
    输出：1..384
    异常：ValueError（number < 1）
    """
    if number < 1:
        raise ValueError("起数必须为正整数")
    return (number - 1) % STEP + 1


def compose_english_three_number_seed(numbers: Sequence[int]) -> int:
    """英文三数字合成九位种子：d1×1,000,000 + d2×1,000 + d3。

    输入：三个 0..999 整数
    输出：1..999,999,999 的种子（全零抛 ValueError）
    异常：ValueError（长度不是 3、某值越界、全零）
    """
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


def english_three_numbers_to_start_index(numbers: Sequence[int]) -> int:
    """三数字映射到 1..384 起查位置。"""
    return reduce_to_start_index(compose_english_three_number_seed(numbers))


def word_to_letter_sum(word: str) -> int:
    """英文单词字母求和：A=1..Z=26，非字母字符剔除。

    输入：英文单词字符串
    输出：字母和（正整数）
    异常：ValueError（剔除后无字母）
    """
    letters = [ch for ch in word.upper() if "A" <= ch <= "Z"]
    if not letters:
        raise ValueError(f"单词无有效字母：{word!r}")
    return sum(ord(ch) - ord("A") + 1 for ch in letters)


def word_to_stroke_digit(word: str) -> int:
    """英文单词到笔画位：字母求和 → stroke_digit。

    输入：英文单词字符串
    输出：1..9 的个位数
    异常：ValueError（无有效字母）
    """
    return stroke_digit(word_to_letter_sum(word))


def three_words_to_start_index(words: Sequence[str]) -> int:
    """三英文词映射到 1..384 起查位置。

    流程：每词 → 字母和 → stroke_digit → 三数字 → compose → reduce。
    示例：["LOVE","WORK","FATE"] → [4,7,2] → 472 → Sign #88。

    输入：三个英文单词
    输出：1..384
    异常：ValueError（长度不是 3、某词无字母）
    """
    if len(words) != 3:
        raise ValueError("三词起签要求恰好三个英文单词")
    digits = [word_to_stroke_digit(word) for word in words]
    return reduce_to_start_index(compose_three_character_number(digits))


def word_transform(word: str) -> dict:
    """返回单词到笔画位的变换过程，供前端展示动画。

    输入：英文单词
    输出：{"word": str, "letter_sum": int, "digit": int}
    """
    letter_sum = word_to_letter_sum(word)
    return {"word": word, "letter_sum": letter_sum, "digit": stroke_digit(letter_sum)}


def words_transform(words: Iterable[str]) -> list[dict]:
    """对多个单词逐个返回变换过程。"""
    return [word_transform(word) for word in words]
