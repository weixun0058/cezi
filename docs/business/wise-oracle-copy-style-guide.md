# 英文文案风格指南

> **文档定位**：W0 产出。定义英文版 UI 文案、提示语、错误消息的语气与措辞规范。
> **创建日期**：2026-06-30
> **状态**：W0 定稿，待用户审阅
> **依赖文档**：`wise-oracle-cultural-expression-guide.md`（文化表达分级）

---

## 一、语气与语调

### 1.1 核心语气

- **温和而克制**（warm and restrained）：不夸大、不恐吓、不诱导
- **文化而务实**（cultural and practical）：解释传统，但不故弄玄虚
- **反思而平等**（reflective and egalitarian）：引导思考，不说教

### 1.2 语气示例

| 场景 | 避免 | 推荐 |
| --- | --- | --- |
| 引导提问 | "Ask the oracle to reveal your destiny" | "Hold a question in mind and draw a sign for reflection" |
| 展示结果 | "The oracle has spoken!" | "Here is your oracle sign." |
| 解签开头 | "This sign means you will..." | "Traditionally, this sign suggests..." |
| 错误提示 | "You entered wrong data!" | "Please enter three numbers between 0 and 999." |
| 重新测算 | "Try again" | "Draw another sign" |

---

## 二、措辞原则

### 2.1 动词选择

| 避免 | 推荐 | 原因 |
| --- | --- | --- |
| predict | suggest / invite reflection | 避免"预测" |
| reveal | offer / present | 避免"揭示天机"的神秘感过度 |
| guarantee | explore / consider | 避免"保证" |
| must | may wish to / could consider | 避免"必须" |
| destiny | life patterns / tendencies | 避免"宿命" |

### 2.2 名词选择

| 避免 | 推荐 | 原因 |
| --- | --- | --- |
| fortune | oracle sign / reading | 避免"好运"暗示 |
| fate | path / tendency | 避免"宿命" |
| luck | favorability / tendency | 避免"运气" |
| answer | interpretation / perspective | D17 硬约束 |
| prediction | reflection / outlook | 避免"预测" |

### 2.3 形容词选择

| 避免 | 推荐 | 原因 |
| --- | --- | --- |
| accurate | thoughtful / cultural | 避免"准确" |
| powerful | traditional / time-honored | 避免"强大"暗示 |
| lucky | favorable / auspicious | 避免"幸运"暗示 |
| doomed | challenging / demanding | 避免"注定" |

---

## 三、UI 文案规范

### 3.1 按钮文案

| 场景 | 文案 | 说明 |
| --- | --- | --- |
| 提交问题 | Draw My Sign | 不用 "Predict" / "Reveal" |
| 查看解签 | View Interpretation | 不用 "View Answer" |
| 重新测算 | Draw Another Sign | 不用 "Try Again" |
| 查看黄历 | View Today's Almanac | 不用 "Check Luck" |
| 生成命盘 | Generate My Chart | 不用 "Reveal My Fate" |
| 追问 | Ask About This | 不用 "Ask More" |

### 3.2 空状态文案

| 场景 | 文案 |
| --- | --- |
| 算事初始 | "Enter three words, or three numbers, to draw your oracle sign." |
| 黄历加载中 | "Loading today's almanac..." |
| 文章列表空 | "Articles coming soon." |
| 未译签文 | "This sign's English translation is under review." |

### 3.3 错误消息

错误消息遵循 `code` 映射（W1.2 定稿）。英文前端只展示按 `code` 映射的英文消息。

