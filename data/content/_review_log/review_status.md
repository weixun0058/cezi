# 诸葛神算英文签文审查进度看板

> 自动生成，请勿手工编辑。运行 `python scripts/sync_review_status.py` 刷新。
> 最后更新：2026-07-12 16:11:32

## 总览

- 总签数：**384**
- 已 Gemini 审查：**384** (100%)
  - 大模型综合审定（定稿）：**384**
  - apply 脚本照搬 Gemini（[待复审]）：**0**
- 未审查：**0** (0%)
- 补译签：**5** 签（因中文考据修正后重译）
  - 签号：96, 142, 146, 260, 332
  - 详见：`data/content/_review_log/retranslated_signs.json`


## 各批状态

| 批次文件 | 签号范围 | 条数 | Gemini审查 | 定稿方式 | 状态 |
|---|---|---|---|---|---|
| `gemini_review_result_signs_1_4.md` | 1-4 | 4 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_5_8.md` | 5-8 | 4 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_9_12.md` | 9-12 | 4 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_13-32.md` | 13-32 | 20 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_33-44.md` | 33-44 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_45-56.md` | 45-56 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_57-68.md` | 57-68 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_69-80.md` | 69-80 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_81-92.md` | 81-92 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_93-104.md` | 93-104 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_105-116.md` | 105-116 | 12 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_105-140.md` | 105-140 | 36 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_141-164.md` | 141-164 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_165-200.md` | 165-200 | 36 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_201-224.md` | 201-224 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_225-248.md` | 225-248 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_249-272.md` | 249-272 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_273-296.md` | 273-296 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_297-320.md` | 297-320 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_321-344.md` | 321-344 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_345-368.md` | 345-368 | 24 | 是 | 大模型综合审定 | [定稿] |
| `gemini_review_result_signs_369-384.md` | 369-384 | 16 | 是 | 大模型综合审定 | [定稿] |

## 流程说明

### 正确流程（每批必走）
1. **生成 Gemini prompt**：`python scripts/build_gemini_review_prompt.py --start 起 --limit 批大小`
2. **贴入 Gemini 审查**：用户把 prompt 贴入 Gemini Studio，拿到审查意见
3. **保存审查结果**：用户把 Gemini 输出存为 `data/content/_review_log/gemini_review_result_signs_起-止.md`
4. **大模型综合评定**（核心步骤，不可跳过）：
   - 输入：中文原文(reinterpreted.json) + DeepSeek 原译(当前 en.json) + Gemini 意见(md)
   - 逐条判断：接受 Gemini 意见 / 否决 Gemini 误判 / 提出第三种更优译法
   - 形成定稿后**直接修改 `oracle_signs_en.json`**
5. **刷新看板**：`python scripts/sync_review_status.py`

### 大模型综合评定检查清单（每签必查）

**核心原则**：纠偏 Gemini 的过度审查，而非扩大审查范围。
Gemini 有神经质敏感倾向（曾禁用 `with` 这种常见词），
大模型评定时需主动否决此类过度审查。

- [ ] 禁止词（仅这些是硬禁止）：`destiny` / `Li Ge` / `heal`(作动词表确定疗效)
- [ ] `fortune` / `gua_type` 字段必须剔除（不翻译这两项）
- [ ] 禁止绝对化预测：`will improve` / `will fail` 等（但保留诗句中 `fate` 等文学表达）
- [ ] sign_text 必须 4 行结构
- [ ] 字段完整：sign_number/sign_text/interpretation1/career/wealth/love/health/study/general 共 9 字段
- [ ] 英文不含中文字符

### 非自动禁止项（按上下文判断，勿过度审查）
- `supremely favorable` / `extremely favorable` 等副词堆叠：
  - **不是禁止词**。原文为吉签时（如"终有庆也"）使用是合理的
  - 仅当原文非吉签却译成 highly favorable 时才需复核
  - 曾误把 supremely favorable 列为禁止词并改第34签，已回退(2026-07-07)
- `fate` 在诗句中：文学表达，保留
- `with` 等常见词：Gemini 曾误禁，大模型须主动否决

### 禁止行为
- **禁止写 `apply_review_fixes_*.py` 脚本机械照搬 Gemini 意见**
  - 13-32、33-44 两批曾犯此错，标记为「待复审」欠债
  - 大模型必须逐条做综合判断，不可只做搬运工

### 已知欠债
- **13-32 批**曾通过 apply 脚本照搬 Gemini，后已补做单签综合评定（2026-07-08）
  - 13-32 共 20 签均已生成 `adjudication_sign_<N>.md`，视为已定稿
  - 残留的 `apply_review_fixes_signs_13_32.py` 仅作历史记录，不影响状态判定
- 从第 45 签起，回归正确流程

### 状态推断依据
- `大模型综合审定`：Gemini 审查文件存在 + 有 `adjudication_sign_<N>.md`（或无 apply 脚本）
- `apply脚本照搬Gemini`：存在 `apply_review_fixes_signs_*.py` 文件且无对应 adjudication 记录
- 判定优先级：adjudication 记录 > apply 脚本 > 默认推断
- 若需精确追踪（含审定时间/审定者），需给 `oracle_signs_en.json` 每签加审计字段，
  属后续优化，不在本脚本范围。
