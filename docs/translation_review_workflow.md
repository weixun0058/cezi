# 诸葛神算英文签文翻译审定全流程

> 适用范围：从签文原始数据到英文定稿的完整工作流
> 涉及脚本：`reprocess_single_sign.py` / `build_gemini_review_prompt.py` / `adjudicate_single_sign.py`

## 三方协作模型

```
DeepSeek（初译）→ Gemini（英文质量审查）→ DeepSeek（综合评定）→ en.json 定稿
   中文母语        英语母语视角            中文母语+裁判
```

**职责划分**：
- **DeepSeek**：中文理解强，负责初译 + 综合评定（核查 Gemini 指控是否属实）
- **Gemini**：英文文学性强，只审英文质量（文学性/可理解性/地道性），不审语义忠实度

## 权威文件

| 文件 | 用途 | 修改方 |
|---|---|---|
| `data/content/oracle_signs_reinterpreted.json` | 中文解读权威源（简体）| DeepSeek 生成 / 复检时覆盖 |
| `data/content/oracle_signs_reinterpreted_hant.json` | 中文解读权威源（繁体）| `build_hant_json.py` 离线生成，不可手改 |
| `data/content/oracle_signs_en.json` | 英文翻译权威源 | DeepSeek 翻译 / 评定时修改 |
| `data/reference/oracle_signs_authoritative_sc.csv` | 签文诗原始数据（简体）| 只读，不可修改 |
| `data/reference/oracle_signs_authoritative_tc.csv` | 签文诗原始数据（繁体，含异体字）| 只读，不可修改 |

**注意**：签文和彭祖百忌已从数据库迁移为 JSON 内存加载（2026-07-13），详见 `docs/architecture/data-source-migration-2026-07-13.md`。数据库（reference.db）运行时仅读取汉字笔画；其中的旧内容表只为可重建兼容保留，不再是签文数据源。

## 禁止词与约束

**禁止词唯一权威来源**：`prompts/translator_system_prompt.md` 的禁止词清单。

**重要原则**：禁止词必须按上下文语义判断，不可一刀切字符串匹配。

**非禁止词**（以下均非禁止词，正常使用）：
- `favorable` / `unfavorable` / `fortune` 等普通英文词
- `destiny` / `fate` / `heal` / `heals`
- `supremely favorable` / `extremely favorable` 等副词堆叠（原文吉签时合理）

**硬约束检查清单**：
- `fortune` / `gua_type` 字段必须剔除（仅指字段名剔除）
- 禁止绝对化预测（`will improve` / `will fail` 等，但保留诗句中文学表达）
- sign_text 行数应与中文原文句数大致对应，允许合理合并短句，不可合并为单行散文
- 9 字段完整：sign_number/sign_text/interpretation1/career/wealth/love/health/study/general
- 英文不含中文字符
- 翻译准确性：不可出现翻译错乱

---

## 流程一：批量审定（已有中文+英文，需批量审查）

**适用场景**：`reinterpreted.json` 和 `en.json` 已有数据，需对一批签进行 Gemini 审查 + DeepSeek 评定。

### 步骤 1：生成 Gemini 审查 prompt（批量）

```powershell
python scripts/build_gemini_review_prompt.py --start 69 --limit 12
```

**参数**：
- `--start`：起始签号（默认 1）
- `--limit`：审查条数（默认 24）

**数据源**：`reinterpreted.json` + `en.json`（权威 JSON）

**输出**：`data/content/_review_log/gemini_review_prompt_signs_69-80.md`

### 步骤 2：手动 Gemini 审查

1. 打开 https://aistudio.google.com/
2. **System instructions**：粘贴 `prompts/gemini_review_system_instructions.md` 的内容
3. **Prompt**：粘贴上一步生成的 `gemini_review_prompt_signs_69-80.md` 内容
4. 运行 Gemini，获取审核结果
5. **结果保存为**：`data/content/_review_log/gemini_review_result_signs_69-80.md`

