# Wise Oracle 全球英语出海商业化计划

状态：草案 v2，待审查，未实施  
创建日期：2026-06-24  
修订说明：吸收 `business/Wise_Oracle_Outbound_Plan.md` 中关于英文交互、本地化、SEO 内容、赞助、Merchant of Record、增长渠道和财务闭环的可取部分。  
项目：诸葛神算 V3 / getwiseoracle.com  
计划文件：`business/2026-06-global-commercialization-plan.md`

## 1. 计划目标

本计划的目标是把当前中文为主的诸葛神算网站，逐步升级为面向全球英语用户的商业化内容站和东方占卜工具站。

第一阶段不追求一次性重构完整商业系统，而是优先验证五件事：

1. 英语市场是否能通过 SEO 获得稳定自然流量。
2. Google AdSense 是否能通过审核并产生基础广告收入。
3. 东方占卜、黄历、诸葛神算、八字文化是否能以英文表达被海外用户理解和接受。
4. 最小付费闭环是否可行：用户是否愿意为更深报告、保存结果、行动建议或赞助付费。
5. 海外收款链路是否可行：AdSense、赞助平台、Merchant of Record、税务资料和银行入账是否能组成可执行路径。

第一阶段明确不做以下事项：

1. 不做 FastAPI 全量迁移。
2. 不做前后端分离重构。
3. 不把直接支付系统做成第一阶段上线前置条件。
4. 不上线人工大师咨询。
5. 不把高级 AI 报告做成复杂会员系统。

第一阶段必须并行完成以下商业设计：

1. 明确免费结果和付费结果的分层。
2. 明确首个可售数字产品。
3. 明确候选收款渠道和拒绝条件。
4. 明确一次交易的收入、手续费、AI 成本、退款风险和净利润模型。
5. 明确如果 AdSense 审核慢或收入低，如何通过赞助或微付费报告补齐财务闭环。

计划实施前，本文件只作为讨论和审查依据。只有在确认执行后，才开始改造代码、页面、内容和部署。

## 2. 核心定位

英文主站品牌建议使用：

`Wise Oracle`

英文定位建议使用：

`Eastern divination for self-reflection, timing, and life guidance.`

这个定位刻意避开直译式的 `Zhuge fortune telling`，原因是海外用户很难理解诸葛亮、签文、黄历、干支、三字起卦等文化背景。更容易被接受的表达是：

1. Eastern oracle
2. Chinese almanac
3. I Ching-inspired guidance
4. BaZi-inspired birth chart insight
5. self-reflection
6. timing
7. cultural exploration

所有页面和报告必须坚持一个边界：这是传统文化、娱乐参考和自我反思工具，不是医疗、法律、投资、心理治疗、移民、考试、赌博、彩票或人生重大决策建议。

统一英文免责声明建议为：

`For entertainment, cultural exploration, and self-reflection only. Not medical, legal, financial, psychological, or life-critical advice.`

统一繁体免责声明建议为：

`本服務僅供娛樂、傳統文化探索與自我反思參考，不構成醫療、法律、財務、心理治療或重大人生決策建議。`

## 3. 产品与财务闭环原则

这个项目不是公益项目。内容、SEO 和 AdSense 只是获客与底层收入方式，最终必须能形成可复用的商业闭环。

第一阶段采用“双轨验证”：

1. 流量轨：英文内容、SEO、Search Console、AdSense 审核。
2. 变现轨：赞助入口、首个高级报告产品、候选收款渠道、订单解锁方案、单位经济模型。

免费内容不能只做成完整替代品，否则用户没有付费理由。建议采用以下分层：

1. 免费层：展示核心签名、基础解释、文化背景、简短提醒。
2. 付费层：展示更完整的行动建议、场景化解读、时间窗口、可保存报告、PDF 或邮件副本。
3. 赞助层：不解锁功能，只作为自愿支持。
4. 人工咨询层：第三阶段以后再考虑，不能作为第一阶段收入前置条件。

首个可售产品建议是（⚠️ 暂时冻结）：

