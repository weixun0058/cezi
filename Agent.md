# Agent 行为约定

> 本文件是 AI Agent 在本项目中必须遵守的行为准则。
> 任何会话开始时，Agent 必须先读本文件，再开始任何工作。

## 一、三个权威文件（数据源头，不可混淆）

**以下三个文件是项目的权威数据源头，Agent 必须直接读写这些文件，不得绕过：**

### 1. 中文签文（最权威源头）
- 文件：`data/reference/oracle_signs_authoritative_sc.csv`
- 内容：仅 `sign_number` + `sign_text` 两列
- 性质：历史文化考据后的权威版本，简体中文
- 衍生：`oracle_signs_authoritative_tc.csv`（繁体版，保留异体字）

### 2. 中文解读（DeepSeek 生成）
- 文件：`data/content/oracle_signs_reinterpreted.json`
- 内容：9 字段（sign_number/fortune/gua_type/sign_text + 7 个解读字段）
- 性质：DeepSeek 基于权威签文生成的典雅散文风解读
- 生成脚本：`scripts/reinterpret_oracle_signs.py`（批量）/ `scripts/reprocess_single_sign.py`（单签复检）

### 3. 英文翻译（DeepSeek 翻译）
- 文件：`data/content/oracle_signs_en.json`
- 内容：9 字段（sign_number/sign_text + 7 个解读字段，**不含 fortune/gua_type**）
- 性质：DeepSeek 基于权威中文解读翻译的英文
- 生成脚本：`scripts/translate_oracle_signs.py`（批量）/ `scripts/reprocess_single_sign.py`（单签复检）

### 非权威（派生物，不得作为数据源）
- `data/reference/reference.db`（数据库，由 backfill 从权威文件同步，**不是数据源头**）
- `data/reference/zhugeshenshuan_jq.xlsx`（Excel，已被权威 CSV 反向覆盖，不是源头）

## 二、英文签文审查工作流程

### 完整流程（每签必走，不可跳步）

```
步骤 1：DeepSeek 翻译（生成英文初译）
  - 批量：python scripts/translate_oracle_signs.py
  - 单签：python scripts/reprocess_single_sign.py --sign N

步骤 2：生成 Gemini 审查 prompt
  - 批量：python scripts/build_gemini_review_prompt.py --start N --limit M
  - 单签：reprocess_single_sign.py 已自动生成

步骤 3：用户贴入 Gemini Studio 审查
  - 用户手动操作，Agent 不参与

步骤 4：用户保存 Gemini 审查结果
  - 批量：存为 data/content/_review_log/gemini_review_result_signs_起-止.md
  - 单签：存为 data/content/_review_log/gemini_review_result_sign_N.md

步骤 5：大模型综合评定（Agent 核心职责，不可跳过）
  - Agent 必须基于：中文原文 + DeepSeek 英文初译 + Gemini 意见
  - 逐条评定：接受 / 否决 / 提出第三种方案
  - 必须留记录：存为 data/content/_review_log/adjudication_sign_N.md（单签）
    或 adjudication_signs_起-止.md（批量）
  - 修改 en.json

步骤 6：刷新看板
  - python scripts/sync_review_status.py
```

### 审查进度判定标准（严格）

**只有同时满足以下条件，才算"已定稿"：**
1. 有 Gemini 审查结果文件
2. **有 adjudication 综合评定记录文件**（关键！之前漏了这步）
3. en.json 已根据评定结果修改

**仅有 Gemini 审查结果文件，不算定稿**——只是"待综合评定"状态。

### 审查必须按顺序进行

- 必须从最小的未审定签号开始，按顺序往后审
- **禁止跳跃式审查**（如跳过 45-104 直接审 141-164）
- 如发现跳跃已发生，必须回头补审漏掉的批次

## 三、大模型综合评定原则

### 核心职责
纠偏 Gemini 的过度审查，而非扩大审查范围。
Gemini 有神经质敏感倾向（曾禁用 `with` 这种常见词），Agent 须主动否决此类过度审查。

