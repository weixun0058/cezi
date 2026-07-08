"""单签复检完整流程脚本

用途：对指定签号重新生成中文解读 + 重新翻译英文 + 生成 Gemini 审查 prompt
      + DeepSeek 综合评定（自动应用修改到 en.json）。
      一口气跑完（Gemini 审查步骤除外，需用户手动）。

权威文件（源头，脚本直接读写这些文件）：
- 中文签文：data/reference/oracle_signs_authoritative_sc.csv（仅 sign_number + sign_text）
- 中文解读：data/content/oracle_signs_reinterpreted.json（DeepSeek 生成的解读）
- 英文翻译：data/content/oracle_signs_en.json（DeepSeek 翻译的英文）

非权威（派生物，由 backfill 从权威文件同步）：
- reference.db（数据库，不作为本流程的数据源）

完整流程（步骤 1-8 脚本自动完成，4-5 手动）：
1. 从权威 CSV 读 sign_text（最权威源头）
2. 从 reinterpreted.json 读 fortune/gua_type（保持一致，不改）
3. 调 DeepSeek（interpreter_system_prompt.md）生成 7 个中文解读字段
4. 覆盖写入 reinterpreted.json（按 sign_number 去重）
5. 调 DeepSeek（translator_system_prompt.md）翻译为英文（仅 9 字段，不含 fortune/gua_type）
6. 覆盖写入 en.json（按 sign_number 去重）
7. 生成 Gemini 审查 prompt 文件：_review_log/gemini_review_prompt_sign_{N}.md

后续手动步骤：
8. 把 prompt 贴入 Gemini Studio，拿到审查意见
9. 把结果存为 _review_log/gemini_review_result_sign_{N}.md

自动步骤（--resume 时自动执行）：
10. 调 DeepSeek（adjudicator_system_prompt.md）做综合评定
11. 根据 DeepSeek 评定结果，自动修改 en.json
12. 生成评定记录：_review_log/adjudication_sign_{N}.md

挂起条件（交用户评判）：
- 无 Gemini 审查结果文件 → 挂起，提示用户先做 Gemini 审查
- DeepSeek 评定返回 pending_user_review → 挂起，交用户评判

使用方式：
  # 完整流程（从零开始，步骤 1-7）
  python scripts/reprocess_single_sign.py --sign 142

  # 续跑模式（判别进度，从断点继续，自动执行步骤 10-12）
  python scripts/reprocess_single_sign.py --sign 142 --resume

设计原则：
- 数据源是权威文件，不是数据库
- 每步有日志输出，便于排查
- 复用现有模块的核心函数（API 调用、JSON 解析、输出写入）
- 进度可判别：根据现有文件判断当前状态，--resume 时自动跳过已完成步骤
"""

import argparse
import csv
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# 确保能 import 同目录下的模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

# 复用现有模块的核心函数
from reinterpret_oracle_signs import (
    call_deepseek as call_deepseek_for_interpretation,
    parse_interpretation,
    load_api_key,
    load_system_prompt as load_interpreter_prompt,
    build_user_message as build_interpretation_message,
)
from translate_oracle_signs import (
    call_deepseek as call_deepseek_for_translation,
    parse_translation_response,
    write_output,
    load_system_prompt as load_translator_prompt,
    build_translate_message,
    append_run_log,
)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger("reprocess_single_sign")

# 权威文件路径（脚本直接读写这些文件，不经过数据库）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE_CSV = PROJECT_ROOT / "data" / "reference" / "oracle_signs_authoritative_sc.csv"
REINTERPRETED_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_reinterpreted.json"
EN_JSON = PROJECT_ROOT / "data" / "content" / "oracle_signs_en.json"
REVIEW_LOG_DIR = PROJECT_ROOT / "data" / "content" / "_review_log"


def load_sign_text_from_csv(sign_number):
    """从权威 CSV 读取指定签号的 sign_text。

    Args:
        sign_number: 签号

    Returns:
        str: sign_text

    Raises:
        SystemExit: 签号不存在时退出。
    """
    if not AUTHORITATIVE_CSV.exists():
        LOGGER.error("权威 CSV 不存在：%s", AUTHORITATIVE_CSV)
        raise SystemExit(1)

    # 注意：用 utf-8-sig 编码读取，自动去除可能的 BOM（字节顺序标记）
    with AUTHORITATIVE_CSV.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["sign_number"]) == sign_number:
                LOGGER.info("从权威 CSV 读取第 %d 签 sign_text：%s",
                            sign_number, row["sign_text"][:30] + "...")
                return row["sign_text"]

    LOGGER.error("签号 %d 在权威 CSV 中不存在", sign_number)
    raise SystemExit(1)