> **暂时冻结（2026-06-30）**：Deep Reading 付费产品定义暂时冻结。用户决策：暂时不作为付费产品，是否付费、怎么付费待深度思考后决定。以下定义仅作为历史参考。

`Wise Oracle Deep Reading`

产品内容：

1. 一次完整英文 oracle reading。
2. 一个诗性但克制的 oracle title。
3. 当前处境解读。
4. 3 条具体行动建议。
5. 7-30 天反思重点。
6. 明确 responsible use 免责声明。

首轮价格测试：

1. USD 2.99：冲动型微付费，适合算事结果页。
2. USD 4.99：标准深度报告，适合默认测试价。
3. USD 9.99：更长报告或 PDF/邮件副本，第二轮再测试。

第一阶段不一定立刻上线支付，但必须完成可实施设计：

1. 选择 2-3 个候选收款平台。
2. 明确每个平台是否支持中国个人或可行主体。
3. 明确平台是否接受 digital self-reflection / cultural insight 类产品。
4. 明确手续费、提现方式、税务资料、退款和争议处理。
5. 明确 webhook、checkout link 或手动交付的最小实现方式。
6. 明确如果支付平台拒绝该品类，是否退回 AdSense + 赞助路线。

## 4. 技术路线决策

### 4.1 第一阶段保留 Flask

当前项目第一阶段建议继续使用 Flask，而不是迁移 FastAPI。

主要原因：

1. 当前项目本质是内容站 + 工具站 + 少量 API，不是 API-first 平台。
2. 现有代码已经围绕 Flask 建立了页面路由、Jinja 模板、Blueprint、安全响应头、健康检查、SSE 流式输出、测试和 Docker/Gunicorn 部署。
3. 多语言能力不是 FastAPI 的根本优势。多语言真正依赖 URL 设计、文案管理、canonical、hreflang、sitemap、模板结构和翻译质量。
4. FastAPI 的优势主要体现在强类型 API、自动 OpenAPI、异步 I/O、前后端分离、移动端 API、复杂账户与订单系统。当前第一阶段最关键的是 SEO、AdSense、合规和英文内容。
5. 现在迁移 FastAPI 会推迟商业验证，而且不会直接提升海外流量、AdSense 审核成功率或用户理解度。

因此第一阶段原则是：

1. Flask 继续承载官网、工具页、SEO 内容页和当前 API。
2. 新增功能时尽量把业务逻辑放在 service 层，避免和 Flask 强绑定。
3. API 输入输出逐步结构化，为未来迁移或拆分预留空间。
4. 不为了“技术更现代”而重构。

### 4.2 未来何时考虑 FastAPI

只有当项目进入以下阶段时，才重新评估 FastAPI：

1. 需要用户账户、登录、订单、订阅。
2. 需要支付 webhook、报告订单状态、用户历史报告。
3. 需要移动 App 或第三方 API。
4. 需要后台 CMS、运营后台或多角色管理。
5. 需要大量异步任务、队列、模型调用编排。
6. 前端准备迁移到 React、Next.js、Vue 等前后端分离架构。

即便未来需要 FastAPI，也建议优先采用渐进式方案：

1. Flask 继续承载官网、SEO 页面、工具页。
2. 新建 FastAPI 子服务承载账户、订单、支付、报告 API。
3. 当 API 复杂度真正上升后，再考虑更完整的迁移。

## 5. 语言策略

第一阶段语言策略：

1. 英文作为默认主站语言。
2. 繁体中文作为第二语言。
3. 简体中文旧入口先保留兼容，不作为海外主入口。

建议 URL：

1. 英文首页：`/`
2. 英文黄历：`/daily-almanac`
3. 英文算事：`/ask-oracle`
4. 英文论命：`/birth-chart-reading`
5. 英文文章：`/articles/<slug>`
6. 繁体首页：`/zh-Hant/`
7. 繁体黄历：`/zh-Hant/huangli`
8. 繁体算事：`/zh-Hant/suanshi`
9. 繁体论命：`/zh-Hant/lunming`

繁体中文不是简单的简转繁。需要同时调整表达方式：

