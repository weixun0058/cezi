# 项目后续工作主台账 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 以一份可追溯、可新增、可修改、可取消的主台账，管理本项目从当前可用状态到公开上线、内容建设与商业化验证的全部剩余工作。

**Architecture:** 本文档是“未完成工作”的唯一主台账；旧总纲、英文站计划和问题审计仅作需求依据与历史证据。每项工作使用稳定 ID，任务状态与计划修订分开记录；删除通过“已取消 + 保留墓碑记录”实现，不破坏追溯链。

**Tech Stack:** Python 3.13、Flask、Jinja2、SQLite、pytest、Black、Ruff、原生 JavaScript/CSS、Docker/Gunicorn、GitHub Actions。

---

## 1. 台账定位与效力

- **建立日期：** 2026-07-15
- **当前版本：** 1.0
- **主维护人：** 项目所有者 + 当次执行者
- **状态基线：** `980fdfc` 之后建立本台账，当前 pytest 285/285、Black、Ruff 均通过；本地分支因网络故障暂时领先远端。
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
| SAFE | 内容安全与文化边界 |
| SEO | 技术 SEO 与搜索收录 |
| ART | 英文文章系统与内容 |
| TRUST | 联系方式、法务与用户信任 |
| OPS | 部署、监控、备份与上线 |
| COM | 商业化调研与代码 |
| MET | 隐私友好的运营指标与复盘 |
| DEC | 需项目所有者拍板的决策 |

## 3. 当前主台账

| ID | 工作项 | 优先级 | 状态 | 依赖/决策 | 产出与验收证据 |
| --- | --- | --- | --- | --- | --- |
| GOV-001 | 建立剩余工作唯一主台账 | P0 | 已完成 | 无 | 本文档、README/旧计划引用、文档契约测试 |
| GOV-002 | 为后续每批实施建立统一验收记录 | P0 | 就绪 | GOV-001 | 每批有提交、测试、CI、文档和回滚证据 |
| SAFE-001 | 建立英文内容安全规则与人工审校表 | P0 | 就绪 | 无 | 审校清单、风险分级、通过/例外记录 |
| SAFE-002 | 实现英文内容扫描器和 CI 测试 | P0 | 就绪 | SAFE-001 | 扫描脚本、测试、可审计的 allowlist |
| SAFE-003 | 复核 384 签英文签文的医疗/财务/确定性表达 | P0 | 就绪 | SAFE-001/002 | 384/384 审校台账、修改 diff、零未处理高风险项 |
| SAFE-004 | 复核英文黄历、文章与四柱 AI 输出边界 | P0 | 就绪 | SAFE-001/002 | 术语/场景/提示词报告和回归测试 |
| TRUST-001 | 确定并配置真实联系与隐私邮箱 | P0 | 待决策 | DEC-002 | 全站无 `.example`，邮箱可接收，合规页同步 |
| SEO-001 | 建立统一站点 URL/canonical/hreflang 配置 | P1 | 就绪 | 公开语言契约 | 单一生成逻辑、多环境测试、不依赖请求 Host 注入 |
| SEO-002 | 实现 `sitemap.xml` 和 `robots.txt` | P1 | 就绪 | SEO-001 | 英文+繁体公开页可抓取；API、调试页和旧跳转入口不入 sitemap |
| SEO-003 | 完善页面 title、description、Open Graph 和结构化数据 | P1 | 就绪 | SEO-001 | 核心页唯一元数据，JSON-LD 可解析，无过度承诺 |
| ART-001 | 确定英文文章存储格式 | P1 | 待决策 | DEC-001 | 决策记录、schema、安全渲染方案 |
| ART-002 | 实现文章加载、列表和详情页 | P1 | 阻塞 | ART-001 | 未知 slug 404，列表稳定排序，无未过滤 HTML |
| ART-003 | 发布第一批 10 篇基础文化解释文章 | P1 | 阻塞 | ART-002、SAFE-001 | 10/10 人工审校，每篇有内链、来源、负责使用说明 |
| ART-004 | 发布 10 篇搜索意图文章 | P2 | 阻塞 | ART-003、Search Console 基线 | 10/10 审校，无重复/薄内容，有搜索意图记录 |
| ART-005 | 发布 5 篇工具使用/转化辅助文章 | P2 | 阻塞 | ART-003、商业化边界 | 5/5 审校，不暗示付费提高准确性 |
| OPS-001 | 完成生产环境配置和域名/HTTPS 验收 | P1 | 就绪 | TRUST-001、SEO-001 | 域名、HTTPS、环境变量、health/readiness 证据 |
| OPS-002 | 建立备份、恢复和回滚演练 | P1 | 就绪 | OPS-001 | `runtime.db`/数据卷备份，恢复演练和镜像回滚记录 |
| OPS-003 | 建立错误、存活性与资源监控 | P1 | 待决策 | DEC-003、OPS-001 | 告警通道、阈值、测试告警证据；不采集出生数据 |
| OPS-004 | 提交 Search Console 并验证收录 | P1 | 阻塞 | SEO-002、OPS-001 | 所有权验证、sitemap 提交、抓取记录 |
| OPS-005 | 执行上线前全量验收 | P1 | 阻塞 | SAFE/SEO/TRUST/OPS 的 P0-P1 项 | 同一提交上全套 CI、Docker 健康、桌面/移动、断网和回滚证据 |
| COM-001 | 实时核验支付、赞助和广告平台政策 | P2 | 就绪 | 上线地区/主体信息 | 官方来源、核验日期、提现/类目/webhook/费用对比 |
| COM-002 | 确定是否解冻赞助/广告/Deep Reading | P2 | 待决策 | COM-001、DEC-004/005 | 明确“上线/不上线”及触发条件 |
| COM-003 | 实现默认关闭的商业化配置开关 | P3 | 阻塞 | COM-002 | 关闭时零 UI/零外部请求，配置和测试完整 |
| COM-004 | 实现赞助组件或广告占位 | P3 | 阻塞 | COM-002/003 | 开关控制、布局安全、无误导点击或运势暗示 |
| COM-005 | 实现模拟付费墙、订单模型与 webhook 边界 | P3 | 阻塞 | COM-002/003、DEC-005 | 无平台时不持久化真订单；未签名 webhook 不可用 |
| MET-001 | 建立隐私友好的使用/成本指标 | P2 | 就绪 | OPS-001 | 只记聚合数据，不记姓名、出生时间或原始问题 |
| MET-002 | 连续四周运营复盘 | P3 | 阻塞 | MET-001、OPS-004 | 4/4 周记录，形成内容、成本和商业化去留决策 |