def load_fortune_gua_type(sign_number):
    """从 reinterpreted.json 读取指定签号的 fortune/gua_type。

    这两个字段是历史遗留的元数据（英文版不展示），仅用于 DeepSeek 解读时参考。
    保持与现有内容一致，不修改。

    Args:
        sign_number: 签号

    Returns:
        tuple: (fortune, gua_type)

    Raises:
        SystemExit: 签号不存在时退出。
    """
    if not REINTERPRETED_JSON.exists():
        LOGGER.error("reinterpreted.json 不存在：%s", REINTERPRETED_JSON)
        raise SystemExit(1)

    data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))
    for s in data:
        if s["sign_number"] == sign_number:
            fortune = s.get("fortune", "")
            gua_type = s.get("gua_type", "")
            LOGGER.info("从 reinterpreted.json 读取第 %d 签 fortune=%s, gua_type=%s",
                        sign_number, fortune, gua_type)
            return fortune, gua_type

    LOGGER.error("签号 %d 在 reinterpreted.json 中不存在", sign_number)
    raise SystemExit(1)


def step1_2_load_authoritative_sign(sign_number):
    """步骤 1-2：从权威源读取签文数据。

    - sign_text 从权威 CSV 读取（最权威源头）
    - fortune/gua_type 从 reinterpreted.json 读取（历史元数据，不改）

    Args:
        sign_number: 签号

    Returns:
        dict: 含 sign_number/fortune/gua_type/sign_text
    """
    LOGGER.info("=" * 60)
    LOGGER.info("步骤 1-2：从权威源读取第 %d 签数据", sign_number)
    LOGGER.info("=" * 60)

    sign_text = load_sign_text_from_csv(sign_number)
    fortune, gua_type = load_fortune_gua_type(sign_number)

    sign = {
        "sign_number": sign_number,
        "fortune": fortune,
        "gua_type": gua_type,
        "sign_text": sign_text,
    }
    LOGGER.info("签文数据准备完成：%s", sign["sign_text"][:50] + "...")
    return sign


def step3_4_regenerate_chinese(sign, api_key, system_prompt):
    """步骤 3-4：调 DeepSeek 重新生成中文解读 + 覆盖写入 reinterpreted.json。

    Args:
        sign: 签文数据（含 sign_number/fortune/gua_type/sign_text）
        api_key: DeepSeek API key
        system_prompt: interpreter 系统提示词

    Returns:
        dict: 含 7 个解读字段（interpretation1/career/wealth/love/health/study/general）

    Raises:
        SystemExit: API 调用失败或解析失败时退出。
    """
    sign_number = sign["sign_number"]
    LOGGER.info("=" * 60)
    LOGGER.info("步骤 3-4：重新生成第 %d 签中文解读", sign_number)
    LOGGER.info("=" * 60)

    # 步骤 3：调 DeepSeek 生成解读
    user_message = build_interpretation_message(sign)
    LOGGER.info("调用 DeepSeek（interpreter）生成中文解读...")
    content = call_deepseek_for_interpretation(api_key, system_prompt, user_message)
    LOGGER.info("API 返回 %d 字符", len(content))

    interpretation = parse_interpretation(content)
    total_chars = sum(len(v) for v in interpretation.values())
    LOGGER.info("中文解读生成成功（共 %d 字）", total_chars)

    # 步骤 4：覆盖写入 reinterpreted.json
    LOGGER.info("覆盖写入 reinterpreted.json...")
    data = json.loads(REINTERPRETED_JSON.read_text(encoding="utf-8"))

    new_entry = {
        "sign_number": sign_number,
        "fortune": sign["fortune"],
        "gua_type": sign["gua_type"],
        "sign_text": sign["sign_text"],
        **interpretation,
    }

    # 按 sign_number 去重合并（覆盖旧条目）
    found = False
    for i, s in enumerate(data):
        if s["sign_number"] == sign_number:
            data[i] = new_entry
            found = True
            LOGGER.info("覆盖第 %d 签旧条目", sign_number)
            break
    if not found:
        data.append(new_entry)
        data.sort(key=lambda x: x["sign_number"])
        LOGGER.info("新增第 %d 签条目", sign_number)

    REINTERPRETED_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    LOGGER.info("reinterpreted.json 已更新")

    return interpretation


