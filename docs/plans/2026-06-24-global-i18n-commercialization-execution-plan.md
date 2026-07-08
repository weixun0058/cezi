﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿# Wise Oracle 多语言化与商业化实施计划

**目标：** 将当前中文为主的诸葛神算 V4，改造为支持繁体中文、英文主站、SEO 内容、合规页面与商业化验证的可上线产品。

**总体方案：** 先完成繁体化与英文产品方案定稿，再准备英文数据与内容，随后按“后端能力、前端体验、商业化组件、SEO 合规、运营复盘”的顺序推进。每个阶段都必须能追踪进度、验证结果、文化表达边界和后续风险，不把战略判断留在口头讨论中。

**涉及技术：** Python、当前后端应用、模板页面、SQLite/reference data、pytest、原生 JavaScript、CSS、Docker/Gunicorn 部署配置。

---

## 0. 计划来源与执行边界

本计划基于以下两份已有文档重写：

- `docs/business/2026-06-global-commercialization-plan.md`
- `docs/business/Wise_Oracle_Outbound_Plan.md`

本计划只保留对执行有直接帮助的内容。已经否定、无关或容易误导执行者的历史讨论，不应在执行计划里反复出现。

执行边界：

1. 旧入口 `/huangli`、`/suanshi`、`/lunming` 必须有明确兼容策略；当前方案允许 301 到新的简体入口。
2. 英文默认主站与繁体中文第二语言并行推进，英文商业化优先级更高。P1 先做繁体的原因是：技术栈完全复用现有后端、为 P5 英文的 i18n 架构做技术 rehearsal、港澳台及海外华人是低摩擦增量市场。繁体改造经技术分析确认为中等前端工作量，无阻塞性技术风险（详见 `docs/plans/p1-technical-analysis-2026-06-24.md`）。
3. "算事""论命""黄历"的英文版不是直译，要做产品交互、术语体系、文化表达和语义边界重写。
4. 商业化代码必须可配置、可关闭、可替换；真实支付上线前必须完成平台政策与主体可行性核验。
5. 中文传统表达可以保留文化语境；英文和商业化文案需要避免把象征性、经验性、模糊性的传统表达误译为确定性承诺。
6. 每个阶段必须更新进度表，并留下测试、截图、文档或人工验收记录。
7. OpenCC 只作为离线构建工具使用，用于生成繁体参考数据或构建产物；网站运行时不应依赖 OpenCC 初始化转换器。

8. 考据结论（见 `docs/research/zhuge-origin-research.md`）作为产品决策硬约束：原版诸葛神算仅有签文，卦属（如"兑宫 小过变恒"）和吉凶分级（如"上上签"）均为后人层累造作，非原貌。本项目据此决策：简/繁/英三语前端均不展示卦属/吉凶；后端数据库保留存量数据，待后续决策是否恢复原貌；解签定位为 interpretation（诠释）而非 answer（答案）。

## 1. 总进度追踪表

| 阶段 | 目标 | 状态 | 负责人 | 完成日期 | 验收证据 |
| --- | --- | --- | --- | --- | --- |
| P0 | 项目现状审计与术语冻结 | 进行中 | Codex | 待定 | 已完成路由/API/模板基础审计；考据文档已完成（`docs/research/zhuge-origin-research.md`）；英文产品术语表与文化表达指南仍待定稿 |
| P1 | 繁体中文改造 | 已完成 | Codex | 2026-06-26 | 提交 `3a4a25e`、`d66fad4`；`python -m pytest -q` 通过；2026-06-28 基于考据结论删除卦属/吉凶展示（4.5 节） |
| P2-P5 | 英文站改造（产品方案、数据、后端、前端） | 进行中 | — | — | 详细任务已迁移至 `docs/plans/2026-06-27-english-site-execution-plan.md`（W0-W8）；W2.1 英文签文翻译 384/384 已超额完成（计划仅要 20 条样本），其余工作包未开始 |
| P6 | 商业化基础代码 | 未开始 | 待定 | 待定 | 配置开关、赞助入口、付费墙原型、订单模型设计 |
| P7 | SEO 与合规上线准备 | 未开始 | 待定 | 待定 | sitemap、robots、法律页、Search Console 清单 |
| P8 | 商业化预验证与上线复盘 | 未开始 | 待定 | 待定 | 平台核验表、单位经济模型、4 周运营台账 |

状态枚举：

- 未开始
- 进行中
- 阻塞
- 待验收
- 已完成

### 1.1 当前改造进度基线

截至 2026-06-30，项目已经完成以下基础改造：

