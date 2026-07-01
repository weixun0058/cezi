"""生成 huangli_terms_en.json 正式英文黄历词表。

职责：
1. activities 部分：从 ``data/content/huangli_activities_curated.json``（人工审校定稿）读取
2. 其他命名空间：从 ``frontend/static/js/lunar.js`` 的 6tail I18n messages 抽取候选词
3. 合并输出 ``data/content/huangli_terms_en.json``

硬约束：
- activities 部分为人工审校定稿，本脚本不可修改/覆盖
- 本脚本只生成候选词（其他命名空间），正式 activities 词表来自 curate 文件
- 未审核的新词一律隐藏并记录 translation_missing=true

依据：
- 用户审校定稿（2026-07-01）：39 活动类别 + 19 剔除 + 馀事勿取特殊处理
- D6 神煞音译+解释（本表不预存，运行时 fallback）
- W5.2 fallback 策略（缺失命名空间 translation_missing）
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LUNAR_JS = ROOT / "frontend" / "static" / "js" / "lunar.js"
CURATE_JSON = ROOT / "data" / "content" / "huangli_activities_curated.json"
OUTPUT_JSON = ROOT / "data" / "content" / "huangli_terms_en.json"

# 匹配 messages 块中的单行：'namespace.key': 'value',
LINE_RE = re.compile(r"^\s+'([\w.]+)':\s*'((?:[^'\\]|\\.)*)',?\s*$")

# lunar.js 命名空间 → JSON key 映射（非 activities）
# activities 由 curate 文件提供，本脚本不处理
NAMESPACE_TO_JSON_KEY: dict[str, str] = {
    "sx": "zodiac",
    "jq": "solar_terms",
    "ps": "directions",
    "wx": "elements",
    "tg": "stems",
    "dz": "branches",
    "jz": "sexagenary",
    "ny": "nayin",
    "bg": "trigrams",
    "w": "weekdays",
    "sz": "seasons",
    "zx": "twelve_duty",
    "jr": "festivals",
    "n": "numbers",
    "ts": "divination_directions",
    "xx": "twenty_eight_mansions",
    "dw": "animals",
    "xz": "western_zodiac",
    "ly": "rokuyo",
    "s": "misc",
    "yx": "moon_phases",
    # sn 神煞：D6 音译+解释，本表不预存，运行时 fallback
    # yj 宜忌：由 curate 文件提供（人工审校定稿），本脚本不处理
}


def extract_messages_block(content: str, lang: str) -> dict[str, str]:
    """从 lunar.js 内容中抽取指定语言的 messages 块。

    输入：
        content: lunar.js 文件内容
        lang: 'chs' 或 'en'
    输出：
        dict[key] = value（已反转义 \' → '）
    """
    block_start_marker = f"'{lang}': {{"
    start_idx = content.find(block_start_marker)
    if start_idx == -1:
        raise ValueError(f"未找到 {lang} messages 块")

    search_start = start_idx + len(block_start_marker)
    close_re = re.compile(r"\n\s{6}\}")
    close_match = close_re.search(content, search_start)
    if not close_match:
        raise ValueError(f"未找到 {lang} messages 块的闭合括号")

    block_content = content[search_start:close_match.start()]
    messages: dict[str, str] = {}
    for line in block_content.splitlines():
        m = LINE_RE.match(line)
        if m:
            key = m.group(1)
            value = m.group(2).replace("\\'", "'")
            messages[key] = value
    return messages


def load_curate() -> dict:
    """读取人工审校定稿的 activities 数据。

    输出：curate 文件完整内容
    异常：文件不存在抛 FileNotFoundError
    """
    if not CURATE_JSON.exists():
        raise FileNotFoundError(f"未找到人工审校定稿：{CURATE_JSON}")
    return json.loads(CURATE_JSON.read_text(encoding="utf-8"))


def build_other_namespaces(en_messages: dict[str, str], chs_messages: dict[str, str]) -> tuple[dict, dict]:
    """构建非 activities 命名空间的中文→英文映射。

    输入：
        en_messages: lunar.js en messages
        chs_messages: lunar.js chs messages
    输出：
        (terms, stats)
        terms: {json_key: {中文: 英文}}
        stats: {json_key: 条目数}
    """
    terms: dict[str, dict[str, str]] = {}
    stats: dict[str, int] = {}

    for ns_key, json_key in NAMESPACE_TO_JSON_KEY.items():
        mapping: dict[str, str] = {}
        prefix = ns_key + "."
        for key, en_val in en_messages.items():
            if not key.startswith(prefix):
                continue
            chs_val = chs_messages.get(key, "")
            if not chs_val or not en_val:
                continue
            mapping[chs_val] = en_val
        if mapping:
            terms[json_key] = mapping
            stats[json_key] = len(mapping)

    return terms, stats


def apply_term_overrides(other_terms: dict, overrides: dict) -> tuple[dict, list[str]]:
    """应用人工审校对非 activities 命名空间的展示覆盖。

    输入：
        other_terms: 从 lunar.js 抽取的命名空间映射 {json_key: {中文: 英文}}
        overrides: curate 文件的 term_overrides 区块
    输出：
        (updated_terms, applied_log)
        updated_terms: 覆盖后的 other_terms（stems 被替换，sexagenary 被派生重生成）
        applied_log: 实际应用的覆盖描述列表（用于 _meta 记录）
    """
    applied_log: list[str] = []
    updated = {k: dict(v) for k, v in other_terms.items()}

    # 1. 覆盖 stems（天干 → 阴阳五行，如 甲→Yang Wood）
    stems_override = overrides.get("stems", {})
    if stems_override:
        updated["stems"] = dict(stems_override)
        applied_log.append(f"stems 覆盖为阴阳五行（{len(stems_override)} 条）")

    # 2. 派生 sexagenary（六十甲子 → 阴阳五行+生肖组合，如 甲子→Yang Wood Rat）
    branch_to_zodiac_cn = overrides.get("branch_to_zodiac", {})
    zodiac_en = updated.get("zodiac", {})  # 生肖中文→英文，如 鼠→Rat
    if stems_override and branch_to_zodiac_cn and zodiac_en and "sexagenary" in updated:
        new_sexagenary: dict[str, str] = {}
        missing: list[str] = []
        for jiazi_key in updated["sexagenary"]:
            if len(jiazi_key) != 2:
                # 非标准双字 key，保留原值
                new_sexagenary[jiazi_key] = updated["sexagenary"][jiazi_key]
                continue
            gan_cn, zhi_cn = jiazi_key[0], jiazi_key[1]
            gan_en = stems_override.get(gan_cn)
            zodiac_cn = branch_to_zodiac_cn.get(zhi_cn)
            zodiac_en_val = zodiac_en.get(zodiac_cn) if zodiac_cn else None
            if gan_en and zodiac_en_val:
                new_sexagenary[jiazi_key] = f"{gan_en} {zodiac_en_val}"
            else:
                # 缺失映射，保留原值并记录
                new_sexagenary[jiazi_key] = updated["sexagenary"][jiazi_key]
                missing.append(jiazi_key)
        updated["sexagenary"] = new_sexagenary
        if missing:
            applied_log.append(
                f"sexagenary 派生（{len(new_sexagenary)} 条，{len(missing)} 条缺失保留原值：{missing}）"
            )
        else:
            applied_log.append(
                f"sexagenary 派生为阴阳五行+生肖组合（{len(new_sexagenary)} 条）"
            )

    # 3. 其他命名空间直接覆盖（moon_phases/rokuyo/twenty_eight_mansions/divination_directions/gods 等）
    # stems 已在上方处理（并参与 sexagenary 派生），_meta/branch_to_zodiac 为辅助映射，均跳过
    # 允许新增 override-only 命名空间（如 gods：无 lunar.js 候选词，仅由 term_overrides 提供）
    AUX_KEYS = {"_meta", "branch_to_zodiac"}
    for key, val in overrides.items():
        if key in AUX_KEYS or key == "stems":
            continue
        if isinstance(val, dict):
            updated[key] = dict(val)
            applied_log.append(f"{key} 人工审校覆盖（{len(val)} 条）")

    return updated, applied_log


def main() -> None:
    """主函数：读 curate + 抽取 lunar.js 其他命名空间，合并生成正式词表。"""
    if not LUNAR_JS.exists():
        raise FileNotFoundError(f"未找到 {LUNAR_JS}")
    if not CURATE_JSON.exists():
        raise FileNotFoundError(f"未找到人工审校定稿：{CURATE_JSON}")

    # 1. 读取人工审校定稿
    curate = load_curate()
    print(f"读取 curate：{len(curate['activity_categories'])} 类别，"
          f"{len(curate['excluded_activities'])} 剔除，"
          f"{len(curate['special_rules'])} 特殊规则")

    # 2. 抽取 lunar.js 其他命名空间候选词
    content = LUNAR_JS.read_text(encoding="utf-8")
    chs_messages = extract_messages_block(content, "chs")
    en_messages = extract_messages_block(content, "en")
    print(f"读取 lunar.js：chs {len(chs_messages)} 条，en {len(en_messages)} 条")

    other_terms, other_stats = build_other_namespaces(en_messages, chs_messages)

    # 2.5 应用人工审校覆盖（天干阴阳五行、六十甲子派生）
    term_overrides = curate.get("term_overrides", {})
    applied_log: list[str] = []
    if term_overrides:
        other_terms, applied_log = apply_term_overrides(other_terms, term_overrides)
        # 重新计算 stats（条目数可能不变，但值已变）
        other_stats = {k: len(v) for k, v in other_terms.items()}

    # 3. 合并生成正式词表
    # activities 部分使用 curate 的新结构（activity_categories/excluded_activities/special_rules）
    # 其他命名空间保持中文→英文映射
    output: dict = {
        "_meta": {
            "source": "huangli_activities_curated.json (activities) + lunar.js I18n (other namespaces)",
            "generated_by": "scripts/build_huangli_terms_en.py",
            "policy": (
                "activities 为人工审校定稿（39 类别+19 剔除+馀事勿取特殊），"
                "其他命名空间为 6tail 候选词经 term_overrides 覆盖"
                "（天干阴阳五行、六十甲子阴阳五行+生肖组合、神煞方案 C 小批审校），"
                "未审核神煞运行时隐藏并记录 translation_missing，缺失命名空间 translation_missing"
            ),
            "activities_source": "data/content/huangli_activities_curated.json",
            "term_overrides_source": "data/content/huangli_activities_curated.json (term_overrides 区块)",
            "other_namespaces_source": "frontend/static/js/lunar.js I18n messages (6tail)",
            "applied_overrides": applied_log,
            "gods_policy": (
                "D6 方案 C：20 个常见神煞使用人工审校英文名、拼音和解释；"
                "其余神煞运行时隐藏并记录 translation_missing"
            ),
            "missing_namespaces": [
                "d (农历日)", "m (农历月)", "h (候/72物候)",
                "ss (十神)", "ds (十二长生)", "od (孟仲季)",
            ],
            "other_namespaces_stats": other_stats,
        },
        # activities 人工审校定稿（从 curate 文件读取，不可被本脚本修改）
        "activity_categories": curate["activity_categories"],
        "excluded_activities": curate["excluded_activities"],
        "special_rules": curate["special_rules"],
        "display_wording": curate["display_wording"],
        "conflict_rules": curate["conflict_rules"],
        # 其他命名空间（从 lunar.js 抽取的候选词 + term_overrides 覆盖/新增）
        **other_terms,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n输出：{OUTPUT_JSON}")
    print(f"文件大小：{OUTPUT_JSON.stat().st_size} 字节")
    print(f"\nactivities：{len(curate['activity_categories'])} 类别（人工审校定稿）")
    print(f"excluded：{len(curate['excluded_activities'])} 词")
    print(f"special_rules：{len(curate['special_rules'])} 条")
    if applied_log:
        print(f"\n应用的人工覆盖（term_overrides）：")
        for line in applied_log:
            print(f"  - {line}")
    print(f"\n其他命名空间：")
    for json_key, count in other_stats.items():
        print(f"  {json_key}: {count} 条")
    gods_count = other_stats.get("gods", 0)
    print(f"\ngods（神煞）：{gods_count} 条（D6 方案 C 小批审校）")


if __name__ == "__main__":
    main()