**Gemini 审查范围**（方案B）：
- ✅ 英文文学性（韵律、诗意、行数与原文对应）
- ✅ 欧美可理解性（文化冒犯、文化意象传达）
- ✅ 语言地道性（Chinglish、语法）
- ❌ 不审语义忠实度
- ❌ 不审占卜硬要素漏译
- ❌ 不审 will 用法
- ❌ 不审吉凶评级（favorable/unfavorable 等不是禁止词）

### 步骤 3：DeepSeek 综合评定（批量自动）

```powershell
python scripts/adjudicate_single_sign.py
```

**无参数**，自动扫描所有待评定的签（状态为 `pending_adjudication`），逐一处理。

**自动化行为**：
- 自动调用 DeepSeek，对比中文原文核查 Gemini 每条指控
- 接受真实问题，否决 Gemini 幻觉/过度审查
- 自动应用修改到 `en.json`
- 生成单签评定记录 `adjudication_sign_N.md`
- 单签失败/挂起不中断批量，继续下一签
- 处理完后生成批量报告 `batch_adjudication_report_*.md`

**挂起条件**（交用户评判）：
1. 无 Gemini 审查结果 → 挂起，提示用户先做 Gemini 审查
2. DeepSeek 返回 `pending_user_review` → 重大分歧，交用户评判
3. DeepSeek 返回解析失败 → 保留原始返回供排查

**输出**：
- `data/content/_review_log/adjudication_sign_N.md`（每签一个）
- `data/content/_review_log/batch_adjudication_report_YYYYMMDD_HHMM.md`（批量报告）
- `en.json`（已应用修改）

### 步骤 4：同步繁体 JSON

```powershell
python scripts/build_hant_json.py
```

将简体 `reinterpreted.json` 的最新内容同步生成繁体 `reinterpreted_hant.json`（sign_text 从 CSV 权威取，解读用 OpenCC s2t 转换）。

> **注意**：不再需要 backfill 到数据库。签文已从数据库迁移为 JSON 内存加载（2026-07-13）。

### 步骤 5（可选）：刷新审查进度看板

```powershell
python scripts/sync_review_status.py
```

刷新 `data/content/_review_log/review_status.md` 看板。

---

## 流程二：单签完整复检（从零开始，重新生成中文+英文+审定）

**适用场景**：对某一签从头重新生成中文解读、英文翻译，并完成审定。

### 步骤 1：完整复检（步骤 1-7 自动）

```powershell
python scripts/reprocess_single_sign.py --sign 142
```

**参数**：
- `--sign`：签号（必填）

**自动执行**：
1. 从权威 CSV 读取签文诗 sign_text
2. 从 `reinterpreted.json` 读取 fortune/gua_type
3. 调 DeepSeek 生成 7 个中文解读字段
4. 覆盖写入 `reinterpreted.json`
5. 调 DeepSeek 翻译为英文（9 字段）
6. 覆盖写入 `en.json`
7. 生成 Gemini 审查 prompt

**输出**：
- `reinterpreted.json`（已更新该签）
- `en.json`（已更新该签）
- `data/content/_review_log/gemini_review_prompt_sign_142.md`

### 步骤 2：手动 Gemini 审查

1. 打开 https://aistudio.google.com/
2. **System instructions**：粘贴 `prompts/gemini_review_system_instructions.md` 的内容
3. **Prompt**：粘贴 `gemini_review_prompt_sign_142.md` 的内容
4. 运行 Gemini，获取审核结果
5. **结果保存为**：`data/content/_review_log/gemini_review_result_sign_142.md`

### 步骤 3：续跑综合评定（步骤 8-10 自动）

```powershell
python scripts/reprocess_single_sign.py --sign 142 --resume
```

**参数**：
- `--sign`：签号（必填）
- `--resume`：续跑模式，自动检测进度，从断点继续

**自动执行**：
8. 检测进度（Gemini 审查结果是否已存在）
9. 调 DeepSeek 综合评定（对比中文原文核查 Gemini 指控）
10. 应用修改到 `en.json` + 生成评定记录

