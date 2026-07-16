# 项目后续工作主台账 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 以一份可追溯、可新增、可修改、可取消的主台账，管理本项目从当前可用状态到公开上线、内容建设与商业化验证的全部剩余工作。

**Architecture:** 本文档是“未完成工作”的唯一主台账；旧总纲、英文站计划和问题审计仅作需求依据与历史证据。每项工作使用稳定 ID，任务状态与计划修订分开记录；删除通过“已取消 + 保留墓碑记录”实现，不破坏追溯链。

**Tech Stack:** Python 3.13、Flask、Jinja2、SQLite、pytest、Black、Ruff、原生 JavaScript/CSS、Docker/Gunicorn、GitHub Actions。

---

## 1. 台账定位与效力

- **建立日期：** 2026-07-15
- **当前版本：** 1.17
- **主维护人：** 项目所有者 + 当次执行者
- **状态基线：** 2026-07-17，生产站与文章系统已上线；CI 修复提交 `44f6925` 已推送到 `main`，GitHub Actions run 20 全部通过。本地基线为 pytest 450/450、Black、Ruff、14/14 JavaScript、pip-audit 和生产 Docker 冒烟通过。run 19 的红灯根因已关闭，OPS-005 只保留外部监控和统一验收证据收尾。
- **上位契约：** `README.md`、`docs/API文档.md`、`Agent.md`。
- **历史依据：**
  - `docs/reviews/2026-07-14-project-completion-issues-audit.md`
  - `docs/plans/2026-06-24-global-i18n-commercialization-execution-plan.md`
  - `docs/plans/2026-06-27-english-site-execution-plan.md`

若历史文档的“待办/进度”与本台账冲突，以本台账为准；产品契约冲突则以 README、API 文档和自动化测试为准。

## 2. 台账维护规则

### 2.1 状态枚举

| 状态 | 含义 | 必填证据 |
| --- | --- | --- |
| 待决策 | 方案会实质改变实现，需项目所有者拍板 | 决策 ID、可选项、建议项 |
| 就绪 | 依赖和决策齐备，可立即开始 | 验收标准、文件范围 |
| 进行中 | 已有执行者正在实施 | 负责人、开始日期、当前步骤 |
| 阻塞 | 外部条件或上游任务未满足 | 阻塞原因、解除条件 |
| 待验收 | 实施完成，等待人工或上线验收 | 提交、测试结果、验收地址 |
| 已完成 | 所有验收标准已满足 | 提交/CI/截图/运行记录 |
| 已取消 | 已删除的计划，不再执行 | 取消原因、替代任务或决策 |

### 2.2 新增、修改与删除

1. **新增：** 使用对应领域的下一个永不重用的 ID，填入主表、任务卡和变更记录。
2. **修改：** 保留 ID，直接更新主表/任务卡，并在第 10 节记录“修改前→修改后”及原因。
3. **删除：** 不物理删除 ID；将状态改为“已取消”，从活动视图移到第 9 节取消区。
4. **状态变更：** 只追加第 8 节进度日志；不把普通状态变更写成计划修订。
5. **完成限制：** 不得仅因为“代码已写”标记完成；必须同时完成测试、文档、验收证据和必要的回滚说明。

### 2.3 ID 前缀

| 前缀 | 领域 |
| --- | --- |
| GOV | 台账与质量治理 |
| UI | 中文站界面与文化呈现 |
| SAFE | 内容安全与文化边界 |
| SEO | 技术 SEO 与搜索收录 |
| ART | 英文文章系统与内容 |
| TRUST | 联系方式、法务与用户信任 |
| OPS | 部署、监控、备份与上线 |
| COM | 商业化调研与代码 |
| MET | 隐私友好的运营指标与复盘 |
| DEC | 需项目所有者拍板的决策 |

### 2.4 SAFE 内容审查治理规则

1. **裁决权：** 项目所有者是内容风险的最终审查人，决定已确认问题项“修改 / 保留并接受风险 / 删除 / 另行指定”以及具体修改方向；执行者、脚本和 CI 均不得代替项目所有者作最终裁决。
2. **执行者初筛责任：** 执行者必须检查全部约定内容，先高召回收集，再结合完整语境逐项判断；覆盖证明、待分析候选、一般边界表达和“极端判词/明确专业操作”必须分开，只有最后一类进入业主审查册。
3. **自动化边界：** 自动化只用于提高覆盖率、定位候选项和核对清单完整性，不得把字段名或关键词命中直接等同于问题，也不得把未完成语义判断的候选转交项目所有者。
4. **先审后改：** 在项目所有者对问题项确认前，不修改 `oracle_signs_en.json` 或其他内容源；执行者须指出具体问题句、判断理由和非约束性修改建议。
5. **审查口径：** 允许一般运势、象征性解释、低风险生活提醒和 `may/could` 式可能性表达；奖金、分红、行业意象、一般财富趋势、储蓄、避免投机、普通饮食和散步默认保留，不因个别词汇进入问题清单。
6. **极端阈值：** 只呈交严重/异常健康判断、穴位/艾灸/疗程等治疗式操作、明确金融产品/仓位/买卖时机、法律结果、生育死亡、重大人生指令、恐吓或诱导付费；不以防止任何理论上的误解或诉讼为目标。
7. **文化保留：** 原签诗、传统意象和必要文化背景默认保留；重点识别后期模型擅自扩写的现代医学、投资、法律和确定性人生建议。
8. **回归门禁：** 只有项目所有者明确确认为“任何情况下均不得出现”的硬红线，才可在审查完成后转化为定向回归测试；普通候选词和上下文判断不得形成一刀切 CI 门禁。

## 3. 当前主台账

