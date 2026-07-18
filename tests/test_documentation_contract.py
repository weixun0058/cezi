from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def test_public_language_contract_is_documented():
    readme = _read("README.md")
    product_spec = _read("docs/business/wise-oracle-english-product-spec.md")

    assert "公开语言切换器只展示繁体中文和英文" in readme
    assert "`/zh-hans/*`" in readme
    assert "`/huangli`、`/suanshi`、`/lunming` 固定 301 到对应繁体页面" in readme
    assert "`/zh-hant/almanac`、`/zh-hant/divination`、`/zh-hant/bazi`" in product_spec


def test_english_almanac_and_pillar_contracts_are_documented():
    readme = _read("README.md")
    api_doc = _read("docs/API文档.md")
    product_spec = _read("docs/business/wise-oracle-english-product-spec.md")

    assert "英文 `/api/en/week-almanac` 返回 10 日" in readme
    assert "10 条英文黄历记录" in api_doc
    assert "固定返回 10 日" in product_spec
    assert "共九天的英文黄历" not in api_doc
    assert "四柱拼音" not in api_doc
    assert "Yang Metal Horse" in api_doc
    assert "Geng-Wu" in api_doc
    assert api_doc.count("### `POST /api/en/oracle/ask`") == 1
    assert api_doc.count("### `POST /api/en/birth-chart/analyze`") == 1
    assert "不再输出 `Jia-Zi`、`Geng-Wu`" in product_spec


def test_json_runtime_data_boundary_is_documented():
    agent_doc = _read("Agent.md")
    architecture = _read("docs/architecture/data-source-migration-2026-07-13.md")
    project_structure = _read("docs/PROJECT_STRUCTURE.md")
    reprocess_script = _read("scripts/reprocess_single_sign.py")
    adjudicate_script = _read("scripts/adjudicate_single_sign.py")

    assert "运行时只读取 `hanzi` 笔画表" in agent_doc
    assert "禁止运行 `backfill_reinterpreted_to_db.py`" in agent_doc
    assert "应用运行时不读取这些表" in architecture
    assert "旧签文/彭祖百忌表只用于历史构建产物可重建" in project_structure
    assert "如需同步数据库" not in reprocess_script
    assert "如需同步数据库" not in adjudicate_script


def test_deployment_commands_use_current_workspace_layout():
    deployment = _read("docs/部署指南.md")

    assert r"V:\诸葛神算V3" not in deployment
    assert r"V:\诸葛神算V4" in deployment
    assert r".\deploy\compose.prod.yml" in deployment
    assert "docker build -f deploy/Dockerfile" in deployment
    assert "CONTACT_EMAIL=5siwei@gmail.com" in deployment