def step5_6_translate_to_english(sign, interpretation, api_key, system_prompt):
    """步骤 5-6：调 DeepSeek 翻译英文 + 覆盖写入 en.json。

    翻译输入仅含 9 字段（sign_number + sign_text + 7 个解读字段），
    不含 fortune/gua_type（英文版不展示这两项）。

    Args:
        sign: 签文数据（含 sign_number/fortune/gua_type/sign_text）
        interpretation: 7 个中文解读字段
        api_key: DeepSeek API key
        system_prompt: translator 系统提示词

    Returns:
        dict: 英文翻译结果（9 字段）

    Raises:
        SystemExit: API 调用失败或解析失败时退出。
    """
    sign_number = sign["sign_number"]
    LOGGER.info("=" * 60)
    LOGGER.info("步骤 5-6：翻译第 %d 签为英文", sign_number)
    LOGGER.info("=" * 60)

    # 构建翻译输入（仅 9 字段，不含 fortune/gua_type）
    translate_input = {
        "sign_number": sign_number,
        "sign_text": sign["sign_text"],
        **interpretation,
    }

    # 步骤 5：调 DeepSeek 翻译
    batch_signs = [translate_input]  # 单签，包装为列表
    user_message = build_translate_message(batch_signs)
    LOGGER.info("调用 DeepSeek（translator）翻译为英文...")
    content = call_deepseek_for_translation(api_key, system_prompt, user_message)
    LOGGER.info("API 返回 %d 字符", len(content))

    translations = parse_translation_response(content, expected_count=1)
    en_result = translations[0]
    LOGGER.info("英文翻译成功（sign_text 开头：%s...）",
                en_result.get("sign_text", "")[:50])

    # 步骤 6：覆盖写入 en.json（复用 write_output 的去重合并逻辑）
    LOGGER.info("覆盖写入 oracle_signs_en.json...")
    source_signs = [translate_input]  # 用于日志记录
    write_output(translations, source_signs)
    LOGGER.info("oracle_signs_en.json 已更新")

    # 记录翻译日志
    append_run_log(sign_number, "success")

    return en_result


def step7_generate_gemini_prompt(sign, interpretation, en_result):
    """步骤 7：生成 Gemini 审查 prompt 文件。

    委托给 gemini_prompt_builder 模块构建 prompt 文本，本函数只负责保存文件。

    Args:
        sign: 签文数据（含 sign_number/fortune/gua_type/sign_text）
        interpretation: 7 个中文解读字段
        en_result: 英文翻译结果（9 字段）

    Returns:
        Path: 生成的 prompt 文件路径
    """
    sign_number = sign["sign_number"]
    LOGGER.info("=" * 60)
    LOGGER.info("步骤 7：生成第 %d 签 Gemini 审查 prompt", sign_number)
    LOGGER.info("=" * 60)

    # 委托给共享模块构建 prompt 文本
    prompt_text = build_single_sign_prompt(
        sign_number=sign_number,
        cn_sign=interpretation,  # interpretation 含 7 个解读字段
        en_sign=en_result,
        fortune=sign["fortune"],
        gua_type=sign["gua_type"],
    )

    # 保存到文件
    REVIEW_LOG_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = REVIEW_LOG_DIR / f"gemini_review_prompt_sign_{sign_number}.md"
    prompt_file.write_text(prompt_text, encoding="utf-8")
    LOGGER.info("Gemini 审查 prompt 已生成：%s", prompt_file)

    return prompt_file


# ============================================================================
# 步骤 8-10：DeepSeek 综合评定（委托给 adjudicate_single_sign 模块）
# ============================================================================

from adjudicate_single_sign import (
    adjudicate as run_deepseek_adjudication,
    detect_review_status as detect_adjudication_status,
    load_sign_from_json as load_sign_from_existing_json,
)
from gemini_prompt_builder import build_single_sign_prompt


