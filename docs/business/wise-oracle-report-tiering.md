# 英文报告分层

> **文档定位**：W0.5 产出。定义免费内容、付费内容（Wise Oracle Deep Reading）、赞助文案的边界。
> **创建日期**：2026-06-30
> **状态**：W0 定稿，待用户审阅
> **依赖文档**：`wise-oracle-cultural-expression-guide.md`、`wise-oracle-english-product-spec.md`

---

## 一、分层总览

| 层级 | 内容 | 价格 | 第一轮上线 |
| --- | --- | --- | --- |
| 免费 | 基础算事、黄历、基础命盘、文章 | 免费 | 是 |
| 付费 | Wise Oracle Deep Reading（深度诠释）——**暂时冻结** | USD 2.99 / 4.99（待 D8） | 暂不实施，付费方案待深度思考 |
| 赞助 | 自愿赞助入口 | 自愿 | 仅占位，不接真实支付 |

---

## 二、免费内容定义

### 2.1 Ask the Oracle（算事）

免费提供：

- 签文展示（sign_text）
- 总体诠释（interpretation1）
- 6 个分项诠释（career / wealth / love / health / study / general）
- 逐字显现动画
- 重新测算

**不收费的理由**：算事是核心引流功能，免费开放以建立用户信任和文化认同。

### 2.2 Daily Chinese Almanac（黄历）

免费提供：

- 当日宜忌（Favorable / Unfavorable Activities）
- 农历日期、节气、生肖
- 本周黄历概览
- 场景查询（wedding / moving / business opening / travel / signing / haircut）

### 2.3 Birth Chart Reading（论命）

免费提供：

- 基础命盘生成（天干地支、五行、十神）
- 基础文化解释

**付费边界**：AI 深度诠释（Wise Oracle Deep Reading）收费。

### 2.4 Articles（文章）

免费提供：

- 所有文章全文阅读
- 无付费墙

---

## 三、Wise Oracle Deep Reading（付费内容）——⚠️ 暂时冻结

> **暂时冻结（2026-06-30）**
>
> Deep Reading 付费产品定义暂时冻结。用户决策：暂时不作为付费产品，是否付费、怎么付费待深度思考后决定。以下定义仅作为历史参考，不作为当前执行依据。

### 3.1 定位

Wise Oracle Deep Reading 是 Birth Chart Reading 的付费深度诠释，由 AI 生成个性化解读。

### 3.2 付费内容

| 项目 | 免费 | Deep Reading（付费） |
| --- | --- | --- |
| 基础命盘 | ✅ | ✅ |
| 五行分析 | 基础 | 深度 |
| 十神关系 | 基础 | 深度 |
| 大运流年 | ❌ | ✅ |
| 个性化追问 | ❌ | ✅（3 次） |
| 文化背景解释 | 基础 | 深度 |

### 3.3 价格测试候选（D8 待确认）

- 候选 A：USD 2.99（低价测试）
- 候选 B：USD 4.99（中价测试）
- 测试方式：A/B 测试，观察转化率

### 3.4 付费文案

```text
Wise Oracle Deep Reading

Go beyond the basics with a personalized, in-depth interpretation of your birth chart. This cultural reading explores traditional BaZi patterns, elemental relationships, and reflective questions tailored to your chart.

[Get Deep Reading — USD 2.99]
```

**文案红线**：

- 不用 "unlock your destiny"
- 不用 "accurate prediction"
- 不用 "change your fate"
- 强调 "cultural interpretation" 和 "self-reflection"

### 3.5 第一轮上线策略

第一轮**不接真实支付**（D9 已确认：先做模拟 checkout）：

- 付费按钮展示为 "Coming Soon" 或 "Get Notified"
- 不收集支付信息
- 等待平台政策核验后再接入真实支付

---

## 四、赞助文案

### 4.1 定位

赞助是低风险补充收入，不能暗示赞助会让结果更准。

### 4.2 赞助文案

```text
Support Wise Oracle

If you find value in these cultural readings, consider supporting the project. Your support helps us maintain the site, improve translations, and add new content.

[Support Us]
```

**文案红线**：

- 不用 "donate for better luck"
- 不用 "pay for accurate results"
- 不暗示赞助与结果质量有任何关系

### 4.3 第一轮上线策略

第一轮仅占位，不接真实支付：

- 赞助按钮展示为 "Coming Soon"
- 或链接到联系页，收集意向

---

## 五、真实支付上线 Go/No-Go 清单

真实支付上线前必须完成以下核验：

| 核验项 | 状态 | 说明 |
| --- | --- | --- |
| 平台政策核验 | 待定 | AdSense / Stripe / PayPal 政策合规性 |
| 主体核验 | 待定 | 法律主体、税务登记 |
| 隐私政策更新 | 待定 | 支付数据处理条款 |
| 使用条款更新 | 待定 | 付费服务条款 |
| 退款政策 | 待定 | 退款流程与条款 |
| 模拟 checkout 测试 | 待定 | D9 已确认先做模拟 |
| 价格 A/B 测试 | 待定 | D8 待确认价格 |

**Go/No-Go 标准**：以上全部"通过"才能接入真实支付。任一"不通过"则维持占位状态。

---

## 六、商业化红线

基于考据结论（D16/D17）和文化表达指南，商业化必须遵循以下红线：

| 红线 | 说明 |
| --- | --- |
| 不售卖"吉凶分级" | D16 硬约束，fortune/gua_type 不展示，更不收费 |
| 不售卖"确定性预测" | D17 硬约束，解签是 interpretation，不是 prediction |
| 不暗示"付费结果更准" | 赞助/付费不能与结果准确性挂钩 |
| 不售卖"改命/改运" | 违反文化表达指南第三级 |
| 付费内容须标注 "cultural interpretation" | 所有付费解读须明确文化诠释性质 |

---

## 七、参考来源

- 总纲第 2.3 节：商业化优先级
- 总纲第 2.2 节：英文命名（Wise Oracle Deep Reading）
- 英文站执行计划 W0.5：商业化分层
- `wise-oracle-cultural-expression-guide.md`：文化表达分级

---

## 八、修订记录

| 日期 | 变更 | 变更人 |
| --- | --- | --- |
| 2026-06-30 | 初稿创建，定义免费/付费/赞助边界与商业化红线 | 助手起草，待用户审阅 |