## 4. 推荐执行顺序

1. **批次 A（可立即开始）：** GOV-002 → SAFE-001 → SAFE-002。
2. **批次 B（内容风险收敛）：** SAFE-003 与 SAFE-004，完成后才扩写文章。
3. **批次 C（技术 SEO）：** SEO-001 → SEO-002 → SEO-003；不必等待文章系统决策。
4. **批次 D（需两项业主输入）：** DEC-001 解锁 ART-001/002；DEC-002 解锁 TRUST-001。
5. **批次 E（内容与上线）：** ART-003、OPS-001/002/003/004 → OPS-005。
6. **批次 F（上线后增长）：** ART-004/005、MET-001/002。
7. **批次 G（最后考虑商业化）：** COM-001 → COM-002 → COM-003/004/005。

## 5. 详细任务卡

### Task SAFE: 英文内容安全闭环

**Files:**
- Create: `docs/reviews/english-content-safety-checklist.md`
- Create: `scripts/audit_english_content.py`
- Create: `data/content/_review_log/content_safety_review.json`
- Create: `tests/test_english_content_safety.py`
- Modify: `data/content/oracle_signs_en.json`
- Modify as findings require: `data/content/huangli_terms_en.json`, `prompts/*`, `frontend/templates/en/*.html`

**Steps:**
1. 从 `wise-oracle-ai-prompt-boundaries.md` 和现有合规页提取“禁止/需人工判断/可接受”三级规则。
2. 先写失败测试：要求所有 384 签有审校状态，且高风险命中不得无 allowlist 理由。
3. 运行 `python -m pytest tests/test_english_content_safety.py -q`，预期初次 FAIL，显示未审校数量。
4. 实现只读扫描器，输出签号、字段、规则、片段和风险等级；扫描器不自动改文。
5. 逐项人工复核，修改真问题，例外必须记录具体理由，不允许整个文件跳过。
6. 运行定向测试与全量 pytest，更新审计清单的统计和修订日期。
7. 提交建议：`test: add English content safety gate`，内容修正另作 `content: resolve reviewed English safety findings`。

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

