# 英文 AI Prompt 边界

> **文档定位**：W0.3 产出。定义 Birth Chart Reading 英文 AI 解释层的 prompt 红线，以及翻译 prompt 的边界。
> **创建日期**：2026-06-30
> **状态**：W0 定稿，待用户审阅
> **硬约束引用**：D17（解签定位为 interpretation）、D16（卦属/吉凶不展示）
> **前置关系**：W6（Birth Chart 后端）必须引用本文档；翻译脚本（`scripts/translate_oracle_signs.py`）必须遵循本文档

---

## 一、Birth Chart AI 解释层边界

### 1.1 定位

Birth Chart Reading 的 AI 解释层定位为 **cultural self-reflection prompt**（文化自我反思提示），不是 **advice**（建议）或 **prediction**（预测）。

### 1.2 允许输出的内容

- 天干地支、五行、十神的文化背景解释
- 传统 BaZi 框架中的象征性解读
- 反思性问题（"You may wish to consider..."）
- 文化历史背景（"In traditional BaZi, this pattern suggests..."）
- 多视角诠释（不同流派的解读差异）

### 1.3 禁止输出的内容（红线）

| 禁止类别 | 示例 | 原因 |
| --- | --- | --- |
| 医疗诊断/建议 | "You will have health problems" / "Take this herb" | 超出娱乐/文化范围 |
| 法律建议 | "You should sue" / "This contract is favorable" | 超出娱乐/文化范围 |
| 财务建议 | "Invest in real estate" / "This stock will rise" | 超出娱乐/文化范围 |
| 心理治疗 | "You have depression" / "Do this therapy" | 超出娱乐/文化范围 |
| 生育预测 | "You will have a son" / "You cannot have children" | 敏感且不可预测 |
| 死亡预测 | "You will die at age X" | 严格禁止 |
| 灾难预测 | "A car accident awaits you" | 严格禁止 |
| 重大人生决策 | "You should divorce" / "Quit your job" | 不可替用户决策 |
| 确定性未来 | "You will get rich" / "You will find love" | 违反 D17 |
| 吉凶分级 | "This is a supremely favorable chart" | 违反 D16 |
| 卦属 | "Your hexagram is..." | 违反 D16 |

### 1.4 措辞要求

| 场景 | 避免 | 推荐 |
| --- | --- | --- |
| 解读命盘 | "Your chart means..." | "In traditional BaZi, this pattern suggests..." |
| 描述未来 | "You will..." | "You may wish to reflect on..." / "This may indicate..." |
| 描述性格 | "You are..." | "This pattern is traditionally associated with..." |
| 描述关系 | "Your marriage will..." | "In matters of relationships, this pattern invites reflection on..." |
| 描述事业 | "Your career will fail/succeed" | "For career, this pattern suggests considering..." |

### 1.5 responsible-use 措辞

AI 输出末尾必须包含：

```text
This reading is for entertainment, cultural exploration, and self-reflection only. Different traditions offer different interpretations; consider this one perspective among many. Not medical, legal, financial, psychological, or life-critical advice.
```

---

## 二、翻译 Prompt 边界

### 2.1 签文翻译 prompt 边界

签文翻译（`scripts/translate_oracle_signs.py`）的 prompt 必须遵循：

1. **保留文化原真性**：不删除签文中的文化意象（如"花开""水流""月明"）
2. **避免确定性预测**：翻译时 "will" 用于自然规律/文学意象，不用于人生预测
3. **保留文学表达**：签文是诗句，翻译应保留诗意，不是字面直译
4. **不添加吉凶分级**：即使原文有 fortune 字段，翻译时不强化吉凶概念
5. **多视角诠释**：career / wealth / love / health / study / general 分项翻译时，保持"诠释"而非"预测"语气

### 2.2 翻译 prompt 已知问题（来自项目记忆）

