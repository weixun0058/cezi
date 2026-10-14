#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

PROJECT_DIR="${WISE_ORACLE_PROJECT_DIR:-/root/zhugeshensuan}"
COMPOSE_FILE="${WISE_ORACLE_COMPOSE_FILE:-compose.prod.yml}"
ENV_FILE="${WISE_ORACLE_ENV_FILE:-.env}"
R2_REMOTE="${WISE_ORACLE_R2_REMOTE:-}"
EXPECTED_RUNTIME_VOLUME="zhugeshensuan_runtime-data"
EXPECTED_ARTICLE_VOLUME="zhugeshensuan_article-content"
BACKUP_ROOT="$PROJECT_DIR/backups"
DAILY_ROOT="$BACKUP_ROOT/daily"
WEEKLY_ROOT="$BACKUP_ROOT/weekly"
FAILED_ROOT="$BACKUP_ROOT/failed"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SNAPSHOT_DIR="$DAILY_ROOT/$STAMP"
SNAPSHOT_VALID=0
APP_STOPPED=0

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "missing required command: $1" >&2
        exit 1
    }
}

start_and_check_app() {
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" start app >/dev/null
    for _attempt in $(seq 1 20); do
        if curl --fail --silent --show-error http://127.0.0.1:8000/healthz >/dev/null \
            && curl --fail --silent --show-error http://127.0.0.1:8000/readyz >/dev/null; then
            APP_STOPPED=0
            return 0
        fi
        sleep 2
    done
    echo "application failed health/readiness checks after backup" >&2
    return 1
}

on_exit() {
    exit_code=$?
    if [[ "$APP_STOPPED" -eq 1 ]]; then
        start_and_check_app || exit_code=1
    fi
    if [[ "$SNAPSHOT_VALID" -eq 0 && -d "$SNAPSHOT_DIR" ]]; then
        mkdir -p "$FAILED_ROOT"
        mv -- "$SNAPSHOT_DIR" "$FAILED_ROOT/$STAMP-incomplete"
    fi
    exit "$exit_code"
}
trap on_exit EXIT

for command_name in curl docker flock python3 sha256sum stat tar; do
    require_command "$command_name"
done

cd "$PROJECT_DIR"
[[ -f "$COMPOSE_FILE" ]] || { echo "missing Compose file" >&2; exit 1; }
[[ -f "$ENV_FILE" ]] || { echo "missing environment file" >&2; exit 1; }

mkdir -p "$DAILY_ROOT" "$WEEKLY_ROOT" "$FAILED_ROOT"
chmod 700 "$BACKUP_ROOT" "$DAILY_ROOT" "$WEEKLY_ROOT" "$FAILED_ROOT"
exec 9>"$BACKUP_ROOT/.backup.lock"
flock -n 9 || { echo "another backup is already running" >&2; exit 1; }

APP_CONTAINER="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q app)"
[[ -n "$APP_CONTAINER" ]] || { echo "app container not found" >&2; exit 1; }

IMAGE_REF="$(docker inspect "$APP_CONTAINER" --format '{{.Config.Image}}')"
IMAGE_ID="$(docker inspect "$APP_CONTAINER" --format '{{.Image}}')"
RUNTIME_VOLUME="$(docker inspect "$APP_CONTAINER" --format '{{range .Mounts}}{{if eq .Destination "/app/instance"}}{{.Name}}{{end}}{{end}}')"
ARTICLE_VOLUME="$(docker inspect "$APP_CONTAINER" --format '{{range .Mounts}}{{if eq .Destination "/app/content"}}{{.Name}}{{end}}{{end}}')"

[[ "$RUNTIME_VOLUME" == "$EXPECTED_RUNTIME_VOLUME" ]] || {
    echo "runtime volume does not match deployment contract" >&2
    exit 1
}
[[ "$ARTICLE_VOLUME" == "$EXPECTED_ARTICLE_VOLUME" ]] || {
    echo "article volume does not match deployment contract" >&2
    exit 1
}