1. 避免大陆互联网式营销语。
2. 避免过度神秘化和恐吓式表达。
3. 使用更适合港澳台和海外华人的传统文化语感。
4. 将“算命”“论命”等词适度弱化为“命理參考”“文化解讀”“自我反思”。

旧中文路由处理原则：

1. `/huangli`、`/suanshi`、`/lunming` 第一阶段不删除。
2. 旧路由可以继续显示当前中文页面，避免破坏已有访问。
3. 英文和繁中页面稳定后，再决定是否把旧路由 301 到 `/zh-Hant/` 对应页面。

## 6. 产品本地化改造

英文版不能只是把中文界面翻译成英文。第一阶段必须重点改造三个核心体验：算事输入、签文表达、黄历命名。

### 6.1 英文算事输入

当前中文算事依赖“三个汉字 + 笔画数”。英语用户无法自然理解这个交互，因此英文版 `/ask-oracle` 提供两种输入：

1. 三个词：用户心中持一问题（不输入），再输入三个英文词，每词按 A=1..Z=26 字母求和后对 10 取模（余 0 取 1）映射为三数字，对应中文“三字→笔画数→笔画位”的神秘变换。
2. 三个数字：用户输入 3 个 0-999 的数字，作为无词汇门槛的起卦方式。

英文引导语建议：

`Hold one question quietly in mind. Do not type it. Take a slow breath, then enter the first three words that come to you. They may be connected to your question—or not. Do not overthink them.`

用户不在输入框键入问题文本，显著减少敏感问题文本的收集和定向回答风险（三个词仍可能组成敏感表达，不能宣称完全消除风险），同时保留“三”母题与神秘仪式感。

三词起卦算法原则（复用源书函数，实现见 `scripts/derive_original_oracle_signs.py`）：

1. 同一组三个词应得到同一个签号，保证可复现。
2. 算法要简单、可解释、无外部依赖：每词字母求和（A=1..Z=26）→ `stroke_digit`（mod 10，余 0 取 1）→ 三数字 d1/d2/d3（均 1-9）→ `compose_three_character_number`（N=100×d1+10×d2+d3）→ `reduce_to_start_index`（r=((N-1) mod 384)+1）。
3. 输入为空或词数不足时给出友好提示，不默认返回固定签。
4. 算法要写入测试，确保同输入同结果、不同输入分布合理、边界输入不会报错。
5. 示例：LOVE=54→4，WORK=67→7，FATE=32→2 → N=472 → Sign #88。

数字起卦算法原则（英文专用，非源书方法）：

1. 三个数字范围为 0-999。
2. seed = d1×1,000,000 + d2×1,000 + d3（`compose_english_three_number_seed`）；r = ((seed-1) mod 384) + 1，计算过程可解释。
3. 三组数字不能全为 0。
4. 结果页不强调“随机决定命运”，而强调“作为反思入口”。

### 6.2 384 签英文重写

384 签不应直译。要做“文化本地化 + 风格重写”。

每条英文签建议结构：

1. Oracle title：短标题，类似 oracle card 名称。
2. Message：当前处境的反思式解读。
3. Guidance：具体但不越界的行动建议。
4. Caution：风险提醒，避免医疗、法律、投资、恐吓式表达。

风格要求：

1. 保留东方 oracle 和 I Ching-inspired 气质。
2. 避免大量中国历史典故，除非文章页专门解释文化背景。
3. 避免过度 New Age 话术，如过度使用 cosmic energy、energy vampires、destiny 等。
4. 语言要神秘但克制，心理上有安抚感，行动上有具体性。
5. 每条签的英文内容要可用于 SEO 摘要、免费结果和付费报告扩展。

第一轮不必一次性上线 384 条完整重写。建议：

1. 先重写 20 条作为样本。
2. 验证页面呈现、语气、转化按钮和用户理解。
3. 再批量扩展到 384 条。
4. 批量生成后必须人工抽检高风险词、误导承诺和重复内容。

### 6.3 黄历英文包装

“黄历”不要翻译为 `Yellow Calendar`。

英文主名称建议：

`Daily Chinese Almanac`