1. 简体 / 繁体核心路由已经落地：`/zh-hans/almanac`、`/zh-hans/divination`、`/zh-hans/bazi`、`/zh-hant/almanac`、`/zh-hant/divination`、`/zh-hant/bazi`。
2. 旧中文入口已有兼容跳转：`/`、`/huangli`、`/suanshi`、`/lunming` 进入当前简体入口。
3. 模板 `<html lang>` 已按当前语言输出 `zh-Hans` / `zh-Hant`。
4. 前端已建立 `dictionary.json`、`i18n.js`、`lang_switcher.js` 的简繁字典基础设施，业务请求通过 `i18n.apiUrl()` 传递语言。
5. 签文、解签、彭祖百忌等内容层已经改为读取已生成的简繁数据，不在网站运行时依赖 OpenCC。
6. 黄历动态数据已经新增项目内本地化层 `zhugeshensuan/huangli_i18n.py`，覆盖 `lunar_python` 生成的宜忌、神煞、生肖、方位、节气、彭祖百忌、状态词等繁体化。
7. `/api/huangli` 和 `/api/week_huangli` 已按 `lang=zh-hant` 返回繁体展示值，并为 `scenario_assessment` 增加 `status_code`、`source_code`，前端不再比较中文状态文案。
8. 前端农历日期格式化已抽为 `frontend/static/js/lang/lunar-format.js`，`huangli_lunar_handler.js` 与 `lunar_date_handler.js` 不再直接显示 `lunar.js` 的简体 `toString()`。
9. 英文黄历暂不进入生产路径，但已形成后续指导文档：`docs/business/huangli-english-localization-guidance.md`。
10. 最新已验证命令：`python -m pytest -q`，结果为通过，包含 2 个既有 skip。
11. 卦属/吉凶已从简繁前端删除（`frontend/templates/suanshi.html`、`frontend/templates/index.html`、`frontend/static/js/main.js`、`frontend/static/js/lang/dictionary.json`）；后端 `divination.py`、`database.py`、`reference.db` 保留存量数据未动。
12. 英文签文翻译 384/384 完成（`data/content/oracle_signs_en.json`），含质量遗留：7 条 interpretation1 残留中文（签号 50/63/101/222/237/261/286）、4 条 general 为空（197-200），待独立 Agent 渐进修复，不阻塞程序落实。
13. 考据文档完成（`docs/research/zhuge-origin-research.md`），确认原版诸葛神算无卦属/吉凶；12,700 字表全量推导 384 条签文已完成。
14. 打字机效果已实现（`main.js` 的 `typeWriter`，chunkSize=1, interval=50，尊重 `prefers-reduced-motion`，每 6 字符自动滚动）。
15. 翻译脚本与提示词已建立（`scripts/translate_oracle_signs.py`、`prompts/translator_system_prompt.md`）；Gemini 审核因 API 缺失仅完成前 12 条（`data/content/_review_log/gemini_review_result_signs_1_4.md` 等）。

仍未完成的内容：

1. 英文主站、英文三大工具页、英文 API、英文 SEO 页面尚未实现。
2. 英文产品规格、文案风格指南、报告分层和文化表达指南尚未定稿。
3. 英文黄历术语表、英文文章简报和合规页面草稿尚未形成可开发数据（英文签文样本已超额完成 384/384）。
4. 英文签文质量遗留（7 条 interpretation1 残留中文、4 条 general 为空）待独立 Agent 渐进修复。
5. W0-W8 工作包进度日志需回填（W2.1 已超额完成，其余未开始）。
6. 商业化代码、支付 / 赞助 / 广告配置和平台政策核验尚未开始。

每完成一个任务，在对应阶段的“进度日志”追加一行：

```text
日期 - 负责人 - 改动 - 验收证据 - 下一步
```

## 2. 关键产品决策

### 2.1 语言与 URL

第一阶段 URL 定稿如下：

| 语言 | 页面 | URL | 旧路由策略 |
| --- | --- | --- | --- |
| 英文 | 首页 | `/` | 英文阶段再调整 |
| 英文 | 黄历 | `/daily-almanac` | 新增，不复用 `/huangli` |
| 英文 | 算事 | `/ask-oracle` | 新增，不复用 `/suanshi` |
| 英文 | 论命 | `/birth-chart-reading` | 新增，不复用 `/lunming` |
| 英文 | 文章列表 | `/articles` | 新增 |
| 英文 | 文章详情 | `/articles/<slug>` | 新增 |
| 英文 | 隐私政策 | `/privacy` | 新增 |
| 英文 | 使用条款 | `/terms` | 新增 |
| 英文 | 免责声明 | `/disclaimer` | 新增 |
| 英文 | 关于 | `/about` | 新增 |
| 英文 | 联系 | `/contact` | 新增 |
| 简体中文 | 黄历 | `/zh-hans/almanac` | 当前主入口 |
| 简体中文 | 算事 | `/zh-hans/divination` | 当前主入口 |
| 简体中文 | 论命 | `/zh-hans/bazi` | 当前主入口 |
| 繁體中文 | 黃曆 | `/zh-hant/almanac` | 新增 |
| 繁體中文 | 算事 | `/zh-hant/divination` | 新增 |
| 繁體中文 | 論命 | `/zh-hant/bazi` | 新增 |
| 兼容入口 | 黄历 | `/huangli` | 可 301 到 `/zh-hans/almanac` |
| 兼容入口 | 算事 | `/suanshi` | 可 301 到 `/zh-hans/divination` |
| 兼容入口 | 论命 | `/lunming` | 可 301 到 `/zh-hans/bazi` |

### 2.2 英文命名

| 中文功能 | 英文定名 | 英文避免表达 |
| --- | --- | --- |
| 诸葛神算 / 算事 | Ask the Oracle | guaranteed fortune telling, accurate prediction |
| 黄历 | Daily Chinese Almanac | Yellow Calendar |
| 论命 / 八字 | Birth Chart Reading | fate guarantee, life prediction |
| 付费报告 | Wise Oracle Deep Reading | destiny changing report |
| 宜 | Favorable Activities | lucky commands |
| 忌 | Unfavorable Activities | doomed actions |

统一英文 responsible-use 底线提示：

```text
For entertainment, cultural exploration, and self-reflection only. Not medical, legal, financial, psychological, or life-critical advice.
```

统一繁体 responsible-use 底线提示：

```text
本服務僅供娛樂、傳統文化探索與自我反思參考，不構成醫療、法律、財務、心理治療或重大人生決策建議。
```

