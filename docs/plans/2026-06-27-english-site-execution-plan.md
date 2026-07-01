# Wise Oracle 英文站改造执行计划

> **文档定位：** 本计划从 `2026-06-24-global-i18n-commercialization-execution-plan.md` 总纲拆出，专门追踪英文站改造（原总纲 P2-P5 + E0-E8 + 相关待决策项）。总纲保留 P0/P1/P6/P7/P8 及非英文阶段；本文档与总纲在英文站范围内互斥，避免双轨追踪。
>
> **维护规则：** 可追溯（每任务有进度日志）、可修改（变更走修订记录）、可插入（新任务用 W{n}.{m} 编号不破坏既有）、与代码严格一致（每工作包标注代码现状）。

---

## 0. 修订记录

| 版本 | 日期 | 修订人 | 变更摘要 |
| --- | --- | --- | --- |
| 0.1 | 2026-06-27 | Codex | 从总纲拆出；建立 W0-W8 单编号体系；新增决策门、代码现状、依赖字段；吸收审查意见 S1/S2/M1/M2/M3/M4 |
| 0.2 | 2026-06-27 | Codex | 3 项修正：API 路径统一 `/api/en/*`、W6 测试文件名改为 `test_birth_chart_english.py`、W0.3 明确 prompt 边界文档文件名；决策门 D1/D2/D4-D7/D9/D10/D12 标记已确认 |
| 0.3 | 2026-06-27 | Codex | W2 产出方式落地：新增 W2.0（DeepSeek+Gemini API key 与系统提示词）；W2.1/W2.3/W2.4/W2.6 明确双 AI 交叉审核流程；W2.5 改为脚本提取 6tail 候选+单次 AI 审核；补充涉及文件（脚本、提示词、.env.example） |
| 0.4 | 2026-06-27 | Codex | W2.0 增补翻译批次策略：批量优先（一次性提交全部中文）、分批兜底（超上下文再分批）、整体审核、差异提取、仅异议条目循环、人工兜底 |
| 0.5 | 2026-06-30 | 助手 | 对齐现状：W2.1 进度日志回填（384/384 翻译完成，计划仅要 20 条样本）；新增 D13-D17 决策门；代码现状基线更新（卦属/吉凶删除、英文签文 JSON 已存在）；W4 明确英文数据走 JSON 内存加载并剔除 fortune/gua_type；引用考据结论（`docs/research/zhuge-origin-research.md`）为硬约束 |
| 0.6 | 2026-06-30 | 助手 | 取消自由提问模式，改为 Three Words + Three Numbers：D4 更新为三词字符长度 mod 10 映射；W0.2/W4.1/W4.2/W4.3/W7.4 重写（payload mode 改 words、字段契约统一为 9 字段、三数字范围 0-999→0-9）；W2.1 字段结构对齐 GUA_COLUMNS 11 字段；W2.7 测试改为 9 字段校验；新增引导语；W4 目标行"文本"改"三词" |
| 0.7 | 2026-06-30 | 助手 | 算法定稿（依据 scripts/derive_original_oracle_signs.py）：D4 三词改为 A=1..Z=26 字母求和 + stroke_digit（mod 10 余 0 取 1）+ compose_three_character_number（复用源书函数）；W4.2 三数字改回 0-999 + 九位种子 compose_english_three_number_seed（英文专用）；W4.1/W4.2/W4.3 标注复用脚本函数；W0.2/W7.4 新增 UI 变换动画与折叠项；示例 LOVE/WORK/FATE→Sign #88 |
| 0.8 | 2026-06-30 | 助手 | W0 审查反馈修正：D11 确认保留完整入口（W0 阻塞解除）；D8 暂停（Deep Reading 付费产品暂时冻结，待用户深度思考）；代码现状更新（W0 五份文档已起草）；W0 涉及文件补充 AI Prompt 边界文档；产品规格补充 W0.1 逐页定义、引导语拆分（公共前半句+两套模式文案）、Three Numbers UI 动画（314|159|265→Sign #33）、全零错误码 ORACLE_NUMBERS_ALL_ZERO、三词页面输入约束；AI Prompt 边界文档删除 Ask the Oracle 敏感词检测（仅保留 Birth Chart Reading）；文化表达指南神煞改为音译+解释、命理改为 life patterns；Wise_Oracle_Outbound_Plan.md 标记已废止 |
| 0.9 | 2026-06-30 | 助手 | W0 视为通过（用户授权按文档落实代码）；W1 完成：W1.1 术语表草稿+抽取脚本（纠正命名空间注释错误 sx=生肖/ss=十神/ps=方位/bg=八卦）；W1.2 错误码策略定稿（21 现有 code + 5 英文新增 + CONTENT_NOT_FOUND）；W2.2-W2.6 暂停（用户将用其他 Agent 更新后台数据）；W5 暂停（黄历上线范围待核实）；W8 暂停（D3 未定，Deep Reading 冻结）；进入 W3 |
| 0.10 | 2026-06-30 | 助手 | W3 完成：W3.2 error_codes.py（27 个 code 常量 + 中英文消息映射 + DEFAULT_HTTP_STATUS + failure_with_code()）；W3.1+W3.3 pages_en.py（11 条英文路由，pages_en_bp 放 ALL_BLUEPRINTS 第一位优先匹配 `/`）；pages.py 删除 `/`→`/zh-hans/almanac` 的 301（`/` 释放给英文首页），保留 `/huangli`/`/suanshi`/`/lunming` 301 兼容；11 个英文模板（base.html + 10 个页面）；test_client 验证 9 条英文路由 200 + 3 条旧中文路由 301 + 中文页面正常 |
| 0.11 | 2026-06-30 | 助手 | W4 完成：oracle_algorithm.py（纯函数：stroke_digit/compose_three_character_number/reduce_to_start_index/compose_english_three_number_seed/word_to_letter_sum/word_to_stroke_digit/three_words_to_start_index/word_transform）；oracle_english.py（load_english_signs 加载到内存 + _sanitize_record 剔除 fortune/gua_type + CJK 残留/空字段 fallback + ask_with_words/ask_with_numbers）；blueprints/oracle_en_api.py（POST /api/en/oracle/ask，words/numbers 双模式，错误码 INVALID_JSON/INVALID_ORACLE_MODE/ORACLE_WORDS_INSUFFICIENT/INVALID_ORACLE_NUMBER/ORACLE_NUMBERS_ALL_ZERO/CONTENT_NOT_FOUND）；config.py 加 ENGLISH_SIGNS_PATH；app.py 启动期加载 english_signs 到 extensions（无缝切换）；测试 76 项全过（含 LOVE/WORK/FATE→Sign #88、314/159/265→Sign #33、D14 字段剔除、CJK fallback、空字段 fallback、384 全覆盖） |
| 0.12 | 2026-06-30 | 助手 | W6 完成：birth_chart_english.py（BirthChartEnglish 服务 + ZODIAC_EN/GAN_EN/ZHI_EN/ELEMENT_EN 映射表 + build_english_prompt 引用 W0.3 边界 + _parse_ai_report + analyze/analyze_stream/build_chart_summary）；birth_chart_en_api.py（POST /analyze + POST /stream）；app.py 注入 birth_chart_en 扩展（复用 lunming 的 OpenAI client）；blueprints/__init__.py 注册蓝图；测试 59 项全过。**两项设计修正：** (1) stream 端点改用 POST（原计划写 GET，与中文 lunming_api.py 一致便于传 JSON body，W7.6 同步更新）；(2) done 帧归属 API 层统一补发（服务层 analyze_stream 只产 chart/report/responsible_use，避免重复 done，与 lunming.analyze_bazi_stream 对齐）。W6.1 文章加载（content.py/seo.py）划归 W8（暂停） |
| 0.13 | 2026-06-30 | 助手 | W7 完成：W7.2 base.html（CSS 链接改为 wise_oracle.css + canonical + wise_oracle_common.js）+ wise_oracle.css（640 行东方克制风：米色背景/墨红/墨色/金色变量、Georgia 衬线标题、卡片式工具布局、@media max-width:640px 响应式）+ wise_oracle_common.js（ERROR_MESSAGES 错误码映射 + postJSON fetch 封装 + readSSE 手动流读取 + DOM 辅助）；W7.3 英文首页（brand + 三大工具入口）；W7.4 Ask the Oracle（ask_oracle.html + ask_oracle_en.js 274 行：模式切换/校验/POST /api/en/oracle/ask/变换动画 word→letter_sum→digit 逐行淡入/9 字段渲染/responsible_use/赞助占位/Draw Another Sign 重启）；W7.5 Daily Almanac 降级（W5 暂停，用户友好 "Coming soon" + 图例保留，去 Yellow Calendar）；W7.6 Birth Chart（birth_chart.html + birth_chart_en.js 290 行：birth_time_unknown checkbox 联动/校验/POST /api/en/birth-chart/stream SSE 流消费，事件 chart/report/responsible_use/error/done）；W7.7 合规页（privacy/terms/disclaimer/about/contact 真实内容 8/10/6/3/2 节 + 隐私提示 + 非预测定位）；W7.9 契约测试 40 项全过（11 路由 200 + base.html 共享布局 + 首页 + Ask the Oracle + Daily Almanac + Birth Chart + 合规页）。**两项决策：** (1) 英文 base.html 链接 wise_oracle.css 而非中文 style.css，中英两套独立布局（W7.2 已知技术债确认落实）；(2) W5/W8 暂停 → 黄历页 "Coming soon" 降级 + articles 占位。**未做：** W7.1（视觉方向文档已在前序定稿，代码落地无独立产出）、W7.8（响应式与可访问性，留待浏览器人工验收） |

