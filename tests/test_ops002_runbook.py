from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_ops002_runbook_documents_the_real_data_boundary_and_safeguards():
    runbook = _read("docs/operations/backup-restore-runbook.md")

    assert "zhugeshensuan_runtime-data" in runbook
    assert "/app/instance/runtime.db" in runbook
    assert "reference.db" in runbook
    assert "不属于 `runtime.db` 备份" in runbook
    assert "PRAGMA quick_check" in runbook
    assert "sha256sum --check" in runbook
    assert "不运行 `docker compose down -v`" in runbook
    assert "不删除 `zhugeshensuan_runtime-data` 或 `zhugeshensuan_article-content`" in runbook
    assert "/app/content/articles_en" in runbook
    assert "articles-$STAMP.tar.gz" in runbook
    assert "runtime.db.pre-restore-" in runbook
    assert "--no-build" in runbook


def test_ops002_rehearsal_script_refuses_non_isolated_resources():
    script = _read("scripts/ops002_rehearsal.ps1")

    assert 'StartsWith("zhugeshensuan-ops002-"' in script
    assert 'if ($Name -eq "zhugeshensuan_runtime-data")' in script
    assert "Refusing to operate on the production runtime volume" in script
    assert "production_volume_identity_unchanged" in script
    assert "production_volume_mounted = $false" in script
    assert "Remove-IsolatedVolume $sourceVolume" in script
    assert "Remove-IsolatedVolume $restoredVolume" in script
    assert "Remove-IsolatedVolume $productionVolumeName" not in script


def test_ops002_acceptance_records_backup_restore_and_real_image_switch():
    acceptance = _read("docs/operations/ops-002-acceptance.md")
    ledger = _read("docs/plans/2026-07-15-project-completion-master-ledger.md")

    assert "OPS-002" in acceptance
    assert "50be86d7405843d1b7a12c553ad1da752dcd9f80ffd6cabeaeb998b80fd57c09" in acceptance
    assert "present-in-backup" in acceptance
    assert "created-after-backup" in acceptance
    assert "生产服务器：** 未连接、未修改" in acceptance
    assert "不同 image ID" in acceptance
    assert "残留 `zhugeshensuan-ops002-` 卷 | 0" in acceptance
    assert "OPS-002 | 建立备份、恢复和回滚演练 | P1 | 已完成" in ledger