### 2.3 商业化优先级

1. 先完成可被 AdSense 审查的网站基础：英文页面、原创内容、合规页、sitemap、robots、Search Console。
2. 并行设计 `Wise Oracle Deep Reading`，但真实支付上线必须等待平台政策和主体核验。
3. 赞助入口作为低风险补充，但不能暗示赞助会让结果更准。
4. 第一阶段不做人工咨询。
5. 第一阶段不做复杂会员、订阅或完整用户账号系统。

### 2.4 文化定位与英文化原则

**考据结论（2026-06-28，硬约束）**：经考据（见 `docs/research/zhuge-origin-research.md`），诸葛神算最早版本仅有签文，卦属（如“兑宫 小过变恒”）和吉凶分级（如“上上签”）均为后人层累造作，非原貌。本项目据此决策：简/繁/英三语前端均不展示卦属/吉凶；后端数据库保留存量数据，待后续决策是否恢复原貌。解签定位为 interpretation（诠释）而非 answer（答案），允许多视角并存（career/wealth/love/health/study/general 6 分项天然满足多视角结构）。

本项目不是把传统文化“消毒”成普通娱乐工具，也不是以恐吓、确定性承诺或诱导付费为目的的项目。项目底层定位是：以中国传统文化、术数、黄历、八字、求签问卜为内容基础，向中文和英文用户解释其文化语境、象征系统、经验积累和自我反思价值。

中文语境中可以保留的传统表达：

1. `天机`、`吉凶`、`宜忌`、`命理`、`八字`、`黄历`、`求签问卜` 等传统语汇。
2. 对黄历、节气、择日、农业生产、民俗经验和古代观察体系的文化解释。
3. 对八字、命理、卦象、签文的象征性、启发性和心理暗示性质的说明。
4. 具有传统文化风格的叙述方式，不需要强行改写成现代科学说明。

英文化时需要注意的是“语义转写”，不是删除传统味道：

1. 不要把中文里模糊、象征、经验性的说法翻译成英文里的强承诺。
2. `预测` 可根据场景译为 `reading`、`interpretation`、`traditional indication`、`reflection prompt`，不默认译为 `accurate prediction`。
3. `天机` 可根据场景译为 `hidden pattern`、`traditional insight`、`oracle message`，不直接写成确定性命运揭示。
4. `吉凶` 可译为 `favorable and unfavorable indications`，不写成会导致现实结果的保证。
5. 黄历宜忌应解释为传统择日经验、节气民俗和文化实践，不写成强制行动命令。

真正需要避免的是商业化和 AI 输出中的确定性承诺：

1. 不写“保证准确”“改变命运”“付费后更准”。
2. 不对医疗、投资、法律、心理治疗、生育、死亡、灾难和重大人生决策给出确定性结论。
3. 不制造焦虑式转化，例如“不购买就会错过机会”“不赞助会影响运势”。
4. 不把赞助、广告或付费报告包装成影响结果的条件。

后续文档中的“文化表达指南”应采用分级方式：

| 级别 | 含义 | 处理方式 |
| --- | --- | --- |
| 传统表达 | 天机、吉凶、宜忌、命理、求签问卜等文化词 | 中文可保留，英文做语境化转写 |
| 需解释表达 | 预测、命运、运势、神煞、择日等容易被英文误读的词 | 保留文化含义，增加背景或弱化确定性 |
| 商业慎用表达 | deep reading、unlock、premium、sponsor 等转化词 | 可用，但不得暗示付费改变结果 |
| 禁止表达 | 保证准确、改变命运、医疗投资法律确定建议、付费更准 | 不进入页面、报告、广告或付费文案 |

### 2.5 英文版改造总路线

> 下表 E0-E8 为高层路线概览。详细工作包、子任务、决策门和进度日志见 `docs/plans/2026-06-27-english-site-execution-plan.md`（编号已统一为 W0-W8，E0-E8 对应 W0-W8）。

英文版不能直接复用中文页面再替换文字。英文用户、搜索引擎和商业化审核关注的是可信度、合规边界、内容完整度和工具可用性。因此英文改造按以下顺序推进：

| 顺序 | 工作包 | 目标产物 | 依赖 | 验收方式 |
| --- | --- | --- | --- | --- |
| E0 | 英文产品边界冻结 | `wise-oracle-english-product-spec.md` | 当前中文功能和文化定位 | 文档评审通过 |
| E1 | 英文术语体系 | `wise-oracle-termbase.md`、`huangli-english-termbase-draft.md` | P1 简繁字典、6tail JS 英文候选词 | 传统表达、需解释表达、商业慎用表达和禁止表达分级明确 |
| E2 | 英文内容数据 | 20 条英文签文样本、25 篇文章简报、合规页草稿 | E0/E1 | 内容数据测试通过 |
| E3 | 英文路由骨架 | `/`、`/ask-oracle`、`/daily-almanac`、`/birth-chart-reading`、法律页 | E0 | 路由测试通过 |
| E4 | 英文 Ask the Oracle 后端 | 英文三词 / 三数字算法与 API（原"自由提问"已取消，详见英文站执行计划 W4） | E0/E2 | 算法确定性和错误码测试通过 |
| E5 | 英文 Daily Chinese Almanac 后端 | 英文黄历术语表、场景映射、API 响应 | E1 | 黄历术语测试和 API 测试通过 |
| E6 | 英文 Birth Chart Reading 后端 | 英文输入校验、报告结构、AI prompt 边界 | E0 | API、SSE、文化表达边界测试通过 |
| E7 | 英文前端页面 | 英文首页和三大工具页 | E3-E6 | 桌面 / 移动端人工验收 |
| E8 | SEO / 合规 / 商业化预埋 | sitemap、robots、文章页、赞助 / 付费墙占位 | E2/E7 | SEO 和配置开关测试通过 |

