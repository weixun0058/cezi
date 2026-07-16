# ART-001/002 服务器文章上传与站长管理纠偏验收

- **验收日期：** 2026-07-16
- **本地工程状态：** ART-001、ART-002 已按纠正后的方案完成
- **生产状态：** 待部署新镜像与 Compose，并由项目所有者做跨设备验收
- **默认私密入口：** `https://getwiseoracle.com/165131`

## 1. 纠偏结论

此前实现的“本机编辑器 + GitHub 自动发布文章”不符合项目所有者需求：它限制只能在特定电脑编辑，并让每篇文章依赖 GitHub 网络、CI、镜像构建和整站部署。该方案已废止，不作为备用路径保留。

已删除：

- `tools/article_editor/`
- `scripts/run_article_editor.ps1`
- `scripts/publish_article.py`
- `.github/workflows/publish.yml`
- `deploy/promote_image.sh`
- 上述功能的测试和错误操作手册

GitHub 只继续管理程序代码，日常 Markdown 文章不提交 Git、不触发 Actions、不构建镜像、不重新部署。

## 2. 实际交付

### 跨设备管理入口

- 默认路径 `/165131`，由 `ARTICLE_ADMIN_PATH` 控制，生产只接受 6 位数字。
- 不进入导航、robots 或 sitemap。
- 页面响应含 `noindex, nofollow, noarchive`、`no-store` 和 `no-referrer`。
- `ARTICLE_ADMIN_PASSWORD` 非空时显示一个简单密码框；没有账号系统、用户数据库或第三方登录。
- 密码由服务器比较并签发 Flask 签名 Cookie。纯前端拦截被拒绝，因为它不能阻止直接 POST 篡改文章。
- 修改路径或密码并重启容器会使旧入口或旧 Cookie 失效。

### 上传与即时生效

- 只接受 UTF-8 `.md`，最大 512 KiB。
- 使用既有 TOML front matter + Markdown schema，管理上传只允许 `status = "published"`。
- 原始 HTML、图片、危险链接、非法字段/slug/日期、文件名不一致等继续拒绝。
- 同 slug 默认 409，必须勾选确认覆盖。
- 使用同卷临时文件、`fsync` 和 `os.replace` 原子替换；失败保留旧文章。
- 当前 Gunicorn worker 上传后立即 reload；其他 worker 下一次请求通过目录指纹发现变化。
- 列表、详情、canonical、Open Graph、JSON-LD 和 sitemap 无需重启立即更新。

### 文章 ZIP

授权页面提供“打包下载全部文章”，ZIP 只包含按 slug 排序的原始 `.md`。不包含 `.env`、数据库、日志、密钥、Cookie 或用户数据。

### 持久化与备份

- runtime 数据：`zhugeshensuan_runtime-data` → `/app/instance`
- 文章数据：`zhugeshensuan_article-content` → `/app/content`
- 应用仍使用只读 rootfs 和非 root `10001:10001`；两个 named volume 可写。
- Dockerfile 预建并授权 `/app/content/articles_en`。
- 部署指南与 OPS-002 已加入文章卷备份、SHA-256、隔离恢复和禁止 `down -v` 规则。

## 3. 自动化验收

`tests/test_article_admin.py` 覆盖：

- 密码正确/错误、锁定态、未经授权直接 GET/POST。
- CSRF、管理页面安全响应头、URL 不进入 sitemap/robots。
- 新文章上传后列表/详情/sitemap 立即出现。
- 两个 `ArticleRepository` 实例模拟多 worker 自动刷新。
- 扩展名、UTF-8、大小、schema、draft、危险 HTML。
- 同名覆盖必须明确确认，拒绝时旧文件不变。
- ZIP 文件名与内容精确，不包含其他数据。
- `ARTICLE_ADMIN_PATH` 可更换，旧入口 404。
- Compose 独立文章卷、Dockerfile 目录权限和环境变量。

最终质量门禁：

| 检查 | 结果 |
| --- | --- |
| 全量 pytest | 448 passed；`ResourceWarning` 与 `PytestUnraisableExceptionWarning` 均升级为错误 |
| Black | 89 个 Python 文件通过 |
| Ruff | 全部通过 |
| pip-audit | No known vulnerabilities found |
| JavaScript | `frontend/static/js/**/*.js` 14/14 通过 `node --check` |
| Compose | `docker-compose --env-file .env -f deploy/compose.prod.yml config --quiet` 通过 |
| Git diff | `git diff --check` 通过；仅有 LF/CRLF 提示 |

## 4. Docker 验收

构建结果：

- 镜像：`zhugeshensuan:2026.07.16-article-upload`
- image ID：`sha256:077d7e40b6d62768b5bb91483c40ef3b77450bcd9491a6ad3abc35654b97b5e6`
- version label：`server-article-upload-poetry-rtl`
- 部署 tag：`zhugeshensuan:2026.07.16-article-upload`
- 导出文件：`zhugeshensuan-2026.07.16-article-upload.tar`（122,730,496 bytes）
- tar SHA-256：`27403E6DD1F801E2C8DD015BE6C3F8663BC28878E17F32342B6B58AAB478B81A`

该最终交付镜像同时包含 UI-001 中文定场诗右起竖排修复；镜像内 `/readyz`、算事、论命、黄历均为 200，桌面和移动 CSS 均确认包含 `row-reverse`。详细证据见 `docs/reviews/2026-07-16-chinese-poetry-direction-acceptance.md`。

隔离 Docker 验收通过：

1. 非 root `10001:10001`、只读 rootfs、独立 runtime/article-content 卷启动。
2. `/readyz` 200。
3. 错误密码 403，正确密码 303 到管理页。
4. 上传测试 Markdown 返回 303；不重启，详情 200、列表和 sitemap 立即出现。
5. 未勾选覆盖返回 409 且旧标题保留；勾选后返回 303，新标题立即出现。
6. ZIP 下载 200 且只含测试 Markdown。
7. 删除容器、复用两个卷创建新容器，更新后的文章仍为 200，证明文章不依赖原容器或镜像层。
8. 桌面 1440×1000 和移动 390×844 页面完成浏览器视觉检查。
9. 验收后隔离容器、卷、Cookie、ZIP、截图和临时 Markdown 均已删除；未接触生产资源。

## 5. 生产待验收

项目所有者部署时需要：

1. 服务器 `.env` 设置 `ARTICLE_ADMIN_PATH=165131` 和自选访问密码。
2. 上传本镜像和新 `compose.prod.yml`，确认 `runtime-data` 与 `article-content` 两个卷存在。
3. 从手机或另一台电脑访问 `/165131`。
4. 真实执行新文章上传、同 slug 覆盖和全部文章 ZIP 下载。
5. 确认整个过程没有 GitHub workflow、Docker build 或容器重启。
6. 按 OPS-002 生成第一次真实文章卷备份。

完成这些证据前，服务器文章上传能力只能标记为“本地完成、待生产验收”；ART-003 内容写作可以准备，但不应把首批文章只留在尚未备份的生产卷中。
