"""
扫描 _review_log/ 与 scripts/，自动生成英文签文审查进度看板。

用途：
  让用户一眼看清"我搞到哪一签了"，避免反复核对文件名。

推断逻辑（基于现有文件，非侵入式）：
  1. 扫描 data/content/_review_log/gemini_review_result_signs_*.md
     → 提取签号范围 → 标记为"Gemini 已审查"
  2. 扫描 data/content/_review_log/adjudication_sign_*.md
     → 提取签号 → 标记为"已有单签综合评定记录"（优先级最高）
  3. 扫描 scripts/apply_review_fixes_signs_*.py
     → 提取签号范围 → 标记为"apply 脚本照搬 Gemini（未经大模型综合评定）"
  4. Gemini 已审查的签：
     - 有 adjudication 记录 → "大模型综合审定（定稿）"
     - 无 adjudication 记录但有 apply 脚本 → "apply 脚本照搬（待复审）"
     - 其他 → "大模型综合审定（定稿）"（保留原推断）
  5. 其余 → "未审查"

输出：
  - data/content/_review_log/review_status.md   (人读看板)
  - data/content/_review_log/review_status.json (机读)

使用：
  python scripts/sync_review_status.py

注意：
  本脚本只读不改原数据。可随时安全重跑。
  13-44 标记为"待复审定稿"是已知欠债，需大模型回头补审。
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 项目根目录（脚本位于 <root>/scripts/，故取上一级）
ROOT = Path(__file__).resolve().parent.parent
REVIEW_LOG = ROOT / "data" / "content" / "_review_log"
SCRIPTS_DIR = ROOT / "scripts"

OUTPUT_MD = REVIEW_LOG / "review_status.md"
OUTPUT_JSON = REVIEW_LOG / "review_status.json"

# 补译签记录文件
RETRANSLATED_FILE = REVIEW_LOG / "retranslated_signs.json"

# 总签数（诸葛神算共 384 签）
TOTAL_SIGNS = 384

# 单批建议条数（用于"剩余批次规划"小节，可调整）
SUGGESTED_BATCH_SIZE = 12

# 从文件名提取签号范围，兼容三种命名：
#   signs_1_4    (下划线)
#   signs_13-32  (连字符)
#   signs_33_44  (下划线)
RANGE_RE = re.compile(r"signs[_\-]?(\d+)[_\-](\d+)")


def parse_range(filename: str):
    """从文件名提取签号范围。返回 (start, end) 或 None。"""
    m = RANGE_RE.search(filename)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return (min(a, b), max(a, b))


def scan_gemini_reviews():
    """扫描 Gemini 审查结果 md 文件。返回 [(start, end, filename), ...]。"""
    results = []
    if not REVIEW_LOG.exists():
        return results
    for p in sorted(REVIEW_LOG.glob("gemini_review_result_signs_*.md")):
        r = parse_range(p.name)
        if r:
            results.append((r[0], r[1], p.name))
    return results


def scan_apply_scripts():
    """扫描 apply 脚本。返回 [(start, end, filename), ...]。"""
    results = []
    if not SCRIPTS_DIR.exists():
        return results
    for p in sorted(SCRIPTS_DIR.glob("apply_review_fixes_signs_*.py")):
        r = parse_range(p.name)
        if r:
            results.append((r[0], r[1], p.name))
    return results


def scan_adjudication_records():
    """
    扫描单签综合评定记录文件 adjudication_sign_<N>.md。
    返回已存在评定记录的签号集合 {sign_number, ...}。
    优先级高于 apply 脚本：有 adjudication 记录的签视为大模型综合审定。
    """
    results = set()
    if not REVIEW_LOG.exists():
        return results
    pattern = re.compile(r"adjudication_sign_(\d+)\.md$")
    for p in REVIEW_LOG.glob("adjudication_sign_*.md"):
        m = pattern.search(p.name)
        if m:
            results.add(int(m.group(1)))
    return results


def load_retranslated_signs():
    """加载补译签记录。返回 {sign_number: reason} 字典，文件不存在则空字典。"""
    if not RETRANSLATED_FILE.exists():
        return {}
    try:
        data = json.loads(RETRANSLATED_FILE.read_text(encoding="utf-8"))
        return {
            item["sign_number"]: item.get("reason", "")
            for item in data.get("retranslated_signs", [])
        }
    except (json.JSONDecodeError, KeyError):
        return {}


def build_sign_status(gemini_batches, apply_batches, adjudication_signs):
    """
    构建每签的状态字典。
    返回 {sign_number: {"gemini_reviewed": bool, "finalized_method": str|None,
    "batch_file": str|None}}。
    finalized_method 取值：
      - "manual_llm_review"  大模型综合审定（有 adjudication 记录或无 apply 脚本）
      - "applied_via_script" apply 脚本照搬 Gemini（待复审）
      - None                 未定稿

    判定优先级（针对已 Gemini 审查的签）：
      1. 有 adjudication_sign_<N>.md → manual_llm_review（最高优先级）
      2. 在 apply 脚本范围内且无 adjudication 记录 → applied_via_script
      3. 其他 → manual_llm_review（保留原推断）
    """
    status = {
        n: {"gemini_reviewed": False, "finalized_method": None, "batch_file": None}
        for n in range(1, TOTAL_SIGNS + 1)
    }

    # 先标记 Gemini 已审查的，默认推断为"大模型综合审定"
    for start, end, fname in gemini_batches:
        for n in range(start, end + 1):
            if n in status:
                status[n]["gemini_reviewed"] = True
                status[n]["batch_file"] = fname
                status[n]["finalized_method"] = "manual_llm_review"

    # 用 apply 脚本覆盖：有 apply 脚本的批次 = 照搬，待复审
    for start, end, _fname in apply_batches:
        for n in range(start, end + 1):
            if n in status and status[n]["gemini_reviewed"]:
                status[n]["finalized_method"] = "applied_via_script"

    # 最终覆盖：有 adjudication 记录的签 → 大模型综合审定（最高优先级）
    # 这一步修正历史欠债：13-32 曾用 apply 脚本照搬，后已补做单签综合评定
    for n in adjudication_signs:
        if n in status and status[n]["gemini_reviewed"]:
            status[n]["finalized_method"] = "manual_llm_review"

    return status


def find_gaps(status):
    """找出未审查的连续区间。返回 [(start, end), ...]。"""
    gaps = []
    cur_start = None
    for n in range(1, TOTAL_SIGNS + 1):
        if not status[n]["gemini_reviewed"]:
            if cur_start is None:
                cur_start = n
            cur_end = n
        else:
            if cur_start is not None:
                gaps.append((cur_start, cur_end))
                cur_start = None
    if cur_start is not None:
        gaps.append((cur_start, cur_end))
    return gaps


def render_markdown(status, gemini_batches, apply_batches):
    """渲染人读看板。"""
    lines = []
    lines.append("# 诸葛神算英文签文审查进度看板")
    lines.append("")
    lines.append("> 自动生成，请勿手工编辑。运行 `python scripts/sync_review_status.py` 刷新。")
    lines.append(f"> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # 统计
    gemini_reviewed = sum(1 for s in status.values() if s["gemini_reviewed"])
    manual_review = sum(1 for s in status.values() if s["finalized_method"] == "manual_llm_review")
    via_script = sum(1 for s in status.values() if s["finalized_method"] == "applied_via_script")
    pending = TOTAL_SIGNS - gemini_reviewed

    # 补译签
    retranslated = load_retranslated_signs()
    retranslated_nums = sorted(retranslated.keys())

    lines.append("## 总览")
    lines.append("")
    lines.append(f"- 总签数：**{TOTAL_SIGNS}**")
    lines.append(
        f"- 已 Gemini 审查：**{gemini_reviewed}** ({gemini_reviewed * 100 // TOTAL_SIGNS}%)"
    )
    lines.append(f"  - 大模型综合审定（定稿）：**{manual_review}**")
    lines.append(f"  - apply 脚本照搬 Gemini（[待复审]）：**{via_script}**")
    lines.append(f"- 未审查：**{pending}** ({pending * 100 // TOTAL_SIGNS}%)")
    if retranslated_nums:
        lines.append(f"- 补译签：**{len(retranslated_nums)}** 签（因中文考据修正后重译）")
        lines.append(f"  - 签号：{', '.join(str(n) for n in retranslated_nums)}")
        lines.append("  - 详见：`data/content/_review_log/retranslated_signs.json`")
    lines.append("")

    # 下一批起点
    next_start = None
    for n in range(1, TOTAL_SIGNS + 1):
        if not status[n]["gemini_reviewed"]:
            next_start = n
            break
    if next_start:
        lines.append(f"- 下一批应从：**第 {next_start} 签** 开始")
    lines.append("")

    # 各批状态表
    lines.append("## 各批状态")
    lines.append("")
    lines.append("| 批次文件 | 签号范围 | 条数 | Gemini审查 | 定稿方式 | 状态 |")
    lines.append("|---|---|---|---|---|---|")

    all_batches = sorted(gemini_batches, key=lambda x: x[0])
    for start, end, fname in all_batches:
        count = end - start + 1
        methods = set(status[n]["finalized_method"] for n in range(start, end + 1))
        if methods == {"manual_llm_review"}:
            method = "大模型综合审定"
            state = "[定稿]"
        elif methods == {"applied_via_script"}:
            method = "apply脚本照搬Gemini"
            state = "[待复审]"
        elif "applied_via_script" in methods and "manual_llm_review" in methods:
            method = "混合"
            state = "[部分待复审]"
        else:
            method = "—"
            state = "[待审查]"
        lines.append(f"| `{fname}` | {start}-{end} | {count} | 是 | {method} | {state} |")

    # 未审查区间
    gaps = find_gaps(status)
    for gs, ge in gaps:
        count = ge - gs + 1
        lines.append(f"| — | {gs}-{ge} | {count} | 否 | — | [待审查] |")

    lines.append("")

    # 剩余批次规划
    if pending > 0 and next_start:
        lines.append(f"## 剩余批次规划（每批 {SUGGESTED_BATCH_SIZE} 签，自动）")
        lines.append("")
        lines.append("| 批次序号 | 签号范围 | 条数 |")
        lines.append("|---|---|---|")
        batch_no = 1
        cur = next_start
        while cur <= TOTAL_SIGNS:
            end = min(cur + SUGGESTED_BATCH_SIZE - 1, TOTAL_SIGNS)
            count = end - cur + 1
            lines.append(f"| {batch_no} | {cur}-{end} | {count} |")
            cur = end + 1
            batch_no += 1
        total_batches = batch_no - 1
        lines.append(f"\n共 **{total_batches}** 批待审查。")
        lines.append("")

    # 流程说明
    lines.append("## 流程说明")
    lines.append("")
    lines.append("### 正确流程（每批必走）")
    lines.append(
        "1. **生成 Gemini prompt**："
        "`python scripts/build_gemini_review_prompt.py --start 起 --limit 批大小`"
    )
    lines.append("2. **贴入 Gemini 审查**：用户把 prompt 贴入 Gemini Studio，拿到审查意见")
    lines.append(
        "3. **保存审查结果**：用户把 Gemini 输出存为 "
        "`data/content/_review_log/gemini_review_result_signs_起-止.md`"
    )
    lines.append("4. **大模型综合评定**（核心步骤，不可跳过）：")
    lines.append(
        "   - 输入：中文原文(reinterpreted.json) + DeepSeek 原译(当前 en.json) + Gemini 意见(md)"
    )
    lines.append("   - 逐条判断：接受 Gemini 意见 / 否决 Gemini 误判 / 提出第三种更优译法")
    lines.append("   - 形成定稿后**直接修改 `oracle_signs_en.json`**")
    lines.append("5. **刷新看板**：`python scripts/sync_review_status.py`")
    lines.append("")
    lines.append("### 大模型综合评定检查清单（每签必查）")
    lines.append("")
    lines.append("**核心原则**：纠偏 Gemini 的过度审查，而非扩大审查范围。")
    lines.append("Gemini 有神经质敏感倾向（曾禁用 `with` 这种常见词），")
    lines.append("大模型评定时需主动否决此类过度审查。")
    lines.append("")
    lines.append("- [ ] 禁止词（仅这些是硬禁止）：`destiny` / `Li Ge` / `heal`(作动词表确定疗效)")
    lines.append("- [ ] `fortune` / `gua_type` 字段必须剔除（不翻译这两项）")
    lines.append(
        "- [ ] 禁止绝对化预测：`will improve` / `will fail` 等（但保留诗句中 `fate` 等文学表达）"
    )
    lines.append("- [ ] sign_text 必须 4 行结构")
    lines.append(
        "- [ ] 字段完整：sign_number/sign_text/interpretation1/career/wealth/"
        "love/health/study/general 共 9 字段"
    )
    lines.append("- [ ] 英文不含中文字符")
    lines.append("")
    lines.append("### 非自动禁止项（按上下文判断，勿过度审查）")
    lines.append("- `supremely favorable` / `extremely favorable` 等副词堆叠：")
    lines.append('  - **不是禁止词**。原文为吉签时（如"终有庆也"）使用是合理的')
    lines.append("  - 仅当原文非吉签却译成 highly favorable 时才需复核")
    lines.append("  - 曾误把 supremely favorable 列为禁止词并改第34签，已回退(2026-07-07)")
    lines.append("- `fate` 在诗句中：文学表达，保留")
    lines.append("- `with` 等常见词：Gemini 曾误禁，大模型须主动否决")
    lines.append("")
    lines.append("### 禁止行为")
    lines.append("- **禁止写 `apply_review_fixes_*.py` 脚本机械照搬 Gemini 意见**")
    lines.append("  - 13-32、33-44 两批曾犯此错，标记为「待复审」欠债")
    lines.append("  - 大模型必须逐条做综合判断，不可只做搬运工")
    lines.append("")
    lines.append("### 已知欠债")
    lines.append("- **13-32 批**曾通过 apply 脚本照搬 Gemini，后已补做单签综合评定（2026-07-08）")
    lines.append("  - 13-32 共 20 签均已生成 `adjudication_sign_<N>.md`，视为已定稿")
    lines.append("  - 残留的 `apply_review_fixes_signs_13_32.py` 仅作历史记录，不影响状态判定")
    lines.append("- 从第 45 签起，回归正确流程")
    lines.append("")
    lines.append("### 状态推断依据")
    lines.append(
        "- `大模型综合审定`：Gemini 审查文件存在 + 有 `adjudication_sign_<N>.md`（或无 apply 脚本）"
    )
    lines.append(
        "- `apply脚本照搬Gemini`：存在 `apply_review_fixes_signs_*.py` 文件"
        "且无对应 adjudication 记录"
    )
    lines.append("- 判定优先级：adjudication 记录 > apply 脚本 > 默认推断")
    lines.append(
        "- 若需精确追踪（含审定时间/审定者），需给 `oracle_signs_en.json` 每签加审计字段，"
    )
    lines.append("  属后续优化，不在本脚本范围。")
    lines.append("")

    return "\n".join(lines)


def build_json(status, gemini_batches, apply_batches):
    """构建机读 JSON。"""
    gemini_reviewed = sum(1 for s in status.values() if s["gemini_reviewed"])
    manual_review = sum(1 for s in status.values() if s["finalized_method"] == "manual_llm_review")
    via_script = sum(1 for s in status.values() if s["finalized_method"] == "applied_via_script")
    pending = TOTAL_SIGNS - gemini_reviewed

    next_start = None
    for n in range(1, TOTAL_SIGNS + 1):
        if not status[n]["gemini_reviewed"]:
            next_start = n
            break

    batches_info = []
    for start, end, fname in sorted(gemini_batches, key=lambda x: x[0]):
        methods = set(status[n]["finalized_method"] for n in range(start, end + 1))
        if methods == {"manual_llm_review"}:
            method = "manual_llm_review"
        elif methods == {"applied_via_script"}:
            method = "applied_via_script"
        elif methods:
            method = "mixed"
        else:
            method = None
        batches_info.append(
            {
                "start": start,
                "end": end,
                "count": end - start + 1,
                "file": fname,
                "finalized_method": method,
            }
        )

    return {
        "total_signs": TOTAL_SIGNS,
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "gemini_reviewed": gemini_reviewed,
            "manual_llm_review": manual_review,
            "applied_via_script": via_script,
            "pending": pending,
            "progress_percent": gemini_reviewed * 100 // TOTAL_SIGNS,
        },
        "next_unreviewed_start": next_start,
        "batches": batches_info,
        "unreviewed_gaps": find_gaps(status),
    }


def main():
    if not REVIEW_LOG.exists():
        print(f"[错误] 审查日志目录不存在：{REVIEW_LOG}", file=sys.stderr)
        sys.exit(1)

    gemini_batches = scan_gemini_reviews()
    apply_batches = scan_apply_scripts()
    adjudication_signs = scan_adjudication_records()
    status = build_sign_status(gemini_batches, apply_batches, adjudication_signs)

    md = render_markdown(status, gemini_batches, apply_batches)
    OUTPUT_MD.write_text(md, encoding="utf-8")

    data = build_json(status, gemini_batches, apply_batches)
    OUTPUT_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 控制台摘要
    print(f"状态看板已生成：{OUTPUT_MD}")
    print(f"状态 JSON 已生成：{OUTPUT_JSON}")
    print()
    print(f"总签数：{TOTAL_SIGNS}")
    print(
        f"已 Gemini 审查：{data['summary']['gemini_reviewed']} "
        f"({data['summary']['progress_percent']}%)"
    )
    print(f"  - 大模型综合审定：{data['summary']['manual_llm_review']}")
    print(f"  - apply脚本照搬（待复审）：{data['summary']['applied_via_script']}")
    print(f"未审查：{data['summary']['pending']}")
    if data["next_unreviewed_start"]:
        print(f"下一批应从：第 {data['next_unreviewed_start']} 签开始")
    if data["summary"]["applied_via_script"] > 0:
        print(
            f"\n已知欠债：仍有 {data['summary']['applied_via_script']} "
            "签为脚本照搬 Gemini，未经大模型综合评定。"
        )
    else:
        print("\n所有已 Gemini 审查的签均已完成大模型综合审定，无历史欠债。")


if __name__ == "__main__":
    main()