> 变更规则：任何对本计划的修改（增删任务、调整顺序、状态变更）都追加一行修订记录，并在第 7 节变更日志写明细节。任务状态变更不记修订记录，只更新任务内的进度日志。

---

## 1. 代码现状基线（2026-06-27 快照）

> 本节与代码严格对齐，作为计划启动基线。每次合并到主干后需复核本节是否漂移。

### 已完成（P1 简繁双语基础设施）

| 能力 | 代码位置 | 状态 |
| --- | --- | --- |
| 简繁路由 `/<lang>/almanac\|divination\|bazi` | `zhugeshensuan/blueprints/pages.py` | 已实现 |
| 旧入口 301 兼容 `/huangli`、`/suanshi`、`/lunming` | `pages.py` | 已实现（`/` 已释放给英文首页） |
| 模板 `<html lang>` 按语言渲染 | `frontend/templates/*.html` | 已实现 |
| 前端字典 `dictionary.json` + `i18n.js` + `lang_switcher.js` | `frontend/static/js/lang/` | 已实现 |
| 黄历动态数据繁体化 | `zhugeshensuan/huangli_i18n.py` | 已实现 |
| 农历日期共享格式化 | `frontend/static/js/lang/lunar-format.js` | 已实现 |
| API 语言参数 + `status_code`/`source_code` | `huangli_api.py` 等 | 已实现 |
| 卦属/吉凶从前端删除（基于考据硬约束） | `suanshi.html`、`index.html`、`main.js`、`dictionary.json` | 已实施（2026-06-28，4.5 节） |
| 打字机逐字显现动画 | `main.js` 的 `typeWriter` | 已实现（chunkSize=1, interval=50） |
| API 错误码 `code` 字段 | `api_utils.py` 的 `failure()` | 已实现（17 个稳定 code） |

### 已完成（W3 英文路由骨架与错误码基础）

| 能力 | 代码位置 | 状态 |
| --- | --- | --- |
| 错误码模块（27 个 code + 中英文消息 + HTTP status + `failure_with_code()`） | `zhugeshensuan/error_codes.py` | 已实现 |
| 英文页面路由（`/`、`/ask-oracle`、`/daily-almanac`、`/birth-chart-reading`、`/articles`、`/articles/<slug>`、`/privacy`、`/terms`、`/disclaimer`、`/about`、`/contact`） | `zhugeshensuan/blueprints/pages_en.py` | 已实现（11 条路由，占位模板） |
| 英文蓝图注册（`pages_en_bp` 放 ALL_BLUEPRINTS 第一位优先匹配 `/`） | `zhugeshensuan/blueprints/__init__.py` | 已实现 |
| 英文占位模板（base.html + 10 个页面） | `frontend/templates/en/*.html` | 已实现（W7 做完整前端） |

### 已完成（W4 Ask the Oracle 后端）

| 能力 | 代码位置 | 状态 |
| --- | --- | --- |
| 签号算法纯函数（源书方法 + 英文三词 + 英文三数字 + 变换过程） | `zhugeshensuan/oracle_algorithm.py` | 已实现 |
| 英文签文服务（内存加载 + 剔除 fortune/gua_type + CJK/空字段 fallback） | `zhugeshensuan/oracle_english.py` | 已实现 |
| 英文算事 API（POST /api/en/oracle/ask，words/numbers 双模式） | `zhugeshensuan/blueprints/oracle_en_api.py` | 已实现 |
| 英文签文路径配置（ENGLISH_SIGNS_PATH，可 env 覆盖） | `zhugeshensuan/config.py` | 已实现 |
| 启动期加载英文签文到 extensions（无缝切换） | `zhugeshensuan/app.py` | 已实现 |

### 已超前完成（W2 部分）

| 能力 | 代码位置 | 状态 |
| --- | --- | --- |
| 英文签文翻译 384/384 | `data/content/oracle_signs_en.json` | 已完成（计划仅要 20 条样本）；含质量遗留：7 条 interpretation1 残留中文（50/63/101/222/237/261/286）、4 条 general 为空（197-200） |
| 翻译脚本与提示词 | `scripts/translate_oracle_signs.py`、`prompts/translator_system_prompt.md` | 已存在 |
| 中文解签数据 | `data/content/oracle_signs_reinterpreted.json` | 已存在（384 条） |

### 未开始（英文站其余）

| 能力 | 预期位置 | 状态 |
| --- | --- | --- |
| 英文黄历适配 | `zhugeshensuan/huangli_english.py` | 不存在 |
| 英文内容加载 | `zhugeshensuan/content.py` | 不存在 |
| SEO 模块 | `zhugeshensuan/seo.py`、`blueprints/seo.py` | 不存在 |
| 商业化模块 | `zhugeshensuan/commerce*.py`、`blueprints/commerce_api.py` | 不存在 |
| 英文黄历术语/场景数据 | `data/content/huangli_terms_en.json`、`huangli_scenarios_en.json` | 不存在 |
| 英文合规页草稿 | `data/content/legal/*_en.md` | 不存在 |
| 英文相关测试 | `tests/test_english_*.py` | 不存在（已有 `tests/test_oracle_english.py`） |

### 已有相关文档

| 文档 | 用途 |
| --- | --- |
| `docs/business/huangli-english-localization-guidance.md` | 英文黄历后续指导（P1 产出） |
| `docs/business/wise-oracle-i18n-string-inventory.md` | 前端硬编码中文清单（P0 产出） |

---

## 2. 决策门（阻塞项）

> 以下决策在进入对应工作包前必须先决。未决时对应工作包状态标记为「阻塞」。

| ID | 决策内容 | 阻塞工作包 | 当前倾向 | 状态 |
| --- | --- | --- | --- | --- |
| D1 | 英文主品牌是否确定为 `Wise Oracle` | W0 | `Wise Oracle` | 已确认 |
| D2 | `/` 是否切换为英文首页；切换后旧 `/` → `/zh-hans/almanac` 的 301 策略是否调整 | W0、W3、W7 | 最终切英文首页，英文首页完成前保持当前跳转 | 已确认 |
| D3 | 英文文章系统用 Markdown / JSON manifest / 数据库 | W8 | 未定 | 待确认 |
| D4 | 英文算事三词到签号映射方式（原"稳定哈希"随自由提问取消而废止） | W4 | 三词各按 A=1..Z=26 字母求和，复用源书 stroke_digit（mod 10，余 0 取 1）→ compose_three_character_number（100×d1+10×d2+d3）→ reduce_to_start_index（((N-1) mod 384)+1）。实现见 scripts/derive_original_oracle_signs.py | 已确认（2026-06-30 定稿） |
| D5 | 第一轮英文签文样本 20 条还是 50 条 | W2 | 20 条 | 已确认 |
| D6 | 神煞名采用音译 / 意译 / 音译+解释 | W1、W2、W5 | 音译+解释 | 已确认 |
| D7 | 英文 Daily Almanac 第一轮是否展示彭祖百忌全文还是 summary | W5 | summary | 已确认 |
| D8 | `Wise Oracle Deep Reading` 首测价格 USD 2.99 还是 4.99 | W8（商业化预埋） | 暂时搁置（Deep Reading 冻结） | 暂停（2026-06-30，待付费方案深度思考） |
| D9 | 是否先做模拟 checkout，等平台政策核验后再接真实 checkout | W8 | 是 | 已确认 |
| D10 | 是否需要邮件订阅作为第一阶段留存 | W8 | 否 | 已确认 |
| D11 | 第一阶段是否弱化 Birth Chart Reading 入口（隐私合规复杂度） | W0、W6 | 未定 | 待确认 |
| D12 | 英文 API 路径前缀统一策略：`/api/en/*` 还是 `/api/*` 靠 Accept-Language | W4、W5、W6 | `/api/en/*` | 已确认 |
| D13 | 英文签文字段是否沿用 GUA_COLUMNS（11 字段）还是重构为 `oracle_title/message/guidance/caution/...` | W0、W2、W4 | 沿用 GUA_COLUMNS | 已确认（2026-06-30 用户拍板） |
| D14 | `fortune`/`gua_type` 字段在英文加载时剔除还是保留不展示 | W4 | 加载时剔除 | 已确认（2026-06-30 用户拍板） |
| D15 | 英文数据走 JSON 内存加载，不入数据库 | W4、W5、W6 | JSON 内存加载 | 已确认 |
| D16 | 卦属/吉凶在三语前端均不展示（基于考据硬约束） | W0、W4、W7 | 不展示 | 已确认（硬约束） |
| D17 | 解签定位为 interpretation 而非 answer（基于考据硬约束） | W0、W6 | interpretation | 已确认（硬约束） |

---

## 3. 工作包总览（W0-W8）

> 单编号体系：W = Work package。取代原总纲的 E0-E8 和 P2-P5 双轨。映射关系见下表。