**输出**：
- `en.json`（已应用修改）
- `data/content/_review_log/adjudication_sign_142.md`

**等价命令**（也可直接调用评定模块）：
```powershell
python scripts/adjudicate_single_sign.py --sign 142
```

### 步骤 4（可选）：同步繁体 JSON + 刷新看板

```powershell
python scripts/build_hant_json.py
python scripts/sync_review_status.py
```

---

## 进度判别逻辑

`adjudicate_single_sign.py` 会自动判别每签的审查进度：

| 状态 | 判定依据 | 行为 |
|---|---|---|
| `finalized` | `adjudication_sign_N.md` 文件已存在 | 跳过，提示已定稿 |
| `pending_adjudication` | Gemini 审查结果存在，无 adjudication | 自动调 DeepSeek 评定 |
| `pending_gemini_review` | 无 Gemini 审查结果 | 挂起，提示用户先做 Gemini 审查 |

---

## 提示词文件

| 文件 | 用途 | 使用方 |
|---|---|---|
| `prompts/interpreter_system_prompt.md` | 中文解读生成的系统提示词 | DeepSeek（步骤3） |
| `prompts/translator_system_prompt.md` | 英文翻译的系统提示词 | DeepSeek（步骤5） |
| `prompts/gemini_review_system_instructions.md` | Gemini 审查的系统提示词（方案B） | Gemini（步骤2） |
| `prompts/adjudicator_system_prompt.md` | DeepSeek 综合评定的系统提示词 | DeepSeek（步骤9） |

---

## 常用命令速查

```powershell
# 批量生成 Gemini 审查 prompt（12签一批）
python scripts/build_gemini_review_prompt.py --start 81 --limit 12

# 批量 DeepSeek 综合评定（自动扫描所有待评定签）
python scripts/adjudicate_single_sign.py

# 单签完整复检（从零开始）
python scripts/reprocess_single_sign.py --sign 142

# 单签续跑评定（Gemini 审查结果已就绪）
python scripts/reprocess_single_sign.py --sign 142 --resume

# 单签直接评定（等价于续跑的步骤8-10）
python scripts/adjudicate_single_sign.py --sign 142

# 同步繁体 JSON（改签文后必跑）
python scripts/build_hant_json.py

# 刷新审查进度看板
python scripts/sync_review_status.py
```

---

## 文件产出位置

所有审查相关文件存放在 `data/content/_review_log/`：

| 文件命名 | 内容 |
|---|---|
| `gemini_review_prompt_signs_N-M.md` | 批量 Gemini 审查 prompt |
| `gemini_review_prompt_sign_N.md` | 单签 Gemini 审查 prompt |
| `gemini_review_result_signs_N-M.md` | 批量 Gemini 审查结果 |
| `gemini_review_result_sign_N.md` | 单签 Gemini 审查结果 |
| `adjudication_sign_N.md` | 单签 DeepSeek 综合评定记录 |
| `adjudication_signs_N-M.md` | 批量综合评定记录（旧格式，人工编写） |
| `batch_adjudication_report_*.md` | 批量评定自动报告 |
| `review_status.md` | 审查进度看板（自动生成） |

---

## 当前审定进度

**截至 2026-07-12**：

- 384 签已全部完成 Gemini 审查 + DeepSeek 综合评定
- 硬约束违规已全部修复：
  - sign_text 散文合并：21 签已修复
  - 中文字符残留：17 签已修复
  - 第 313 签 Li Ge 翻译错乱：已修复
  - 197-200 签 general 字段缺失：已补全
- 约束条件已修正：
  - 移除 destiny/Li Ge/heal 作为禁止词
  - sign_text 行数从"必须 4 行"放宽为"与原文句数大致对应"
  - 禁止词清单统一以 translator_system_prompt.md 为唯一权威

**已知遗留**（非硬约束违规）：
- 62 签 sign_text 行数与原文句数不完全对应（译者合理合并短句，按新约束允许）
- 第 120 签 health 字段中文原文过度解读，已精简为一句话，中文原文待后续修正