def main():
    parser = argparse.ArgumentParser(
        description="单签复检完整流程（重新生成中文解读 + 翻译英文 + 生成 Gemini prompt + DeepSeek 综合评定）"
    )
    parser.add_argument(
        "--sign", type=int, required=True,
        help="要复检的签号（如 --sign 142）"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="续跑模式：检测当前进度，从断点继续。"
             "若 Gemini 审查结果已存在，自动执行 DeepSeek 综合评定。"
             "若已定稿（adjudication 文件存在），则跳过。"
    )
    args = parser.parse_args()

    sign_number = args.sign
    LOGGER.info("#" * 60)
    LOGGER.info("# 单签复检完整流程启动")
    LOGGER.info("# 签号：第 %d 签", sign_number)
    if args.resume:
        LOGGER.info("# 模式：续跑（--resume）")
    LOGGER.info("#" * 60)

    start_time = time.time()

    # --resume 模式：先检测进度
    if args.resume:
        review_status = detect_adjudication_status(sign_number)
        status = review_status["status"]
        LOGGER.info("当前进度状态：%s", status)
        LOGGER.info("  Gemini 审查文件：%s",
                    review_status["gemini_file"].name if review_status["gemini_file"] else "无")
        LOGGER.info("  评定记录文件：%s",
                    review_status["adjudication_file"].name if review_status["adjudication_file"] else "无")

        if status == "finalized":
            LOGGER.info("第 %d 签已定稿（adjudication 文件已存在），无需继续。", sign_number)
            LOGGER.info("如需重新评定，请删除对应的 adjudication 文件后再运行。")
            return

        if status == "pending_gemini_review":
            LOGGER.warning("Gemini 审查结果文件不存在，无法做综合评定。")
            LOGGER.info("请按以下步骤操作：")
            if review_status["prompt_file"]:
                LOGGER.info("  1. Gemini prompt 已生成：%s", review_status["prompt_file"])
            else:
                LOGGER.info("  1. 先运行不带 --resume 的命令生成 Gemini prompt")
            LOGGER.info("  2. 把 prompt 贴入 Gemini Studio 审查")
            LOGGER.info("  3. 结果存为：data/content/_review_log/gemini_review_result_sign_%d.md", sign_number)
            LOGGER.info("  4. 重新运行：python scripts/reprocess_single_sign.py --sign %d --resume", sign_number)
            return

        # status == "pending_adjudication"：Gemini 审查已完成，可以继续评定
        LOGGER.info("Gemini 审查已完成，开始 DeepSeek 综合评定...")

        # 加载 API key
        api_key = load_api_key()

        # 从现有 JSON 加载数据（跳过步骤 1-7）
        sign, interpretation, en_result = load_sign_from_existing_json(sign_number)

        # 步骤 8-10：DeepSeek 综合评定（委托给 adjudicate_single_sign 模块）
        result = run_deepseek_adjudication(sign_number, api_key,
                                           sign, interpretation, en_result)

        elapsed = time.time() - start_time
        LOGGER.info("#" * 60)
        LOGGER.info("# 续跑流程完成")
        LOGGER.info("# 总耗时：%.1f 秒", elapsed)
        LOGGER.info("#" * 60)
        LOGGER.info("")
        LOGGER.info("评定结果：")
        LOGGER.info("  状态：%s", result["status"])
        if result["modified_fields"]:
            LOGGER.info("  已修改字段：%s", ", ".join(result["modified_fields"]))
        if result["record_file"]:
            LOGGER.info("  评定记录：%s", result["record_file"])
        LOGGER.info("")
        LOGGER.info("说明：%s", result["message"])

        if result["status"] == "pending_user_review":
            LOGGER.info("")
            LOGGER.info("该签已挂起，请用户评判后决定下一步。")
        elif result["status"] == "finalized":
            LOGGER.info("")
            LOGGER.info("该签已定稿。如需同步数据库，请运行 backfill_reinterpreted_to_db.py")
        return

    # 非 --resume 模式：执行完整流程（步骤 1-7）
    # 加载 API key
    api_key = load_api_key()
    LOGGER.info("API key 已加载（前 6 位：%s...）", api_key[:6])

    # 加载两个系统提示词
    interpreter_prompt = load_interpreter_prompt()
    LOGGER.info("interpreter 提示词已加载（%d 字符）", len(interpreter_prompt))

    translator_prompt = load_translator_prompt()
    LOGGER.info("translator 提示词已加载（%d 字符）", len(translator_prompt))

    # 步骤 1-2：从权威源读取签文数据
    sign = step1_2_load_authoritative_sign(sign_number)

    # 步骤 3-4：重新生成中文解读 + 写入 reinterpreted.json
    interpretation = step3_4_regenerate_chinese(sign, api_key, interpreter_prompt)

    # 步骤 5-6：翻译英文 + 写入 en.json
    en_result = step5_6_translate_to_english(sign, interpretation, api_key, translator_prompt)

    # 步骤 7：生成 Gemini 审查 prompt
    prompt_file = step7_generate_gemini_prompt(sign, interpretation, en_result)

    elapsed = time.time() - start_time
    LOGGER.info("#" * 60)
    LOGGER.info("# 单签复检流程完成")
    LOGGER.info("# 总耗时：%.1f 秒", elapsed)
    LOGGER.info("#" * 60)
    LOGGER.info("")
    LOGGER.info("输出文件：")
    LOGGER.info("  1. 中文解读（已覆盖）：%s", REINTERPRETED_JSON)
    LOGGER.info("  2. 英文翻译（已覆盖）：%s", EN_JSON)
    LOGGER.info("  3. Gemini 审查 prompt：%s", prompt_file)
    LOGGER.info("")
    LOGGER.info("后续手动步骤：")
    LOGGER.info("  4. 把 prompt 贴入 Gemini Studio 审查")
    LOGGER.info("  5. 把结果存为 data/content/_review_log/gemini_review_result_sign_%d.md", sign_number)
    LOGGER.info("  6. 续跑综合评定：python scripts/reprocess_single_sign.py --sign %d --resume", sign_number)
    LOGGER.info("")
    LOGGER.info("注意：")
    LOGGER.info("  - 数据库（reference.db）未同步，如需同步请运行 backfill_reinterpreted_to_db.py")


if __name__ == "__main__":
    main()
