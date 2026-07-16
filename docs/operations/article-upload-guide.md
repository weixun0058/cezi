# 私密 URL 上传与发布 Markdown 文章

- **默认入口：** `https://getwiseoracle.com/165131`
- **适用设备：** 手机、平板、任意电脑浏览器
- **发布方式：** 直接上传服务器持久卷，即时生效
- **不需要：** GitHub、CI、重新构建镜像、重新部署网站

## 1. 第一次部署前配置

服务器 `~/zhugeshensuan/.env` 增加：

```env
ARTICLE_ADMIN_PATH=165131
ARTICLE_ADMIN_PASSWORD=你选择的访问密码
```

`ARTICLE_ADMIN_PATH` 必须是 6 位数字。密码可以使用便于自己输入的值；如果留空，访问正确 URL 后会直接进入上传页。修改路径或密码并重启容器，会让旧入口或旧登录 Cookie 失效。

Compose 把文章保存在独立卷 `zhugeshensuan_article-content`，容器内路径为 `/app/content/articles_en`。重新部署或回滚程序镜像不会删除文章。禁止执行 `docker compose down -v` 或手工删除该卷。

本批部署工件是 `zhugeshensuan-2026.07.16-article-upload.tar`，镜像标签为 `zhugeshensuan:2026.07.16-article-upload`。部署时必须把以下三份文件一起上传到服务器部署目录：

1. `zhugeshensuan-2026.07.16-article-upload.tar`；
2. 新版 `deploy/compose.prod.yml`，上传后命名为 `compose.prod.yml`；
3. 已设置 `IMAGE_TAG=2026.07.16-article-upload`、`ARTICLE_ADMIN_PATH=165131` 和管理密码的实际 `.env`。

`.env` 含真实密钥，只能通过 SSH/SCP 等安全方式传输，不得发到公开仓库或聊天中。三份文件上传完成后执行：

```bash
cd ~/zhugeshensuan
docker load -i zhugeshensuan-2026.07.16-article-upload.tar
docker compose --env-file .env -f compose.prod.yml up -d --no-build --force-recreate
docker compose --env-file .env -f compose.prod.yml ps
curl --fail http://127.0.0.1:8000/readyz
```

第一次启动时 Compose 自动创建 article-content 卷。不要把旧 `compose.prod.yml` 与新镜像混用，否则文章目录不会挂载为持久卷。

## 2. Markdown 文件格式

上传文件必须使用 UTF-8 编码，扩展名是 `.md`，文件名必须与 front matter 的 slug 完全一致。模板：

```markdown
+++
slug = "how-oracle-signs-work"
title = "How Oracle Signs Work"
description = "A concise cultural introduction to symbolic oracle readings."
published_at = "2026-07-16"
status = "published"
tags = ["oracle", "culture"]
source_notes = "Public sources or editorial note suitable for readers."
+++
# How Oracle Signs Work

Write the article in Markdown here.
```

本例文件名必须是 `how-oracle-signs-work.md`。不接受原始 HTML、图片、`javascript:`/`data:` 链接、非法日期、未知 metadata、draft 状态或超过 512 KiB 的文件。

## 3. 上传并立即发布

1. 在任意设备打开 `https://getwiseoracle.com/165131`。
2. 如已配置密码，输入密码进入页面。
3. 选择准备好的 `.md` 文件。
4. 新文章不要勾选覆盖；如果要更新同一个 slug，核对文件后勾选“确认覆盖原文章”。
5. 点击“上传并立即发布”。
6. 页面显示成功后，直接打开 `/articles/<slug>` 检查。文章列表和 sitemap 同时更新，不需要重启。

上传失败不会删除旧文章。常见错误会在页面直接指出：文件名/slug 不一致、格式错误、非 UTF-8、危险 Markdown、重复文章未确认覆盖等。

## 4. 打包下载全部文章

进入管理页面后点击“打包下载全部文章”。浏览器会下载形如：

```text
getwiseoracle-articles-20260716-120000Z.zip
```

ZIP 只包含按 slug 排序的原始 `.md` 文件，不包含 `.env`、数据库、日志、密钥或用户数据。可以在手机或电脑保存这个 ZIP 作为人工副本；服务器仍应按照部署指南和 OPS-002 手册备份文章卷。

## 5. 更换入口或密码

编辑服务器 `.env`：

```bash
cd ~/zhugeshensuan
nano .env
docker compose --env-file .env -f compose.prod.yml up -d --no-build --force-recreate
```

- 更换 `ARTICLE_ADMIN_PATH`：旧 URL 立即失效，新 URL 使用新的 6 位数字。
- 更换 `ARTICLE_ADMIN_PASSWORD`：旧签名 Cookie 失效，需要输入新密码。
- 留空密码：只凭 URL 进入。此方式符合“没有机密内容”的低门槛需求，但知道 URL 的人也能上传和覆盖文章。

管理页不出现在网站导航、robots 或 sitemap，并返回 `noindex`/`no-store`。但 6 位 URL 不是强认证；如发现异常文章，先修改路径和密码并重启，再从下载 ZIP 或服务器备份恢复正确版本。

服务器首次配置、镜像更新和 Compose 命令见 `docs/部署指南.md`；文章卷备份与恢复使用 `docs/operations/backup-restore-runbook.md`（OPS-002）。