def test_master_ledger_is_the_active_plan_for_remaining_work():
    readme = _read("README.md")
    global_plan = _read("docs/plans/2026-06-24-global-i18n-commercialization-execution-plan.md")
    english_plan = _read("docs/plans/2026-06-27-english-site-execution-plan.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    ledger_name = "2026-07-15-project-completion-master-ledger.md"
    assert ledger_name in readme
    assert ledger_name in global_plan
    assert ledger_name in english_plan
    assert "已取消任务（墓碑）" in ledger
    assert "计划变更记录" in ledger
    assert "DEC-001" in ledger
    assert "SAFE-001" in ledger
    assert "OPS-005" in ledger
    assert "GOV-003" in ledger
    assert "OPS-006" in ledger


def test_ops001_production_acceptance_is_documented():
    acceptance = _read("docs/operations/production-acceptance.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    assert "OPS-001" in acceptance
    assert "https://getwiseoracle.com" in acceptance
    assert "AI_API_KEY" in acceptance
    assert "原文未输出" in acceptance
    assert "healthz" in acceptance
    assert "readyz" in acceptance
    assert "OPS-001 | 完成生产环境配置和域名/HTTPS 验收 | P1 | 已完成" in ledger


def test_ops004_search_console_acceptance_is_documented():
    acceptance = _read("docs/operations/search-console-acceptance.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    assert "OPS-004" in acceptance
    assert "sc-domain:getwiseoracle.com" in acceptance
    assert "https://getwiseoracle.com/sitemap.xml" in acceptance
    assert "| 状态 | 成功 |" in acceptance
    assert "| 发现的网页 | 9 |" in acceptance
    assert "网页已编入索引" in acceptance
    assert "google-site-verification=" not in acceptance
    assert "OPS-004 | 提交 Search Console 并验证收录 | P1 | 已完成" in ledger


def test_server_uploaded_article_publishing_decision_is_documented():
    architecture = _read("docs/architecture/article-publishing-architecture-2026-07-16.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    assert "服务器私密 URL 上传并即时发布" in architecture
    assert "https://getwiseoracle.com/165131" in architecture
    assert "手机、其他电脑或任何地点" in architecture
    assert "不触发 Git commit、GitHub Actions、Docker build 或部署" in architecture
    assert "下载全部文章" in architecture
    assert "服务器私密 URL 上传并即时发布" in ledger
    assert "GitHub 仅管理程序代码" in ledger


def test_article_system_and_site_management_acceptance_is_documented():
    acceptance = _read("docs/reviews/2026-07-16-art-001-002-site-management-acceptance.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    for required in (
        "ART-001、ART-002 已按纠正后的方案完成",
        "https://getwiseoracle.com/165131",
        "不提交 Git、不触发 Actions、不构建镜像、不重新部署",
        "打包下载全部文章",
        "zhugeshensuan_article-content",
        "zhugeshensuan:2026.07.16-article-upload",
        "手机或另一台电脑",
        "生产状态更新（2026-07-17）",
        "新镜像与 Compose 已部署",
        "sitemap.xml` 已动态包含文章列表和首篇文章 URL，共 11 个 URL",
    ):
        assert required in acceptance

    assert "ART-001 | 确定英文文章存储与发布架构 | P1 | 已完成" in ledger
    assert "ART-002 | 实现文章加载、列表、详情与服务器上传 | P1 | 已完成" in ledger
    assert "ART-003 | 按机会持续发布基础文化解释文章 | P3 | 就绪（非阻塞、非硬性）" in ledger
    assert "OPS-003 | 建立错误、存活性与资源监控 | P1 | 已完成" in ledger
    assert "OPS-006 | 处理 Cloudflare Browser Insights 与 CSP 冲突 | P2 | 已完成" in ledger


def test_current_product_and_ledger_status_match_the_deployed_article_system():
    product_spec = _read("docs/business/wise-oracle-english-product-spec.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")
    seo_acceptance = _read("docs/reviews/2026-07-16-seo-001-003-acceptance.md")
    search_console = _read("docs/operations/search-console-acceptance.md")

    stale_snapshot = (
        "文章页仍为占位；`sitemap.xml`、`robots.txt`、Search Console、"
        "商业化配置和真实支付尚未实现"
    )
    assert stale_snapshot not in product_spec
    assert "服务器私密文章上传" in product_spec
    assert "正式站已有首篇文章" in product_spec

    assert "**当前版本：** 1.24" in ledger
    assert "2026-07-17 实测 11 URL" in ledger
    assert "OPS-005 | 执行上线后统一全量验收 | P1 | 已完成" in ledger
    assert "GitHub Actions run 20 全部通过" in ledger
    assert "下一步先部署包含文章持久卷" not in ledger
    assert "GitHub 自动部署生产验收并行" not in ledger

    assert "9 URL 是 SEO 批次验收时的静态基线" in seo_acceptance
    assert "生产 sitemap 已扩展到 11 URL" in search_console


def test_commercialization_and_operations_next_stage_is_documented():
    roadmap = _read("docs/business/2026-07-19-commercialization-readiness-roadmap.md")
    weekly = _read("docs/business/weekly-growth-review-template.md")
    backup = _read("docs/operations/automated-backup-r2-runbook.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    assert "基础站点和生产版本已完成；商业化准备进行中" in roadmap
    assert "不重新引入" in roadmap
    assert "出生资料输入页、占卜输入页和个性化结果页暂不展示广告" in roadmap
    assert "连续四个完整自然周" in weekly
    assert "未启用" in weekly
    assert "R2尚未启用" in backup
    assert "项目所有者明确确认" in backup
    assert "COM-001 | 实时核验支付、赞助和广告平台政策 | P2 | 进行中" in ledger
    assert "MET-001 | 建立隐私友好的使用/成本指标 | P2 | 进行中" in ledger
