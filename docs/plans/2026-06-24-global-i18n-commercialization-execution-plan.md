# Wise Oracle 多语言化与商业化实施计划

**目标：** 将当前中文为主的诸葛神算 V4，改造为支持繁体中文、英文主站、SEO 内容、合规页面与商业化验证的可上线产品。

**总体方案：** 先完成繁体化与英文产品方案定稿，再准备英文数据与内容，随后按“后端能力、前端体验、商业化组件、SEO 合规、运营复盘”的顺序推进。每个阶段都必须能追踪进度、验证结果、记录风险，不把战略判断留在口头讨论中。

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
3. "算事""论命""黄历"的英文版不是直译，要做产品交互、术语体系、文化表达和风险边界重写。
4. 商业化代码必须可配置、可关闭、可替换；真实支付上线前必须完成平台政策与主体可行性核验。
5. 所有涉及预测、命运、健康、投资、法律、心理治疗、重大人生决策的文案，必须明确限定为娱乐、传统文化探索与自我反思参考。
6. 每个阶段必须更新进度表，并留下测试、截图、文档或人工验收记录。
7. OpenCC 只作为离线构建工具使用，用于生成繁体参考数据或构建产物；网站运行时不应依赖 OpenCC 初始化转换器。

## 1. 总进度追踪表

| 阶段 | 目标 | 状态 | 负责人 | 完成日期 | 验收证据 |
| --- | --- | --- | --- | --- | --- |
| P0 | 项目现状审计与术语冻结 | 未开始 | 待定 | 待定 | 审计记录、术语表 |
| P1 | 繁体中文改造 | 未开始 | 待定 | 待定 | `/zh-hans/*` 与 `/zh-hant/*` 核心页面可用 |
| P2 | 英文产品方案定稿 | 未开始 | 待定 | 待定 | 英文信息架构、术语、交互、免责声明定稿 |
| P3 | 英文数据准备 | 未开始 | 待定 | 待定 | 前 20 条签文样本、内容清单、合规草稿 |
| P4 | 英文后端改造 | 未开始 | 待定 | 待定 | 英文 API、路由、SEO 元数据测试通过 |
| P5 | 英文前端改造 | 未开始 | 待定 | 待定 | 英文三大工具页桌面和移动端验收通过 |
| P6 | 商业化基础代码 | 未开始 | 待定 | 待定 | 配置开关、赞助入口、付费墙原型、订单模型设计 |
| P7 | SEO 与合规上线准备 | 未开始 | 待定 | 待定 | sitemap、robots、法律页、Search Console 清单 |
| P8 | 商业化预验证与上线复盘 | 未开始 | 待定 | 待定 | 平台核验表、单位经济模型、4 周运营台账 |

状态枚举：

- 未开始
- 进行中
- 阻塞
- 待验收
- 已完成

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

| 中文功能 | 英文定名 | 禁用表达 |
| --- | --- | --- |
| 诸葛神算 / 算事 | Ask the Oracle | guaranteed fortune telling, accurate prediction |
| 黄历 | Daily Chinese Almanac | Yellow Calendar |
| 论命 / 八字 | Birth Chart Reading | fate guarantee, life prediction |
| 付费报告 | Wise Oracle Deep Reading | destiny changing report |
| 宜 | Favorable Activities | lucky commands |
| 忌 | Unfavorable Activities | doomed actions |

统一英文免责声明：

```text
For entertainment, cultural exploration, and self-reflection only. Not medical, legal, financial, psychological, or life-critical advice.
```

统一繁体免责声明：

```text
本服務僅供娛樂、傳統文化探索與自我反思參考，不構成醫療、法律、財務、心理治療或重大人生決策建議。
```

### 2.3 商业化优先级

1. 先完成可被 AdSense 审查的网站基础：英文页面、原创内容、合规页、sitemap、robots、Search Console。
2. 并行设计 `Wise Oracle Deep Reading`，但真实支付上线必须等待平台政策和主体核验。
3. 赞助入口作为低风险补充，但不能暗示赞助会让结果更准。
4. 第一阶段不做人工咨询。
5. 第一阶段不做复杂会员、订阅或完整用户账号系统。

## 3. P0 项目现状审计与术语冻结

**目标：** 在动代码前确认现有路由、API、模板、测试、部署路径和高风险文案，冻结第一轮术语表。

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
- 新建：`docs/business/wise-oracle-risk-copy-review.md`

**执行步骤：**

