# 服务器私密文章上传与站长管理实施方案

**状态：** 本地实施完成，等待生产部署与跨设备验收
**默认入口：** `https://getwiseoracle.com/165131`
**目标：** 站长从手机或任意电脑上传准备好的 Markdown，文章立即发布；日常文章发布与 GitHub、CI、镜像构建和整站部署解耦。

## 1. 已确认的产品口径

1. 不要本机编辑器，不限制只能在某台电脑工作。
2. 不把文章提交 GitHub，不让每篇文章触发测试、镜像构建和重新部署。
3. 站长访问一个没有公开链接的 6 位数字 URL；默认后缀为 `165131`。
4. 页面可配置简单访问密码。没有用户注册、角色、数据库账号或第三方登录。
5. 页面只负责上传已经编辑好的 `.md`、明确覆盖同名文章、显示当前文章和打包下载全部 Markdown。
6. 上传成功后，文章列表、详情页和 sitemap 立即更新。

## 2. 架构

```text
浏览器（手机/任意电脑）
  -> Cloudflare HTTPS
  -> Flask /<ARTICLE_ADMIN_PATH>
  -> ARTICLE_ADMIN_PASSWORD 服务器核对
  -> Flask 签名 Session Cookie + CSRF
  -> Markdown schema 校验
  -> /app/content/articles_en/.upload-*.tmp
  -> fsync + os.replace
  -> 当前 worker reload
  -> 其他 worker 下一请求检测目录指纹
  -> /articles、详情、sitemap 即时可见

文章持久化：Docker named volume article-content
程序发布：继续使用现有代码 CI 与手工 Docker 部署
两条路径互不依赖
```

## 3. 配置

### 应用环境变量

| 变量 | 生产值/规则 | 用途 |
| --- | --- | --- |
| `ARTICLE_ADMIN_PATH` | 默认 `165131`，必须 6 位数字 | 管理 URL 后缀；改值并重启使旧 URL 失效 |
| `ARTICLE_ADMIN_PASSWORD` | 简单站长密码，可留空 | 非空时服务器核对并签发 Cookie；改值使旧 Cookie 失效 |
| `ARTICLES_PATH` | `/app/content/articles_en` | 持久化 Markdown 目录 |
| `SECRET_KEY` | 既有 32+ 字符生产密钥 | 签名 Session/CSRF 状态，不保存密码原文到 Cookie |

### Cookie 与页面响应

- `HttpOnly=true`
- 生产 `Secure=true`
- `SameSite=Strict`
- 管理响应：`X-Robots-Tag: noindex, nofollow, noarchive`
- `Cache-Control: no-store`
- `Referrer-Policy: no-referrer`
- 管理路径不出现在导航、robots 或 sitemap

## 4. 上传契约

上传只接受：

- 单个 `.md` 文件；UTF-8/UTF-8 BOM。
- 最大 512 KiB。
- TOML front matter 使用 `+++` 包围。
- `slug/title/description/published_at/status/tags` 必填。
- 文件名必须为 `<slug>.md`。
- 管理上传要求 `status = "published"`。

继续拒绝：原始 HTML、图片、危险/未知链接 scheme、未知 metadata、控制字符、非法日期/slug、空正文和超限字段。

同名文章默认返回 409 并保留旧文件；只有上传表单勾选覆盖才原子替换。写入使用同卷临时文件、flush、`fsync` 和 `os.replace`。失败路径删除临时文件并恢复旧内容。

## 5. 多 worker 即时生效

Gunicorn 当前可运行多个 worker，不能只修改上传请求所在进程的内存。`ArticleRepository` 为文章目录计算 `(filename, mtime_ns, size)` 指纹：

- 上传 worker 原子写入后立即 reload。
- 其他 worker 在下一次 `list_public/get_public` 时比较指纹；发生变化才重新验证目录。
- 没变化时只做小目录 stat，不重复 Markdown 渲染。
- 任一无效文章仍会被拒绝，不以“热更新”为由绕过 schema。

## 6. ZIP 导出

管理页授权后可请求 `/<path>/articles.zip`：

- 文件名为 `getwiseoracle-articles-<UTC>.zip`。
- 只包含文章卷根目录下按 slug 排序的 `.md`。
- 不包含 `.env`、runtime.db、日志、Cookie、密钥或用户数据。
- ZIP 是站长人工副本；生产恢复仍以 article-content 卷备份为准。

## 7. Docker 与备份

Compose 新增：

```yaml
volumes:
  - runtime-data:/app/instance
  - article-content:/app/content
```

镜像预建 `/app/content/articles_en` 并归属非 root UID/GID `10001:10001`，因此只读 rootfs 下仍能写文章卷。镜像回滚不能删除文章卷，也不会自动撤回文章。

OPS-002 与部署指南同步增加：

- `zhugeshensuan_article-content` tar.gz + SHA-256。
- 临时卷解压、当前镜像加载、列表/详情/sitemap 验证。
- 禁止 `docker compose down -v`。

## 8. 已删除的错误实现

以下内容因偏离需求而删除，不保留为备用发布方式：

- `tools/article_editor/`
- `scripts/run_article_editor.ps1`
- `scripts/publish_article.py`
- `.github/workflows/publish.yml`
- `deploy/promote_image.sh`
- 对应编辑器、Git 发布和 workflow 测试
- “本机编辑器 + GitHub 自动发布文章”操作手册

GitHub 既有 `.github/workflows/ci.yml` 仍只负责程序代码质量，不参与日常文章。

## 9. 测试与验收

### 自动化

- 服务器密码正确/错误、锁定状态和直接 POST 绕过。
- CSRF、Secure/HttpOnly/SameSite、noindex/no-store/no-referrer。
- UTF-8、扩展名、大小、schema、危险 Markdown。
- 新文章即时发布、同名覆盖确认、失败保留旧文件。
- 两个 ArticleRepository 实例模拟两个 worker，下一请求发现新文件。
- ZIP 内容精确，仅含 Markdown。
- Compose 独立卷、Dockerfile 权限和环境变量契约。
- 原文章路由、SEO、sitemap 与全量回归。

### Docker

1. 构建生产镜像。
2. 使用只读 rootfs、非 root 用户、runtime 和 article-content 两个隔离卷启动。
3. 登录 `/165131`，上传测试 Markdown。
4. 不重启容器，确认列表、详情、sitemap 立即出现。
5. 覆盖同 slug 并确认正文立即变化。
6. 下载 ZIP 并核对文件。
7. 重建容器但复用 article-content 卷，确认文章仍存在。
8. 删除本次隔离容器/卷；不接触生产资源。

### 生产（待项目所有者）

1. 在服务器 `.env` 设置 `ARTICLE_ADMIN_PATH=165131` 和访问密码。
2. 上传新镜像和 Compose，确认两个 named volume。
3. 从手机或另一台电脑登录。
4. 上传测试文章、覆盖更新、下载 ZIP。
5. 确认没有 GitHub workflow、Docker build 或重部署发生。
6. 做首次真实文章卷备份后，才能标记生产验收完成。

## 10. 回滚

- 管理页代码故障：回滚应用镜像，保留 article-content 卷。
- 异常文章：上传同 slug 的正确 Markdown并勾选覆盖；或从 ZIP/卷备份恢复。
- URL 泄露：修改 `ARTICLE_ADMIN_PATH` 和密码，重启容器。
- 密码遗忘：服务器修改 `.env`，不需要数据库重置。
- 文章卷损坏：按 OPS-002 在隔离卷验证备份后恢复，不直接删除生产卷。