| ID | 工作项 | 优先级 | 状态 | 依赖/决策 | 产出与验收证据 |
| --- | --- | --- | --- | --- | --- |
| GOV-001 | 建立剩余工作唯一主台账 | P0 | 已完成 | 无 | 本文档、README/旧计划引用、文档契约测试 |
| GOV-002 | 为后续每批实施建立统一验收记录 | P0 | 已完成 | GOV-001 | `docs/reviews/2026-07-15-safe-001-002-acceptance.md`，含范围、验证、限制和回滚记录 |
| GOV-003 | 为已部署源码、镜像与导出工件建立 Git 发布追溯 | P1 | 就绪（非阻塞） | SEO-001/002/003 已完成 | 对应源码提交、镜像标签 `2026.07.16-seo` 与 tar SHA-256 的映射记录；不改变当前生产运行结果 |
| UI-001 | 修正中文定场诗的古典右起列序 | P0 | 已完成 | 无 | 算事、论命、黄历的诗句保持单列自上而下、列序从右向左；桌面/390px 浏览器坐标、契约测试和全量回归通过；见 `docs/reviews/2026-07-16-chinese-poetry-direction-acceptance.md` |
| SAFE-001 | 确定英文产品内容边界与业主裁决规则 | P0 | 已完成 | 无 | 第 2.4 节、`docs/reviews/english-content-boundary-policy.md`、候选格式和项目所有者确认记录 |
| SAFE-002 | 全量检查英文内容并生成极端判词审查册 | P0 | 已完成 | SAFE-001 | 384/384 签、3,072 字段实例均已检查；只确认 69 签的 74 个极端问题字段和 2 个非签文问题；每项有具体问题句，受审内容零修改 |
| SAFE-003 | 由项目所有者裁决已确认签文极端问题并实施获批修改 | P0 | 已完成 | SAFE-002、项目所有者审查 | 74/74 字段已写回 `oracle_signs_en.json`；69 签；批复映射、全量测试和 `docs/reviews/2026-07-15-safe-003-004-acceptance.md` |
| SAFE-004 | 由项目所有者裁决已确认非签文极端问题并实施获批修改 | P0 | 已完成 | SAFE-001/002、项目所有者审查 | 黄历医疗分类已删除；法律事项提示进入 API 和结果页；定向测试与桌面/移动验收通过 |
| TRUST-001 | 确定并配置真实联系与隐私邮箱 | P0 | 已完成 | DEC-002 已决定：`5siwei@gmail.com` | 全站公开模板无 `.example`；四个信任页、正式域名、Cloudflare 邮箱保护和实际收信均已验收；测试邮件进入垃圾箱作为非阻塞运营提醒 |
| SEO-001 | 建立统一站点 URL/canonical/hreflang 配置 | P1 | 已完成 | 公开语言契约 | `SITE_BASE_URL` 单一可信源；Host 注入、四组 hreflang、HTTPS 与 `www` path/query 301 均通过本地和生产验收 |
| SEO-002 | 实现 `sitemap.xml` 和 `robots.txt` | P1 | 已完成 | SEO-001 | 生产 sitemap 200 + XML；9 个静态基线 URL 加已发布文章动态 URL，2026-07-17 实测 11 URL；robots 200 + text、唯一正式 sitemap；未知文章 404 |
| SEO-003 | 完善页面 title、description、Open Graph 和结构化数据 | P1 | 已完成 | SEO-001 | 生产核心页唯一元数据与 Open Graph 正确；Schema.org Validator 0 错误/0 警告；1440/390 验收通过 |
| ART-001 | 确定英文文章存储与发布架构 | P1 | 已完成 | DEC-001 已纠正：服务器私密 URL 上传并即时发布 | `/165131` 跨设备入口、可选简单密码、独立文章持久卷、原子上传/覆盖和全部 Markdown ZIP 下载；GitHub 不参与日常文章发布；2026-07-17 已确认生产入口与文章卷版本上线 |
| ART-002 | 实现文章加载、列表、详情与服务器上传 | P1 | 已完成 | ART-001 | 上传后无需重启或部署即可跨 worker 刷新列表、详情、canonical/OG/JSON-LD/sitemap；生产已有首篇文章且 sitemap 动态增至 11 URL；剩余生产写入/覆盖/ZIP/真实备份证据见验收文档第 5 节 |
| ART-003 | 发布第一批 10 篇基础文化解释文章 | P1 | 就绪 | ART-002、SAFE-001 均已完成 | 正式站当前有 1 篇文章，但尚无 10/10 基础文化文章人工审校完成证据；每篇仍需内链、来源和负责使用说明 |
| ART-004 | 发布 10 篇搜索意图文章 | P2 | 阻塞 | ART-003、Search Console 基线 | 10/10 审校，无重复/薄内容，有搜索意图记录 |
| ART-005 | 发布 5 篇工具使用/转化辅助文章 | P2 | 阻塞 | ART-003、商业化边界 | 5/5 审校，不暗示付费提高准确性 |
| OPS-001 | 完成生产环境配置和域名/HTTPS 验收 | P1 | 已完成 | TRUST-001、SEO-001 | `docs/operations/production-acceptance.md`；域名、HTTPS、脱敏环境变量、静态资源、安全头、AI 降级、health/readiness 均通过 |
| OPS-002 | 建立备份、恢复和回滚演练 | P1 | 已完成 | OPS-001 | `docs/operations/backup-restore-runbook.md`；隔离卷完成 `runtime.db` 备份/恢复和不同 image ID 镜像回滚，生产卷未挂载；见 `docs/operations/ops-002-acceptance.md` |
| OPS-003 | 建立错误、存活性与资源监控 | P1 | 待验收 | DEC-003 已决定、OPS-001 | UptimeRobot `readyz`/5 分钟/邮件口径和运行手册已固化；待项目所有者创建账号并验证 Down/恢复邮件；第三方错误平台默认关闭 |
| OPS-004 | 提交 Search Console 并验证收录 | P1 | 已完成 | SEO-002、OPS-001 均已完成 | DNS 所有权验证成功；sitemap 成功读取并发现 9 个网页；首页已编入索引且 HTTPS 正常；见 `docs/operations/search-console-acceptance.md` |
| OPS-005 | 执行上线后统一全量验收 | P1 | 阻塞 | SAFE/SEO/TRUST/OPS 的 P0-P1 项 | CI 修复提交 `44f6925` 的 GitHub Actions run 20 已通过；待 OPS-003 外部监控验收后，汇总 CI、Docker 健康、桌面/移动、断网和回滚证据 |
| OPS-006 | 处理 Cloudflare Browser Insights 与 CSP 冲突 | P2 | 待验收（非阻塞） | 已决定使用 Cloudflare Web Analytics | `script-src` 仅增加 `https://static.cloudflareinsights.com`，无脚本 inline/eval；待部署、Cloudflare 启用、浏览器无 CSP 错误且出现 Analytics 数据 |
| COM-001 | 实时核验支付、赞助和广告平台政策 | P2 | 就绪 | 上线地区/主体信息 | 官方来源、核验日期、提现/类目/webhook/费用对比 |
| COM-002 | 确定是否解冻赞助/广告/Deep Reading | P2 | 待决策 | COM-001、DEC-004/005 | 明确“上线/不上线”及触发条件 |
| COM-003 | 实现默认关闭的商业化配置开关 | P3 | 阻塞 | COM-002 | 关闭时零 UI/零外部请求，配置和测试完整 |
| COM-004 | 实现赞助组件或广告占位 | P3 | 阻塞 | COM-002/003 | 开关控制、布局安全、无误导点击或运势暗示 |
| COM-005 | 实现模拟付费墙、订单模型与 webhook 边界 | P3 | 阻塞 | COM-002/003、DEC-005 | 无平台时不持久化真订单；未签名 webhook 不可用 |
| MET-001 | 建立隐私友好的使用/成本指标 | P2 | 就绪 | OPS-001 | 只记聚合数据，不记姓名、出生时间或原始问题 |
| MET-002 | 连续四周运营复盘 | P3 | 阻塞 | MET-001、OPS-004 | 4/4 周记录，形成内容、成本和商业化去留决策 |