| 工作包 | 名称 | 原总纲映射 | 前置 | 状态 |
| --- | --- | --- | --- | --- |
| W0 | 英文产品边界冻结 | E0 / P2.1-P2.5、P2.8 | D1、D2、D11 | 已完成（用户授权按文档落实代码，视为通过；黄历上线范围待用户核实，Deep Reading 冻结） |
| W1 | 英文术语体系 | E1 / P2.6、P2.7 | W0、D6 | 已完成（W1.1 术语表草稿+脚本完成，W1.2 错误码策略定稿） |
| W2 | 英文内容数据 | E2 / P3.1-P3.7 | W0、W1、D5、D6、D7 | 进行中（W2.1 已超额完成 384/384；W2.2-W2.6 暂停，用户将用其他 Agent 更新后台数据） |
| W3 | 英文路由骨架 | E3 / P4.1、P4.1a、P4.2 | W0、D2、D12 | 已完成（11 条英文路由 + 错误码模块 + 11 个英文模板，test_client 全部通过） |
| W4 | Ask the Oracle 后端 | E4 / P4.3-P4.5 | W0、W2、D4、D12 | 已完成（oracle_algorithm.py + oracle_english.py + oracle_en_api.py + 76 项测试全过） |
| W5 | Daily Almanac 后端 | E5 / P4.6、P4.6a | W0、W2、D6、D7、D12 | 暂停（黄历上线范围待用户核实） |
| W6 | Birth Chart Reading 后端 | E6 / P4.7、P4.8 | W0、W2、D11、D12 | 进行中 |
| W7 | 英文前端 | E7 / P5.1-P5.8 | W3、W4、W5、W6 | 未开始 |
| W8 | SEO / 合规 / 商业化预埋 | E8 / P7 部分 + P6 部分 | W2、W7、D3、D8、D9、D10 | 暂停（D3 未定，Deep Reading 冻结） |

状态枚举：未开始 / 进行中 / 阻塞 / 待验收 / 已完成

---

## 4. 工作包详情

### W0：英文产品边界冻结

**目标：** 对「算事」「论命」「黄历」英语化做出完整、可确认、可交给开发执行的定稿方案。

**代码现状：** W0 五份文档已起草完成（产品规格、文案风格、报告分层、文化表达指南、AI prompt 边界），待用户审阅定稿。

**涉及文件：**
- 已建：`docs/business/wise-oracle-english-product-spec.md`
- 已建：`docs/business/wise-oracle-copy-style-guide.md`
- 已建：`docs/business/wise-oracle-report-tiering.md`
- 已建：`docs/business/wise-oracle-cultural-expression-guide.md`
- 已建：`docs/business/wise-oracle-ai-prompt-boundaries.md`
- 已建：`docs/business/huangli-english-localization-guidance.md`

**子任务：**

#### W0.1 定稿英文信息架构
1. 记录每个英文 URL（见总纲 2.1 表格）。
2. 为每个页面定义：页面目的、主按钮、次级按钮、SEO 标题、meta description、responsible-use 底线提示位置。
3. 确认 D2（`/` 作为英文首页，旧中文路由兼容）。
4. 未决问题记入第 2 节决策门。

