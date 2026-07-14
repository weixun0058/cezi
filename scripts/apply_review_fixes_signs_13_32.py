"""应用 Gemini 审核 result_signs_13-32 的采纳修改。

修改范围：第 13、15、20、21、22、23、24、25、32 签。
每处替换均用 assert 验证 old 字符串存在，不掩盖错误。

依据：data/content/_review_log/gemini_review_result_signs_13-32.md
"""

import json
from pathlib import Path

PATH = Path("data/content/oracle_signs_en.json")

# (sign_number, field, old, new)
FIXES = [
    # ---- 第 13 签 ----
    # sign_text：fate→natural affinity, woman→gentle companion, reunite→fulfillment comes
    (
        13,
        "sign_text",
        "Delight meets when the woman appears, / The path ahead is guided by fate. / "
        "Fame and fortune are within reach at last, / In three or five moons we reunite.",
        "Joy is found when meeting the gentle companion, / "
        "The path ahead aligns with natural affinity. / "
        "Fame and fortune are within reach at last, / "
        "In three or five months, fulfillment comes.",
    ),
    # interpretation1：引用 sign_text 的 fate 同步 + destiny 禁用词
    (13, "interpretation1", "guided by fate", "aligns with natural affinity"),
    (13, "interpretation1", "drawn by destiny", "guided by potential affinities"),
    # ---- 第 15 签 ----
    # interpretation1（两处 Li Ge）+ love：Li Ge's → the Ge hexagram's
    (15, "interpretation1", "Li Ge's change", "the Ge hexagram's change"),
    (
        15,
        "interpretation1",
        "Li Ge governs gradual change",
        "the Ge hexagram governs gradual change",
    ),
    (15, "love", "Li Ge's image", "the Ge hexagram's image"),
    # ---- 第 20 签 ----
    # 6 字段同步：thank the spring breeze → blossoms fade in the spring breeze
    (20, "sign_text", "thank the spring breeze", "blossoms fade in the spring breeze"),
    (20, "interpretation1", "thank the spring breeze", "blossoms fade in the spring breeze"),
    (20, "career", "thank the spring breeze", "blossoms fade in the spring breeze"),
    (20, "love", "thank the spring breeze", "blossoms fade in the spring breeze"),
    (20, "health", "thank the spring breeze", "blossoms fade in the spring breeze"),
    (20, "general", "thank the spring breeze", "blossoms fade in the spring breeze"),
    # ---- 第 21 签 ----
    (21, "interpretation1", "Li Ge (Reform and Change)", "Ge (Reform and Change)"),
    # ---- 第 22 签 ----
    # sign_text 格式 2行→4行
    (
        22,
        "sign_text",
        "Matters support each other, yet halfway through,\n"
        "Ups and downs can finally be avoided; not a ripple of trouble appears.",
        "Matters support each other,\n"
        "Yet only halfway through.\n"
        "Ups and downs can finally be avoided,\n"
        "Not a single ripple of trouble appears.",
    ),
    # health 漏译胆：liver and tendons → liver, gallbladder, and tendons
    (
        22,
        "health",
        "governing the liver and tendons",
        "governing the liver, gallbladder, and tendons",
    ),
    # ---- 第 23 签 ----
    # sign_text 整句：格式 2行→4行 + 人千里 语义修正
    (
        23,
        "sign_text",
        "Joy, joy, joy — the spring breeze gives birth to peach and plum.\n"
        "No need to force anxiety and worry; beneath the bright moon, "
        "one travels a thousand miles.",
        "Joy, joy, joy—\n"
        "The spring breeze nurtures peach and plum.\n"
        "No need to force anxiety and worry,\n"
        "Though separated by a thousand miles under the bright moon.",
    ),
    # 6 字段引用同步：one travels a thousand miles → separated by a thousand miles
    (23, "interpretation1", "one travels a thousand miles", "separated by a thousand miles"),
    (23, "career", "one travels a thousand miles", "separated by a thousand miles"),
    (23, "wealth", "one travels a thousand miles", "separated by a thousand miles"),
    (23, "love", "one travels a thousand miles", "separated by a thousand miles"),
    (23, "health", "one travels a thousand miles", "separated by a thousand miles"),
    (23, "study", "one travels a thousand miles", "separated by a thousand miles"),
    # ---- 第 24 签 ----
    # sign_text 格式 2行→4行
    (
        24,
        "sign_text",
        "Restless mind, heavy heart;\nTo be safe, beware of going out and coming in.",
        "Restless is the mind,\n"
        "Heavy is the heart.\n"
        "To seek safety and peace,\n"
        "Beware of going out and coming in.",
    ),
    # ---- 第 25 签 ----
    # sign_text 格式 2行→4行
    (
        25,
        "sign_text",
        "See but not see, beware of hidden foes;\nMeet but not meet, in the end no proof goes.",
        "See but not see,\nBeware of hidden foes.\nMeet but not meet,\nIn the end no proof goes.",
    ),
    # ---- 第 32 签 ----
    # sign_text：tomb（死亡暗示）→ western hills' loom
    (
        32,
        "sign_text",
        "Like the setting sun's glow on a western tomb.",
        "As the sun fades behind the western hills' loom.",
    ),
]


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    by_num = {s["sign_number"]: s for s in data}

    applied = 0
    for sn, field, old, new in FIXES:
        sign = by_num[sn]
        assert field in sign, f"第{sn}签缺字段 {field}"
        current = sign[field]
        assert old in current, (
            f"第{sn}签 {field}: 未找到旧字符串\n"
            f"  期望含: {old[:60]!r}\n"
            f"  实际内容: {current[:120]!r}"
        )
        count = current.count(old)
        sign[field] = current.replace(old, new)
        applied += count
        print(f"✓ 第{sn}签 {field}: 替换 {count} 处")

    # 写回（indent=2 保持原格式）
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n共替换 {applied} 处，已写回 {PATH}")

    # 验证：扫描残留
    residuals = [
        "Li Ge",
        "thank the spring breeze",
        "drawn by destiny",
        "one travels a thousand miles",
        "western tomb",
        "liver and tendons",
    ]
    data2 = json.loads(PATH.read_text(encoding="utf-8"))
    target_sns = {13, 15, 20, 21, 22, 23, 24, 25, 32}
    found = False
    for s in data2:
        if s["sign_number"] not in target_sns:
            continue
        for field, val in s.items():
            if not isinstance(val, str):
                continue
            for kw in residuals:
                if kw in val:
                    print(f"⚠ 残留: 第{s['sign_number']}签 {field} 仍含 '{kw}'")
                    found = True
    if not found:
        print("验证通过：目标签内无残留关键词")


if __name__ == "__main__":
    main()