## 4. 推荐执行顺序

1. **批次 A（已完成）：** GOV-002 → SAFE-001；确认人机分工、审查口径和审查册格式。
2. **批次 B（已完成）：** SAFE-002 完成全量覆盖和语义初筛；项目所有者完成 SAFE-003/004 最终裁决，批准修改已进入正文和运行路径。
3. **批次 C（已完成）：** SEO-001 → SEO-002 → SEO-003；代码、测试、Docker、正式域名、Schema.org Validator 和桌面/移动验收均已完成，证据见 `docs/reviews/2026-07-16-seo-001-003-acceptance.md`。
4. **批次 D（业主输入已完成）：** DEC-001 已解锁 ART-001；DEC-002 已解锁 TRUST-001。
5. **批次 E（进行中）：** OPS-001/002/004、ART-001/002 已完成并已上线，CI 红灯已关闭；并行推进 ART-003 与 OPS-003/006 外部验收，最后汇总 OPS-005。
6. **批次 F（上线后增长）：** ART-004/005、MET-001/002。
7. **批次 G（最后考虑商业化）：** COM-001 → COM-002 → COM-003/004/005。

## 5. 详细任务卡

### Task SAFE: 英文产品内容边界与业主审查闭环

**Files:**
- Create: `docs/reviews/english-content-boundary-policy.md`
- Create: `docs/reviews/english-content-owner-review/index.md`
- Create during inventory: `docs/reviews/english-content-owner-review/*.md`
- Create after owner decisions: `data/content/_review_log/english_content_owner_decisions.json`
- Modify only after owner approval: `data/content/oracle_signs_en.json`
- Modify only after owner approval: `data/content/huangli_terms_en.json`, `prompts/*`, `frontend/templates/en/*.html`
- Conditional test after owner approval: targeted regression tests for explicitly confirmed hard red lines only

**Steps:**
1. 将第 2.4 节的业主确认口径写入独立审查说明，明确 SAFE 的目标是“允许正常谈运势，但不在高风险领域表现得像医生、理财顾问、律师或掌握确定未来的人”。
2. 定义审查册单项格式：内容位置、签号/页面、字段、完整英文原文、对应中文或文化上下文、候选风险类别、提出理由、非约束性处理选项、业主决定、业主修改要求和复核状态。
3. 对 384 签所有公开英文字段以及英文黄历、文章、四柱 prompt/输出场景做高召回候选收集；自动化或临时分析只能帮助定位，执行者必须结合完整语境完成初筛判断。
4. 建立独立覆盖清单，证明 384/384 签及约定字段均已检查；覆盖项不得自动转化为项目所有者待办。
5. 审查册只列出执行者明确判断达到“极端判词/明确专业操作”阈值的问题；每项必须逐句引用具体问题位置、解释极端点并给出修改建议。此时不得修改内容源，也不得创建关键词式 CI 测试。
6. 项目所有者只对问题项填写“按建议修改 / 保留并接受风险 / 删除 / 另行指定”；选择修改时，可直接给出文本或授权执行者提出改写稿后再复核。
7. 执行者仅实施已有明确业主决定的修改；未决定项保持原文并继续标记为待审，不得推断默许。
8. 生成修改前后 diff 和决定映射，由项目所有者进行第二次复核；只有复核通过的内容才能标记完成。
9. 若项目所有者明确指定硬红线，再为这些确定规则建立最小定向回归测试；全量 pytest 等工程测试只验证数据结构和程序未回归，不代替内容判断。
10. 提交建议：审查规则与候选册使用 `docs: add owner-led English content review`；经业主批准的内容修改另作 `content: apply owner-approved English revisions`。

