from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_backup_script_has_exact_volume_and_data_guards():
    script = _read("scripts/production_backup.sh")

    assert 'EXPECTED_RUNTIME_VOLUME="zhugeshensuan_runtime-data"' in script
    assert 'EXPECTED_ARTICLE_VOLUME="zhugeshensuan_article-content"' in script
    assert '[[ "$RUNTIME_VOLUME" == "$EXPECTED_RUNTIME_VOLUME" ]]' in script
    assert '[[ "$ARTICLE_VOLUME" == "$EXPECTED_ARTICLE_VOLUME" ]]' in script
    assert "source.backup(backup)" in script
    assert 'backup.execute("PRAGMA quick_check")' in script
    assert "sha256sum --check runtime.db.sha256" in script
    assert "tar -tzf" in script
    assert "docker compose down" not in script
    assert "down -v" not in script


def test_production_backup_script_restores_service_and_uploads_immutably():
    script = _read("scripts/production_backup.sh")

    assert "trap on_exit EXIT" in script
    assert "start_and_check_app" in script
    assert "http://127.0.0.1:8000/healthz" in script
    assert "http://127.0.0.1:8000/readyz" in script
    assert "https://getwiseoracle.com/readyz" in script
    assert "rclone copy" in script
    assert "--immutable" in script
    assert "access_key" not in script.lower()
    assert "secret_key" not in script.lower()


def test_backup_timer_is_daily_and_persistent():
    service = _read("deploy/wise-oracle-backup.service")
    timer = _read("deploy/wise-oracle-backup.timer")

    assert "scripts/production_backup.sh" in service
    assert "wise-oracle-crypt:production" in service
    assert "OnCalendar=*-*-* 19:15:00 UTC" in timer
    assert "RandomizedDelaySec=15m" in timer
    assert "Persistent=true" in timer