1. 运行 `rg -n "算命|预测|发财|投资|疾病|医疗|法律|准确|保证|改命|运势" frontend zhugeshensuan docs`。
2. 把高风险文案记录到 `docs/business/wise-oracle-risk-copy-review.md`。
3. 运行 `rg -n "@.*route|Blueprint|get\\(|post\\(" zhugeshensuan`。
4. 列出现有页面路由和 API 端点。
5. 阅读现有模板，判断是否需要抽取共享页面骨架。
6. 创建 `docs/business/wise-oracle-termbase.md`，字段包含：简体、繁体、英文、使用场景、禁用表达。
7. 运行 `rg -n "正在|加载|请输入|请选择|失败|成功|未知|错误" frontend/static/js`，列出 main.js / huangli.js / lunming.js 的全部硬编码中文字符串清单，为统一字典方案做准备。
8. 确认 OpenCC 只存在于构建脚本或一次性数据生成脚本中；如果运行时代码导入 OpenCC，需要改为读取已生成的繁体数据或使用项目内静态字典。
9. 运行 `rg -n "error.*message|message.*=" zhugeshensuan/blueprints`，标记后端 API 错误消息的语言（当前为简体中文），登记为 P4 显性债务：P4 英文后端改造时统一为所有错误增加 `code` 字段，前端按 code 映射多语言消息。
10. 将 P0 状态更新为“待验收”。

**已验证事项（无需再审计）：**

- DB 笔画查询支持繁体字输入：`hanzi` 表同时存储简繁（18620 条，7456 条有 traditional_strokes），查询优先返回 `kangxi_strokes`，康熙笔画对简繁统一。详见 `docs/plans/p1-technical-analysis-2026-06-24.md` 难点 4。

**验证命令：**

```powershell
pytest
```

预期：现有测试在正式实施前全部通过。

**进度日志：**

- 待记录

## 4. P1 繁体中文改造

**目标：** 完成本项目的“繁体”化改造，让港澳台及海外华人用户可以通过 `/zh-hant/almanac`、`/zh-hant/divination`、`/zh-hant/bazi` 访问核心功能。

**范围：** 第一轮只做核心页面和核心交互，不做繁体文章系统，不删除简体旧入口。

**涉及文件：**

- 修改：`zhugeshensuan/blueprints/pages.py`
- 修改：`frontend/templates/index.html`
- 修改：`frontend/templates/huangli.html`
- 修改：`frontend/templates/suanshi.html`
- 修改：`frontend/templates/lunming.html`
- 修改：`frontend/static/js/huangli.js`
- 修改：`frontend/static/js/lunming.js`
- 修改：`frontend/static/js/main.js`
- 新建：`frontend/static/js/lang/dictionary.json`
- 新建：`frontend/static/js/lang/i18n.js`
- 新建：`frontend/static/js/lang/lang_switcher.js`
- 新建或修改：`scripts/build_hant_db.py`
- 修改：`scripts/build_reference_db.py`
- 修改：`frontend/static/css/style.css`
- 修改：`frontend/static/css/style_mobile.css`
- 测试：`tests/test_frontend_contract.py`
- 测试：`tests/test_api.py`

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
4. 在页脚或结果区域展示对应语言免责声明。
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

**验证命令：**

