# 英文文化表达指南

> **文档定位**：W0.4 产出。定义英文版中国文化内容（算事、黄历、论命）的表达分级、英文化原则、禁忌词清单。
> **创建日期**：2026-06-30
> **状态**：W0 定稿，待用户审阅
> **硬约束引用**：考据结论（`docs/research/zhuge-origin-research.md`）、D16（卦属/吉凶不展示）、D17（解签定位为 interpretation）

---

## 一、考据结论作为硬约束

经考据（见 `docs/research/zhuge-origin-research.md`），诸葛神算最早版本仅有签文，卦属（如"兑宫 小过变恒"）和吉凶分级（如"上上签"）均为后人层累造作。本项目据此决策：

1. **卦属/吉凶不展示**（D16）：简/繁/英三语前端均不展示 `fortune`（吉凶分级）和 `gua_type`（卦属）字段。英文数据加载时剔除这两个字段（D14）。
2. **解签定位为 interpretation**（D17）：解签内容定位为"文化视角的诠释"，不是"标准答案"。允许多视角并存（career/wealth/love/health/study/general 6 分项）。
3. **逐字显现动画**：已实现（`main.js` 的 `typeWriter`），英文版复用，模拟古人查字过程的仪式感。

---

## 二、四级文化表达分级

英文版涉及的中国传统文化内容，按以下四级分级处理。

### 第一级：传统术语，保留并解释

| 中文术语 | 英文表达 | 说明 |
| --- | --- | --- |
| 诸葛神算 | Zhuge Oracle / Ask the Oracle | 品牌名保留 Zhuge，功能名用 Ask the Oracle |
| 签文 | oracle sign / sign text | 核心内容，直接使用 |
| 解签 | interpretation | 不用 answer / solution |
| 黄历 | Daily Chinese Almanac | 不用 Yellow Calendar |
| 八字 | BaZi (Birth Chart) | 保留拼音，括注英文 |
| 宜 | Favorable Activities | 不用 lucky commands |
| 忌 | Unfavorable Activities | 不用 doomed actions |
| 节气 | Solar Term | 天文术语，直接使用 |
| 生肖 | Chinese Zodiac | 国际通用表达 |
| 神煞 | Auspicious / Inauspicious Spirits | 需解释，不用 evil spirits |
| 彭祖百忌 | Peng Zu's Taboos | 保留人名拼音 |

**原则**：保留文化原真性，用英文解释而非替换。首次出现时括注拼音或文化背景。

### 第二级：需解释的概念，提供简短说明

| 中文概念 | 英文处理 | 简短说明 |
| --- | --- | --- |
| 天机 | heavenly mystery | "a mysterious pattern that tradition holds is beyond full human knowing" |
| 吉凶 | favorable / unfavorable tendencies | 不用 good / bad fortune；强调"倾向"而非"判定" |
| 命理 | life patterns | 不用 fate / destiny；强调"模式"而非"宿命" |
| 求签问卜 | drawing an oracle sign | 不用 fortune telling |
| 择日 | date selection | 不用 lucky day picking |

**原则**：用 "reflection / pattern / tendency" 等软性词汇，避免 "determination / guarantee / fortune" 等硬性词汇。

### 第三级：商业慎用，需合规审查

| 表达 | 慎用原因 | 替代方案 |
| --- | --- | --- |
| prediction | 暗示确定性预测 | forecast / reflection / perspective |
| fortune telling | 英美法律语境敏感 | oracle reading / cultural divination |
| destiny | 暗示宿命论 | life patterns / tendencies |
| lucky | 暗示可购买好运 | favorable / auspicious |
| curse / hex | 暗示诅咒 | 不使用 |
| change your fate | 暗示付费改命 | 不使用 |

**原则**：涉及商业化时，避免任何可能被解读为"付费换取确定结果"的表达。

### 第四级：禁止使用

| 禁止表达 | 原因 |
| --- | --- |
| guaranteed result | 违反 responsible-use 底线 |
| accurate prediction | 违反 D17（interpretation 而非 answer） |
| 100% correct | 任何形式的确定性承诺 |
| medical advice | 超出娱乐/文化探索范围 |
| legal advice | 超出娱乐/文化探索范围 |
| financial advice | 超出娱乐/文化探索范围 |
| fortune grade / fortune level | 违反 D16（卦属/吉凶不展示） |
| gua type / hexagram type | 违反 D16（卦属/吉凶不展示） |
| will（表示确定未来） | 避免绝对未来预测；保留文学性自然规律的 will |

**关于 "will" 的使用**（来自项目记忆）：