页面内部可使用：

1. Auspicious Date Guide
2. Favorable Activities
3. Unfavorable Activities
4. Lunar Date
5. Solar Term
6. Chinese Zodiac

谨慎使用 `Daoist Auspicious Calendar`。只有在页面明确说明来源和边界时才使用，否则容易被理解成宗教权威背书。

## 7. 商业化优先级

第一阶段收入优先级：

1. Google AdSense：底层收入与内容站商业化验证。
2. 最小高级报告：验证用户是否愿意为更深解读付费。
3. 赞助/打赏：低摩擦补充收入，不与广告点击绑定。
4. SEO 自然流量：长期获客渠道。
5. 邮件列表或用户留存：为后续复购和新品测试准备。
6. 人工咨询：第三阶段以后再考虑。

财务闭环优先级不是“先做支付系统”，而是“先证明存在可卖的东西、可收的钱、可交付的结果、可控制的成本”。因此第一阶段要同时准备 AdSense 和付费报告 MVP，但付费报告是否上线取决于支付平台核验结果。

### 7.1 AdSense

AdSense 是第一阶段最适合验证的收入方式，因为它不需要马上处理复杂支付、退款、跨境税务和咨询履约。

AdSense 上线前必须完成：

1. 英文主站核心页面。
2. 至少 25 篇原创英文内容；其中 10 篇为核心解释页，10 篇为搜索意图页，5 篇为转化辅助页。
3. Privacy Policy。
4. Terms of Use。
5. Disclaimer。
6. About。
7. Contact。
8. sitemap.xml。
9. robots.txt。
10. Google Search Console 验证。

广告位原则：

1. 不靠近主要操作按钮。
2. 不伪装成导航或内容。
3. 不引导用户点击广告支持网站。
4. 不做“看广告解锁报告”。
5. 不做弹窗广告。
6. 不牺牲移动端阅读和工具使用体验。
7. 不把 AdSense 当成唯一商业模式；AdSense 只能验证基础流量变现，不能保证覆盖 AI 成本和内容成本。

### 7.2 高级 AI 报告 ——⚠️ 暂时冻结

> **暂时冻结（2026-06-30）**：Deep Reading 付费产品定义暂时冻结。用户决策：暂时不作为付费产品，是否付费、怎么付费待深度思考后决定。以下内容仅作为历史参考，不作为当前执行依据。

高级 AI 报告必须作为第一阶段并行设计项，但不一定在第一批上线。它的作用是验证"用户是否愿意为更深解释付费"，避免网站只变成低 RPM 内容站。

第一阶段推荐先做一个最小产品：

`Wise Oracle Deep Reading`

免费结果页展示：

1. Oracle title。
2. 简短 message。
3. 基础 guidance 摘要。
4. responsible use 免责声明。

付费报告展示：

1. 完整 message。
2. 3 条具体 guidance。
3. 7-30 天 reflection focus。
4. 适合复制或邮件保存的报告格式。
5. 明确说明不提供医疗、法律、财务、心理治疗和重大人生决策建议。

后续可测试产品：

1. Year Ahead Reading
2. Love & Relationship Insight
3. Career Crossroads Report
4. Auspicious Date Report
5. Compatibility Reading
6. Birth Chart Deep Report

价格测试建议：

1. 微付费报告：USD 2.99
2. 标准报告：USD 4.99
3. 深度报告：USD 9.99
4. USD 19.99 只适合后续更完整的出生盘或年度报告，不作为第一轮默认价。

上线付费前必须先确认支付平台政策。由于 psychic services、fortune telling、occult services 在部分支付平台或部分地区可能属于限制或高风险业务，产品描述应真实定位为：

1. digital self-reflection report
2. cultural insight report
3. entertainment report
4. Eastern oracle interpretation

避免使用：

1. guaranteed fortune telling
2. accurate future prediction
3. change your destiny
4. remove bad luck
5. cure illness
6. investment decision

候选支付实现优先级：