### Task SEO: 技术 SEO 基础

**Files:**
- Create: `zhugeshensuan/blueprints/seo.py`
- Create: `frontend/templates/sitemap.xml`
- Create: `frontend/templates/robots.txt`
- Create: `tests/test_sitemap.py`
- Create: `tests/test_robots.py`
- Create: `tests/test_seo_metadata.py`
- Modify: `zhugeshensuan/config.py`, `zhugeshensuan/app.py`, `zhugeshensuan/blueprints/__init__.py`
- Modify: `frontend/templates/en/base.html`, Chinese templates as needed, `.env.example`

**Steps:**
1. 先写测试锁定 `SITE_BASE_URL`、canonical、hreflang、sitemap MIME type 与 robots 规则。
2. 验证测试 FAIL，且失败原因为端点/配置尚未存在。
3. 实现基础 URL 配置；生产环境禁止用任意请求 Host 生成 canonical。
4. sitemap 纳入英文和繁体公开页；不收录 `/zh-hans/*`、API、旧跳转路由和未发布文章。
5. robots 指向 sitemap，并禁止 API/调试/管理端点；不依赖 robots 保护敏感数据。
6. 运行 `python -m pytest tests/test_sitemap.py tests/test_robots.py tests/test_seo_metadata.py -q`。
7. 运行全套质量门禁并更新 API/部署文档。
8. 提交建议：`feat: add production SEO foundations`。

### Task ART: 跨设备即时发布的英文文章系统

**Files:**
- Create: `zhugeshensuan/content.py`
- Create: `zhugeshensuan/blueprints/article_admin.py`
- Create: `tests/test_articles.py`
- Create: `tests/test_article_admin.py`
- Modify: `zhugeshensuan/blueprints/pages_en.py`
- Modify: `frontend/templates/en/articles.html`, `frontend/templates/en/article_detail.html`, `deploy/compose.prod.yml`

**Steps:**
1. DEC-001 已纠正为“服务器私密 URL 上传并即时发布”：默认入口 `/165131`，手机和任意电脑均可使用；GitHub、CI、镜像构建和重新部署不参与日常文章发布。
2. 定义 schema：`slug/title/description/published_at/updated_at/status/tags/body/source_notes`。
3. 先写密码/CSRF、未经授权直调、上传校验、覆盖确认、原子写入、跨 worker 刷新、ZIP 导出、列表/详情和 HTML 安全测试。
4. Markdown 写入独立 Docker volume；上传成功后当前 worker 重载，其他 worker 在下一请求通过目录指纹刷新。
5. 管理页不出现在导航、robots 或 sitemap，统一 `noindex/no-store/no-referrer`；密码由服务器核对，不做可绕过的纯前端判断。
6. 运行 `python -m pytest tests/test_article_admin.py tests/test_articles.py tests/test_english_frontend_contract.py -q`。
7. 内容按 10 + 10 + 5 三批由站长上传，每批附人工审校记录；文章本身不进入 GitHub 发布流水线。

### Task TRUST/OPS: 信任页与生产上线

**Files:**
- Modify: `frontend/templates/en/contact.html`, legal templates, `.env.example`, `docs/部署指南.md`
- Create: `docs/operations/production-acceptance.md`
- Create: `docs/operations/backup-restore-runbook.md`
- Create: `docs/operations/monitoring-runbook.md`
- Test: `tests/test_english_frontend_contract.py`, `tests/test_config.py`

**Steps:**
1. 由项目所有者提供实际可收信邮箱，决定是否分开 contact/privacy。
2. 先写测试，禁止生产模板出现 `.example` 和未配置联系方式。
3. 替换联系信息，同步 Privacy/Terms/Disclaimer 中的联系与数据处理说明。
4. 在真实生产域名上验收 HTTPS、canonical、healthz、readyz、静态资源和 AI 超时降级。
5. 备份并恢复 `runtime.db`/数据卷，用旧镜像做一次回滚演练；记录时间和结果。
6. 选定监控/告警通道，仅上报错误、延迟和资源指标，排除出生数据和原始用户输入。
7. 执行 CI 同款全量门禁、1440px/390px 浏览器验收、断网/API 失败和回滚验收。

### Task COM/MET: 商业化预验证与四周复盘

**Files:**
- Create: `docs/business/payment-platform-verification.md`
- Create: `docs/business/unit-economics-model.md`
- Create: `docs/business/adsense-readiness-checklist.md`
- Create: `docs/business/weekly-growth-review-template.md`
- Conditional create/modify: commerce modules, partials, tests and `.env.example`

**Steps:**
1. 执行时联网核验 Lemon Squeezy、Paddle、Gumroad、Ko-fi、Buy Me a Coffee 和 AdSense 当期官方政策；不用旧记忆代替实时核验。
2. 记录主体/国家支持、限制类目、提现、费用、税务、退款和 webhook 验签要求。
3. 建立 USD 2.99/4.99 两种价格下的 AI、服务器、平台、税务与 5%-10% 退款模型。
4. 项目所有者作出 COM-002 决策；若不解冻，COM-003/004/005 全部取消或继续阻塞。
5. 若解冻，先写“默认关闭、无外部请求、未签名 webhook 拒绝”测试，再实现最小代码。
6. 上线后只记录聚合使用次数、成本和转化；不保存出生资料、原问题或可识别个人文本。
7. 连续 4 周记录后再决定文章扩张、广告、赞助和真实付费的去留。

## 6. 待决策台账