| code | 英文消息 |
| --- | --- |
| INVALID_JSON | "The request format was invalid. Please try again." |
| INVALID_INPUT | "Some fields were missing or invalid. Please check and try again." |
| ORACLE_WORDS_INSUFFICIENT | "Please enter exactly three words." |
| INVALID_ORACLE_NUMBER | "Each number must be between 0 and 999." |
| ORACLE_NUMBERS_ALL_ZERO | "The three numbers cannot all be zero." |
| INVALID_ORACLE_MODE | "Invalid input mode. Choose 'three words' or 'three numbers'." |
| SIGN_NOT_FOUND | "This oracle sign could not be found." |
| STROKE_NOT_FOUND | "Could not determine the stroke count. Please try different characters." |
| INVALID_DATE | "The date provided was invalid." |
| INVALID_SCENARIO | "The selected scenario is not supported." |
| CONTENT_NOT_FOUND | "The requested content is not available." |
| RATE_LIMITED | "Too many requests. Please slow down." |
| SERVICE_UNAVAILABLE | "The service is temporarily unavailable. Please try again later." |

### 3.4 日期与数字格式

- 日期：`June 30, 2026`（美式英文）
- 农历日期：`6th lunar month, day 15`（不用"正月/初一"）
- 签号：`Sign #24` 或 `Oracle Sign 24`
- 价格：`USD 2.99`（不用 `$2.99`，避免货币符号歧义）

---

## 四、responsible-use 提示风格

### 4.1 底线提示（所有页面）

```text
For entertainment, cultural exploration, and self-reflection only. Not medical, legal, financial, psychological, or life-critical advice.
```

### 4.2 论命结果提示

```text
This birth chart reading is a cultural framework for self-reflection, not a destiny prediction. Different traditions offer different interpretations; consider this one perspective among many.
```

---

## 五、文化解释文案风格

### 5.1 首次出现术语

首次出现中国传统文化术语时，括注简短解释：

> The oracle sign (签, qiān) is a short poetic text drawn from a traditional Chinese divination text.

### 5.2 避免过度解释

- 每个术语解释不超过 1-2 句
- 不在 UI 主流程中插入长篇文化背景
- 长篇解释放文章页（`/articles`）

### 5.3 拼音使用

- 品牌名保留拼音：Zhuge Oracle
- 术语首次出现括注拼音：BaZi (八字)
- 不在所有出现处都标拼音，避免干扰阅读

---

## 六、翻译文案规范（签文与解签）

### 6.1 签文翻译

- 保留诗意意象（花、水、月、风等）
- 不强求押韵，但保持节奏感
- 不添加原文没有的解释性文字
- 翻译后长度允许比原文长 20-50%（英文表达通常比中文长）

### 6.2 解签翻译

- 用 "Traditionally, this suggests..." 开头
- 保留文化视角，不西化为现代心理学
- 6 个分项（career/wealth/love/health/study/general）保持各自视角独立，不重复

### 6.3 已知翻译问题（来自项目记忆）

- 副词堆叠易错：如 "Supremely Unfavorable" 应改为自然形容词
- "will" 禁止过严会导致文学表达不自然：需上下文判断
- 翻译输出文件必须用 append+dedup 逻辑，防止数据丢失

---

## 七、参考来源

- `wise-oracle-cultural-expression-guide.md`：文化表达分级
- 总纲第 2.2 节：英文命名与避免表达
- 项目记忆：翻译规则（避免副词堆叠、保留文学表达）

---

## 八、修订记录

| 日期 | 变更 | 变更人 |
| --- | --- | --- |
| 2026-06-30 | 初稿创建，定义语气/措辞/UI 文案/responsible-use 规范 | 助手起草，待用户审阅 |
| 2026-06-30 | 取消自由提问：按钮改为 Draw Another Sign；空状态文案改写；删除 ORACLE_QUESTION_TOO_SHORT/TOO_LONG 错误码，新增 ORACLE_WORDS_INSUFFICIENT；INVALID_ORACLE_MODE 描述改为 'three words' or 'three numbers'；删除 4.2 敏感场景提示节（不再有自由提问输入），4.3 论命结果提示重编号为 4.2 | 助手修订，待用户审阅 |
| 2026-06-30 | 算法定稿同步：Three Numbers 范围 0-9→0-999（九位种子），INVALID_ORACLE_NUMBER 消息与语气示例同步改为 0-999；语气示例"重新测算"推荐语改为"Draw another sign" | 助手修订，待用户审阅 |