英文版执行约束：

1. `/` 何时切换为英文首页必须作为明确发布决策处理；切换前不得破坏当前简体入口兼容。
2. 英文 API 必须返回稳定 `code`，前端按 code 映射文案；不要让英文前端依赖中文错误消息。
3. 英文黄历术语先从 `frontend/static/js/lunar.js` 的 6tail 英文 messages 抽取候选，再人工审校；不得直接把库内英文作为正式产品文案上线。
4. 不把 6tail JS 运行库接入 Flask 后端作为跨进程服务。
5. 不修改 `site-packages/lunar_python` 或 `frontend/static/js/lunar.js` 来维护项目语言。
6. 英文页面的 responsible-use 提示作为底线存在，不应喧宾夺主；页面主体仍应保留中国传统文化表达。
7. 商业化入口默认关闭；真实支付和广告代码必须等 P8 平台政策核验后再上线。

## 3. P0 项目现状审计、术语冻结与文化表达指南

**目标：** 在动代码前确认现有路由、API、模板、测试和部署路径，冻结第一轮术语表，并建立“传统表达可保留、英文化需解释、商业承诺需避免”的文化表达指南。

**涉及文件：**

- 读取：`zhugeshensuan/blueprints/pages.py`
- 读取：`zhugeshensuan/blueprints/divination.py`
- 读取：`zhugeshensuan/blueprints/huangli_api.py`
- 读取：`zhugeshensuan/blueprints/lunming_api.py`
- 读取：`frontend/templates/index.html`
- 读取：`frontend/templates/huangli.html`
- 读取：`frontend/templates/suanshi.html`
- 读取：`frontend/templates/lunming.html`
- 读取：`frontend/static/css/style.css`
- 读取：`frontend/static/css/style_mobile.css`
- 修改：`docs/plans/2026-06-24-global-i18n-commercialization-execution-plan.md`
- 新建：`docs/business/wise-oracle-termbase.md`
- 新建：`docs/business/wise-oracle-cultural-expression-guide.md`

**执行步骤：**

1. 运行 `rg -n "天机|吉凶|宜忌|命理|八字|黄历|求签|预测|命运|运势|准确|保证|改命|付费|赞助" frontend zhugeshensuan docs`。
2. 把命中的文案按分级记录到 `docs/business/wise-oracle-cultural-expression-guide.md`，不要把传统词本身当作问题。
3. 运行 `rg -n "@.*route|Blueprint|get\\(|post\\(" zhugeshensuan`。
4. 列出现有页面路由和 API 端点。
5. 阅读现有模板，判断是否需要抽取共享页面骨架。
6. 创建 `docs/business/wise-oracle-termbase.md`，字段包含：简体、繁体、英文候选、使用场景、文化说明、英文化注意事项。
7. 运行 `rg -n "正在|加载|请输入|请选择|失败|成功|未知|错误" frontend/static/js`，列出 main.js / huangli.js / lunming.js 的全部硬编码中文字符串清单，为统一字典方案做准备。
8. 确认 OpenCC 只存在于构建脚本或一次性数据生成脚本中；如果运行时代码导入 OpenCC，需要改为读取已生成的繁体数据或使用项目内静态字典。
9. 运行 `rg -n "error.*message|message.*=" zhugeshensuan/blueprints`，标记后端 API 错误消息的语言（当前为简体中文），登记为 P4 显性债务：P4 英文后端改造时统一为所有错误增加 `code` 字段，前端按 code 映射多语言消息。
10. 将 P0 状态更新为“待验收”。

`wise-oracle-cultural-expression-guide.md` 建议分级：

| 级别 | 示例 | 处理方式 |
| --- | --- | --- |
| 传统表达 | 天机、吉凶、宜忌、命理、八字、黄历、求签问卜 | 中文可保留，英文解释文化语境 |
| 需解释表达 | 预测、命运、运势、神煞、择日 | 英文避免强承诺，改为 reading / indication / reflection |
| 商业慎用表达 | Deep Reading、unlock、sponsor、premium | 可用于产品分层，不暗示付费影响结果 |
| 禁止表达 | 保证准确、改变命运、付费后更准、医疗投资法律确定建议 | 不进入页面、报告、广告、付费文案 |

**已验证事项（无需再审计）：**

- DB 笔画查询支持繁体字输入：`hanzi` 表同时存储简繁（18620 条，7456 条有 traditional_strokes），查询优先返回 `kangxi_strokes`，康熙笔画对简繁统一。详见 `docs/plans/p1-technical-analysis-2026-06-24.md` 难点 4。

**验证命令：**

```powershell
pytest
```

预期：现有测试在正式实施前全部通过。

**进度日志：**

- 2026-06-26 - Codex - 完成简繁路由、模板语言、前端字典、内容层繁体化和黄历动态数据繁体化审计；确认 OpenCC 不进入网站运行时 - 提交 `3a4a25e`、`d66fad4`；`python -m pytest -q` 通过 - 下一步定稿英文产品术语表和文化表达指南。

## 4. P1 繁体中文改造

**目标：** 完成本项目的“繁体”化改造，让港澳台及海外华人用户可以通过 `/zh-hant/almanac`、`/zh-hant/divination`、`/zh-hant/bazi` 访问核心功能。