| ID | 决策 | 可选项 | 建议 | 影响任务 | 状态 |
| --- | --- | --- | --- | --- | --- |
| DEC-001 | 英文文章存储与发布方式 | 服务器私密上传 / Git-backed 编辑 / 数据库后台 / Headless CMS | 已决定：默认 `/165131` + 可选简单密码；任意设备上传 Markdown 到独立持久卷并立即生效；可打包下载全部文章；GitHub 仅管理程序代码 | ART-001/002、部署与备份 | 已决定（纠正后） |
| DEC-002 | 对外联系方式 | 单邮箱 / contact+privacy 分开 | 已决定：Contact 与 Privacy 统一使用 `5siwei@gmail.com` | TRUST-001、OPS-005 | 已决定 |
| DEC-003 | 生产监控与告警通道 | 自建/托管；邮件/即时通知 | 已决定：首批使用 UptimeRobot 免费 HTTP monitor 检查公网 `readyz`，5 分钟，邮件到 `5siwei@gmail.com`；第三方错误平台保持关闭 | OPS-003/005 | 已决定（待外部验收） |
| DEC-004 | 商业化解冻门槛 | 按时间 / 流量 / 使用量 / 全部满足 | 同时满足政策可行、站点稳定、有 4 周真实数据 | COM-002 | 待决策 |
| DEC-005 | Deep Reading 价格与是否上线 | 不上线 / USD 2.99 / USD 4.99 | 先不定价；等 COM-001 与单位经济模型完成 | COM-002/005 | 待决策 |

## 7. 全局验收门禁

每个实施批次至少执行：

```powershell
python -m pytest -W error::ResourceWarning
python -m black --check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
python -m ruff check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
python -m pip_audit -r requirements.txt --no-deps --progress-spinner off
git diff --check
python -c "import pathlib, subprocess; files=sorted(pathlib.Path('frontend/static/js').rglob('*.js')); assert files; [subprocess.run(['node', '--check', str(path)], check=True) for path in files]; print(f'node --check: {len(files)}/{len(files)} passed')"
```

数据或部署变更还必须执行 reference DB logical dump 比较、Docker 生产镜像构建、`/healthz` 与 `/readyz` 健康检查。前端改动还必须保留 1440px/390px 人工验收证据。

## 8. 进度日志

