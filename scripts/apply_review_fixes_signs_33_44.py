"""应用 Gemini 审核 result_signs_33-44 的采纳修改。

修改范围：第 33、34、35、36、37、40、43 签（共 7 签，14 处替换）。
支持幂等运行：已应用的修改会跳过，不报错。

依据：data/content/_review_log/gemini_review_result_signs_33-44.md

未处理的签：
- 第 38、41、42 签：审核结论为无 Critical/High/Medium 问题，无需修改
- 第 39 签：审核提到 [Low] "heal yourself"，但当前 json 中 "heal" 仅作为 "health" 的子串出现，
  不存在独立的 "heal" 动词，审核引用不精确，跳过
- 第 44 签：审核提到 general 含 "this supremely favorable sign is auspicious"，但当前 json 中
  该短语不存在（审核可能基于旧版本翻译），跳过

注意：第34签 interpretation1/general 中的 "supremely favorable" 未修改——
      审核未提及第34签有评级问题，且第34签原文"终有庆也"确实是吉签，不在本次修改范围。
"""
import json
from pathlib import Path

PATH = Path("data/content/oracle_signs_en.json")

# (sign_number, field, old, new)
FIXES = [
    # ---- 第 33 签 [High] 评级偏差 ----
    # 原文"恐有波涛惊远客，扁舟一叶若为凭"暗示中平偏下，非"moderately favorable"
    (33, "interpretation1",
     "This is a moderately favorable sign:",
     "This is a neutral sign:"),

    # ---- 第 34 签 [High] "heal" 禁止词 ----
    # "heal" 暗示确定疗效，违反 responsible-use 准则
    (34, "health",
     "Old ailments may heal,",
     "Old ailments may resolve,"),

    # ---- 第 35 签 [High] 评级严重偏差 + [Medium] will 绝对化 ----
    # 原文"一向平顺，今突生险"属中平/平吉，非"supremely favorable"（上上大吉）
    (35, "interpretation1",
     "This is supremely favorable: confidence born from difficulty, and the resolve to move forward.",
     "This is a mixed fortune sign: progress comes through navigating sudden difficulty, "
     "requiring confidence and the resolve to move forward."),
    # general 字段同步修正评级（审核未提及，但为一致性同步）
    (35, "general",
     "This supremely favorable sign turns hardship into growth.",
     "This mixed fortune sign turns hardship into growth."),
    # love 字段 "will grow" → "is likely to grow"（避免绝对化预测）
    (35, "love",
     "the connection will grow slowly but solidly",
     "the connection is likely to grow slowly but solidly"),

    # ---- 第 36 签 [Medium] 漏译肝木调理 ----
    # 原文"消融、气血游走、蛰伏生机"重点在肝气疏泄，英文版缺 Liver and gallbladder
    (36, "health",
     "Kidney and urinary health benefit from increased water intake and outdoor walks.",
     "Liver and gallbladder health benefit from gentle expansion, while kidney and urinary "
     "systems should be supported with increased water intake and outdoor walks to assist "
     "the transition of seasonal qi."),

    # ---- 第 37 签 [Medium] 评级偏差（interpretation1 + love 同步）----
    # 原文"万马归源、千猿拜洞、虎龙俱伏"表面威仪但内藏隐忧，非"Moderately Unfavorable"可概括
    (37, "interpretation1",
     "Yet this sign is rated Moderately Unfavorable.",
     "Yet this sign is rated Neutral to Cautionary, advising inner cultivation rather than outward pursuit."),
    # love 字段引用评级，需同步修改
    (37, "love",
     "The Moderately Unfavorable sign reminds you",
     "The Neutral to Cautionary sign reminds you"),

    # ---- 第 40 签 [High] "barely" 语义错误（多字段同步）----
    # 原文"非人误己，几丧生身" = 不是别人误导你，而是你几乎丢了性命
    # sign_text 中是倒装 "barely have you lost your life"
    # interpretation1/wealth/love/general 中引用是非倒装 "barely you have lost your life"
    # 统一改为 "almost lost your very life"（准确传达"几乎丧生"的语义）
    (40, "sign_text",
     "barely have you lost your life",
     "you have almost lost your very life"),
    (40, "interpretation1",
     "barely you have lost your life",
     "almost lost your very life"),
    (40, "wealth",
     "barely you have lost your life",
     "almost lost your very life"),
    (40, "love",
     "barely you have lost your life",
     "almost lost your very life"),
    (40, "general",
     "barely you have lost your life",
     "almost lost your very life"),

    # ---- 第 43 签 [Medium] sign_text 格式 5行→4行 + "Seek them"→"Seek them out" ----
    # 原文5行结构不符合4句诗的格式，第2、3句应合并
    # "Seek them yourself" 补 "out" 更贴切"自求之"的语义
    (43, "sign_text",
     "No going up, it is ahead.\n"
     "Turn back and realize—\n"
     "Collect the reins well.\n"
     "A thousand paths and ten thousand roads always exist,\n"
     "Seek them yourself.",
     "No going up, it is ahead,\n"
     "Turn back and realize—collect the reins well.\n"
     "A thousand paths and ten thousand roads always exist,\n"
     "Seek them out yourself."),
]


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    by_num = {s["sign_number"]: s for s in data}

    applied = 0
    skipped = 0
    for sn, field, old, new in FIXES:
        sign = by_num[sn]
        assert field in sign, f"第{sn}签缺字段 {field}"
        current = sign[field]
        if old not in current:
            # 幂等检查：如果 new 已存在，说明已应用过，跳过
            if new in current:
                print(f"⊙ 第{sn}签 {field}: 已应用过，跳过")
                skipped += 1
                continue
            # old 不存在且 new 也不存在，报错
            raise AssertionError(
                f"第{sn}签 {field}: 未找到旧字符串，且新字符串也不存在\n"
                f"  期望含: {old[:80]!r}\n"
                f"  实际内容: {current[:150]!r}"
            )
        count = current.count(old)
        sign[field] = current.replace(old, new)
        applied += count
        print(f"✓ 第{sn}签 {field}: 替换 {count} 处")

    # 写回（indent=2 保持原格式）
    PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\n共替换 {applied} 处，跳过 {skipped} 处（已应用），已写回 {PATH}")

    # 验证：扫描本脚本修改范围内的残留关键词
    # 注意：只检查实际修改过的关键词，不检查审核未提及的（如第34签的 supremely favorable）
    residuals_by_sign = {
        33: ["moderately favorable sign:"],
        34: ["Old ailments may heal,"],
        35: ["supremely favorable", "the connection will grow slowly"],
        36: ["Kidney and urinary health benefit from increased water intake"],
        37: ["Moderately Unfavorable"],
        40: ["barely you have lost your life", "barely have you lost your life"],
        43: ["Seek them yourself."],
    }
    data2 = json.loads(PATH.read_text(encoding="utf-8"))
    found = False
    for s in data2:
        sn = s["sign_number"]
        if sn not in residuals_by_sign:
            continue
        for field, val in s.items():
            if not isinstance(val, str):
                continue
            for kw in residuals_by_sign[sn]:
                if kw in val:
                    print(f"⚠ 残留: 第{sn}签 {field} 仍含 '{kw}'")
                    found = True
    if not found:
        print("验证通过：目标签内无残留关键词")


if __name__ == "__main__":
    main()
