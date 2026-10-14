import tarfile
from pathlib import Path

from scripts.package_build_context import (
    collect_files,
    find_forbidden,
    is_excluded,
    main,
    parse_dockerignore,
    write_archive,
)

ROOT = Path(__file__).resolve().parents[1]


def _touch(root, relative, content="x"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_rules_follow_docker_order_negation_and_parent_matching():
    rules = parse_dockerignore("data/*\n!data/content\ndata/content/_review_log\n**/*.bak*\n")

    assert is_excluded("data/client_secret.json", rules)
    assert not is_excluded("data/content/signs.json", rules)
    assert is_excluded("data/content/_review_log/sign-001.md", rules)
    assert is_excluded("data/content/signs.json.bak", rules)
    assert not is_excluded("app.py", rules)


def test_project_dockerignore_keeps_runtime_data_and_drops_local_files(tmp_path):
    rules = parse_dockerignore((ROOT / ".dockerignore").read_text(encoding="utf-8"))
    for relative in (
        "app.py",
        ".env",
        ".env.example",
        "zhugeshensuan/app.py",
        "data/reference/reference.db",
        "data/reference/reference.db.bak_before_backfill",
        "data/content/oracle_signs_en.json",
        "data/content/_review_log/sign-001.md",
        "data/client_secret_1.apps.googleusercontent.com.json",
        "data/cloudflare analytics token.txt",
        "windows-tray-backup-20260625-160514/after.csv",
        ".git/HEAD",
        ".venv/pyvenv.cfg",
        "instance/runtime.db",
        "zhugeshensuan-4.1.5-analytics.tar",
        "zhugeshensuan-4.1.6-analytics-context.tar.gz",
    ):
        _touch(tmp_path, relative)

    files = collect_files(tmp_path, rules)

    assert files == [
        ".env.example",
        "app.py",
        "data/content/oracle_signs_en.json",
        "data/reference/reference.db",
        "zhugeshensuan/app.py",
    ]
    assert find_forbidden(files) == []


def test_credential_files_are_reported_as_forbidden():
    files = [
        ".env",
        ".env.production",
        ".env.example",
        "data/client_secret_1.json",
        "deploy/server.key",
        "data/cloudflare 令牌.txt",
        "app.py",
    ]

    assert find_forbidden(files) == [
        ".env",
        ".env.production",
        "data/client_secret_1.json",
        "deploy/server.key",
        "data/cloudflare 令牌.txt",
    ]


def test_archive_normalizes_owner_and_permissions(tmp_path):
    _touch(tmp_path, "pkg/module.py", "print('ok')\n")
    output = tmp_path / "context.tar.gz"

    write_archive(tmp_path, ["pkg/module.py"], output)

    with tarfile.open(output) as archive:
        member = archive.getmember("pkg/module.py")
        assert (member.uid, member.gid, member.mode) == (0, 0, 0o644)
        assert archive.extractfile(member).read() == b"print('ok')\n"


def test_main_refuses_to_package_credentials(tmp_path, capsys):
    project = tmp_path / "project"
    _touch(project, ".dockerignore", "*.tar\n")
    _touch(project, "app.py")
    _touch(project, ".env", "SECRET_KEY=do-not-ship\n")
    output = tmp_path / "context.tar.gz"

    assert main([str(output)], project=project) == 1
    assert not output.exists()
    assert ".env" in capsys.readouterr().err


def test_main_packages_filtered_context_without_its_own_output(tmp_path):
    project = tmp_path / "project"
    _touch(project, ".dockerignore", ".env\n")
    _touch(project, "app.py")
    _touch(project, ".env", "SECRET_KEY=do-not-ship\n")
    output = project / "context.tar.gz"

    assert main([str(output)], project=project) == 0

    with tarfile.open(output) as archive:
        assert sorted(archive.getnames()) == [".dockerignore", "app.py"]