| 日期 | 任务 ID | 执行者 | 状态变更 | 实际改动 | 验收证据 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-15 | GOV-002 | Codex | 就绪 → 已完成 | 建立 SAFE-001/002 批次验收记录 | 范围、覆盖、验证、限制和回滚说明 | 后续批次沿用同一证据结构 |
| 2026-07-15 | SAFE-001 | Codex + 项目所有者 | 就绪 → 已完成 | 固化“行业中间偏稳健”边界、业主裁决权和审查册格式 | `english-content-boundary-policy.md` | 项目所有者按审查册裁决 |
| 2026-07-15 | SAFE-002 | Codex | 纠偏后已完成 → 极端阈值版已完成 | 废止仍然过宽的 674 项版本并删除 16 个旧分册；排除奖金、分红、行业意象、普通养生等正常内容，只保留 69 签的 74 个极端问题和 2 个非签文问题 | 3 个极端签文清单；每项含具体问题句、极端点、完整原文与建议 | SAFE-003/004 由项目所有者只裁决极端问题 |
| 2026-07-15 | SAFE-003/004 | 项目所有者 | 就绪（再次缩减） | 业主待办从 680 个宽泛问题缩减为 76 个极端问题；内容源保持未修改 | 74 签文问题 + 2 非签文问题，决定栏全部待填 | 从极端判词总索引进入 |
| 2026-07-15 | SAFE-003/004 | 项目所有者 + Codex | 就绪 → 已完成 | 74 个批准签文字段写回正文；删除黄历医疗分类；法律提示进入 API 和结果页；修正 5 处残留和 1 处语病 | 74/74 映射、全量测试、依赖审计、DB 重建、1440/390 页面验收；Docker 因本机服务未运行留待 OPS-005 补验 | 进入 SEO-001/002/003 |
| 2026-07-15 | GOV-001 | Codex | 就绪 → 已完成 | 建立主台账、决策台账、变更和取消规则 | 文档契约测试与 Git 提交 | 从 SAFE-001 开始 |
| 2026-07-16 | DEC-001/002 | 项目所有者 | 待决策 → 已决定 | 英文文章采用仓库 Markdown + 受控元数据；Contact/Privacy 统一使用 `5siwei@gmail.com`；正式域名确认为 `https://getwiseoracle.com` | 项目所有者在当前任务中明确确认 | SEO 按详细实施方案执行；TRUST-001 与 ART-001 均已解锁 |
| 2026-07-16 | SEO-001/002/003 | 项目所有者 + Codex | 就绪 → 已完成 | 建立固定公开 URL、集中页面注册表、canonical/hreflang、9 URL sitemap、robots、Open Graph、保守 JSON-LD、未知文章 404；项目所有者完成生产部署 | SEO 定向 85 passed；全量 381 passed；Black/Ruff/pip-audit/14 JS/diff 与 Docker 通过；生产 HTTPS/重定向/health/ready/sitemap/robots/源码、1440/390 和 Schema.org Validator 全通过 | 进入 TRUST-001、ART-001/002 与 OPS-001；另补 Git 发布追溯和 Cloudflare Analytics/CSP 决策 |
| 2026-07-16 | GOV-003 | 项目所有者 + Codex | 新增 → 就绪（非阻塞） | 登记已部署源码、镜像标签和导出 tar 的发布追溯收尾 | SEO 验收记录已保存镜像标签 `2026.07.16-seo` 与 tar SHA-256；待补对应 Git 提交映射 | 不阻塞 TRUST-001 和文章主线，工程收尾时完成 |
| 2026-07-16 | OPS-006 | 项目所有者 + Codex | 新增 → 待决策（非阻塞） | 登记 Cloudflare Browser Insights beacon 被现有 CSP 拦截的问题及两种安全处置 | 已确认不影响页面、SEO 或 JSON-LD；只影响 Cloudflare Web Analytics 采集 | OPS-003 选型时决定关闭 Browser Insights 或放行单一静态脚本域名 |
| 2026-07-16 | TRUST-001 | Codex | 就绪 → 待验收 | 新增 `CONTACT_EMAIL` 生产配置与校验；Contact/Privacy/Terms/Disclaimer 统一显示 `5siwei@gmail.com`；同步 Compose、环境模板和部署指南；构建并导出 TRUST 镜像 | 定向 66/66、全量 388/388、Black/Ruff/14 JS/pip-audit/diff 通过；只读生产容器四页、healthz、readyz 均 200；见 `docs/reviews/2026-07-16-trust-001-acceptance.md` | 项目所有者部署新工件，确认正式页面和实际收信后标记完成 |
| 2026-07-16 | TRUST-001 | 项目所有者 + Codex | 待验收 → 待验收 | 项目所有者完成新镜像部署；正式域名四个信任页、healthz、readyz 验收通过；确认 Cloudflare Email Address Obfuscation 正确保护并还原公开邮箱 | 四页均 200、无 `.example`；四组 `data-cfemail` 均解码为 `5siwei@gmail.com`；同源解码脚本与现有 CSP 兼容 | 项目所有者确认测试邮件实际收到后标记完成 |
| 2026-07-16 | TRUST-001 | 项目所有者 + Codex | 待验收 → 已完成 | 项目所有者确认 `5siwei@gmail.com` 实际收到测试邮件；测试邮件进入 Gmail 垃圾箱，记录为非阻塞运营提醒 | 代码、全量门禁、生产镜像、正式页面与实际收信五项证据完整 | 进入 OPS-001；运营初期定期检查垃圾箱，重复误判时再评估邮箱方案 |
| 2026-07-16 | OPS-001 | Codex | 就绪 → 已完成 | 汇总并复测正式域名/HTTPS、脱敏生产配置、静态资源、安全响应头、health/readiness；补充 AI 上游超时同步与流式降级测试 | `docs/operations/production-acceptance.md`；定向 100/100、全量 391/391、Black/Ruff/14 JS/pip-audit/Compose/diff 通过；正式站所有检查通过 | OPS-004 解除阻塞；下一步进行 Search Console 所有权验证和 sitemap 提交 |
| 2026-07-16 | OPS-004 | 项目所有者 + Codex | 就绪 → 已完成 | 项目所有者完成网域 DNS 所有权验证，提交正式 sitemap，并检查首页收录状态；Codex 固化验收记录 | Search Console 显示 sitemap 状态成功、2026-07-16 已读取、发现 9 个网页；首页“网址在 Google 服务中”、已编入索引、HTTPS 正常；见 `docs/operations/search-console-acceptance.md` | 内容主线进入 ART-001；OPS-002 可并行执行 |
| 2026-07-16 | OPS-002 | Codex | 就绪 → 已完成 | 新增生产 backup/restore/image rollback runbook；用两个隔离临时卷完成 SQLite 快照恢复，并将恢复卷从当前镜像切换到不同 image ID 的旧镜像 | 备份 SHA-256 与 `quick_check=ok`；恢复卷仅保留备份前标记；当前/旧镜像 `readyz` 均成功；生产卷身份未变且未挂载；见 `docs/operations/ops-002-acceptance.md` | 首次真实生产备份由服务器操作者按 runbook 执行并追加脱敏记录；不阻塞 ART 主线 |
| 2026-07-16 | DEC-001 | 项目所有者 + Codex | 已决定 → 已决定（细化） | 项目所有者确认采用私有编辑界面 + GitHub 自动发布；Markdown/Git 为文章权威源，生产应用不直接写文章数据 | `docs/architecture/article-publishing-architecture-2026-07-16.md`；包含发布门禁、凭据边界、失败保留旧版本和手动回退路径 | ART-001 按新架构固化 schema；站长分析/监控由 OPS-003/006、MET-001 独立设计 |
| 2026-07-16 | ART-001/002 | Codex | 就绪/阻塞 → 已完成 | 实现公开 published Markdown + 本机私有草稿、loopback 编辑器、生产同源安全预览、单篇 Git 发布器、只读 ArticleRepository、列表/详情/动态 SEO/sitemap | 452 passed；Black 94、Ruff、pip-audit、14 JS、diff 通过；Docker 空/有文章双路径通过；见 `docs/reviews/2026-07-16-art-001-002-site-management-acceptance.md` | ART-003 就绪；先建立干净 Git 基线，再用编辑器发布首批文章 |
| 2026-07-16 | DEC-003/OPS-003 | 项目所有者 + Codex | 待决策 → 已决定/待验收 | 选择 UptimeRobot 免费 HTTP monitor 检查公网 `readyz`，5 分钟，告警邮箱 `5siwei@gmail.com`；第三方错误平台默认关闭；固化站长与监控手册 | `docs/operations/site-owner-management.md`、`docs/operations/monitoring-runbook.md`；待账号、正式 Up、Down 和恢复邮件证据 | 项目所有者注册并完成邮件验收后关闭 OPS-003 |
| 2026-07-16 | OPS-006 | 项目所有者 + Codex | 待决策 → 待验收（非阻塞） | 决定使用 Cloudflare Web Analytics；CSP 仅放行 `https://static.cloudflareinsights.com`，保持 `connect-src 'self'` | 本地 73 项 CSP/SEO 测试与 Docker 响应头通过；正式站仍为旧 CSP、无 beacon、GET `/cdn-cgi/rum` 404 | 部署新镜像，在 Cloudflare 启用后检查浏览器控制台、同源 RUM POST 和 Analytics 数据 |
| 2026-07-16 | 自动发布骨架 | Codex | 新增 → 待生产验收 | 增加 CI 成功后 GHCR SHA 镜像构建、production environment、SSH known_hosts、服务器原子切换和自动回滚 | 15 项工作流测试、Compose/shell、成功/失败模拟通过；四个 Action SHA 经 GitHub API 核实存在 | 项目所有者配置 environment、四 secrets 和 GHCR 拉取方式，完成一次真实发布/回滚 |
| 2026-07-16 | DEC-001/ART-001/002 | 项目所有者 + Codex | 已完成（错误实现） → 已纠正并重新完成 | 项目所有者指出本机编辑器限制设备、GitHub/CI/重部署链路过重；删除本机编辑器、Git 发布器、文章 publish workflow 和 promote 脚本，改为 `/165131` 跨设备上传、服务器密码、独立持久卷、即时刷新及全部文章 ZIP 下载 | `tests/test_article_admin.py`、Docker 文章卷和跨 worker 验收；新架构文档明确取代旧方案 | 首次部署新镜像和 Compose 后，从手机/其他电脑实测上传与 ZIP 下载，再进入 ART-003 |
| 2026-07-16 | ART-001/002 | Codex | 纠正实施 → 本地已完成/待生产验收 | 完成服务器密码、CSRF、原子上传、跨 worker 热刷新、覆盖确认、ZIP 导出和独立文章卷；同步部署、备份与站长文档 | 447 passed；Black 89、Ruff、pip-audit、14 JS、Compose/diff 通过；只读非 root Docker 完成上传、覆盖、ZIP 和重建容器持久化验收 | 项目所有者部署后从手机/其他电脑完成生产验收 |
| 2026-07-16 | 自动发布骨架 | 项目所有者 + Codex | 待生产验收 → 已取消 | 删除 `.github/workflows/publish.yml`、`deploy/promote_image.sh` 及相关测试和文档 | 日常文章不应依赖 GitHub 网络、CI、镜像重建或整站部署；程序代码继续使用既有 CI 与手工部署 | 无替代自动部署任务；文章由服务器私密页面即时发布 |
| 2026-07-16 | UI-001 | 项目所有者 + Codex | 新增 → 已完成 | 项目所有者发现算事、论命、黄历定场诗列序反向；桌面和手机共用样式改为 `row-reverse`，保留每列 `vertical-rl`，并校正黄历动画顺序 | 定向契约 1/1、前端契约 15/15、全量 448/448、Black 89、Ruff、diff 通过；真实 Chrome 在 1280px/390px 下三页均确认第一句位于第二句右侧 | 将修复纳入本批部署镜像；生产部署后做一次页面刷新验收 |
| 2026-07-17 | ART-001/002、UI-001 | Codex | 生产状态复核 | 正式站已运行文章管理版本；`/165131`、文章列表、首篇文章、动态 sitemap 和桌面/移动 `row-reverse` 静态资源均存在 | `/readyz` ready；管理页 200 且 noindex/no-store；sitemap 11 URL；文章详情 200 | 补写入/覆盖/ZIP/真实文章备份和中文页面最终视觉记录 |
| 2026-07-17 | OPS-005 | Codex | 阻塞原因明确 → CI 阻塞已关闭 | GitHub CI run 19 仅在生产 Docker 冒烟失败；工作流漏传生产必填 `CONTACT_EMAIL`，且未显式覆盖独立 article-content 路径；已补齐邮箱、管理路径、文章路径和独立内容卷，并增加工作流契约测试 | pytest 450/450、Black、Ruff、14/14 JavaScript、pip-audit、diff 和独立双卷 Docker `healthz/readyz` 冒烟通过；提交 `44f6925` 对应 GitHub Actions run 20 成功 | 等待 OPS-003 外部验收，随后汇总 OPS-005 |