RUNTIME_MOUNT="$(docker volume inspect "$RUNTIME_VOLUME" --format '{{.Mountpoint}}')"
ARTICLE_MOUNT="$(docker volume inspect "$ARTICLE_VOLUME" --format '{{.Mountpoint}}')"
[[ -f "$RUNTIME_MOUNT/runtime.db" ]] || { echo "runtime.db not found" >&2; exit 1; }
[[ -d "$ARTICLE_MOUNT" ]] || { echo "article mountpoint not found" >&2; exit 1; }

mkdir "$SNAPSHOT_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" stop app >/dev/null
APP_STOPPED=1

python3 - "$RUNTIME_MOUNT/runtime.db" "$SNAPSHOT_DIR/runtime.db" <<'PY'
import sqlite3
import sys

source_path, backup_path = sys.argv[1:]
source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
backup = sqlite3.connect(backup_path)
try:
    source.backup(backup)
    result = backup.execute("PRAGMA quick_check").fetchone()[0]
    if result != "ok":
        raise RuntimeError(result)
finally:
    backup.close()
    source.close()
print("runtime quick_check=ok")
PY

tar -czf "$SNAPSHOT_DIR/articles.tar.gz" -C "$ARTICLE_MOUNT" .
tar -tzf "$SNAPSHOT_DIR/articles.tar.gz" >/dev/null

(
    cd "$SNAPSHOT_DIR"
    sha256sum runtime.db > runtime.db.sha256
    sha256sum articles.tar.gz > articles.tar.gz.sha256
    sha256sum --check runtime.db.sha256
    sha256sum --check articles.tar.gz.sha256
)

cat >"$SNAPSHOT_DIR/manifest.txt" <<EOF
snapshot_utc=$STAMP
image_ref=$IMAGE_REF
image_id=$IMAGE_ID
runtime_volume=$RUNTIME_VOLUME
article_volume=$ARTICLE_VOLUME
runtime_size_bytes=$(stat -c %s "$SNAPSHOT_DIR/runtime.db")
article_size_bytes=$(stat -c %s "$SNAPSHOT_DIR/articles.tar.gz")
EOF
chmod 600 "$SNAPSHOT_DIR"/*
SNAPSHOT_VALID=1

start_and_check_app
curl --fail --silent --show-error https://getwiseoracle.com/readyz >/dev/null

WEEKLY_DIR=""
if [[ "$(date -u +%u)" == "7" ]]; then
    WEEKLY_DIR="$WEEKLY_ROOT/$STAMP"
    cp -a -- "$SNAPSHOT_DIR" "$WEEKLY_DIR"
fi

python3 - "$DAILY_ROOT" 7 "$WEEKLY_ROOT" 4 <<'PY'
import re
import shutil
import sys
from pathlib import Path

pattern = re.compile(r"^\d{8}T\d{6}Z$")
for root_text, keep_text in ((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4])):
    root = Path(root_text).resolve()
    keep = int(keep_text)
    snapshots = sorted(
        (path for path in root.iterdir() if path.is_dir() and pattern.fullmatch(path.name)),
        key=lambda path: path.name,
        reverse=True,
    )
    for path in snapshots[keep:]:
        resolved = path.resolve()
        if resolved.parent != root:
            raise RuntimeError("retention target escaped backup root")
        shutil.rmtree(resolved)
PY

if [[ -n "$R2_REMOTE" ]]; then
    require_command rclone
    rclone copy "$SNAPSHOT_DIR" "${R2_REMOTE%/}/daily/$STAMP" \
        --checksum --immutable --metadata
    if [[ -n "$WEEKLY_DIR" ]]; then
        rclone copy "$WEEKLY_DIR" "${R2_REMOTE%/}/weekly/$STAMP" \
            --checksum --immutable --metadata
    fi
fi

echo "backup completed: $STAMP"