**范围：** 第一轮只做核心页面和核心交互，不做繁体文章系统，不删除简体旧入口。

**涉及文件：**

- 修改：`zhugeshensuan/blueprints/pages.py`
- 修改：`zhugeshensuan/blueprints/huangli_api.py`
- 修改：`zhugeshensuan/huangli.py`
- 修改：`zhugeshensuan/i18n_utils.py`
- 修改：`zhugeshensuan/lunming.py`
- 新建：`zhugeshensuan/huangli_i18n.py`
- 修改：`frontend/templates/index.html`
- 修改：`frontend/templates/huangli.html`
- 修改：`frontend/templates/suanshi.html`
- 修改：`frontend/templates/lunming.html`
- 修改：`frontend/static/js/huangli.js`
- 修改：`frontend/static/js/lunming.js`
- 修改：`frontend/static/js/main.js`
- 修改：`frontend/static/js/lunar_date_handler.js`
- 修改：`frontend/static/js/huangli_lunar_handler.js`
- 修改：`frontend/static/js/lang/dictionary.json`
- 修改：`frontend/static/js/lang/i18n.js`
- 修改：`frontend/static/js/lang/lang_switcher.js`
- 新建：`frontend/static/js/lang/lunar-format.js`
- 修改：`scripts/build_reference_db.py`
- 修改：`frontend/static/css/style.css`
- 修改：`frontend/static/css/style_mobile.css`
- 修改：`frontend/static/css/huangli.css`
- 修改：`frontend/static/css/huangli_mobile.css`
- 测试：`tests/test_frontend_contract.py`
- 测试：`tests/test_api.py`
- 测试：`tests/test_reference_database.py`
- 新建：`tests/test_huangli_i18n.py`

### 任务 P1.1：新增繁体路由

1. 先写测试，断言 `/zh-hans/almanac`、`/zh-hans/divination`、`/zh-hans/bazi`、`/zh-hant/almanac`、`/zh-hant/divination`、`/zh-hant/bazi` 返回 HTTP 200。
2. 运行 `pytest tests/test_frontend_contract.py -q`，确认测试先失败。
3. 在 `zhugeshensuan/blueprints/pages.py` 添加路由。
4. 允许简体和繁体复用同一套模板，但必须通过 `current_lang` 或前端字典渲染对应语言文案。
5. 再次运行 `pytest tests/test_frontend_contract.py -q`。
6. 更新 P1 进度日志。

### 任务 P1.2：调整模板语言渲染

1. P1 不强制创建独立繁体模板；可采用同模板 + 语言字典的方式。
2. 模板里的 class 名、DOM 层级、JS 选择器保持稳定。
3. `<html lang>` 必须按当前语言渲染：`zh-hans` 对应 `zh-Hans`，`zh-hant` 对应 `zh-Hant`。
4. 在页脚或结果区域展示对应语言的 responsible-use 底线提示。
5. 避免大陆互联网式营销语。
6. 运行页面契约测试。

### 任务 P1.3：本地化前端交互文案

1. API 响应结构保持不变。
2. 采用统一字典方案：`dictionary.json` 保存语义 key 与各语言文案，`i18n.js` 提供 `t()`、`applyTranslations()`、`apiUrl()` 等接口，`lang_switcher.js` 负责简繁切换。
3. 在前端增加繁体加载、空状态、错误、重试、结果、校验提示。
4. **不翻译后端错误码，不修改后端错误消息**。当前后端 API 错误消息为简体中文，繁体用户会看到简体错误提示——这是已知问题，登记为 P4 显性债务：P4 英文后端改造时统一为所有错误增加 `code` 字段，前端按 code 映射多语言消息。P1 阶段不处理。
5. 人工测试三个繁体页面的非法输入。

### 任务 P1.4：取消 P1 的 canonical 和 hreflang 要求

1. P1 阶段不强制实现 canonical 和 hreflang。
2. canonical / hreflang 留到英文主站和最终 URL 策略稳定后统一处理。
3. 当前阶段只保证简体、繁体核心页面可访问，且旧入口有明确跳转策略。
4. 若后续进入 SEO 阶段，再补专门测试页面元数据。

### 任务 P1.5：完成黄历动态数据繁体化

1. 已新增 `zhugeshensuan/huangli_i18n.py`，在项目内维护黄历术语本地化层，不修改 `site-packages`。
2. `lunar_python` 继续生成简体基础数据，API 返回前对 record 副本做语言本地化，避免缓存串读。
3. `/api/huangli` 和 `/api/week_huangli` 保持原字段名，按 `lang` 返回简体或繁体展示值。
4. `scenario_assessment` 已新增 `status_code`、`source_code`，前端逻辑不再比较中文 `status`。
5. 已覆盖 2026 全年 `lunar_python` 实际输出中出现的简繁异形字，并明确不将神煞名中的 `后` 转成 `後`。
6. 已新增 `tests/test_huangli_i18n.py`，覆盖真实样本、2026 全年扫描和缓存副本不变性。

### 任务 P1.6：完成农历日期前端格式化共享层

1. 已新增 `frontend/static/js/lang/lunar-format.js`。
2. `huangli_lunar_handler.js` 与 `lunar_date_handler.js` 已改为通过 `LunarFormat` 格式化农历月份、闰月、日期和时辰文案。
3. 前端不再直接把 `lunar.js` 的简体 `month.toString()` 作为可见文案。
4. `lunar_date_handler.js` 中直接调用 `i18n.t()` 且无 fallback 的位置已统一改为 `LunarFormat.tr()`。