## 9. 已取消任务（墓碑）

| ID | 原工作项 | 取消日期 | 取消原因 | 替代项/决策 |
| --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — |

## 10. 计划变更记录

| 版本 | 日期 | 修订人 | 类型 | 变更内容 | 原因 |
| --- | --- | --- | --- | --- | --- |
| 1.17 | 2026-07-17 | Codex | CI 远端验收收尾 | 记录修复提交 `44f6925` 已推送且 GitHub Actions run 20 成功；OPS-005 的 CI 阻塞关闭，仅保留外部监控和统一验收收尾 | 1.16 写入时远端 CI 尚未运行完成，必须用真实远端结果替换“待验收”状态 |
| 1.16 | 2026-07-17 | Codex | 生产状态与 CI 契约同步 | 将文章系统从“待部署”更新为已上线，记录首篇文章和 11 URL sitemap；将 OPS-005 改为上线后统一验收；登记并修复 CI Docker 冒烟遗漏生产必填邮箱和文章卷路径的问题 | 代码、生产状态和当前文档已超出 1.15 基线，且 `8c60f4e` 的远端 CI 实际为红灯，必须恢复真实可追溯状态 |
| 1.15 | 2026-07-16 | 项目所有者 + Codex | 中文文化呈现纠正 | 新增并完成 UI-001；中文算事、论命、黄历定场诗改为右起竖排，同时增加桌面/移动契约和真实浏览器验收 | 旧样式明确使用 `flex-direction: row`，使第一句落在最左侧，不符合中国古典竖排的阅读顺序 |
| 1.14 | 2026-07-16 | 项目所有者 + Codex | 重大纠偏 | 废止 1.12/1.13 中“本机编辑器 + GitHub 自动发布文章”；DEC-001 改为 `/165131` 服务器私密上传、简单密码、独立持久卷、上传即时刷新和全部文章 ZIP 下载；删除错误实现与文档 | 原方案不能从手机或其他电脑使用，而且把每篇文章绑定到 GitHub、CI、镜像构建和部署，故障面与运营成本不符合项目所有者需求 |
| 1.13 | 2026-07-16 | 项目所有者 + Codex | 文章系统与站长能力实施 | ART-001/002 标记已完成，ART-003 解锁；DEC-003 决定 UptimeRobot 首批方案，OPS-003/006 转待外部验收；增加本机私有编辑、受控 Git 发布、GHCR/production 部署回滚和站长手册证据 | 项目所有者已确认继续实施；本地代码、全量门禁和 Docker 验收齐全，但账号、secrets、Cloudflare 数据与真实自动部署不得提前视为完成 |
| 1.12 | 2026-07-16 | 项目所有者 + Codex | 文章发布架构细化 | DEC-001 从“仓库 Markdown”细化为“私有编辑界面 + GitHub 自动发布”，增加生产只读、发布门禁、凭据隔离、健康检查和失败回退约束 | 项目所有者不应直接编辑 Markdown 或手动部署每篇文章，同时需保留 Git 审校、版本回滚和较小生产攻击面 |
| 1.11 | 2026-07-16 | Codex | 运维演练完成 | OPS-002 从就绪改为已完成；新增生产 runbook、安全演练脚本、隔离恢复和不同 image ID 镜像回滚证据 | 在不连接生产服务器、不挂载或删除生产卷的前提下，已验证备份快照语义、SQLite 完整性和镜像回滚可用性 |
| 1.10 | 2026-07-16 | 项目所有者 + Codex | Search Console 验收 | OPS-004 从就绪改为已完成；记录 DNS 所有权验证、sitemap 成功读取 9 个网页和首页已编入索引 | 所有权、提交、抓取和首页索引证据均已由正式 Search Console 页面确认 |
| 1.9 | 2026-07-16 | 项目所有者 + Codex | 非阻塞收尾登记 | 新增 GOV-003 和 OPS-006，分别追踪已部署版本的 Git/镜像映射，以及 Cloudflare Browser Insights 与 CSP 冲突；明确二者不阻塞下一主线 | 将 SEO 验收记录中的遗留说明转为有稳定 ID、状态、验收证据和后续动作的正式任务 |
| 1.8 | 2026-07-16 | 项目所有者 + Codex | 技术 SEO 生产验收 | SEO-001/002/003 从待验收改为已完成；补入正式域名、重定向、Schema.org 和浏览器证据 | 项目所有者完成镜像部署，生产端点与页面源码已实测符合完成定义 |
| 1.7 | 2026-07-16 | Codex | 技术 SEO 实施 | SEO-001/002/003 完成本地施工与门禁，新增验收记录并标记待生产验收 | 代码与本地证据齐全，但当前生产 sitemap/robots 仍为 404，按完成定义不能提前标记已完成 |
| 1.6 | 2026-07-16 | Codex | 外部评审复核 | 核实 `.env.example` 与 Gunicorn 文件实际存在；吸收全量 JS/CI 检查、测试隔离、文章 404 契约、metadata 盘点、CSP 实测、locale 映射、蓝图注册和路径注入测试建议；补充 Compose 显式传递 `SITE_BASE_URL` | 区分基于错误仓库快照的误报与真实实施风险，并补上评审未发现的容器环境变量传递风险，使 SEO 施工图可直接执行且便于第三方复审 |
| 1.5 | 2026-07-16 | 项目所有者 + Codex | 决策与细化 | 固化正式域名、联系邮箱和 Markdown 文章方案；新增可供第三方评审的 SEO-001/002/003 详细实施方案 | 项目所有者要求不必参与技术细节，但所有施工、测试、验收和回滚细节必须文档化、可交由专业人士评估 |
| 1.4 | 2026-07-15 | 项目所有者 + Codex | 完成 | SAFE-003/004 的 74 个签文字段和 2 个非签文决定全部实施并验收 | 项目所有者完成批复并明确批准直接写回正文，本阶段至此完成 |
| 1.3 | 2026-07-15 | 项目所有者 + Codex | 纠偏 | SAFE-002 改为高阈值极端判词审查；废止 674 项版本，只保留 74 个签文极端问题和 2 个非签文问题 | 旧版仍把普通财富、行业、养生和个别词汇泛化为风险，不符合普通用户的合理理解，也无法供项目所有者有效审查 |
| 1.2 | 2026-07-15 | 项目所有者 + Codex | 纠偏 | SAFE-002 明确由执行者承担全量检查和语义初筛；覆盖项不再转成业主待办；每个 `health`/`wealth` 问题必须逐句指出具体越界位置 | 首版把高召回候选和全部敏感字段摊给项目所有者，错误转移了筛选责任且缺少逐句问题依据 |
| 1.1 | 2026-07-15 | 项目所有者 + Codex | 修改 | SAFE-001 明确采用“行业中间偏稳健”边界；SAFE-002 从自动扫描/CI 裁决改为全量候选呈交；SAFE-003/004 改为项目所有者逐项裁决、执行者仅实施获批修改 | 内容风险由项目所有者承担并作最终决定；自动化应保证覆盖率而非代替语境判断，避免生硬关键词门禁误伤正常占卜内容 |
| 1.0 | 2026-07-15 | Codex | 新增 | 建立 GOV/SAFE/SEO/ART/TRUST/OPS/COM/MET/DEC 统一台账 | 原有三份计划同时记录待办，存在重复、过时和不可追溯风险 |

## 11. 下一个可执行批次

**ART-001/002 已按纠正后的服务器上传架构完成并上线，CI 红灯也已关闭。下一步由项目所有者补齐手机/其他电脑上传、同 slug 覆盖、全部文章 ZIP 和首次真实文章卷备份记录，同时进入 ART-003 的 10 篇基础文化解释文章。**

可并行的项目所有者外部步骤：确认 Cloudflare Web Analytics 数据；创建 UptimeRobot monitor 并验证 Down/恢复邮件。这些外部验收不包含 GitHub 文章发布或 GHCR 自动部署。

GOV-003 仍是已登记的非阻塞工程收尾项。SEO 完整验收证据见 `docs/reviews/2026-07-16-seo-001-003-acceptance.md`，本批证据见 `docs/reviews/2026-07-16-art-001-002-site-management-acceptance.md`。