### Task ART: 版本可控的英文文章系统

**Files:**
- Decision-dependent create: `data/content/articles_en/` and article manifest/schema
- Create: `zhugeshensuan/content.py`
- Create: `tests/test_articles.py`
- Modify: `zhugeshensuan/blueprints/pages_en.py`
- Modify: `frontend/templates/en/articles.html`, `frontend/templates/en/article_detail.html`

**Steps:**
1. 先完成 DEC-001；推荐“版本库内 Markdown + 受控元数据”，不建议第一版上数据库或 CMS。
2. 定义 schema：`slug/title/description/published_at/updated_at/status/tags/body/source_notes`。
3. 先写列表、详情、未知 slug 404、draft 不可见、重复 slug 启动失败和 HTML 安全测试。
4. 实现最小加载器；启动时验证内容，运行期只读，不在请求内扫描磁盘。
5. 修正占位路由，让列表只显示已发布文章，详情页使用文章自身 meta/canonical。
6. 运行 `python -m pytest tests/test_articles.py tests/test_english_frontend_contract.py -q`。
7. 发布内容时按 10 + 10 + 5 三批提交，每批附人工审校记录。

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
| DEC-001 | 英文文章存储方式 | 仓库 Markdown / JSON / SQLite/CMS | 仓库 Markdown + 受控元数据；便于 Git 审校与回滚 | ART-001/002 | 待决策 |
| DEC-002 | 对外联系方式 | 单邮箱 / contact+privacy 分开 | 两个别名指向同一可管理邮箱 | TRUST-001、OPS-005 | 待决策 |
| DEC-003 | 生产监控与告警通道 | 自建/托管；邮件/即时通知 | 先选低成本托管存活性+错误告警，严格脱敏 | OPS-003/005 | 待决策 |
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
node --check frontend/static/js/main.js
node --check frontend/static/js/daily_almanac.js
node --check frontend/static/js/birth_chart_en.js
node --check frontend/static/js/lang/lang_switcher.js
```

数据或部署变更还必须执行 reference DB logical dump 比较、Docker 生产镜像构建、`/healthz` 与 `/readyz` 健康检查。前端改动还必须保留 1440px/390px 人工验收证据。

## 8. 进度日志

| 日期 | 任务 ID | 执行者 | 状态变更 | 实际改动 | 验收证据 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-15 | GOV-001 | Codex | 就绪 → 已完成 | 建立主台账、决策台账、变更和取消规则 | 文档契约测试与 Git 提交 | 从 SAFE-001 开始 |

## 9. 已取消任务（墓碑）

| ID | 原工作项 | 取消日期 | 取消原因 | 替代项/决策 |
| --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — |

## 10. 计划变更记录

| 版本 | 日期 | 修订人 | 类型 | 变更内容 | 原因 |
| --- | --- | --- | --- | --- | --- |
| 1.0 | 2026-07-15 | Codex | 新增 | 建立 GOV/SAFE/SEO/ART/TRUST/OPS/COM/MET/DEC 统一台账 | 原有三份计划同时记录待办，存在重复、过时和不可追溯风险 |

## 11. 下一个可执行批次

**建议立即执行：SAFE-001 + SAFE-002。** 这两项不需要新的产品决策，会把目前问题清单中最重要的“英文内容安全审校”变成可重复执行、可审计的质量门禁。

并行需要项目所有者提供的最小决策为：DEC-001（文章存储方式）和 DEC-002（真实联系邮箱）。