**验证命令：**

```powershell
pytest tests/test_frontend_contract.py tests/test_api.py -q
pytest tests/test_huangli_i18n.py tests/test_reference_database.py -q
python -m pytest -q
```

**人工验收：**

1. 访问 `/zh-hans/almanac`。
2. 访问 `/zh-hans/divination`。
3. 访问 `/zh-hans/bazi`。
4. 访问 `/zh-hant/almanac`。
5. 访问 `/zh-hant/divination`。
6. 访问 `/zh-hant/bazi`。
7. 确认移动端无横向溢出。

**验收标准：**

- 简体与繁体核心路由返回 200。
- 旧中文入口跳转到当前简体入口，或按最终路由策略保持兼容。
- 繁体页面可读且无乱码。
- 没有新增保证结果、付费更准或敏感场景确定建议。
- 网站运行时不依赖 OpenCC 初始化转换器。
- 当前测试通过。

**进度日志：**

- 2026-06-26 - Codex - 完成简繁路由、旧入口 301、模板 `html lang`、前端字典、简繁内容层和 API 语言参数传递 - 提交 `3a4a25e`；`python -m pytest -q` 通过 - 下一步补齐黄历动态数据。
- 2026-06-26 - Codex - 完成黄历动态数据繁体化、本地 `huangli_i18n.py`、`status_code/source_code`、`LunarFormat` 共享模块和英文黄历后续指导文档 - 提交 `d66fad4`；`python -m pytest -q` 通过 - 下一步进入英文产品方案和数据准备。
- 2026-06-28 - 用户决策 - 基于考据结论（`docs/research/zhuge-origin-research.md` 4.5 节），从简繁前端删除卦属/吉凶展示（`suanshi.html`、`index.html`、`main.js`、`dictionary.json`）；后端 API 仍返回 `fortune`/`gua_type` 字段，前端不再使用；后端数据库保留存量数据 - `pytest tests/test_frontend_contract.py tests/test_api.py` 27 项通过 - 详见考据文档 4.5 节。

## 5. P2-P5 英文站改造

> 英文站改造的完整执行计划、工作包详情、决策门、进度日志已迁移至独立文档：
> [2026-06-27-english-site-execution-plan.md](2026-06-27-english-site-execution-plan.md)
>
> 总纲不再保留英文 P2-P5 的详细任务，避免双文档漂移。英文站执行以该独立文档为准。

**进度日志：**

- 2026-06-27 - 独立文档创建完成，P2-P5 详细任务迁移至 `docs/plans/2026-06-27-english-site-execution-plan.md` - 决策门 D1/D2/D4-D7/D9/D10/D12 已确认 - 下一步按 W0 开始执行。

## 9. P6 商业化基础代码构建和植入

**目标：** 构建商业化基础设施：配置开关、赞助入口、付费报告分层、订单数据模型草案、广告位占位和基础事件记录。真实支付和广告代码上线前必须另行验收。

**涉及文件：**

- 修改：`zhugeshensuan/config.py`
- 新建：`zhugeshensuan/commerce.py`
- 新建：`zhugeshensuan/commerce_models.py`
- 新建：`zhugeshensuan/blueprints/commerce_api.py`
- 新建：`frontend/templates/partials/sponsor.html`
- 新建：`frontend/templates/partials/paywall.html`
- 新建：`frontend/templates/partials/ad_slot.html`
- 新建：`frontend/static/js/commerce.js`
- 修改：`.env.example`
- 测试：`tests/test_commerce_config.py`
- 测试：`tests/test_commerce_api.py`

### 任务 P6.1：增加商业化配置开关

1. 增加配置项：
   - `WISE_ORACLE_SPONSOR_ENABLED`
   - `WISE_ORACLE_PAYWALL_ENABLED`
   - `WISE_ORACLE_ADS_ENABLED`
   - `WISE_ORACLE_CHECKOUT_URL`
   - `WISE_ORACLE_SPONSOR_URL`
2. 所有开关默认关闭。
3. 在 `.env.example` 记录说明。
4. 增加测试，确认开关关闭时不渲染赞助、付费墙、广告组件。

### 任务 P6.2：增加赞助组件

1. 创建赞助 partial。
2. 文案使用：`If this reading helped you reflect, you can support Wise Oracle.`
3. 不把赞助入口放在 AdSense 广告位旁边。
4. 不暗示赞助会让结果更准。
5. 增加渲染测试或路由快照断言。

### 任务 P6.3：增加付费墙原型

1. 为 `Wise Oracle Deep Reading` 创建付费墙 partial。
2. 展示价值点：
   - 完整 message。
   - 3 条具体 guidance。
   - 7-30 天 reflection focus。
   - 可复制报告格式。
3. 平台未核验前只使用禁用或模拟 checkout。
4. 如果 checkout URL 为空，显示等待名单或 coming soon，不显示坏链接。

### 任务 P6.4：定义最小订单记录

1. 草拟字段：
   - `order_id`
   - `provider`
   - `product_code`
   - `amount`
   - `currency`
   - `status`
   - `created_at`
   - `unlock_token_hash`
   - `refund_status`
2. 平台未选定前不持久化真实订单。
3. 只增加模型校验测试。

### 任务 P6.5：设计 webhook，不直接上线生产 webhook

1. 在完成实时政策调研后，记录 Lemon Squeezy、Paddle、Gumroad webhook 验签要求。
2. 只有在配置关闭时可以先放置占位路由。
3. 未配置时返回 404 或 disabled 响应。
4. 生产模式禁止接受未签名 webhook payload。