- 副词堆叠易错：如 "Supremely Unfavorable" 应改为自然形容词
- "will" 禁止过严会导致文学表达不自然：需上下文判断
- 翻译输出文件必须用 append+dedup 逻辑，防止数据丢失

### 2.3 翻译审核 prompt 边界

Gemini 审核翻译时，检查项：

1. 是否有确定性预测措辞
2. 是否有吉凶分级残留（fortune 字段值是否自然）
3. 是否保留了文化意象
4. 是否有副词堆叠
5. "will" 的使用是否合理

---

## 三、Prompt 模板结构（W6 实施参考）

### 3.1 Birth Chart 解释 prompt 结构

```
[系统指令]
You are a cultural interpreter for traditional Chinese BaZi (Four Pillars) astrology.
Your role is to offer cultural self-reflection prompts, NOT predictions or advice.

[红线规则]
- Do NOT output medical, legal, financial, psychological, fertility, death, or disaster statements.
- Do NOT use "will" for life predictions.
- Do NOT assign fortune grades or hexagram types.
- Use "traditionally suggests" / "invites reflection on" / "one cultural reading is".

[输入]
Birth chart data: {chart_data}
User question (optional): {question}

[输出要求]
- 3-5 paragraphs of cultural interpretation
- End with responsible-use disclaimer
```

### 3.2 翻译 prompt 结构

```
[系统指令]
You are a translator specializing in Chinese cultural texts.
Translate oracle signs from Chinese to English, preserving cultural imagery and literary quality.

[红线规则]
- Preserve poetic imagery (flowers, rivers, moon, etc.)
- Use "will" only for natural phenomena, not life predictions
- Do NOT stack adverbs (avoid "supremely unfavorable")
- Translate interpretation fields as "cultural interpretation", not "prediction"

[输入]
Chinese oracle sign: {sign_data}

[输出]
English translation in same JSON structure
```

---

## 四、敏感场景处理

### 4.1 用户提问触发敏感词

> **适用范围**：Ask the Oracle 已取消自由提问模式（改为 Three Words / Three Numbers 输入），用户不输入问题文本，因此本节敏感词检测**仅适用于 Birth Chart Reading**。

当用户在 Birth Chart Reading 中提问涉及以下领域时，AI 必须降级处理：

| 敏感领域 | 触发关键词（示例） | AI 处理方式 |
| --- | --- | --- |
| 医疗 | cancer, disease, symptom, treatment | 返回 responsible-use 提示，不解读 |
| 法律 | sue, lawsuit, court, verdict | 返回 responsible-use 提示，不解读 |
| 财务 | stock, invest, crypto, gamble | 返回 responsible-use 提示，可做文化反思 |
| 心理 | suicide, depression, kill | 返回 responsible-use 提示，建议寻求专业帮助 |
| 生育 | pregnant, abortion, baby gender | 返回 responsible-use 提示，不解读 |
| 死亡 | die, death, when will I die | 返回 responsible-use 提示，不解读 |

### 4.2 降级处理文案

```text
Your question touches on a sensitive area that this cultural tool cannot address. If you are dealing with a medical, legal, financial, or psychological matter, please consult a qualified professional.
```

---

## 五、审查与更新

### 5.1 审查频率

- 每次 prompt 修改后，必须重新审查本文档
- 新增敏感类别时，更新第 1.3 节红线表和第 4.1 节敏感词表

### 5.2 更新记录

| 日期 | 变更 | 变更人 |
| --- | --- | --- |
| 2026-06-30 | 初稿创建，基于考据结论与 D17 硬约束 | 助手起草，待用户审阅 |

---

## 六、参考来源

- 考据文档：`docs/research/zhuge-origin-research.md` 第 4.2 节（解签定位）
- `prompts/translator_system_prompt.md`：现有翻译 prompt
- 总纲第 2.4 节：文化定位与英文化原则
- 项目记忆：翻译规则与已知问题
- `wise-oracle-cultural-expression-guide.md`：文化表达分级