1. Merchant of Record 候选：Lemon Squeezy、Paddle、Gumroad。重点核验品类政策、国家/地区支持、提现、税务和 webhook。
2. 赞助平台候选：Ko-fi、Buy Me a Coffee。重点核验是否支持当前主体、PayPal/Stripe 绑定、提现和内容品类。
3. 直接支付候选：PayPal、Stripe。只作为后续路线，因为风控和主体要求更复杂。

最小解锁方案：

1. 优先使用 checkout link 验证购买意愿。
2. 第二步再接 webhook 自动解锁。
3. 如果 webhook 暂不做，允许先用一次性临时链接或邮件交付做小规模验证。
4. 订单数据必须最少记录：订单 ID、产品、金额、币种、支付平台、状态、创建时间、解锁 token、退款状态。

### 7.3 赞助和打赏

赞助可以作为轻量补充，但不应作为主收入。

赞助文案可以使用：

`If this reading helped you reflect, you can support Wise Oracle.`

赞助入口建议出现位置：

1. 免费算事结果页底部。
2. 文章末尾。
3. About 页面。
4. 不放在广告旁边，不放在主要工具按钮旁边。

候选平台：

1. Ko-fi。
2. Buy Me a Coffee。
3. Gumroad tip product。

禁止：

1. 将赞助和广告点击绑定。
2. 暗示赞助可以带来更准结果。
3. 暗示不赞助会影响运势。

### 7.4 人工咨询

人工咨询只能作为第三阶段或更后阶段。

上线前必须具备：

1. 咨询师身份和背景介绍。
2. 清晰服务范围。
3. 退款政策。
4. 预约流程。
5. 订单记录。
6. 风险边界。
7. 禁止医疗、投资、法律、心理治疗等承诺。

咨询定位建议为：

`Cultural interpretation and reflective guidance.`

而不是：

`Guaranteed fortune reading.`

## 8. 信息架构

英文主站第一阶段页面：

1. `/`：Wise Oracle 首页。
2. `/daily-almanac`：每日黄历工具。
3. `/ask-oracle`：三字起卦/诸葛神算工具。
4. `/birth-chart-reading`：八字/出生盘文化解读。
5. `/articles`：文章列表。
6. `/articles/<slug>`：英文 SEO 文章详情。
7. `/privacy`：隐私政策。
8. `/terms`：使用条款。
9. `/disclaimer`：免责声明。
10. `/about`：关于网站。
11. `/contact`：联系页面。

繁体中文第一阶段页面：

1. `/zh-Hant/`
2. `/zh-Hant/huangli`
3. `/zh-Hant/suanshi`
4. `/zh-Hant/lunming`

繁体法律页可在第二批补齐，但英文法律页必须在 AdSense 申请前完成。

## 9. SEO 内容计划

第一批至少 25 篇英文原创文章，建议目标为 30 篇。核心文章建议 1000-1500 英文词；工具说明页可短一些，但必须有清晰结构、真实信息量和内部链接。

### 9.1 基础解释类

1. What Is a Chinese Almanac?
2. What Is BaZi?
3. What Is an Eastern Oracle?
4. What Is I Ching Divination?
5. Chinese Zodiac vs Western Astrology
6. BaZi vs Western Astrology
7. I Ching vs Tarot
8. How to Ask an Oracle Question
9. What Are Auspicious Days?
10. How Chinese Lunar Calendar Works
11. Who Was Zhuge Liang and Why Is He Linked to Oracle Traditions?
12. Chinese Numerology vs Western Numerology

### 9.2 搜索意图类

1. Best Day for Wedding According to Chinese Almanac
2. Best Day for Moving House
3. Best Day to Sign a Contract
4. Best Day to Start a Business
5. Best Day for Travel
6. Best Day for Haircut
7. Chinese Almanac Today
8. Daily Auspicious and Inauspicious Activities
9. How to Choose a Lucky Date
10. What to Avoid Today According to Chinese Almanac

### 9.3 转化辅助类

1. How to Use Wise Oracle
2. How to Read an Oracle Result
3. Why Oracle Readings Are for Reflection
4. How to Use Divination Without Giving Up Agency
5. Eastern Wisdom for Modern Decisions
6. Beginner's Guide to Wise Oracle
7. How to Use Oracle Readings Without Giving Up Agency

