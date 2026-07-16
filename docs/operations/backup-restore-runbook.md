# OPS-002 备份、恢复与镜像回滚手册

- **适用环境：** `getwiseoracle.com` 当前 Docker Compose 部署
- **Compose 文件：** `~/zhugeshensuan/compose.prod.yml`
- **持久化卷：** `zhugeshensuan_runtime-data`、`zhugeshensuan_article-content`
- **容器内数据目录：** `/app/instance`、`/app/content/articles_en`
- **当前可变数据：** `/app/instance/runtime.db`、上传的 Markdown 文章
- **原则：** 不删除生产数据卷；恢复前保留现场副本；镜像回滚与数据恢复分开执行

## 1. 备份范围

`runtime.db` 保存运行期可变数据，包括笔画缓存、AI 使用计数和限流状态。私密文章管理页上传的 Markdown 保存在独立 article-content 卷中。数据库和文章卷都必须备份，恢复和校验方法分开。

以下内容不属于 `runtime.db` 备份：

- 签文和黄历英文词表：随源码与版本化镜像发布，应由 Git 和镜像标签追溯。
- `reference.db`：随镜像发布的只读构建工件，不在运行期数据卷中。
- `.env`：含密钥，不得装进普通数据备份；应在密码管理器或服务器安全配置库中单独保管。
- Docker 镜像：用不可变版本标签和导出的镜像 tar 保留，不混入数据库备份。

## 2. 最低运维策略

1. 每次升级、数据库结构变更或恢复操作前，必须同时备份 runtime 数据库和文章卷。
2. 正常运营至少每日备份一次；建议保留最近 7 份日备份和 4 份周备份。
3. 每份备份同时保存 `.sha256`；只保留在同一台服务器上不算完整备份，至少再复制一份到加密的异机存储。
4. 备份文件权限设为 `600`，备份目录权限设为 `700`。
5. 每月至少在隔离卷中做一次恢复演练；不得直接用生产卷做“测试恢复”。
6. 不运行 `docker compose down -v`，不删除 `zhugeshensuan_runtime-data` 或 `zhugeshensuan_article-content`。

当前基线目标为 **RPO 不超过 24 小时**；升级和迁移前的备份把该次变更的 RPO 降到升级前一刻。实际 RTO 取决于镜像和备份传输速度，本手册要求恢复后必须通过 `readyz` 才能恢复流量。

## 3. 生产操作前检查

在服务器执行：

```bash
cd ~/zhugeshensuan

APP_CONTAINER="$(docker compose --env-file .env -f compose.prod.yml ps -q app)"
test -n "$APP_CONTAINER" || { echo '找不到 app 容器，停止操作'; exit 1; }

IMAGE_REF="$(docker inspect "$APP_CONTAINER" --format '{{.Config.Image}}')"
DATA_VOLUME="$(docker inspect "$APP_CONTAINER" --format '{{range .Mounts}}{{if eq .Destination "/app/instance"}}{{.Name}}{{end}}{{end}}')"
ARTICLE_VOLUME="$(docker inspect "$APP_CONTAINER" --format '{{range .Mounts}}{{if eq .Destination "/app/content"}}{{.Name}}{{end}}{{end}}')"

test "$DATA_VOLUME" = 'zhugeshensuan_runtime-data' || {
  echo "数据卷不符合预期：$DATA_VOLUME，停止操作"
  exit 1
}
test "$ARTICLE_VOLUME" = 'zhugeshensuan_article-content' || {
  echo "文章卷不符合预期：$ARTICLE_VOLUME，停止操作"
  exit 1
}

docker inspect "$APP_CONTAINER" --format 'image={{.Config.Image}} id={{.Image}}'
docker volume inspect "$DATA_VOLUME" --format 'volume={{.Name}} created={{.CreatedAt}}'
docker volume inspect "$ARTICLE_VOLUME" --format 'volume={{.Name}} created={{.CreatedAt}}'
docker compose --env-file .env -f compose.prod.yml ps
curl --fail http://127.0.0.1:8000/readyz
```

必须明确看到两个预期数据卷。任何名称不一致都先停止，不凭猜测继续。

## 4. 停机备份 `runtime.db`

以下流程会短暂停止应用，避免复制 SQLite WAL 写入中的文件：

```bash
cd ~/zhugeshensuan
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$PWD/backups"
BACKUP_PATH="$BACKUP_DIR/runtime-$STAMP.db"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

docker compose --env-file .env -f compose.prod.yml stop app
docker cp "$APP_CONTAINER:/app/instance/runtime.db" "$BACKUP_PATH"
```

先在应用镜像内检查备份的 SQLite 完整性：