### 任务 P6.6：增加广告位占位

1. 创建布局安全的广告位 partial。
2. 只有 `WISE_ORACLE_ADS_ENABLED=true` 时显示。
3. 不靠近主要工具按钮。
4. 不出现引导点击广告的文案。

**验证命令：**

```powershell
pytest tests/test_commerce_config.py tests/test_commerce_api.py -q
pytest -q
```

**验收标准：**

- 商业化组件受配置开关控制。
- 默认配置对开发和审查安全。
- 本地测试不依赖真实支付或广告代码。
- 赞助、付费墙、广告文案符合合规边界。

**进度日志：**

- 待记录

## 10. P7 SEO、内容系统与合规上线准备

**目标：** 让英文站具备被搜索引擎抓取、被 AdSense 审查、被用户信任的基础。

**涉及文件：**

- 新建：`zhugeshensuan/blueprints/seo.py`
- 新建：`frontend/templates/sitemap.xml`
- 新建：`frontend/templates/robots.txt`
- 新建或修改：25 篇英文文章的内容来源。
- 测试：`tests/test_sitemap.py`
- 测试：`tests/test_robots.py`
- 测试：`tests/test_articles.py`

### 任务 P7.1：实现文章系统

1. 确定文章来源：Markdown 文件、结构化 JSON 或数据库。
2. 渲染 `/articles`。
3. 渲染 `/articles/<slug>`。
4. 添加唯一标题和 meta description。
5. 添加指向相关工具页的内链。

### 任务 P7.2：发布第一批内容

1. 起草至少 10 篇基础解释文章。
2. 起草至少 10 篇搜索意图文章。
3. 起草至少 5 篇转化辅助文章。
4. 审查薄内容、重复 AI 句式和夸大表达。
5. 在需要的位置添加文化说明或 responsible-use 提示。

### 任务 P7.3：实现 sitemap 和 robots

1. 包含英文路由。
2. 包含繁体路由。
3. 包含文章 URL。
4. 排除 admin、API、debug URL。
5. 增加预期 URL 测试。

### 任务 P7.4：准备 Search Console 和 AdSense 清单

1. 确认域名所有权验证方式。
2. 准备 sitemap 提交。
3. 准备 AdSense 审核清单。
4. 确认 Privacy、Terms、Disclaimer、About、Contact 全站可达。
5. 确认没有空白或占位法律页。

**验证命令：**

```powershell
pytest tests/test_sitemap.py tests/test_robots.py tests/test_articles.py -q
```

**人工验收：**

1. 访问 `/sitemap.xml`。
2. 访问 `/robots.txt`。
3. 随机访问 5 篇文章。
4. 确认页脚法律入口。

**验收标准：**

- 至少 25 个英文文章页面上线或进入待上线状态。
- sitemap 和 robots 有效。
- 英文法律页完整。
- AdSense 准备清单完成。

**进度日志：**

- 待记录

## 11. P8 商业化预验证与上线复盘

**目标：** 在真实投入广告、支付或内容扩量前，完成平台政策、收款主体、单位经济模型和运营数据闭环。

**涉及文件：**

- 新建：`docs/business/payment-platform-verification.md`
- 新建：`docs/business/unit-economics-model.md`
- 新建：`docs/business/adsense-readiness-checklist.md`
- 新建：`docs/business/monthly-business-ledger-template.md`
- 新建：`docs/business/weekly-growth-review-template.md`

### 任务 P8.1：核验支付和赞助平台

1. 实时核验 Lemon Squeezy 的政策和国家/主体支持。
2. 实时核验 Paddle 的政策和国家/主体支持。
3. 实时核验 Gumroad 的政策和国家/主体支持。
4. 实时核验 Ko-fi 和 Buy Me a Coffee 的赞助可行性。
5. 记录来源 URL、核验日期、账户要求、限制品类、提现路径、费用、webhook 支持和拒绝风险。

### 任务 P8.2：选择第一条收款路径

1. 选择首选平台。
2. 选择备用平台。
3. 定义无支付 fallback：AdSense + 赞助。
4. 定义不启动付费报告的条件。

### 任务 P8.3：建立单位经济模型

1. 价格：USD 2.99 和 USD 4.99 两种场景。
2. 支付手续费。
3. Merchant of Record 费用或税务处理。
4. AI 生成成本。
5. 服务器成本摊销。
6. 5%-10% 退款预留。
7. 单单净利润。
8. 盈亏平衡订单数。

### 任务 P8.4：准备上线数据指标

1. 定义周度指标：
   - 自然搜索展示。
   - 自然搜索点击。
   - 工具使用次数。
   - 结果生成次数。
   - 赞助点击次数。
   - checkout 点击次数。
   - 付费订单数。
   - AI 成本。
   - 服务器成本。
2. 不收集不必要的敏感个人数据。
3. 明确记录出生信息的处理方式。

### 任务 P8.5：四周运营复盘

1. 连续记录 4 周增长数据。
2. 复盘文章流量。
3. 复盘工具使用。
4. 复盘 AdSense 准备状态或审核结果。
5. 复盘赞助和付费墙点击。
6. 判断是否从 20 条英文签文扩展到 384 条。
7. 判断是否上线真实付费报告。

**验收标准：**

- 至少两个变现平台完成当期核验。
- 单位经济模型为正，或明确阻止上线。
- 未完成政策和提现可行性前，不上线真实付费报告。
- 四周复盘数据足够支持下一阶段判断。

**进度日志：**

- 待记录

## 12. 建议提交顺序