每篇文章要求：

1. 唯一 title。
2. 唯一 meta description。
3. 一个 H1。
4. 清晰 H2 结构。
5. canonical。
6. hreflang。
7. 内链到相关工具页。
8. 免责声明或 responsible use 提示。
9. 不使用 AI 痕迹明显的空泛段落。
10. 不夸大预测能力。

## 10. 合规和信任建设

必须新增或改造以下页面：

1. Privacy Policy
2. Terms of Use
3. Disclaimer
4. About
5. Contact

Privacy Policy 必须说明：

1. cookies。
2. Google advertising cookies。
3. server logs。
4. AI report input。
5. 出生日期、出生时间、性别、出生地等敏感输入如何处理。
6. 是否保存报告。
7. 是否分享给第三方。
8. 用户如何联系删除或询问数据。

Terms of Use 必须说明：

1. 服务仅供娱乐和文化参考。
2. 用户不得把结果作为重大决策唯一依据。
3. 服务可能中断。
4. AI 生成内容可能不准确。
5. 禁止滥用、攻击、自动化抓取。

Disclaimer 必须说明：

1. 不提供医疗建议。
2. 不提供法律建议。
3. 不提供投资建议。
4. 不提供心理治疗。
5. 不保证预测准确。
6. 不处理紧急危机。

About 页面要建立信任：

1. 说明网站聚焦东方传统文化。
2. 说明算法和 AI 的关系：历法和基础数据由程序计算，AI 只做解释和表达。
3. 说明 responsible use。
4. 不伪装成权威宗教、医疗或心理机构。

## 11. 财务链路规划

第一阶段必须把财务闭环设计清楚，不能只做内容和流量。商业闭环分三条收入线：

1. AdSense：底层广告收入，依赖 SEO 和访问量。
2. 微付费报告：验证用户是否愿意为更深解读付费。
3. 赞助/打赏：低摩擦补充收入，验证用户好感和支持意愿。

### 11.1 AdSense 收入线

需要准备：

1. Google AdSense 账户。
2. 收款资料。
3. 税务资料。
4. 银行入账路径。
5. 月度收入记录。
6. 成本记录。

AdSense 验证指标：

1. 是否通过审核。
2. 页面 RPM 是否能覆盖基础服务器成本。
3. 工具页广告是否影响用户体验。
4. 内容页和工具页哪类页面带来更高收入。

### 11.2 微付费报告收入线

第一阶段要完成最小付费闭环设计，并在条件允许时小规模上线测试。

候选产品：

1. `Wise Oracle Deep Reading`：USD 2.99 或 USD 4.99。
2. `Birth Chart Deep Report`：后续 USD 9.99 起。
3. `Auspicious Date Report`：后续按场景收费。

最小闭环：

1. 用户生成免费结果。
2. 页面展示付费报告价值点。
3. 用户点击 checkout link。
4. 支付平台完成收款。
5. 网站通过 webhook、临时 token 或邮件交付完整报告。
6. 后台记录订单状态和退款状态。

第一阶段可先验证 checkout link 和交付流程，不必一开始做完整账号系统。

### 11.3 赞助收入线

赞助用于验证用户支持意愿，不应替代产品付费。

候选方式：

1. Ko-fi。
2. Buy Me a Coffee。
3. Gumroad tip product。

赞助验证指标：

1. 结果页赞助点击率。
2. 文章页赞助点击率。
3. 赞助转化率。
4. 平均赞助金额。

### 11.4 平台核验清单

上线任何付费或赞助前，必须逐项核验：

1. 平台是否支持当前个人或公司主体。
2. 平台是否支持中国大陆、香港、新加坡或美国 LLC 等候选主体。
3. 平台是否接受 digital self-reflection / cultural insight / entertainment report。
4. 平台是否限制 fortune telling、psychic services、occult services。
5. 平台支持的收款方式、提现路径和币种。
6. 交易手续费、提现手续费、退款手续费。
7. 是否提供 Merchant of Record。
8. 是否提供 webhook。
9. 是否要求税务表格。
10. 账号冻结或拒绝时的替代方案。