```bash
docker run --rm \
  --user 0:0 \
  --read-only \
  --tmpfs /tmp:size=16m,mode=1777 \
  --mount "type=bind,src=$BACKUP_DIR,dst=/backup,readonly" \
  --entrypoint python \
  "$IMAGE_REF" \
  -c "import sqlite3; db=sqlite3.connect('file:/backup/$(basename "$BACKUP_PATH")?mode=ro', uri=True); result=db.execute('PRAGMA quick_check').fetchone()[0]; db.close(); assert result == 'ok', result; print('quick_check=ok')"

sha256sum "$BACKUP_PATH" > "$BACKUP_PATH.sha256"
chmod 600 "$BACKUP_PATH" "$BACKUP_PATH.sha256"
```

只有出现 `quick_check=ok` 后才重新启动：

```bash
docker compose --env-file .env -f compose.prod.yml start app
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
sha256sum --check "$BACKUP_PATH.sha256"
ls -lh "$BACKUP_PATH" "$BACKUP_PATH.sha256"
```

若复制或完整性检查失败，先启动原应用恢复服务，再调查原因；不要把失败文件当成有效备份。

### 4.1 备份文章卷

文章写入使用同卷原子替换。为获得明确时间点的完整副本，仍建议在 runtime 备份的同一次停机窗口执行：

```bash
ARTICLE_BACKUP="$BACKUP_DIR/articles-$STAMP.tar.gz"
docker run --rm \
  --mount "type=volume,src=$ARTICLE_VOLUME,dst=/data,readonly" \
  --mount "type=bind,src=$BACKUP_DIR,dst=/backup" \
  alpine \
  tar -czf "/backup/$(basename "$ARTICLE_BACKUP")" -C /data .

sha256sum "$ARTICLE_BACKUP" > "$ARTICLE_BACKUP.sha256"
chmod 600 "$ARTICLE_BACKUP" "$ARTICLE_BACKUP.sha256"
sha256sum --check "$ARTICLE_BACKUP.sha256"
tar -tzf "$ARTICLE_BACKUP"
```

恢复文章时先在新临时卷解压并用当前镜像加载 `/app/content/articles_en`，确认所有 Markdown 可解析、`/articles` 和 sitemap 正常，再在停机窗口替换生产卷内容。管理页面的 ZIP 下载也应定期保存，但它不是生产卷恢复演练的替代品。

## 5. 隔离恢复演练

runtime 数据库恢复演练必须写入新建的临时卷，不得挂载 `zhugeshensuan_runtime-data`。文章卷按上一节另行做临时卷解压与加载验证。Windows 开发机可直接运行仓库脚本：

```powershell
cd "V:\诸葛神算V4"
.\scripts\ops002_rehearsal.ps1 `
  -CurrentImage zhugeshensuan:local `
  -RollbackImage zhugeshensuan:final-audit
```

脚本会完成：

1. 创建带 `zhugeshensuan-ops002-` 前缀的两个临时卷。
2. 用当前镜像初始化源卷并写入演练标记。
3. 停止当前容器，复制并计算 `runtime.db` 的 SHA-256。
4. 在备份之后向源卷写入第二个标记。
5. 把备份恢复到另一个临时卷，确认第二个标记不存在且 `PRAGMA quick_check` 为 `ok`。
6. 用旧镜像挂载恢复卷，确认 `/readyz` 成功。
7. 只删除本次生成的临时容器、临时卷和临时文件。

脚本会拒绝操作不带 `zhugeshensuan-ops002-` 前缀的资源，并记录生产卷在演练前后身份是否一致。输出 JSON 应保存到当次验收记录。

## 6. 生产恢复

只有在备份的 `.sha256` 和 SQLite 完整性都通过后才能执行。下例不会删除生产卷；现有数据库及其 WAL/SHM 文件会被改名保留。

### 6.1 校验并保留恢复前现场

```bash
cd ~/zhugeshensuan
BACKUP_PATH="$PWD/backups/runtime-要恢复的时间戳.db"
test -s "$BACKUP_PATH" || { echo '备份不存在或为空'; exit 1; }
sha256sum --check "$BACKUP_PATH.sha256"

RESTORE_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EMERGENCY_PATH="$PWD/backups/runtime-before-restore-$RESTORE_STAMP.db"

docker compose --env-file .env -f compose.prod.yml stop app
docker cp "$APP_CONTAINER:/app/instance/runtime.db" "$EMERGENCY_PATH"
sha256sum "$EMERGENCY_PATH" > "$EMERGENCY_PATH.sha256"
chmod 600 "$EMERGENCY_PATH" "$EMERGENCY_PATH.sha256"

docker cp "$BACKUP_PATH" "$APP_CONTAINER:/app/instance/runtime.db.restore"
```

### 6.2 验证候选文件并原子替换