为了让开发进度可追踪，建议使用小提交：

已完成：

1. `f8681b2 docs: add Wise Oracle execution plan`
2. `3a4a25e feat(i18n): 实现简繁双语基础设施与内容层繁体化`
3. `d66fad4 Complete traditional Chinese huangli localization`

后续建议：

1. `docs: finalize English product spec and termbase`
2. `data: add reviewed English oracle and almanac sample data`
3. `test: add English route and content contract tests`
4. `feat: add English route skeleton and legal pages`
5. `feat: add English oracle service and API`
6. `feat: add English almanac terminology and API`
7. `feat: add English birth chart API boundaries`
8. `feat: add English Wise Oracle frontend pages`
9. `feat: add commerce feature flags and disabled placeholders`
10. `feat: add SEO article and sitemap support`
11. `docs: add payment verification and unit economics`

## 13. 推荐实施顺序

1. P1 已完成，不再返工繁体基础设施；后续只修复实际缺陷。
2. P2-P5 英文站改造的实施顺序、工作包依赖和并行策略见 `docs/plans/2026-06-27-english-site-execution-plan.md` 第 3 节工作包总览（W0-W8）。
3. P6 等英文结果页存在后再做，因为赞助和付费墙需要真实结果场景。
4. P7 必须早于 AdSense 申请，因为广告审核依赖信任页和内容完整度。
5. P8 必须早于真实支付上线，因为平台政策和单位经济模型可能直接阻止付费产品发布。

## 14. 待确认决策

> 英文站改造的决策门 D1-D12 已迁移至 `docs/plans/2026-06-27-english-site-execution-plan.md` 第 2 节。以下为总纲层面的遗留决策同步。

| 决策 | 状态 | 备注 |
| --- | --- | --- |
| D1 英文主品牌 `Wise Oracle` | 已确认 | — |
| D2 `/` 切英文首页 | 已确认 | 英文首页完成前保持当前跳转 |
| D3 英文文章系统存储方式 | 待确认 | Markdown / JSON manifest / 数据库 |
| D4 英文算事用稳定哈希 | 已确认 | — |
| D5 第一轮 20 条英文签文 | 已确认 | — |
| D6 神煞名音译+解释 | 已确认 | — |
| D7 彭祖百忌第一轮 summary | 已确认 | — |
| D8 Deep Reading 首测价格 | 待确认 | USD 2.99 / 4.99 |
| D9 先做模拟 checkout | 已确认 | — |
| D10 第一阶段不做邮件订阅 | 已确认 | — |
| D11 是否弱化 Birth Chart 入口 | 待确认 | 隐私合规复杂度 |
| D12 API 前缀 `/api/en/*` | 已确认 | — |
| D13 英文签文字段是否沿用 GUA_COLUMNS | 已确认 | 沿用 GUA_COLUMNS（11 字段），用户 2026-06-30 拍板 |
| D14 fortune/gua_type 字段在英文加载时剔除还是保留不展示 | 已确认 | 加载时剔除，用户 2026-06-30 拍板 |
| D15 英文数据走 JSON 内存加载，不入数据库 | 已确认 | 用户定调；英文签文从 `oracle_signs_en.json` 加载，中文仍走 `database.py` |
| D16 卦属/吉凶在三语前端均不展示 | 已确认 | 基于考据（`docs/research/zhuge-origin-research.md`），硬约束 |
| D17 解签定位为 interpretation 而非 answer | 已确认 | 基于考据，硬约束 |

## 15. 考据结论对实施的影响

本节引用 `docs/research/zhuge-origin-research.md` 的考据结论，明确对项目实施的影响。考据结论已列为硬约束（见第 0 节执行边界第 8 条）。

### 15.1 卦属/吉凶从产品中彻底删除

- **不是降级、不是标注层累、不是参考倾向**，而是删除。
- 英文版**不应**出现 `fortune`/`gua_type` 字段；`oracle_signs_en.json` 中的这两个字段在加载到内存时应剔除（D14 倾向确认）。
- 简繁前端已删除展示（4.5 节已实施）；英文前端实施时不得引入。
- 后端 `divination.py` 的 `/get_gua_info` 仍返回 `fortune`/`gua_type`，服务于中文存量逻辑；英文 API 不复用该响应结构。

### 15.2 解签定位为 interpretation

- `interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general` 字段定位为"文化视角的诠释"，不是"标准答案"。
- responsible-use 提示应强调 "reflection prompt" 性质。
- 英文翻译时避免 `accurate prediction`、`guaranteed result` 等强承诺措辞。

### 15.3 逐字显现动画已落地

- `main.js` 的 `typeWriter`（chunkSize=1, interval=50）已实现"一字一字蹦出来"的查字过程模拟。
- 尊重 `prefers-reduced-motion: reduce`，无障碍兼容。
- 英文前端实施时复用同一动画机制，不需要额外工作。

### 15.4 多视角诠释已天然满足

- 现有 `career/wealth/love/health/study/general` 6 分项结构天然满足考据 4.2 节"允许多种解读并存"的要求。
- 不需要重构字段结构。
- 英文版沿用同一结构。

---

## 16. 修订记录

| 日期 | 修订人 | 变更内容 | 原因 |
| --- | --- | --- | --- |
| 2026-06-30 | 助手 | 总纲对齐现状：回填 P1 卦属/吉凶删除实施、W2.1 签文翻译超额完成、考据结论入硬约束；新增 D13-D17 决策门；新增第 15 节考据影响 | 总纲落后于实际进度，避免认知偏差 |