#### W0.2 定稿 Ask the Oracle 交互
1. 两种输入模式：三个词（Three Words）、三个数字（Three Numbers）。原"自由提问"模式已取消（用户不输入问题文本，显著减少敏感问题文本的收集和定向回答风险）。
2. 引导语（两种模式共用）：`Hold one question quietly in mind. Do not type it. Take a slow breath, then enter the first three words that come to you. They may be connected to your question—or not. Do not overthink them.`
3. 三词算法（D4 已定稿，依据 `scripts/derive_original_oracle_signs.py`）：每词按 A=1..Z=26 字母求和 → 复用源书 `stroke_digit`（和对 10 取模，余 0 取 1）→ 三数字 d1/d2/d3（均 1-9）→ `compose_three_character_number`（N=100×d1+10×d2+d3）→ `reduce_to_start_index`（r=((N-1) mod 384)+1）。示例：LOVE/WORK/FATE → 4/7/2 → N=472 → Sign #88。
4. 三数字算法（英文专用，非源书方法）：三个 0-999 数字 → `compose_english_three_number_seed`（seed=d1×1,000,000+d2×1,000+d3）→ `reduce_to_start_index`（r=((seed-1) mod 384)+1）。
5. 校验规则：三词词数/字母校验（`ORACLE_WORDS_INSUFFICIENT`）、三数字范围 `0-999` 且不全零（`INVALID_ORACLE_NUMBER`）；不再有自由提问长度校验和敏感场景检测。
6. 结果字段（D13/D14 已确认）：`sign_number`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`（共 9 字段，已剔除 fortune/gua_type）。
7. UI 变换动画（仅 Three Words）：提交后依次展示 LOVE→54→4 等变换过程，再显示签号；旁提供折叠项 "How were these numbers formed?"。

#### W0.3 定稿 Birth Chart Reading 边界
1. 页面命名 `Birth Chart Reading`，定位 BaZi-inspired cultural self-reflection。
2. 现有八字计算仅作基础盘生成；AI 仅作解释层。
3. 定义免费/付费结果边界。
4. AI 解释层不输出医疗、法律、财务、心理治疗、生育、死亡、灾难、重大人生决策的确定性结论。
5. **隐性依赖（审查 M3）：** 本任务需产出英文 AI prompt 边界文档，作为 W6 的前置。

#### W0.4 定稿 Daily Chinese Almanac 边界
1. 页面命名 `Daily Chinese Almanac`。
2. 标签：Favorable Activities、Unfavorable Activities、Lunar Date、Solar Term、Chinese Zodiac。
3. 禁用 `Yellow Calendar`；`Daoist Auspicious Calendar` 仅在解释文章谨慎使用。
4. 场景：wedding、moving、business opening、travel、signing、haircut。

#### W0.5 定稿商业化分层
1. 免费内容定义。
2. `Wise Oracle Deep Reading` 付费内容定义。
3. 赞助文案、付费墙文案。
4. 价格测试候选：USD 2.99 / USD 4.99（待 D8）。
5. 真实支付上线 Go/No-Go 清单。

#### W0.6 定稿英文上线范围
第一轮上线：`/`、`/ask-oracle`、`/daily-almanac`、`/birth-chart-reading`、`/articles` + ≥10 篇内容、Privacy/Terms/Disclaimer/About/Contact、赞助/付费墙仅占位。
第一轮不上线：完整会员、复杂订单、人工咨询、多语言文章、未核验政策的真实支付。

**验收标准：**
- 产品规格无第一版路由待定项。
- 文案风格指南含四级文化表达分级。
- 报告分层区分免费/付费/赞助。
- 不读代码也能确认 W0 通过。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-30 | 助手 | W0 五份文档起草完成：①产品规格、②文案风格、③报告分层、④文化表达指南、⑤AI prompt 边界；D13/D14 正式拍板（沿用 GUA_COLUMNS + 加载时剔除 fortune/gua_type） | `docs/business/wise-oracle-{english-product-spec,copy-style-guide,report-tiering,cultural-expression-guide,ai-prompt-boundaries}.md` | 待用户统一审阅；审阅通过后进入 W1 |
| 2026-06-30 | 助手 | W0 审查反馈修正：D11 确认保留完整入口（阻塞解除）；D8 暂停（Deep Reading 冻结）；产品规格补充 W0.1 逐页定义、引导语拆分、Three Numbers 动画、全零错误码 ORACLE_NUMBERS_ALL_ZERO、三词约束；AI Prompt 边界删除 Ask the Oracle 敏感词检测；文化表达指南神煞音译+解释、命理改 life patterns；Wise_Oracle_Outbound_Plan.md 标记已废止；Deep Reading 付费定义暂时冻结 | 各文档修订 | 待用户二审；黄历上线范围待用户核实 |

---

### W1：英文术语体系

**目标：** 建立英文黄历术语表和错误码策略，为 W2 数据准备和 W5 后端提供输入。

**代码现状：** `huangli-english-termbase-draft.md` 不存在；`error_codes.py` 不存在。

**前置：** W0、D6

**涉及文件：**
- 新建：`docs/business/wise-oracle-termbase.md`
- 新建：`docs/business/huangli-english-termbase-draft.md`
- 修改：本计划（记录错误码定稿）

**子任务：**

#### W1.1 抽取 6tail 英文候选词
1. 编写一次性脚本（建议放 `scripts/`，命名 `extract_lunar_en_candidates.py`），从 `frontend/static/js/lunar.js` 的 6tail `I18n` 英文 messages 抽取候选词。
2. 只抽取候选，不直接上线：`sx.*`、`yj.*`、`jq.*`、`sn.*`、`ps.*`、`bg.*`。
3. 生成 `docs/business/huangli-english-termbase-draft.md`。
4. 每个术语记录：中文源词、6tail 英文候选、产品英文候选、使用场景、是否可直接用于 UI、风险备注。
5. 人工审校 `Yellow Calendar`、`Auspicious`、`Evil Spirit` 等易误读词。
6. 定稿后再写入项目英文黄历词表，不改 `lunar.js`。

#### W1.2 定稿错误码策略
1. 列出现有后端错误消息（运行 `rg -n "error.*message|message.*=" zhugeshensuan/blueprints`）。
2. 为每个 API 错误定义稳定 `code`，例如：`INVALID_INPUT`、`INVALID_DATE`、`INVALID_SCENARIO`、`CONTENT_NOT_FOUND`、`RATE_LIMITED`、`SERVICE_UNAVAILABLE`。
3. 前端英文页面只展示按 `code` 映射的英文消息。
4. 中文页面保持现有兼容。
5. **与 W3.2 的关系（审查 M2）：** 本任务产出的是文档定稿；W3.2 产出 `error_codes.py` 代码。W3.2 的 code 列表必须引用本任务定稿。

**验收标准：**
- 术语表完成候选抽取 + 人工审校。
- 错误码策略文档明确每个 code 的含义和触发场景。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-30 | 助手 | W1.1 完成：编写 `scripts/extract_lunar_en_candidates.py`，从 lunar.js 抽取 chs 799 条/en 500 条/29 命名空间，生成 `docs/business/huangli-english-termbase-draft.md`（50KB）。纠正执行计划命名空间注释错误（sx=生肖非十神，ss=十神，ps=方位非彭祖百忌，bg=八卦）。标识 6 个 en 完全缺失命名空间（d/ds/h/m/od/ss）+ sn 缺 137 条 | `scripts/extract_lunar_en_candidates.py`、`docs/business/huangli-english-termbase-draft.md` | 待人工审校定稿（用户将用其他 Agent 更新数据） |
| 2026-06-30 | 助手 | W1.2 完成：基于代码扫描（22 处 failure 调用、21 个唯一 code、前端零 code 消费）定稿错误码策略 `docs/business/wise-oracle-error-code-strategy.md`。定义现有 21 code + 英文版新增 5 code（INVALID_INPUT/INVALID_ORACLE_MODE/ORACLE_WORDS_INSUFFICIENT/INVALID_ORACLE_NUMBER/ORACLE_NUMBERS_ALL_ZERO）+ CONTENT_NOT_FOUND。SSE 流错误保持字符串格式（按语言切换）。W3.2 将产出 error_codes.py 引用本文档 | `docs/business/wise-oracle-error-code-strategy.md` | W3.2 实施 error_codes.py |

---

### W2：英文内容数据

**目标：** 对定稿方案做前期数据准备，先完成样本，再批量扩展。

**代码现状：** `data/content/` 目录不存在；`tests/test_english_content_data.py` 不存在。

**前置：** W0、W1、D5、D6、D7

**涉及文件：**
- 新建：`data/content/oracle_signs_en_sample.json`
- 新建：`data/content/oracle_signs_en_schema.json`
- 新建：`data/content/oracle_signs_en_review_checklist.md`
- 新建：`data/content/huangli_terms_en.json`
- 新建：`data/content/huangli_scenarios_en.json`
- 新建：`data/content/articles/articles_manifest.json`
- 新建：`data/content/legal/{privacy,terms,disclaimer,about,contact}_en.md`
- 新建：`docs/business/wise-oracle-seo-content-briefs.md`
- 新建：`docs/business/wise-oracle-legal-page-drafts.md`
- 新建：`scripts/translate_and_review.py`（双 AI 交叉审核脚本）
- 新建：`prompts/translator_system_prompt.md`（DeepSeek 初译提示词）
- 新建：`prompts/reviewer_system_prompt.md`（Gemini 审核提示词）
- 新建：`.env.example`（API key 模板，实际 `.env` 不入库）
- 测试：`tests/test_english_content_data.py`

**产出方式（双 AI 交叉审核）：** W2.1/W2.3/W2.4/W2.6 采用 DeepSeek 初译 + Gemini 审核 + 异议循环（最大 2 轮）+ 人工兜底；W2.5 采用脚本提取 6tail 英文候选 + 单次 AI 审核（不循环）。详见各子任务。

**子任务：**

#### W2.0 API key 准备与系统提示词规范（W2.1-W2.6 前置）
1. 注册 DeepSeek API，获取 key，写入 `.env`（变量名 `DEEPSEEK_API_KEY`）。
2. 注册 Google Gemini API，获取 key，写入 `.env`（变量名 `GEMINI_API_KEY`）。
3. 编写 `prompts/translator_system_prompt.md`：含文化表达指南、禁止词清单、签文字段结构、responsible-use 要求、神秘克制风格指引。供 DeepSeek 初译使用。
4. 编写 `prompts/reviewer_system_prompt.md`：含审核维度（cultural_boundary/deterministic_claim/grammar/terminology/literary）、异议结构化输出格式、severity 标准（low/medium/high，仅 high 触发循环）。供 Gemini 审核使用。
5. 测试 API 连通性：各发一条 ping 请求确认 key 有效。
6. `.env` 加入 `.gitignore`（如未加入）。
7. **翻译批次策略（脚本 `translate_and_review.py` 核心规则）：**
   - 批量优先：一次性把该子任务全部中文源文本提交给 DeepSeek 初译，保持上下文一致性，避免逐句翻译导致语境断裂。
   - 分批兜底：若单次提交超出模型上下文窗口或返回不稳定，再按合理边界（如每 10 条签文、每 5 篇简报）分批，但批次内仍整体翻译。
   - 整体审核：DeepSeek 全部初译完成后，把完整英文成果整体提交给 Gemini 审查（同样批量优先、分批兜底）。
   - 差异提取：Gemini 审查后只提取有 `severity=high` 异议的条目，不重审无异议部分。
   - 差异循环：仅对异议条目把 Gemini 意见返回 DeepSeek 修订 → Gemini 再审，最大循环 2 轮。
   - 人工兜底：2 轮后仍有异议的条目标记 `needs_human_review`，输出到 `data/content/_review_log/*.jsonl` 供人工定稿。

#### W2.1 前 20 条英文签文样本（数量待 D5）
1. 从参考数据库导出/标记前 N 条中文源签文。
2. 每条结构化字段沿用 GUA_COLUMNS（D13 已确认）：`sign_number`、`fortune`、`gua_type`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`（共 11 字段；W4 加载时按 D14 剔除 fortune/gua_type，剩 9 字段）。
3. 语言保持神秘但克制。
4. 按文化表达指南处理：保留 oracle/reading/reflection，避免 `guaranteed`、`cure`、`lawsuit win`、`death prediction`、`change your destiny`。
5. **产出方式：双 AI 交叉审核（批量翻译+差异循环）。** 按 W2.0 第 7 条批次策略：DeepSeek 一次性初译全部 20 条 → Gemini 整体审查 → 仅对 `severity=high` 差异条目循环（最大 2 轮）→ 仍不一致标记 `needs_human_review`。
6. 输出：`data/content/oracle_signs_en_sample.json` + `data/content/_review_log/oracle_signs_review.jsonl`（含每条的 A/B 对话历史、最终状态）。
7. 人工复核 `needs_human_review` 条目并定稿。

#### W2.2 数据校验测试
1. 测试必填字段、签号范围、空字符串。
2. 测试确定性承诺和敏感场景词不进入英文文案。
3. `pytest tests/test_english_content_data.py -q`。

#### W2.3 SEO 文章简报（25 篇）
1. 先简报后正文。每篇含 slug、标题、搜索意图、目标内链、文化说明/底线提示需求、转化入口。
2. 分组：10 篇基础解释 + 10 篇搜索意图 + 5 篇转化辅助。
3. **产出方式：双 AI 交叉审核。** DeepSeek 基于 W0 文化指南和 SEO 框架起草简报 → Gemini 审核搜索意图准确性、文化边界、内链合理性 → 异议循环（最大 2 轮）→ 人工兜底。脚本同 W2.1。
4. 简报未审核前不批量生成正文。

#### W2.4 合规页草稿
1. 起草 Privacy Policy、Terms of Use、Disclaimer、About、Contact。
2. **产出方式：双 AI 交叉审核。** DeepSeek 基于标准模板起草 → Gemini 审核法律用词准确性、管辖条款、免责边界 → 异议循环（最大 2 轮）→ 人工兜底。脚本同 W2.1。
3. 标注非律师草稿，上线前待专业律师复核。

#### W2.5 英文黄历术语数据
1. W1.1 的 `scripts/extract_lunar_en_candidates.py` 从 6tail `lunar.js` I18n messages 提取成熟英文候选词（6tail 已有完整英文版本，无需翻译）。
2. 每条：`source_zh`、`category`（`yi_ji`/`ji_shen`/`xiong_sha`/`zodiac`/`solar_term`/`direction`/`pengzu`/`status`）、`candidate_from_6tail`、`product_en`、`review_status`（`draft`/`approved`/`rejected`）、`notes`。
3. **产出方式：脚本提取 + 单次 AI 审核（不循环）。** `product_en` 直接采用 6tail 候选词；调用 DeepSeek 单次审核文化边界和禁止表达，标记 `review_status`。无需双 AI 循环，因为 6tail 英文已是成熟版本，只需确认符合本产品文化指南。
4. 只有 `review_status=approved` 进入英文 API 输出。
5. 无法准确翻译的神煞名用拼音/音译+简短解释（待 D6）。
6. 测试确认术语都有 approved 译名或明确 fallback。

#### W2.6 英文黄历场景映射
1. 新建 `huangli_scenarios_en.json`。
2. 第一轮场景：`wedding`→嫁娶/结婚、`moving`→入宅/移徙、`business_opening`→开市/开业、`travel`→出行、`signing`→立券/交易、`haircut`→理发/剃头。
3. 每场景提供英文显示名、文化说明、responsible-use 短句。
4. **产出方式：双 AI 交叉审核。** DeepSeek 基于中文场景映射起草英文 → Gemini 审核文化说明准确性和 responsible-use 边界 → 异议循环（最大 2 轮）→ 人工兜底。脚本同 W2.1。
5. 测试确认场景 key 稳定且能映射到现有中文宜忌和彭祖百忌判断。

#### W2.7 内容质量测试
1. 测试所有英文内容文件 UTF-8。
2. 测试每条签文 9 字段（剔除 fortune/gua_type 后）齐全且非空，或含 CJK 残留时触发 fallback 占位。
3. 测试法律页非空、文章 slug 唯一。
4. 测试禁止表达不出现在标题/meta/CTA/付费墙。

**验证命令：**
```powershell
pytest tests/test_english_content_data.py -q
```

**验收标准：**
- 签文结构化可审阅；内容测试能捕获确定性承诺、敏感场景、付费诱导。
- 25 篇简报完成；合规草稿存在且符合风险边界。
- 英文黄历术语和场景数据完成，只有 approved 术语进 API。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-28 至 2026-06-29 | 独立 Agent | W2.1 英文签文翻译超额完成 384/384（计划仅要 20 条样本）；字段结构沿用 GUA_COLUMNS（11 字段，含 fortune/gua_type，违反 D16 硬约束，待 W4 加载时剔除）；用 `scripts/translate_oracle_signs.py` + DeepSeek 翻译；Gemini 审核因 API 缺失仅完成前 12 条 | `data/content/oracle_signs_en.json` 存在 384 条；`data/content/_review_log/gemini_review_result_signs_1_4.md` 等 3 份审核记录；7 条 interpretation1 残留中文（50/63/101/222/237/261/286）、4 条 general 为空（197-200） | 质量遗留由独立 Agent 渐进修复，不阻塞程序落实；W2.2-W2.7 仍未做 |

---

### W3：英文路由骨架与错误码基础

**目标：** 建立英文路由、统一语言上下文、错误码模块。为 W4-W6 提供地基。

**代码现状：** `pages.py` 仅有 `/<lang>/*` 路由，无英文路由；`error_codes.py` 不存在。

**前置：** W0、D2、D12

**涉及文件：**
- 修改：`zhugeshensuan/blueprints/pages.py`
- 新建：`zhugeshensuan/error_codes.py`
- 新建：`zhugeshensuan/i18n.py`（语言上下文工具）
- 测试：`tests/test_english_routes.py`
- 测试：`tests/test_api_error_codes.py`

**子任务：**

#### W3.1 英文路由测试（TDD）
1. 测试 `/`、`/daily-almanac`、`/ask-oracle`、`/birth-chart-reading`、`/articles`、`/privacy`、`/terms`、`/disclaimer`、`/about`、`/contact` 返回 200。
2. 断言英文页面不出现仅属于简体中文首页的标题。
3. 运行确认先失败。

#### W3.2 错误码模块（审查 M2）
1. 新建 `error_codes.py`，code 列表**引用 W1.2 定稿**。
2. `api_utils.failure()` 保持向后兼容，但所有新英文 API 必须返回 `code`。
3. 增加 `test_api_error_codes.py`，确认英文 API 不依赖中文 `message`。
4. 不强行重写全部中文 API，只给英文路径留稳定接口。

#### W3.3 实现英文页面路由
1. 在 `pages.py` 添加英文路由处理，返回英文模板。
2. 保持简体和繁体路由不变。
3. 运行路由测试通过。

**验证命令：**
```powershell
pytest tests/test_english_routes.py tests/test_api_error_codes.py -q
```

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-30 | 助手 | W3 完成：W3.2 error_codes.py（27 个 code + MESSAGES_ZH/MESSAGES_EN/DEFAULT_HTTP_STATUS + get_message/get_http_status/failure_with_code）；W3.1+W3.3 pages_en.py（11 条英文路由 + `_render_en` 统一注入 `current_lang='en'`/`html_lang='en'`）；pages.py 删除 `index_redirect`（`/` 释放给英文首页）；blueprints/__init__.py 注册 pages_en_bp 并放第一位；11 个英文模板（base.html + 10 个页面） | test_client 验证：9 条英文路由 200 + 3 条旧中文路由 301 + `/zh-hans/almanac` 200；预存在测试 `test_suanshi_uses_chunked_typewriter_rendering` 失败与 W3 无关 | W4 Ask the Oracle 后端 |

---

### W4：Ask the Oracle 后端

**目标：** 英文算事的三词/三数字算法与 API。

**代码现状：** `oracle_english.py` 不存在；`tests/test_oracle_english.py` 不存在。

**前置：** W0、W2、D4、D12

**涉及文件：**
- 新建：`zhugeshensuan/oracle_english.py`
- 测试：`tests/test_oracle_english.py`

**子任务：**

#### W4.1 三词到签号算法（D4 已定稿）
1. 新建 `oracle_english.py`，复用 `scripts/derive_original_oracle_signs.py` 的 `stroke_digit`、`compose_three_character_number`、`reduce_to_start_index` 三个函数（直接 import 或抽取到共享模块）。
2. 接收三个英文词（以空白分隔），每词按 A=1..Z=26 对字母求和 → `stroke_digit`（和对 10 取模，余 0 取 1）→ d1/d2/d3（均 1-9），对应中文"三字→笔画数→笔画位"的神秘变换。
3. N = `compose_three_character_number`([d1,d2,d3]) = 100×d1+10×d2+d3；r = `reduce_to_start_index`(N) = ((N-1) mod 384)+1。
4. 词数不足返回 `ORACLE_WORDS_INSUFFICIENT`；空输入返回 `INVALID_INPUT`；非字母字符剔除后无字母的词按校验失败处理。
5. 测试：确定性（同三词同签号）、范围（N=111..999 → 1-384）、边界（空词、单字母词如"A"=1、超长词、含非字母字符的词）、字母求和正确性（LOVE=54→4, WORK=67→7, FATE=32→2）、0→1 规则（如字母和为 50/60/70 的词→1）。

#### W4.1a 英文签文数据加载（D15、D16、D17 硬约束）
1. 从 `data/content/oracle_signs_en.json` 加载 384 条签文到内存字典（D15：JSON 内存加载，不入数据库；中文仍走 `database.py`）。
2. **加载时剔除 `fortune` 和 `gua_type` 字段**（D14 倾向确认，D16 硬约束）：英文 API 响应不包含这两个字段。
3. 内存字典键为 `sign_number`（int），值为剔除后的字段 dict（`sign_number, sign_text, interpretation1, career, wealth, love, health, study, general`，共 9 字段）。
4. **未译签文 fallback**（项目硬约束）：若某签号的 `interpretation1` 含中文残留（CJK 字符检测）或 `general` 等必填字段为空，对应字段返回 `"This sign's English translation is under review."` 占位。
5. 启动时加载一次，运行期只读，不修改原 JSON 文件。
6. 测试：加载后字段数 = 9（无 fortune/gua_type）；中文残留触发 fallback；空字段触发 fallback；384 条全覆盖。

#### W4.2 三数字算法（英文专用，非源书方法）
1. 复用 `scripts/derive_original_oracle_signs.py` 的 `compose_english_three_number_seed` 和 `reduce_to_start_index`。
2. 接收三个整数，每个 0-999。
3. seed = `compose_english_three_number_seed`([d1,d2,d3]) = d1×1,000,000 + d2×1,000 + d3；r = `reduce_to_start_index`(seed) = ((seed-1) mod 384)+1。
4. 每个数超范围或三组全零返回 `INVALID_ORACLE_NUMBER`。
5. 测试：最小（0,0,1）/最大（999,999,999）/全零拒绝/非法类型/缺失/确定性。

#### W4.3 英文算事 API
1. 接口 `POST /api/en/oracle/ask`（D12 已确认统一 `/api/en/*` 前缀）。
2. Payload：`{ "mode": "words", "words": ["love","work","fate"] }` 或 `{ "mode": "numbers", "numbers": [123,45,678] }`。
3. 返回英文签文结构化字段（9 字段，D14 已确认剔除 fortune/gua_type）。
4. 非法输入返回稳定错误码。
5. 保持现有 `/calculate_sign`、`/get_gua_info` 不变，继续服务中文。
6. 返回字段固定（D13/D14）：`sign_number`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`。
7. 测试：同一三词输入多次返回同一签号；`numbers` 和 `words` 模式不互收错误 payload；未译签文触发 fallback 占位。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-30 | 助手 | W4 完成：oracle_algorithm.py（纯函数算法模块，复用 derive_original_oracle_signs.py 的 stroke_digit/compose_three_character_number/reduce_to_start_index，新增 word_to_letter_sum/word_to_stroke_digit/three_words_to_start_index/word_transform）；oracle_english.py（load_english_signs 内存加载 + _sanitize_record 剔除 fortune/gua_type + CJK/空字段 fallback + ask_with_words/ask_with_numbers）；blueprints/oracle_en_api.py（POST /api/en/oracle/ask 双模式）；config.py 加 ENGLISH_SIGNS_PATH；app.py 启动期加载 english_signs 到 extensions（无缝切换） | pytest tests/test_oracle_english.py 76 passed；含 LOVE/WORK/FATE→Sign #88、314/159/265→Sign #33、D14 字段剔除、CJK fallback、空字段 fallback、384 全覆盖、模式不互收、错误码全验证 | W6 Birth Chart Reading 后端 |

---

### W5：Daily Almanac 后端

**完成状态（2026-07-01）：** 已完成。英文词表、20 个常见神煞审校、转换服务、
`GET /api/en/daily-almanac`、`GET /api/en/week-almanac`、英文页面接入和 2026
全年无中文泄漏扫描均已通过；未审校术语默认隐藏并仅在 `debug=1` 时进入 `_missing`。

**目标：** 英文黄历适配与 API。

**代码现状：** `huangli_english.py` 不存在；`tests/test_huangli_english.py` 不存在。

**前置：** W0、W2、D6、D7、D12

**涉及文件：**
- 新建：`zhugeshensuan/huangli_english.py`
- 测试：`tests/test_huangli_english.py`

**子任务：**

#### W5.1 英文黄历适配
1. 保持现有 `/api/huangli`、`/api/week_huangli` 兼容。
2. 新增英文专用接口（D12 已确认统一 `/api/en/*` 前缀）：
   - `GET /api/en/daily-almanac?date=YYYY-MM-DD&scenario=wedding`
   - `GET /api/en/week-almanac?scenario=wedding`
3. 内部复用当前简体基础 record 和 `scenario_assessment.status_code`。
4. 使用 `data/content/huangli_terms_en.json` 输出英文展示值。
5. 使用 `data/content/huangli_scenarios_en.json` 映射英文场景到中文关键词。
6. 返回字段固定：`date`、`lunar_date`、`zodiac`、`solar_term`、`favorable_activities`、`unfavorable_activities`、`scenario_assessment`、`responsible_use`、`source_language`。
7. `scenario_assessment` 用 `status_code`，英文 `status_label` 仅供展示。
8. 测试：未知英文场景返回 `INVALID_SCENARIO`；未 approved 术语不静默进入输出。

#### W5.2 fallback 策略（审查 M4 并行 workaround）
1. 若某中文黄历术语无 approved 英文译名，英文 API 不直接输出中文。
2. 可选 fallback：返回 `translation_missing=true` 并隐藏该术语；或返回拼音+`notes`（仅限人工批准）。
3. fallback 规则写入测试。
4. **并行 workaround：** 允许 W5.1 在 W1.1 术语未全部 approved 时先用 `translation_missing=true` 开发，术语后补，不阻塞后端。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |

---

### W6：Birth Chart Reading 后端

**目标：** 英文论命输入边界、报告结构、AI prompt 边界。

**代码现状：** `zhugeshensuan/birth_chart_english.py` 已实现（BirthChartEnglish 服务 + 映射表 + prompt + 解析）；`zhugeshensuan/blueprints/birth_chart_en_api.py` 已实现（POST /api/en/birth-chart/analyze + POST /api/en/birth-chart/stream）；`app.py` 注入 `birth_chart_en` 扩展（复用 lunming 的 OpenAI client）；`tests/test_birth_chart_english.py` 59 项测试全过。W6.1 文章加载归属 W8（已暂停），不在本轮范围。

**前置：** W0（含 W0.3 AI prompt 边界文档）、W2、D11、D12

**涉及文件：**
- 新建：`zhugeshensuan/birth_chart_english.py`（BirthChartEnglish 服务、映射表、build_english_prompt、_parse_ai_report）
- 新建：`zhugeshensuan/blueprints/birth_chart_en_api.py`（analyze + stream API）
- 修改：`zhugeshensuan/app.py`（注入 birth_chart_en 扩展）
- 修改：`zhugeshensuan/blueprints/__init__.py`（注册 birth_chart_en_api_bp）
- 测试：`tests/test_birth_chart_english.py`
- 待建（W8 解冻后）：`zhugeshensuan/content.py`（文章加载，与 W8 共用）、`zhugeshensuan/seo.py`

**子任务：**

#### W6.1 英文内容加载
1. 加载文章 manifest、文章正文来源。
2. 未知 slug 返回 404。
3. SEO 元数据辅助函数。
4. 测试：文章列表、详情、canonical、标题唯一性。

#### W6.2 英文论命后端边界
1. 复用现有八字计算能力。
2. 英文 API 输入字段：`name`、`birth_date`、`birth_time`、`birth_time_unknown`、`gender`、`timezone`。
3. 输入校验明确处理出生时间未知。
4. **英文 prompt 必须引用 W0.3 产出的边界文档**（审查 M3 隐性依赖）。
5. 返回结构：`chart_summary`、`element_balance`、`reflection_points`、`cautions`、`responsible_use`。
6. 不输出医疗/法律/财务/心理/生育/死亡/灾难的确定性结论。
7. SSE 流保留错误事件和结束事件。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-30 | 助手 | W6.1 文章加载（content.py/seo.py）划归 W8，本轮不实施 | W8 暂停（D3 文章系统格式未定） | W8 解冻后再实施 |
| 2026-06-30 | 助手 | W6.2 Birth Chart English 服务模块：birth_chart_english.py（ZODIAC_EN/GAN_EN/ZHI_EN/ELEMENT_EN/GENDER_ZH 映射表 + pillar_to_english + normalize_gender + normalize_payload + build_english_chart_summary + build_english_prompt 引用 W0.3 边界 + _parse_ai_report + BirthChartEnglish.analyze/analyze_stream/build_chart_summary）；responsible_use 文案内嵌；AI prompt 禁医疗/法律/财务/心理/生育/死亡/灾难/确定性未来/吉凶分级/卦属 | 提交 3d8b9dc（WIP 检查点） | API 蓝图 + 注入 + 测试 |
| 2026-06-30 | 助手 | W6.3 API 蓝图 birth_chart_en_api.py：POST /api/en/birth-chart/analyze（同步）+ POST /api/en/birth-chart/stream（SSE）；payload 校验（name 1-30 字符、birth_date 必填、birth_time 字符串或 null、birth_time_unknown 布尔）；usage 配额 acquire/release；错误码 INVALID_BIRTH_DATA/MODEL_NOT_CONFIGURED/ANALYSIS_FAILED + AI 用量 429；SSE 事件序列 chart→report→responsible_use→done | 验证脚本确认路由注册 + 空载荷 400 + 非 JSON 400 + 合法无 key 503 + stream 200 SSE chart 英文化 | 注入 + 测试 |
| 2026-06-30 | 助手 | W6.3 app.py 注入 birth_chart_en 扩展（复用 lunming 实例的 OpenAI client，配置统一）；blueprints/__init__.py 注册 birth_chart_en_api_bp | app.extensions["birth_chart_en"] 可用 | 测试 |
| 2026-06-30 | 助手 | W6.4 测试 test_birth_chart_english.py（59 项）：映射表完整性 + 四柱英文化 + 性别归一化 + payload 归一化 + 英文基础盘摘要 + AI prompt 红线 + AI 报告解析（合法/代码栅栏/非法/不完整/cautions str+dict/上限 4） + 服务层 mock AI（responsible_use/chart_summary dict/reflection_points/no fortune-gua_type/stream 事件序列/chart 英文/invalid birth raises/json_object+stream） + API 契约无 key 路径（missing_name/empty_name/too_long/missing_date/invalid_time_type/invalid_time_unknown/non_json/invalid_date/valid_no_key 503/stream_*） + API 契约 mock AI 完整路径（analyze_full_success/stream_full_success） | `pytest tests/test_birth_chart_english.py` 59 passed in 2.41s | 提交 |
| 2026-06-30 | 助手 | 设计修正：stream 端点用 POST 而非 GET（与中文 lunming_api.py 一致，便于传 JSON body）；done 帧归属 API 层统一补发（服务层 analyze_stream 只产 chart/report/responsible_use，避免重复 done，与 lunming.analyze_bazi_stream 对齐） | 见变更日志 0.12 | — |

**W6 完成状态：** 已完成（W6.1 划归 W8 暂停）。Birth Chart Reading 英文后端可投入 W7 前端对接。

---

### W7：英文前端

**目标：** 英文 Wise Oracle 主站、三个工具页、合规页、核心转化位。

**代码现状：** `frontend/templates/en/` 不存在；`base.html` 不存在；英文 JS/CSS 不存在。

**前置：** W3、W4、W5、W6

**涉及文件：**
- 新建：`frontend/templates/base.html`
- 新建：`frontend/templates/en/{index,daily_almanac,ask_oracle,birth_chart_reading,articles,article_detail,privacy,terms,disclaimer,about,contact}.html`
- 新建：`frontend/static/js/{ask_oracle_en,daily_almanac_en,birth_chart_en,wise_oracle_common}.js`
- 新建：`frontend/static/css/wise_oracle.css`
- 测试：`tests/test_english_frontend_contract.py`

**子任务：**

#### W7.1 视觉方向
1. 东方文化、克制、清晰、可信。
2. 避免紫色渐变、装饰光球、过暗神秘风。
3. 工具优先布局，首屏展示真实可用工具。

#### W7.2 英文共享布局（已知技术债）
1. `base.html` 提供：`<html lang="en">`、title/meta description block、canonical block、responsive viewport、页眉导航、页脚法律入口。
2. 英文页面继承 base，不复制整页 HTML。
3. **已知技术债：** 中文现有模板不迁移到 base，中英长期两套布局，维护成本高。接受此权衡以缩小回归面。

#### W7.3 英文首页
1. H1 `Wise Oracle`；主按钮→`/ask-oracle`；次按钮→`/daily-almanac`。
2. 简短 responsible-use 提示；三大工具页和文章页内链。

#### W7.4 Ask the Oracle 页面
1. 三词+三数字模式切换；显示引导语（Hold one question quietly in mind...）；校验/加载状态。
2. 【仅 Three Words】提交后动画展示变换过程（LOVE→54→4 等），再显示签号；旁提供折叠项 "How were these numbers formed?"；输入前不展示公式。
3. 渲染 9 字段（D13/D14）：`sign_number`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`。
4. 免费结果后展示克制赞助/付费墙占位。
5. 调用 `POST /api/en/oracle/ask`，不复用中文 `/calculate_sign` 前端交互。
6. 输入错误显示英文文案，保留后端 `code` 便于调试。
7. 契约测试：含两种输入模式、responsible-use、结果容器；不出现 `oracle_title`/`message`/`guidance_summary`/`caution` 旧字段名。

#### W7.5 Daily Almanac 页面
1. 日期选择器、场景筛选；渲染 Favorable/Unfavorable Activities。
2. 可用时渲染 lunar date、solar term、zodiac。
3. 调用 `GET /api/en/daily-almanac`、`GET /api/en/week-almanac`。
4. 场景选项用稳定 key（wedding 等）。
5. `translation_missing=true` 时显示温和 fallback，不展示原始中文。
6. 契约测试：页面不含 `Yellow Calendar`。

#### W7.6 Birth Chart Reading 页面
1. 复用现有论命必要交互；文案用 birth chart insight、self-reflection。
2. 输入隐私提示可见；AI 生成/加载状态明确。
3. 出生时间未知用 checkbox/toggle，不要求选"未知"中文值。
4. 调用 `POST /api/en/birth-chart/analyze` 和 SSE `POST /api/en/birth-chart/stream`（注：stream 用 POST 而非 GET，与中文 lunming_api.py 一致便于传 JSON body，详见变更日志 0.12），不直接把中文 SSE 文案暴露给英文页面。
5. 契约测试：不出现 `fate guarantee`、`accurate prediction`、`pay to change your destiny`。

#### W7.7 合规页
1. 渲染 Privacy/Terms/Disclaimer/About/Contact。
2. 每个英文页页脚可达这些页面。
3. Contact 上线前必须有真实联系方式或明确标记待补。

#### W7.8 响应式与可访问性
1. 桌面/移动端宽度测试；无横向溢出。
2. 控件有 label；键盘焦点可见；错误信息不只依赖颜色。

#### W7.9 浏览器人工验收清单
1. 桌面 1440px：首页、三大工具页、文章页、法律页。
2. 移动 390px：输入框、按钮、结果卡片、日期选择器。
3. Ask the Oracle 测两模式；Daily Almanac 测日期切换+六场景；Birth Chart 测出生时间未知。
4. 断网/API 失败检查错误状态。

**验证命令：**
```powershell
pytest tests/test_frontend_contract.py tests/test_english_frontend_contract.py tests/test_english_routes.py -q
```

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |
| 2026-06-30 | 助手 | W7.2 英文共享布局：`base.html` 修改 CSS 链接 `css/style.css`→`css/wise_oracle.css`、加 `<link rel="canonical">`、在 `{% block scripts %}` 前加 `wise_oracle_common.js`；新建 `wise_oracle.css`（640 行，CSS 变量 `--wo-bg #faf7f2`/`--wo-accent #8a3324`/`--wo-ink #3a2e25`/`--wo-gold #b08d3e`、Georgia 衬线标题、卡片式工具布局、@media max-width:640px 响应式）；新建 `wise_oracle_common.js`（158 行，`ERROR_MESSAGES` 错误码→英文文案映射、`postJSON` fetch POST 封装、`readSSE` 手动流读取 response.body.getReader + TextDecoder、`el`/`setStatus` DOM 辅助、`window.WiseOracle` 命名空间） | 文件已建；冒烟验证 11 路由 200 | W7.3 首页 |
| 2026-06-30 | 助手 | W7.1 视觉方向：在 W7.2 CSS 落地东方克制风（米色背景、墨红 accent、Georgia 衬线标题、卡片式工具布局），避免紫色渐变/装饰光球/过暗神秘风 | wise_oracle.css 变量与排版体现 | — |
| 2026-06-30 | 助手 | W7.3 英文首页：`index.html` 含 H1 `Wise Oracle`、三大工具入口卡（Ask the Oracle / Daily Almanac / Birth Chart Reading）、responsible-use 提示 | 冒烟验证元素存在 | W7.4 |
| 2026-06-30 | 助手 | W7.4 Ask the Oracle 前端：重写 `ask_oracle.html`（mode tabs Three Words/Three Numbers、3 词输入、3 数字输入、Draw a Sign 按钮、变换动画区、结果区、折叠项 "How were these numbers formed?"）；新建 `ask_oracle_en.js`（274 行：模式切换、校验词数/字母与数字范围/全零、`POST /api/en/oracle/ask`、变换动画 word→letter_sum→digit 逐行淡入 350ms 间隔、9 字段渲染 sign_number/sign_text/interpretation1/career/wealth/love/health/study/general、responsible_use、赞助占位、Draw Another Sign 重启） | 文件已建；契约测试覆盖两模式/Draw a Sign/折叠项/JS 加载/引导语/禁止旧字段 oracle_title/guidance_summary/Ask Another Question | W7.5 |
| 2026-06-30 | 助手 | W7.5 Daily Almanac 降级：重写 `daily_almanac.html` 去除内部 W5 引用，用户友好 "Coming soon" + 图例保留；不调用 `/api/en/daily-almanac`（W5 暂停） | 契约测试覆盖 Coming soon + 不含 Yellow Calendar | W7.6 |
| 2026-06-30 | 助手 | W7.6 Birth Chart 前端：重写 `birth_chart.html`（name/gender/birth_date/birth_time/birth_time_unknown checkbox/timezone、隐私提示 "Your birth details are processed only to generate this reading and are not stored"、Generate Chart 按钮、loading 区、结果区）；新建 `birth_chart_en.js`（290 行：checkbox 联动、校验、`POST /api/en/birth-chart/stream` SSE 流消费，事件处理 chart→四柱网格 + Day Master/Zodiac/Lunar Date facts + Element Balance + limitations、report→AI chart_summary + element_balance + reflection_points + cautions、responsible_use、error→错误码映射、done→流结束） | 文件已建；契约测试覆盖 checkbox/Generate Chart/JS 加载/隐私提示/非预测定位/禁止 fate guarantee/accurate prediction/pay to change your destiny | W7.7 |
| 2026-06-30 | 助手 | W7.7 合规页：重写 `privacy.html`（8 节真实内容：信息收集/AI 服务/Cookies/不收集的数据/用户权利/儿童隐私/联系/变更，修复 `\"we\"`→`"we"` HTML 转义错误）；`terms.html`（10 节：服务性质/非专业建议/AI 内容/可接受使用/免费使用与配额/无担保/责任限制/第三方链接/变更/联系）；`disclaimer.html`（6 节：娱乐文化定位/非专业建议/无预测或保证/AI 内容/文化内容准确性/责任限制/外部链接）；`about.html`（定位 "mirror, not a map" + 三大工具链接 + responsible use）；`contact.html`（contact@wise-oracle.example / privacy@wise-oracle.example + 支持响应时间） | 契约测试覆盖 5 合规页真实内容关键词 | W7.9 |
| 2026-06-30 | 助手 | W7 文章页占位：重写 `articles.html` 与 `article_detail.html` 去除 W8/D3 引用，"Coming soon"（W8 暂停） | 契约测试覆盖 11 路由 200 | — |
| 2026-06-30 | 助手 | W7.9 契约测试：新建 `tests/test_english_frontend_contract.py`（280 行，40 测试），覆盖 11 路由 200、base.html（lang=en/wise_oracle.css 非 style.css/common.js/canonical/responsible-use footer）、首页（brand + 三大工具入口）、Ask the Oracle（两模式/Draw a Sign/折叠项/JS/引导语/禁止旧字段）、Daily Almanac（Coming soon/不含 Yellow Calendar）、Birth Chart（checkbox/Generate Chart/JS/隐私提示/非预测定位/禁止短语）、合规页（Privacy/Terms/Disclaimer/About/Contact 真实内容）。辅助函数 `_normalize_ws()` 归一化空白解决跨行断言、`_raw()` 保留原始空白用于 HTML 属性断言 | `pytest tests/test_english_frontend_contract.py` 40 passed in 10.28s | — |

---

### W8：SEO / 合规 / 商业化预埋

**目标：** sitemap、robots、文章系统、赞助/付费墙/广告位占位（默认关闭）。

**代码现状：** `seo.py`、`commerce*.py`、`blueprints/commerce_api.py` 均不存在；`sitemap.xml`、`robots.txt` 模板不存在。

**前置：** W2、W7、D3、D8、D9、D10

> **范围说明：** 本工作包只覆盖英文站相关的 SEO 和商业化预埋。完整的商业化基础代码（订单模型、webhook 等）和非英文 SEO 仍在总纲 P6/P7 追踪。

**涉及文件：**
- 新建：`zhugeshensuan/blueprints/seo.py`
- 新建：`frontend/templates/{sitemap.xml,robots.txt}`
- 新建：`zhugeshensuan/commerce.py`、`zhugeshensuan/commerce_models.py`、`zhugeshensuan/blueprints/commerce_api.py`
- 新建：`frontend/templates/partials/{sponsor,paywall,ad_slot}.html`
- 新建：`frontend/static/js/commerce.js`
- 修改：`zhugeshensuan/config.py`、`.env.example`
- 测试：`tests/test_{sitemap,robots,articles,commerce_config,commerce_api}.py`

**子任务：**

#### W8.1 文章系统（待 D3）
1. 确定文章来源（Markdown/JSON/数据库，待 D3）。
2. 渲染 `/articles`、`/articles/<slug>`。
3. 唯一标题和 meta description；指向相关工具页内链。

#### W8.2 发布第一批内容
1. ≥10 篇基础解释 + ≥10 篇搜索意图 + ≥5 篇转化辅助。
2. 审查薄内容、重复 AI 句式、夸大表达。
3. 需要处添加文化说明或 responsible-use 提示。

#### W8.3 sitemap 和 robots
1. 包含英文路由、繁体路由、文章 URL。
2. 排除 admin、API、debug URL。
3. 预期 URL 测试。

#### W8.4 Search Console 和 AdSense 清单
1. 域名所有权验证方式；sitemap 提交；AdSense 审核清单。
2. 确认 Privacy/Terms/Disclaimer/About/Contact 全站可达、无空白。

#### W8.5 商业化配置开关
1. 配置项：`WISE_ORACLE_SPONSOR_ENABLED`、`WISE_ORACLE_PAYWALL_ENABLED`、`WISE_ORACLE_ADS_ENABLED`、`WISE_ORACLE_CHECKOUT_URL`、`WISE_ORACLE_SPONSOR_URL`。
2. 全部默认关闭；`.env.example` 记录说明。
3. 测试：开关关闭时不渲染赞助/付费墙/广告。

#### W8.6 赞助组件
1. 文案：`If this reading helped you reflect, you can support Wise Oracle.`
2. 不靠近 AdSense 广告位；不暗示赞助让结果更准。

#### W8.7 付费墙原型（待 D8、D9）
1. `Wise Oracle Deep Reading` 付费墙 partial。
2. 价值点：完整 message、3 条具体 guidance、7-30 天 reflection focus、可复制报告格式。
3. 平台未核验前只用禁用/模拟 checkout（待 D9）。
4. checkout URL 为空时显示等待名单，不显示坏链接。

#### W8.8 最小订单记录（草案）
1. 字段：`order_id`、`provider`、`product_code`、`amount`、`currency`、`status`、`created_at`、`unlock_token_hash`、`refund_status`。
2. 平台未选定前不持久化真实订单，只增加模型校验测试。

#### W8.9 广告位占位
1. 布局安全的广告位 partial；仅 `WISE_ORACLE_ADS_ENABLED=true` 显示。
2. 不靠近主要工具按钮；不出现引导点击广告文案。

**验证命令：**
```powershell
pytest tests/test_sitemap.py tests/test_robots.py tests/test_articles.py tests/test_commerce_config.py tests/test_commerce_api.py -q
```

**人工验收：** 访问 `/sitemap.xml`、`/robots.txt`、随机 5 篇文章、页脚法律入口。

**进度日志：**

| 日期 | 负责人 | 改动 | 证据 | 下一步 |
| --- | --- | --- | --- | --- |

---

## 5. 推荐实施顺序

1. **先决决策门 D1、D2、D11** → 解锁 W0。
2. W0 → W1（术语+错误码策略）→ W2（数据）。
3. W3（路由+错误码）可与 W2 后半并行，前提是 W1.2 错误码策略已定稿。
4. W4、W5、W6 可在 W3 完成后并行推进（三个独立后端）。
5. W7 依赖 W3-W6 全部完成。
6. W8 依赖 W2、W7。
7. **关键串行链：** W1.1（术语）→ W2.5（术语数据）→ W5.1（黄历 API）。若 W1.1 卡住，用 W5.2 的 `translation_missing=true` fallback 先行开发 W5.1，不阻塞。

---

## 6. 代码一致性校验点

> 每次合并到主干后，复核以下项是否与代码一致。不一致时更新本节和第 1 节基线。

| 校验项 | 命令 | 预期 |
| --- | --- | --- |
| 英文路由存在性 | `rg -n "ask-oracle\|daily-almanac\|birth-chart-reading" zhugeshensuan/blueprints/pages.py` | W3 完成前无命中；完成后有命中 |
| 错误码模块存在性 | `Test-Path zhugeshensuan/error_codes.py` | W3.2 完成前 False；完成后 True |
| 英文模板目录 | `Test-Path frontend/templates/en` | W7 完成前 False；完成后 True |
| 英文数据目录 | `Test-Path data/content` | W2 完成前 False；完成后 True |
| 英文测试存在性 | `rg -l "english" tests/` | 随工作包推进逐步增加 |

---

## 7. 变更日志

> 记录对本计划本身的修改（增删任务、调整顺序、修正错误）。任务状态变更不记此处，只更新对应进度日志。

| 日期 | 修订人 | 变更内容 | 原因 |
| --- | --- | --- | --- |
| 2026-06-27 | Codex | 初版创建，从总纲拆出英文站改造 | 总纲英文部分过重，需独立可追溯文档 |
| 2026-06-27 | Codex | 建立 W0-W8 单编号体系取代 E/P 双轨 | 审查 S1：双轨交叉不对齐 |
| 2026-06-27 | Codex | 新增第 2 节决策门，标注 12 个阻塞决策 | 审查 S2：决策项无门标记 |
| 2026-06-27 | Codex | W3.2 错误码模块明确引用 W1.2 定稿 | 审查 M2：P2.7 与 P4.1a 重叠 |
| 2026-06-27 | Codex | W0.3 增加 AI prompt 边界文档产出 | 审查 M3：W6 隐性依赖 |
| 2026-06-27 | Codex | W5.2 增加 translation_missing fallback 并行 workaround | 审查 M4：串行链无并行 |
| 2026-06-27 | Codex | 新增 D12 决策项统一 API 路径前缀 | 审查 M1：前缀不一致 |
| 2026-06-27 | Codex | W7.2 标注中文不迁移 base 为已知技术债 | 避免未来疑问 |
| 2026-06-27 | Codex | API 路径统一为 `/api/en/*`：W4.3 改 `POST /api/en/oracle/ask`，W6.2 加 `POST /api/en/birth-chart/analyze` + `GET /api/en/birth-chart/stream`，W7.4/W7.6 同步 | 修正 1：D12 已确认后示例不一致 |
| 2026-06-27 | Codex | W6 测试文件名从 `test_seo_pages.py` 改为 `test_birth_chart_english.py` | 修正 2：test_seo_pages 更贴切 W8 |
| 2026-06-27 | Codex | W0.3 明确 prompt 边界文档文件名 `docs/business/wise-oracle-ai-prompt-boundaries.md`；W0 涉及文件列表补入；W6.2 引用具体路径 | 修正 3：避免口头依赖 |
| 2026-06-27 | Codex | 决策门 D1/D2/D4/D5/D6/D7/D9/D10/D12 状态更新为「已确认」 | 用户拍板 9 项决策 |
| 2026-06-27 | Codex | W2 新增 W2.0 前置任务：DeepSeek+Gemini API key 准备、translator/reviewer 系统提示词规范 | 用户确定双 AI 交叉审核方案 |
| 2026-06-27 | Codex | W2.1/W2.3/W2.4/W2.6 明确产出方式为双 AI 交叉审核（DeepSeek 初译+Gemini 审核+异议循环最大 2 轮+人工兜底） | 用户方案落地 |
| 2026-06-27 | Codex | W2.5 产出方式改为脚本提取 6tail 英文候选+单次 AI 审核（不循环） | 6tail 已有成熟英文版本，无需反复折腾 |
| 2026-06-27 | Codex | W2 涉及文件补充：scripts/translate_and_review.py、prompts/translator_system_prompt.md、prompts/reviewer_system_prompt.md、.env.example | 支撑双 AI 方案的文件清单 |
| 2026-06-27 | Codex | W2.0 增补翻译批次策略（批量优先+分批兜底+整体审核+差异提取+仅异议循环+人工兜底）；W2.1 产出方式引用该策略 | 避免逐句翻译破坏上下文一致性 |
| 2026-06-30 | 助手 | W6.2 stream 端点从 `GET /api/en/birth-chart/stream` 改为 `POST`；W7.6 同步更新 | GET 不便传 birth chart JSON body（body 非标准、query param 暴露出生数据）；与中文 `lunming_api.py` 的 POST stream 一致 |
| 2026-06-30 | 助手 | W6.2 done 帧归属设计：服务层 `analyze_stream` 只产 chart/report/responsible_use 内容事件，终止帧 `done` 由 API 层（`birth_chart_en_api.stream`）统一补发（正常完成 + 异常分支） | 避免 service 与 API 层都补 done 导致重复；与 `lunming.analyze_bazi_stream` 对齐 |
| 2026-06-30 | 助手 | W6.1 文章加载（content.py/seo.py）从 W6 划归 W8 | W8 暂停（D3 文章系统格式未定）；W6 聚焦 Birth Chart Reading 后端 |
| 2026-06-30 | 助手 | W6 涉及文件更新：移除 content.py/seo.py（划归 W8），新增 birth_chart_english.py、birth_chart_en_api.py、app.py、blueprints/__init__.py | 与实际代码现状一致 |
| 2026-06-30 | 助手 | W7.2 CSS 独立决策：英文 `base.html` 链接 `wise_oracle.css` 而非中文 `style.css`，中英两套独立布局（W7.2 已知技术债确认落实） | 避免中文暗棕卷轴风污染英文东方克制风；缩小回归面，不强行迁移中文模板到 base |
| 2026-06-30 | 助手 | W7.5 Daily Almanac 降级策略：W5 暂停导致黄历后端未就绪，前端做用户友好 "Coming soon" + 图例保留，不调用 `/api/en/daily-almanac` | W5 暂停（黄历上线范围待用户核实）；保证页面可达 200 + SEO 友好，不留死链 |
| 2026-06-30 | 助手 | W7 文章页占位策略：W8 暂停（D3 文章系统格式未定），`articles.html`/`article_detail.html` "Coming soon" 占位 | W8 暂停；保证路由可达与契约测试覆盖 |
| 2026-06-30 | 助手 | W7.9 契约测试跨行断言修复：`_normalize_ws()` 归一化空白（连续空白折叠为单空格）解决 HTML 源码跨行折断导致字面匹配假阳性；`_raw()` 保留原始空白用于 HTML 属性断言 | 冒烟脚本曾因 "not a destiny reading" 跨行折断字面匹配失败，正式契约测试改用归一化匹配 |
| 2026-06-30 | 助手 | W7 完成：W7.2-W7.7 全部落地 + W7.9 契约测试 40 项全过；W7.1（视觉方向文档无独立产出）、W7.8（响应式可访问性留待浏览器人工验收）标注未做 | W7 英文前端主线完成，英文站改造 W1→W3→W4→W6→W7 全部完成 |