平台候选优先级：

1. Merchant of Record：Lemon Squeezy、Paddle、Gumroad。
2. 赞助平台：Ko-fi、Buy Me a Coffee。
3. 直接支付：PayPal、Stripe。

### 11.5 单位经济模型

每个付费报告都要计算：

1. 售价。
2. 支付平台手续费。
3. AI 生成成本。
4. 服务器和日志成本摊销。
5. 退款率假设。
6. 税费或 MoR 扣费。
7. 单单净利润。

示例模型：

1. 售价：USD 4.99。
2. 支付和平台成本：待平台核验后填写。
3. AI 成本：按实际模型调用成本填写。
4. 退款预留：先按 5%-10% 做压力测试。
5. 单单净利润必须为正，否则不能放量。

### 11.6 主体和税务

第二阶段如接直接支付，再重新评估主体：

1. 个人收款。
2. 香港公司。
3. 新加坡公司。
4. 美国 LLC。
5. Merchant of Record 平台。

在没有会计或法律专业人士确认前，不把海外公司注册作为第一阶段前置条件。但第一阶段必须收集这些路径的要求和成本，避免后期流量起来后无法收款。

月度台账字段建议：

1. 月份。
2. SEO 点击和展示。
3. 工具使用次数。
4. AdSense 页面浏览量。
5. AdSense 展示次数。
6. AdSense 收入。
7. 付费报告订单数。
8. 付费报告收入。
9. 赞助次数和收入。
10. AI API 成本。
11. 服务器成本。
12. 域名/CDN 成本。
13. 内容生产成本。
14. 支付手续费和退款。
15. 净利润。

## 12. 实施阶段划分

### 阶段 0：计划审查

输出：

1. 本计划文件。
2. 待讨论问题清单。
3. 最终确认版计划。

验收：

1. 用户确认技术路线。
2. 用户确认语言策略。
3. 用户确认第一阶段收入优先级。
4. 用户确认是否开始实施。

### 阶段 1：英文主站与繁中路由

输出：

1. 英文首页。
2. 英文三大工具页。
3. 繁中三大工具页。
4. 旧中文路由兼容。
5. 基础 canonical 和 hreflang。

验收：

1. 页面 200。
2. 工具可用。
3. 移动端不溢出。
4. 旧路由不破坏。

### 阶段 2：产品本地化与付费分层

输出：

1. 英文算事三词输入。
2. 英文算事三数字输入。
3. 三词到签号的可复现算法。
4. 前 20 条英文签文重写样本。
5. 免费结果与付费报告的分层原型。
6. `Wise Oracle Deep Reading` 产品说明和价格测试方案。

验收：

1. 英文用户不需要输入汉字也能完成算事。
2. 同一个英文问题稳定映射到同一个签号。
3. 数字输入边界有校验。
4. 前 20 条英文签文没有高风险承诺、恐吓、医疗、投资或法律建议。
5. 用户能清楚看到免费内容和付费内容的差异。

### 阶段 3：合规页与信任页

输出：

1. Privacy Policy。
2. Terms of Use。
3. Disclaimer。
4. About。
5. Contact。
6. 页脚统一入口。

验收：

1. 所有核心页面可从页脚进入法律页。
2. 免责声明可见。
3. 不存在高风险承诺文案。

### 阶段 4：SEO 内容系统

输出：

1. 文章列表页。
2. 文章详情页。
3. 至少 25 篇英文原创文章。
4. sitemap.xml。
5. robots.txt。

验收：

1. Search Console 可抓取。
2. 文章 meta 完整。
3. 内链指向工具页。
4. 页面加载正常。

### 阶段 5：财务闭环预验证

输出：

1. AdSense 收款资料准备清单。
2. Ko-fi / Buy Me a Coffee / Gumroad 赞助路径核验。
3. Lemon Squeezy / Paddle / Gumroad Merchant of Record 路径核验。
4. `Wise Oracle Deep Reading` checkout link 或模拟 checkout 方案。
5. webhook / 临时 token / 邮件交付三选一的最小交付设计。
6. 单位经济模型表。
7. Go / No-Go 判断：是否具备小规模上线付费报告条件。

