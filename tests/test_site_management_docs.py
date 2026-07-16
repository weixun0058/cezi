from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_site_owner_guide_maps_each_management_surface_to_its_real_role():
    guide = _read("docs/operations/site-owner-management.md")

    assert "Google Search Console" in guide
    assert "Cloudflare Analytics & Logs" in guide
    assert "私密文章上传页" in guide
    assert "GitHub Actions" in guide
    assert "UptimeRobot" in guide
    assert "Docker health/readiness" in guide
    assert "docs/operations/backup-restore-runbook.md" in guide
    assert "sitemap 状态成功" in guide
    assert "首页已编入 Google 索引" in guide
    assert "私密文章上传页只负责正式 Markdown 的上传、覆盖和导出" in guide


def test_monitoring_runbook_locks_the_external_monitor_and_completion_boundary():
    runbook = _read("docs/operations/monitoring-runbook.md")

    assert "https://getwiseoracle.com/readyz" in runbook
    assert "5 分钟" in runbook
    assert "5siwei@gmail.com" in runbook
    assert "账号创建、条款接受和邮箱确认必须由项目所有者完成" in runbook
    assert "告警邮件和恢复邮件" in runbook
    assert "不得声称 OPS-003 已完成" in runbook
    assert "https://uptimerobot.com/pricing/" in runbook
    assert "核对日期：2026-07-16" in runbook


def test_management_docs_define_routines_privacy_and_incident_escalation():
    guide = _read("docs/operations/site-owner-management.md")
    runbook = _read("docs/operations/monitoring-runbook.md")
    combined = guide + runbook

    for cadence in ("每日", "每周", "每月"):
        assert cadence in guide

    for prohibited_data in (
        "原始问题",
        "出生日期",
        "出生时间",
        "Cookie",
        "Authorization",
        "AI 原文",
        "`.env`",
    ):
        assert prohibited_data in combined

    assert "事故升级" in runbook
    assert "恢复服务优先" in runbook
    assert "第三方错误上报平台默认关闭" in runbook
    assert "数据区域" in runbook
    assert "保留期" in runbook
    assert "scrubbing" in runbook


def test_monitoring_commands_match_the_current_compose_and_log_contract():
    runbook = _read("docs/operations/monitoring-runbook.md")

    assert "docker compose --env-file .env -f compose.prod.yml ps" in runbook
    assert "curl --fail http://127.0.0.1:8000/healthz" in runbook
    assert "curl --fail http://127.0.0.1:8000/readyz" in runbook
    assert "curl --fail https://getwiseoracle.com/readyz" in runbook
    assert "docker compose --env-file .env -f compose.prod.yml logs --tail=200 app" in runbook
    for log_field in ("time", "level", "logger", "message", "exception"):
        assert f"`{log_field}`" in runbook
    assert "request_id" in runbook


def test_article_upload_guide_explains_cross_device_immediate_publish_and_export():
    guide = _read("docs/operations/article-upload-guide.md")

    for required in (
        "https://getwiseoracle.com/165131",
        "手机、平板、任意电脑",
        "ARTICLE_ADMIN_PATH=165131",
        "ARTICLE_ADMIN_PASSWORD",
        "不需要：** GitHub",
        "上传并立即发布",
        "打包下载全部文章",
        "zhugeshensuan_article-content",
        "不需要重启",
        "确认覆盖原文章",
    ):
        assert required in guide

    assert "docs/部署指南.md" in guide
    assert "OPS-002" in guide