```bash
docker run --rm \
  --user 0:0 \
  --mount "type=volume,src=$DATA_VOLUME,dst=/data" \
  --entrypoint python \
  -e RESTORE_STAMP="$RESTORE_STAMP" \
  "$IMAGE_REF" \
  -c "import os, sqlite3; stamp=os.environ['RESTORE_STAMP']; candidate='/data/runtime.db.restore'; db=sqlite3.connect('file:'+candidate+'?mode=ro', uri=True); result=db.execute('PRAGMA quick_check').fetchone()[0]; db.close(); assert result == 'ok', result; current='/data/runtime.db'; os.replace(current, f'/data/runtime.db.pre-restore-{stamp}'); [(os.replace(current+s, f'/data/runtime.db.pre-restore-{stamp}'+s)) for s in ('-wal','-shm') if os.path.exists(current+s)]; os.replace(candidate, current); os.chown(current, 10001, 10001); print('restore-promoted=ok')"
```

启动并验收：

```bash
docker compose --env-file .env -f compose.prod.yml start app
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
curl --fail https://getwiseoracle.com/readyz
docker compose --env-file .env -f compose.prod.yml logs --tail=100 app
```

验收通过前，保留卷内 `runtime.db.pre-restore-*` 和服务器上的 `runtime-before-restore-*.db`。确认稳定后再按保留策略清理；不得为了清理旧文件删除整个卷。

### 6.3 恢复失败时撤回

若新数据库导致 `readyz` 失败，先停止应用，再把新文件改名并恢复刚才保留的现场文件：

```bash
docker compose --env-file .env -f compose.prod.yml stop app

docker run --rm \
  --user 0:0 \
  --mount "type=volume,src=$DATA_VOLUME,dst=/data" \
  --entrypoint python \
  -e RESTORE_STAMP="$RESTORE_STAMP" \
  "$IMAGE_REF" \
  -c "import os; stamp=os.environ['RESTORE_STAMP']; current='/data/runtime.db'; os.replace(current, f'/data/runtime.db.failed-{stamp}'); os.replace(f'/data/runtime.db.pre-restore-{stamp}', current); [os.replace(f'/data/runtime.db.pre-restore-{stamp}'+s, current+s) for s in ('-wal','-shm') if os.path.exists(f'/data/runtime.db.pre-restore-{stamp}'+s)]; os.chown(current, 10001, 10001); print('pre-restore-db-restored=ok')"

docker compose --env-file .env -f compose.prod.yml start app
curl --fail http://127.0.0.1:8000/readyz
```

## 7. 镜像回滚

镜像回滚只切换版本标签，不删除或重建数据卷。必须使用不可变的版本标签；被反复覆盖的 `local` 或 `latest` 不能作为可靠回滚点。

### 7.1 回滚前

```bash
cd ~/zhugeshensuan
grep -E '^(IMAGE_NAME|IMAGE_TAG)=' .env
docker compose --env-file .env -f compose.prod.yml images
docker image inspect "zhugeshensuan:旧版本标签" --format 'id={{.Id}} version={{index .Config.Labels "org.opencontainers.image.version"}}'
```

若新版本改变了数据库 schema 或运行时数据格式，先执行第 4 节备份，并确认旧镜像是否需要配套的旧数据备份。不要把“切旧镜像”和“恢复旧数据库”混成一个不可撤销动作。

### 7.2 切换旧镜像

把服务器 `.env` 中的 `IMAGE_TAG` 改为已存在的旧版本标签，然后确认 Compose 解析结果：

```bash
docker compose --env-file .env -f compose.prod.yml config --images
docker compose --env-file .env -f compose.prod.yml up -d --no-build
docker compose --env-file .env -f compose.prod.yml ps
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
curl --fail https://getwiseoracle.com/readyz
```

`config --images` 必须显示预期旧标签。若 `--no-build` 报镜像不存在，先导入已留存的旧镜像 tar，不要临时从未知源码重建一个同名标签。

### 7.3 回滚失败

把 `.env` 的 `IMAGE_TAG` 改回刚才记录的原标签，再执行：

```bash
docker compose --env-file .env -f compose.prod.yml up -d --no-build
curl --fail http://127.0.0.1:8000/readyz
```

整个镜像回滚流程不得出现 `down -v` 或任何生产卷删除命令。代码镜像回滚不应改动已经上传的 Markdown 文章。

## 8. 每次操作的验收记录

每次备份、恢复或回滚至少记录：

- UTC 开始/结束时间和执行人。
- 操作前镜像标签及不可变 image ID。
- 数据卷名。
- 备份文件名、大小和 SHA-256；不得记录密钥或 `.env` 原文。
- `PRAGMA quick_check` 结果。
- 恢复前后需要核对的业务标记或表行数。
- `healthz`、`readyz` 和公网 `readyz` 结果。
- 回滚镜像标签及 image ID。
- 是否触碰生产卷、是否发生失败和撤回。

本地演练记录见 `docs/operations/ops-002-acceptance.md`。