验收：

1. 至少 2 个收款候选平台完成政策和主体可行性核验。
2. 明确一个首选平台和一个备选平台。
3. 明确付费报告单单净利润模型。
4. 明确无法收款时的替代路线。
5. 不以规避平台审核为目的修改产品描述。

### 阶段 6：AdSense 准备与申请

输出：

1. AdSense 审核准备清单。
2. 合理广告位占位。
3. Google Search Console 数据追踪。
4. 基础访问统计。

验收：

1. AdSense 申请前页面体验完整。
2. 广告位不干扰工具使用。
3. 不存在诱导点击文案。

### 阶段 7：运营复盘

输出：

1. 每周 SEO 数据记录。
2. 每周页面表现记录。
3. 每月收入和成本台账。
4. AdSense 收入记录。
5. 付费报告点击和订单记录。
6. 赞助点击和收入记录。
7. 下一阶段是否放大付费报告或接入人工咨询的判断。

验收：

1. 至少连续 4 周数据记录。
2. 明确哪些页面带来搜索流量。
3. 明确 AdSense、付费报告、赞助三条收入线的表现。
4. 明确是否具备放大付费报告的条件。

## 13. 第一阶段验收标准

第一阶段完成的最低验收标准：

1. 英文首页上线。
2. 英文三大工具页上线。
3. 繁中三大工具页上线。
4. 旧中文路由不破坏。
5. Privacy、Terms、Disclaimer、About、Contact 上线。
6. 至少 25 篇英文原创 SEO 文章上线。
7. sitemap.xml 和 robots.txt 可访问。
8. Search Console 已验证。
9. AdSense 审核资料准备完成。
10. 英文算事支持三词和三数字输入。
11. 前 20 条英文签文重写样本上线或完成可验收稿。
12. `Wise Oracle Deep Reading` 免费/付费分层原型完成。
13. 至少 2 个收款候选平台完成政策、主体、提现和费用核验。
14. 付费报告单位经济模型完成。
15. 移动端和桌面端核心路径人工验收通过。
16. 没有保证预测、恐吓付费、医疗投资法律建议等高风险文案。
17. 现有测试通过。

## 14. 待审查问题

后续讨论时建议重点审查以下问题：

1. 英文品牌是否最终确定为 Wise Oracle。
2. 是否需要保留“Zhuge”作为文化介绍，而不是主品牌。
3. 繁体中文是否第一阶段就做完整，还是先做核心工具页。
4. 文章系统使用静态 Markdown、数据库，还是 Jinja 模板硬编码。
5. AdSense 广告位数量和位置。
6. ~~英文算事首版是否同时支持自由提问和三数字输入。~~ 已决：取消自由提问，改为三词 + 三数字（2026-06-30）。
7. ~~文本到签号算法采用字符权重、哈希，还是其他可解释映射。~~ 已决：三词按 A=1..Z=26 字母求和 + `stroke_digit`（mod 10，余 0 取 1）→ 三数字 d1/d2/d3 → `compose_three_character_number` → `reduce_to_start_index`（实现见 `scripts/derive_original_oracle_signs.py`，2026-06-30 定稿）。
8. `Wise Oracle Deep Reading` 首轮价格使用 USD 2.99 还是 USD 4.99。
9. 首选收款平台是否先核验 Lemon Squeezy、Paddle、Gumroad。
10. 是否需要邮件订阅。
11. 是否需要在第一阶段隐藏或弱化八字论命入口。
12. 是否需要针对美国、英国、加拿大、澳大利亚分别做 SEO 页面。
13. 是否需要找会计确认 AdSense 入账和税务路径。

## 15. 明确不实施声明

本文件只是计划草案。创建本文件不代表已经开始执行出海改造。

在用户明确确认实施前，不应改动：

1. 后端路由。
2. 模板页面。
3. 静态资源。
4. API 行为。
5. 数据库结构。
6. 部署配置。
7. 支付或广告代码。