### 硬约束检查清单（每签必查）
- [ ] `fortune` / `gua_type` 字段必须剔除（不翻译这两项）——仅指字段名剔除，不含 favorable/fortune 等普通英文词
- [ ] 禁止绝对化预测：`will improve` / `will fail` 等（但保留诗句中 `will` 等文学表达）
- [ ] sign_text 行数应与中文原文句数大致对应，允许译者合理合并短句，但不可合并为单行散文
- [ ] 字段完整：sign_number/sign_text/interpretation1/career/wealth/love/health/study/general 共 9 字段
- [ ] 英文不含中文字符
- [ ] 翻译准确性：不可出现翻译错乱（如把卦名或术语错译为不相关词汇）

### 非禁止词（以下均非禁止词，不可机械字符串匹配）
- `favorable` / `unfavorable` / `fortune` 等普通英文词：正常使用，不是禁止词
- `destiny`：不是禁止词
- `heal` / `heals`：不是禁止词
- `fate`：不是禁止词
- `supremely favorable` / `extremely favorable` 等副词堆叠：原文吉签时使用合理
- `with` 等常见词：Gemini 曾误禁，Agent 须主动否决
- `will` 在哲理总结中：表自然规律/谚语时保留（如 "real effort will bring real honor"）

**禁止词的唯一权威来源是 `prompts/translator_system_prompt.md` 的禁止词清单，且必须按上下文判断，不可一刀切字符串匹配。**

### 禁止行为
- **禁止写 `apply_review_fixes_*.py` 脚本机械照搬 Gemini 意见**
  - 13-32、33-44 两批曾犯此错，标记为「待复审」欠债
  - 大模型必须逐条做综合判断，不可只做搬运工
- **禁止在未做综合评定前标记为"已完成"**
- **禁止跳跃式审查**
- **禁止把"流程跑完"误判为"审定完成"**

## 四、单签复检流程（用于修正特定签）

当需要重新检查或修改某一签时：

```bash
python scripts/reprocess_single_sign.py --sign N
```

该脚本会一口气完成：
1. 从权威 CSV 读 sign_text
2. 从 reinterpreted.json 读 fortune/gua_type
3. 调 DeepSeek 重新生成中文解读
4. 覆盖写入 reinterpreted.json
5. 调 DeepSeek 翻译英文
6. 覆盖写入 en.json
7. 生成 Gemini 审查 prompt

**数据源是权威文件，不是数据库。**

## 五、数据库同步（非自动）

数据库（reference.db）不自动同步。如需同步，手动运行：
```bash
python scripts/backfill_reinterpreted_to_db.py
```

backfill 不会动 sign_text/fortune/gua_type，只同步 7 个解读字段。

## 六、当前真实审查状态（2026-07-12）

### 已知事实
- 看板显示 384 签全部审查完毕，0 签未审查
- 13-32 批曾通过 apply 脚本照搬 Gemini，后已于 2026-07-08 补做单签综合评定，20 签均已生成 `adjudication_sign_<N>.md`，视为已定稿
- 全部签文均有 adjudication 记录或无 apply 脚本

### 审查进度
- 总签数：384
- 已定稿：384（100%）
- 未审查：0（0%）
- 看板最后更新：2026-07-12 16:11:32

### 处理原则
- **存疑默认为未审定**：没有 adjudication 记录的批次，默认视为"待综合评定"
- 如用户确认某批次已在前几次会话中审定过，可补建 adjudication 记录
- 不得仅凭"有 Gemini 报告文件"就标记为"已审定"
- 审查必须按顺序进行，从最小未审定签号开始，禁止跳跃式审查

## 七、行为准则

1. **诚实原则**：不确定时明确说明"不确定"或"无法判断"，不编造
2. **未验证=未完成**：未经用户验证的结果视为未完成
3. **不宣称完成**：不主动宣称任务完成或正确
4. **阶段说明**：每阶段明确目标、做了什么、状态与限制
5. **等待反馈**：主动请求反馈，未获确认不进入下一阶段
6. **避免过度工程**：只做直接请求或必要的事
7. **数据库不权威**：千万记住，数据库内容是派生物，不是源头
