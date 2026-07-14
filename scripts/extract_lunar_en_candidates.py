"""从 frontend/static/js/lunar.js 抽取 6tail I18n 英文候选词，生成黄历术语表草稿。

用途：W1.1 一次性脚本。从 lunar.js 的 _messages['chs'] 和 _messages['en'] 块
抽取所有命名空间的 key-value，按命名空间分组对比，输出 markdown 草稿供人工审校。

输入：frontend/static/js/lunar.js
输出：docs/business/huangli-english-termbase-draft.md

注意：只抽取候选，不直接上线。定稿后再写入项目英文黄历词表，不改 lunar.js。
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

# 项目根目录（脚本位于 scripts/ 下）
ROOT = Path(__file__).resolve().parent.parent
LUNAR_JS = ROOT / "frontend" / "static" / "js" / "lunar.js"
OUTPUT_MD = ROOT / "docs" / "business" / "huangli-english-termbase-draft.md"

# 命名空间含义对照（基于源码分析，纠正了执行计划中的注释错误）
NAMESPACE_MEANING: dict[str, str] = {
    "tg": "天干 (Heavenly Stems)",
    "dz": "地支 (Earthly Branches)",
    "zx": "十二值日 (Twelve Duty Officers)",
    "jz": "六十甲子 (Sixty Jiazi)",
    "sx": "生肖 (Chinese Zodiac)",  # 注意：不是十神
    "dw": "动物 (Animals, 28宿对应)",
    "wx": "五行+日月 (Five Elements + Sun/Moon)",
    "n": "数字 (Numbers)",
    "d": "农历日 (Lunar Days)",
    "m": "农历月 (Lunar Months)",
    "w": "星期 (Weekdays)",
    "xz": "星座 (Western Zodiac)",
    "bg": "八卦 (Eight Trigrams)",  # 注意：不是拜功
    "ps": "方位 (Directions)",  # 注意：不是彭祖百忌
    "jq": "节气 (Solar Terms)",
    "sn": "神煞 (Spirits / Deities)",  # D6 已确认：音译+解释
    "s": "杂项 (Misc: 黄道/吉凶/阴阳/颜色)",
    "jr": "节日 (Festivals)",
    "ds": "十二长生 (Twelve Life Stages)",
    "h": "候 (Phenology, 72物候)",
    "ts": "占方 (Divination Directions)",
    "ly": "六曜 (Rokuyō)",
    "yj": "宜忌 (Favorable/Unfavorable Activities)",
    "xx": "28宿 (Twenty-Eight Mansions)",
    "sz": "四季 (Four Seasons)",
    "od": "孟仲季 (Meng/Zhong/Ji)",
    "yx": "月相 (Moon Phases)",
    "ny": "纳音 (Nayin / Melodic Elements)",
    "ss": "十神 (Ten Gods)",  # 注意：不是生肖
}

# 易误读词审校清单（W1.1 第 5 条要求）
REVIEW_FOCUS: dict[str, str] = {
    "Yellow Calendar": "黄历的误译，应使用 Daily Chinese Almanac",
    "Auspicious": "宜的翻译，需检查是否过度宗教化",
    "Evil Spirit": "神煞的误译，D6 已确认用音译+解释（Shén Shà）",
    "Consecretion": "yj.kaiGuang 的拼写错误，应为 Consecration",
    "Paint sculptural": "yj.suHui 的生硬翻译，需审校",
}

# 匹配 messages 块中的单行：'namespace.key': 'value',
# value 中含单引号时会转义为 \'
LINE_RE = re.compile(r"^\s+'([\w.]+)':\s*'((?:[^'\\]|\\.)*)',?\s*$")


def extract_messages_block(content: str, lang: str) -> dict[str, str]:
    """从 lunar.js 内容中抽取指定语言的 messages 块。

    输入：
        content: lunar.js 文件内容
        lang: 'chs' 或 'en'
    输出：
        dict[key] = value（已反转义 \' → '）
    """
    # 定位 'chs': { ... } 或 'en': { ... } 块
    block_start_marker = f"'{lang}': {{"
    start_idx = content.find(block_start_marker)
    if start_idx == -1:
        raise ValueError(f"未找到 {lang} messages 块")

    # 找到对应的闭合 }（注意块内有嵌套？实际是扁平 key，无嵌套）
    # 块结构：'lang': { ... },  或  'lang': { ... }（最后一个无逗号）
    # 简单方法：从 start_idx 找到第一个 } 出现的位置（但要跳过字符串内的 }）
    # 实际 lunar.js 的 messages 是扁平的 key-value，value 是字符串，不会包含 }
    # 所以可以直接找下一个 \n      } （缩进 6 空格的闭合括号）
    search_start = start_idx + len(block_start_marker)
    # 闭合括号在单独一行，缩进 6 空格
    close_re = re.compile(r"\n\s{6}\}")
    close_match = close_re.search(content, search_start)
    if not close_match:
        raise ValueError(f"未找到 {lang} messages 块的闭合括号")

    block_content = content[search_start : close_match.start()]

    messages: dict[str, str] = {}
    for line in block_content.splitlines():
        m = LINE_RE.match(line)
        if m:
            key = m.group(1)
            value = m.group(2).replace("\\'", "'")
            messages[key] = value
    return messages


def group_by_namespace(messages: dict[str, str]) -> dict[str, dict[str, str]]:
    """按命名空间（key 的第一段）分组。

    输入：dict[key] = value
    输出：dict[namespace] = dict[key] = value
    """
    grouped: dict[str, dict[str, str]] = defaultdict(dict)
    for key, value in messages.items():
        if "." in key:
            ns, _ = key.split(".", 1)
        else:
            ns = key
        grouped[ns][key] = value
    return grouped


def render_markdown(
    chs_grouped: dict[str, dict[str, str]],
    en_grouped: dict[str, dict[str, str]],
) -> str:
    """渲染术语表草稿 markdown。

    输入：
        chs_grouped: 中文 messages 按命名空间分组
        en_grouped: 英文 messages 按命名空间分组
    输出：
        markdown 字符串
    """
    lines: list[str] = []
    lines.append("# 英文黄历术语表草稿（6tail 候选词抽取）")
    lines.append("")
    lines.append(
        "> **文档定位**：W1.1 产出。从 `frontend/static/js/lunar.js` 的 "
        "6tail I18n 英文 messages 抽取候选词，供人工审校。"
    )
    lines.append("> **创建日期**：2026-06-30")
    lines.append("> **状态**：草稿，待人工审校定稿")
    lines.append("> **硬约束引用**：D6（神煞采用音译+解释）")
    lines.append(
        "> **注意**：本草稿只抽取候选，不直接上线。定稿后再写入项目英文黄历词表，不改 `lunar.js`。"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 一、命名空间含义对照（纠正执行计划注释错误）")
    lines.append("")
    lines.append(
        "> 执行计划 W1.1 列出的 6 个命名空间（sx/yj/jq/sn/ps/bg）含义正确，但注释有误，已纠正："
    )
    lines.append("> - `sx.*` = 生肖（非十神）")
    lines.append("> - `ss.*` = 十神（en 完全缺失）")
    lines.append("> - `ps.*` = 方位（非彭祖百忌）")
    lines.append("> - `bg.*` = 八卦（非拜功）")
    lines.append("")
    lines.append("| 前缀 | 含义 | chs 条目数 | en 条目数 | en 完整度 |")
    lines.append("| --- | --- | --- | --- | --- |")

    all_namespaces = sorted(set(chs_grouped.keys()) | set(en_grouped.keys()))
    for ns in all_namespaces:
        meaning = NAMESPACE_MEANING.get(ns, "未定义")
        chs_count = len(chs_grouped.get(ns, {}))
        en_count = len(en_grouped.get(ns, {}))
        if en_count == 0:
            completeness = "❌ en 完全缺失"
        elif en_count < chs_count:
            completeness = f"⚠️ en 部分缺失（缺 {chs_count - en_count} 条）"
        else:
            completeness = "✅ 完整"
        lines.append(f"| `{ns}.*` | {meaning} | {chs_count} | {en_count} | {completeness} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 二、易误读词审校清单（W1.1 第 5 条）")
    lines.append("")
    lines.append("以下词汇需人工审校，避免文化误读：")
    lines.append("")
    lines.append("| 待审校词 | 审校要点 |")
    lines.append("| --- | --- |")
    for word, note in REVIEW_FOCUS.items():
        lines.append(f"| {word} | {note} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 各命名空间详情
    lines.append("## 三、各命名空间候选词详情")
    lines.append("")
    lines.append(
        "> 每个命名空间列出：key、中文源词、6tail 英文候选、"
        "产品英文候选（待人工填写）、使用场景、是否可直接用于 UI、风险备注。"
    )
    lines.append("> - **产品英文候选**：留空表示沿用 6tail 候选；填入表示建议替换。")
    lines.append(
        "> - **是否可直接用于 UI**：✅ 可直接用 / ⚠️ 需审校 / ❌ 不建议（将回退到中文或需重译）。"
    )
    lines.append("")

    for ns in all_namespaces:
        meaning = NAMESPACE_MEANING.get(ns, "未定义")
        chs_items = chs_grouped.get(ns, {})
        en_items = en_grouped.get(ns, {})

        lines.append(f"### `{ns}.*` — {meaning}")
        lines.append("")
        lines.append(
            "| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | "
            "使用场景 | 可直接用于 UI | 风险备注 |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")

        for key in sorted(chs_items.keys()):
            chs_val = chs_items[key]
            en_val = en_items.get(key, "")
            if en_val:
                ui_flag = "⚠️ 需审校"
                risk = ""
            else:
                ui_flag = "❌ 缺失（回退中文）"
                risk = "en 未翻译，运行时回退到中文"

            lines.append(f"| `{key}` | {chs_val} | {en_val} |  |  | {ui_flag} | {risk} |")

        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 四、en 完全缺失的命名空间（需补译）")
    lines.append("")
    lines.append("以下 6 个命名空间 en 完全缺失，运行时回退到中文显示，需补译：")
    lines.append("")
    missing_ns = [
        ns
        for ns in all_namespaces
        if len(en_grouped.get(ns, {})) == 0 and len(chs_grouped.get(ns, {})) > 0
    ]
    if missing_ns:
        lines.append("| 前缀 | 含义 | chs 条目数 | 补译优先级 |")
        lines.append("| --- | --- | --- | --- |")
        for ns in missing_ns:
            meaning = NAMESPACE_MEANING.get(ns, "未定义")
            chs_count = len(chs_grouped.get(ns, {}))
            # 补译优先级：黄历核心（d/m 农历日月）高，其他低
            priority = "高" if ns in ("d", "m") else "中" if ns == "ss" else "低"
            lines.append(f"| `{ns}.*` | {meaning} | {chs_count} | {priority} |")
    else:
        lines.append("（无）")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 五、彭祖百忌说明")
    lines.append("")
    lines.append(
        "彭祖百忌不在 I18n messages 里，而在 "
        "`_arrays.LunarUtil.PENGZU_GAN` 和 `PENGZU_ZHI` 数组中"
        "（lunar.js 行 8260-8261），通过 `{tg.jia}` 等占位符引用 messages，"
        "由 `_updateArray` 渲染。"
    )
    lines.append("")
    lines.append(
        "若需抽取彭祖百忌英文候选，需单独解析这两个数组"
        "（本草稿暂不覆盖，待 W5 黄历后端实施时按需处理）。"
    )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 六、参考来源")
    lines.append("")
    lines.append("- `frontend/static/js/lunar.js` 行 6876-8471（I18n 模块）")
    lines.append("- `docs/plans/2026-06-27-english-site-execution-plan.md` W1.1 任务定义")
    lines.append("- `docs/business/wise-oracle-cultural-expression-guide.md` D6 神煞翻译策略")
    lines.append("- `docs/business/huangli-english-localization-guidance.md` 黄历英文指导")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """主函数：读取 lunar.js，抽取 messages，生成 markdown 草稿。"""
    if not LUNAR_JS.exists():
        raise FileNotFoundError(f"未找到 {LUNAR_JS}")

    content = LUNAR_JS.read_text(encoding="utf-8")
    print(f"读取 lunar.js：{len(content)} 字符")

    chs_messages = extract_messages_block(content, "chs")
    en_messages = extract_messages_block(content, "en")
    print(f"chs messages：{len(chs_messages)} 条")
    print(f"en messages：{len(en_messages)} 条")

    chs_grouped = group_by_namespace(chs_messages)
    en_grouped = group_by_namespace(en_messages)
    print(f"chs 命名空间数：{len(chs_grouped)}")
    print(f"en 命名空间数：{len(en_grouped)}")

    markdown = render_markdown(chs_grouped, en_grouped)

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    print(f"输出：{OUTPUT_MD}")
    print(f"输出大小：{len(markdown)} 字符")


if __name__ == "__main__":
    main()