- 禁止：表示确定未来的 will（如 "you will get rich"）
- 保留：文学性自然规律的 will（如 "the river will flow to the sea"）
- 判断标准：will 后接的是"确定的人生预测"还是"自然现象/文学意象"

---

## 三、英文化核心原则

### 3.1 定位：reflection 而非 prediction

英文版的核心定位是 **cultural self-reflection**（文化自我反思），不是 fortune telling（算命）。

- 签文是 **mirror**（镜子），不是 **answer**（答案）
- 解签是 **interpretation**（诠释），不是 **solution**（解决方案）
- 用户拿到的是 **perspective**（视角），不是 **prediction**（预测）

### 3.2 措辞原则

| 场景 | 避免 | 推荐 |
| --- | --- | --- |
| 描述签文 | "This sign predicts..." | "This sign suggests..." / "This sign invites reflection on..." |
| 描述解签 | "The answer is..." | "One interpretation is..." / "Traditionally, this suggests..." |
| 描述未来 | "You will..." | "You may wish to consider..." / "This may indicate..." |
| 描述吉凶 | "Good luck / Bad luck" | "Favorable tendencies / Challenging tendencies" |
| 描述结果 | "Accurate result" | "Cultural perspective" / "Traditional interpretation" |

### 3.3 responsible-use 底线提示

所有英文页面底部必须包含：

```text
For entertainment, cultural exploration, and self-reflection only. Not medical, legal, financial, psychological, or life-critical advice.
```

提示位置：

- 算事结果页：解签内容下方
- 黄历页：页面底部
- 论命页：结果下方
- 首页：页面底部
- 文章页：页面底部

---

## 四、卦属/吉凶处理（D14、D16 硬约束）

### 4.1 数据层处理

- `oracle_signs_en.json` 的 `fortune` 和 `gua_type` 字段在加载到内存时剔除（D14）
- 英文 API 响应不包含这两个字段
- JSON 文件保留原样不动（遵循"归档不删除"原则）

### 4.2 前端处理

- 英文前端不得有任何展示 fortune / gua_type 的 UI 元素
- 不得有"查看吉凶""查看卦属"按钮
- 不得在签文标题或描述中引用吉凶分级（如 "Supremely Favorable Sign"）

### 4.3 文案处理

- 签文展示用 "Oracle Sign #N" 或 "Sign N"，不用 "Supremely Favorable Sign #N"
- 解签内容中若原文提及吉凶倾向，翻译时降级为 "favorable / challenging tendencies"
- 不得出现 fortune grade / fortune level / gua type 等表述

---

## 五、解签定位（D17 硬约束）

### 5.1 定位声明

解签内容定位为 **cultural interpretation**（文化诠释），不是 **authoritative answer**（权威答案）。

### 5.2 多视角诠释

现有 6 个分项天然满足"多视角诠释"要求：

| 字段 | 英文标签 | 定位 |
| --- | --- | --- |
| interpretation1 | Overall Interpretation | 总体诠释 |
| career | Career | 事业视角 |
| wealth | Wealth | 财富视角 |
| love | Relationships | 感情视角 |
| health | Well-being | 健康视角 |
| study | Learning | 学业视角 |
| general | General Guidance | 综合指引 |

### 5.3 措辞要求

- 每个分项开头可用 "Traditionally, this sign suggests..." / "One cultural reading is..."
- 避免 "This means you will..." / "The sign indicates you should..."
- 允许保留文学性表达（如 "the river flows" / "the flower blooms"），但不得用于做确定性预测

---

## 六、未译签文 fallback

基于项目硬约束，未译签文（interpretation1 含中文残留或字段为空）的英文展示：

```text
This sign's English translation is under review.
```

触发条件：

- `interpretation1` 含 CJK 字符（中文残留）
- `general` 或其他必填字段为空字符串

已知质量遗留（待独立 Agent 渐进修复）：

- 7 条 interpretation1 残留中文：签号 50 / 63 / 101 / 222 / 237 / 261 / 286
- 4 条 general 为空：签号 197 / 198 / 199 / 200

---

## 七、参考来源

- `docs/research/zhuge-origin-research.md`：考据文档
- `docs/plans/2026-06-24-global-i18n-commercialization-execution-plan.md` 第 2.4 节：文化定位与英文化原则
- `docs/business/huangli-english-localization-guidance.md`：黄历英文改造指导
- 项目记忆：翻译规则（避免绝对未来预测、保留文学表达、副词堆叠易错）

---

## 八、修订记录

| 日期 | 变更 | 变更人 |
| --- | --- | --- |
| 2026-06-30 | 初稿创建，基于考据结论与 D16/D17 硬约束 | 助手起草，待用户审阅 |