```powershell
pytest tests/test_frontend_contract.py tests/test_api.py -q
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
- 没有新增高风险文案。
- 网站运行时不依赖 OpenCC 初始化转换器。
- 当前测试通过。

**进度日志：**

- 待记录

## 5. P2 英文产品方案定稿

**目标：** 对“算事”“论命”“黄历”英语化做出完整、可确认、可交给开发执行的定稿方案。

**涉及文件：**

- 新建：`docs/business/wise-oracle-english-product-spec.md`
- 新建：`docs/business/wise-oracle-copy-style-guide.md`
- 新建：`docs/business/wise-oracle-report-tiering.md`
- 修改：`docs/plans/2026-06-24-global-i18n-commercialization-execution-plan.md`

### 任务 P2.1：定稿英文信息架构

1. 记录每个英文 URL。
2. 为每个页面定义页面目的、主按钮、次级按钮、SEO 标题、meta description 和免责声明位置。
3. 确认 `/` 作为英文首页，旧中文路由保持兼容。
4. 把仍未确定的问题记录到“决策日志”。

### 任务 P2.2：定稿 Ask the Oracle 交互

1. 定义两种输入模式：自由提问、三个数字。
2. 安全示例使用：`What should I reflect on before making this decision?`
3. 禁止使用投资、疾病、诉讼、彩票、考试保证、移民结果作为示例。
4. 定义校验规则：自由提问最短长度、最长长度、高风险提示、三个数字范围 `0-999`。
5. 定义结果字段：`oracle_title`、`message`、`guidance_summary`、`caution`、`responsible_use`。

### 任务 P2.3：定稿 Birth Chart Reading 边界

1. 页面命名为 `Birth Chart Reading`。
2. 定位为 BaZi-inspired cultural self-reflection。
3. 现有八字计算只作为基础盘生成能力。
4. AI 只作为解释与表达层。
5. 定义免费结果和未来付费结果的边界。
6. 禁止医疗、法律、财务、心理治疗、生育、死亡、灾难和重大人生决策承诺。

### 任务 P2.4：定稿 Daily Chinese Almanac 边界

1. 页面命名为 `Daily Chinese Almanac`。
2. 标签使用 Favorable Activities、Unfavorable Activities、Lunar Date、Solar Term、Chinese Zodiac。
3. 禁用 `Yellow Calendar`。
4. `Daoist Auspicious Calendar` 只在解释文章里谨慎使用，且必须有准确背景。
5. 场景包括 wedding、moving、business opening、travel、signing、haircut。

### 任务 P2.5：定稿商业化分层

1. 定义免费内容。
2. 定义 `Wise Oracle Deep Reading` 付费内容。
3. 定义赞助文案。
4. 定义付费墙文案。
5. 定义价格测试候选：USD 2.99 和 USD 4.99。
6. 定义真实支付上线的 Go / No-Go 清单。

**验收标准：**

- 产品规格中不再有第一版路由命名的待定项。
- 文案风格指南包含可用表达和禁用表达。
- 报告分层清楚区分免费、付费、赞助。
- 不读代码也能确认 P2 是否通过。

**进度日志：**

- 待记录

## 6. P3 英文数据准备

**目标：** 对已经定稿的方案做前期数据准备，先完成样本，再批量扩展。

**涉及文件：**

- 新建：`data/content/oracle_signs_en_sample.json`
- 新建：`data/content/oracle_signs_en_review_checklist.md`
- 新建：`data/content/articles/articles_manifest.json`
- 新建：`docs/business/wise-oracle-seo-content-briefs.md`
- 新建：`docs/business/wise-oracle-legal-page-drafts.md`
- 测试：`tests/test_english_content_data.py`

### 任务 P3.1：准备前 20 条英文签文样本

1. 从参考数据库导出或标记前 20 条中文源签文。
2. 每条签文创建结构化字段：
   - `sign_number`
   - `oracle_title`
   - `message`
   - `guidance`
   - `caution`
   - `seo_summary`
   - `risk_notes`
3. 语言保持神秘但克制。
4. 删除 `guaranteed`、`fated`、`cure`、`investment`、`lawsuit win`、`death`、`curse` 等高风险词。
5. 人工复核全部 20 条。

### 任务 P3.2：增加数据校验测试

1. 测试必填字段。
2. 测试签号范围。
3. 测试空字符串。
4. 测试禁用高风险词。
5. 运行 `pytest tests/test_english_content_data.py -q`。

### 任务 P3.3：准备 SEO 文章简报

1. 先创建 25 篇文章简报，再写正文。
2. 每篇简报包含 slug、标题、搜索意图、目标内链、免责声明需求和转化入口。
3. 简报分组：
   - 10 篇基础解释文章。
   - 10 篇搜索意图文章。
   - 5 篇转化辅助文章。
4. 简报未审核前，不批量生成正文。

### 任务 P3.4：起草合规和信任页面

1. 起草 Privacy Policy。
2. 起草 Terms of Use。
3. 起草 Disclaimer。
4. 起草 About。
5. 起草 Contact。
6. 标注为非律师草稿，正式上线前待专业复核。

**验证命令：**

```powershell
pytest tests/test_english_content_data.py -q
```

**验收标准：**

- 20 条英文签文结构化且可审阅。
- 禁用词测试能捕获高风险文案。
- 25 篇文章简报准备完成。
- 合规页面草稿存在且符合项目风险边界。

**进度日志：**

- 待记录

## 7. P4 英文后端改造

**目标：** 构建英文版后端能力：英文路由、英文算事输入算法、英文黄历输出适配、英文论命输入边界和 SEO 页面支持。

**涉及文件：**

- 修改：`zhugeshensuan/blueprints/pages.py`
- 修改：`zhugeshensuan/blueprints/divination.py`
- 修改：`zhugeshensuan/blueprints/huangli_api.py`
- 修改：`zhugeshensuan/blueprints/lunming_api.py`
- 新建：`zhugeshensuan/i18n.py`
- 新建：`zhugeshensuan/oracle_english.py`
- 新建：`zhugeshensuan/content.py`
- 新建：`zhugeshensuan/seo.py`
- 测试：`tests/test_english_routes.py`
- 测试：`tests/test_oracle_english.py`
- 测试：`tests/test_seo_pages.py`

### 任务 P4.1：新增英文路由测试

1. 测试 `/`、`/daily-almanac`、`/ask-oracle`、`/birth-chart-reading`、`/articles`、`/privacy`、`/terms`、`/disclaimer`、`/about`、`/contact`。
2. 断言 HTTP 200。
3. 断言英文页面不出现仅属于简体中文首页的标题。
4. 运行测试并确认先失败。

### 任务 P4.2：实现英文页面路由

1. 在 `pages.py` 添加路由处理。
2. 返回英文模板。
3. 保持简体和繁体路由不变。
4. 运行路由测试。

### 任务 P4.3：实现文本到签号算法

1. 新建 `zhugeshensuan/oracle_english.py`。
2. 对英文文本做小写、空白整理和稳定 Unicode 处理。
3. 空输入和过短输入返回明确错误。
4. 映射到 `1-384`，或在确认数据库实际范围后映射到真实可用签号范围。
5. 使用稳定哈希，不使用 Python 进程随机化的 `hash()`。
6. 增加确定性、范围、空白归一、边界输入测试。

### 任务 P4.4：实现三数字算法

1. 接收且只接收三个整数。
2. 每个数字范围为 `0-999`。
3. 使用文档化公式映射到有效签号范围。
4. 增加最小值、最大值、非法类型、缺失数字、确定性结果测试。

### 任务 P4.5：新增英文算事 API

1. 新增接口，例如 `POST /api/oracle/ask`。
2. 支持 payload：
   - `{ "mode": "question", "question": "..." }`
   - `{ "mode": "numbers", "numbers": [12, 345, 678] }`
3. 返回英文签文结构化字段。
4. 非法输入返回稳定错误码。
5. 保持现有 `/calculate_sign` 和 `/get_gua_info` 不变，继续服务中文页面。

### 任务 P4.6：新增英文黄历适配

1. 保持现有 `/api/huangli` 兼容。
2. 增加 `lang=en` 支持，或在更清晰时新增英文接口。
3. 将中文场景标签映射到英文场景标签。
4. 返回英文展示字段，同时保留原始数据。
5. 增加日期校验和场景校验测试。

### 任务 P4.7：新增英文内容加载能力

1. 加载文章 manifest。
2. 加载文章正文来源。
3. 未知 slug 返回 404。
4. 增加 SEO 元数据辅助函数。
5. 增加文章列表、详情、canonical、标题唯一性测试。

**验证命令：**

```powershell
pytest tests/test_english_routes.py tests/test_oracle_english.py tests/test_seo_pages.py -q
pytest -q
```

**验收标准：**

- 英文路由可用。
- 英文算事不要求输入汉字。
- 现有中文 API 保持兼容。
- 测试覆盖算法确定性。
- SEO 页面可以渲染元数据。

**进度日志：**

- 待记录

## 8. P5 英文前端设计与改造

**目标：** 设计并改造现有前端，建立英文 Wise Oracle 主站、三个英文工具页、繁体入口和核心商业转化位置。

**涉及文件：**

- 新建：`frontend/templates/base.html`
- 新建：`frontend/templates/en/index.html`
- 新建：`frontend/templates/en/daily_almanac.html`
- 新建：`frontend/templates/en/ask_oracle.html`
- 新建：`frontend/templates/en/birth_chart_reading.html`
- 新建：`frontend/templates/en/articles.html`
- 新建：`frontend/templates/en/article_detail.html`
- 新建：`frontend/templates/en/privacy.html`
- 新建：`frontend/templates/en/terms.html`
- 新建：`frontend/templates/en/disclaimer.html`
- 新建：`frontend/templates/en/about.html`
- 新建：`frontend/templates/en/contact.html`
- 新建：`frontend/static/js/ask_oracle_en.js`
- 新建：`frontend/static/js/daily_almanac_en.js`
- 新建：`frontend/static/js/birth_chart_en.js`
- 新建：`frontend/static/css/wise_oracle.css`
- 修改：仅在共享布局确实需要时改动现有 CSS。

### 任务 P5.1：确定视觉方向

1. 视觉语气保持东方文化、克制、清晰、可信。
2. 避免紫色渐变、装饰光球、过暗神秘风。
3. 使用清晰的工具优先布局。
4. 首屏展示真实可用的工具或产品，不做空泛营销页。

### 任务 P5.2：创建英文首页

1. H1 使用 `Wise Oracle`。
2. 主按钮指向 `/ask-oracle`。
3. 次级按钮指向 `/daily-almanac`。
4. 展示简短 responsible-use 提示。
5. 提供三大工具页和文章页内链。

### 任务 P5.3：创建 Ask the Oracle 页面

1. 增加自由提问和三数字模式切换。
2. 增加校验状态。
3. 增加加载状态。
4. 渲染 `oracle_title`、`message`、`guidance_summary`、`caution`。
5. 只在免费结果之后展示克制的赞助或付费墙占位。
6. 在结果附近展示免责声明。

### 任务 P5.4：创建 Daily Chinese Almanac 页面

1. 增加日期选择器。
2. 增加场景筛选。
3. 渲染 Favorable Activities 和 Unfavorable Activities。
4. 在可用时渲染 lunar date、solar term、zodiac。
5. 页面说明不做确定性承诺。

### 任务 P5.5：创建 Birth Chart Reading 页面

1. 复用现有论命流程的必要交互。
2. 文案使用 birth chart insight、self-reflection 等谨慎表达。
3. 保持输入隐私提示可见。
4. 明确展示 AI 生成和加载状态。
5. 不承诺准确预测或命运结论。

### 任务 P5.6：创建合规和信任页面

1. 根据已审核草稿渲染 Privacy、Terms、Disclaimer、About、Contact。
2. 每个英文页面页脚都能进入这些页面。
3. Contact 上线前必须有真实联系方式，或明确标记待补齐。

### 任务 P5.7：响应式和可访问性检查

1. 测试桌面宽度。
2. 测试移动端宽度。
3. 确认没有横向溢出。
4. 确认控件有 label。
5. 确认键盘焦点可见。
6. 确认错误信息不只依赖颜色表达。

**验证命令：**

```powershell
pytest tests/test_frontend_contract.py tests/test_english_routes.py -q
```

**人工验收页面：**

1. `/`
2. `/ask-oracle`
3. `/daily-almanac`
4. `/birth-chart-reading`
5. `/articles`
6. `/privacy`
7. `/terms`
8. `/disclaimer`
9. `/about`
10. `/contact`

**验收标准：**

- 英文首屏可用，不只是宣传。
- 工具交互具备加载、空状态、错误、结果状态。
- 移动端不裁切、不重叠。
- 法律和免责声明入口全站可达。

**进度日志：**

- 待记录

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
5. 在需要的位置添加免责声明或 responsible-use 提示。

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

1. `docs: add Wise Oracle execution plan`
2. `docs: add termbase and copy risk review`
3. `feat: add zh-hans and zh-hant routes`
4. `feat: add Traditional Chinese templates`
5. `docs: finalize English product spec`
6. `data: add English oracle sample content`
7. `feat: add English oracle service`
8. `feat: add English Wise Oracle pages`
9. `feat: add commerce feature flags`
10. `feat: add SEO article and sitemap support`
11. `docs: add payment verification and unit economics`

## 13. 推荐实施顺序

1. 先做 P0，避免误改现有路由、API 和模板。
2. 再做 P1，用繁体中文页面验证多语言路由和模板组织方式。
3. P2 必须早于英文代码，因为产品语言会影响 API 字段、模板、SEO 和商业化文案。
4. P3 早于批量开发，因为内容结构会反过来决定后端契约。
5. P4 和 P5 按小垂直切片推进：一个路由、一个 API、一个模板、一个测试。
6. P6 等英文结果页存在后再做，因为赞助和付费墙需要真实结果场景。
7. P7 必须早于 AdSense 申请，因为广告审核依赖信任页和内容完整度。
8. P8 必须早于真实支付上线，因为平台政策和单位经济模型可能直接阻止付费产品发布。

## 14. 待确认决策

1. 是否确认英文主品牌为 `Wise Oracle`。
2. 是否确认 `/` 改为英文首页，旧中文首页改由 `/huangli` 或后续 `/zh-Hans/` 承接。
3. 繁体中文第一轮是否只做核心工具页，不做繁体文章。
4. 英文文章系统使用 Markdown 文件、JSON manifest，还是数据库。
5. 英文算事文本映射使用稳定哈希还是字符权重公式。
6. 第一轮英文签文样本是 20 条还是 50 条。
7. `Wise Oracle Deep Reading` 首测价格优先 USD 2.99 还是 USD 4.99。
8. 是否先只做模拟 checkout，等平台政策核验后再接真实 checkout link。
9. 是否需要邮件订阅作为第一阶段留存能力。
10. 是否在第一阶段弱化 `Birth Chart Reading` 的入口，避免隐私和合规复杂度过高。
