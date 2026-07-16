# ADR-2026-07-16：服务器私密 URL 上传并即时发布 Markdown 文章

## 状态

已接受。取代“本机编辑器 + GitHub 自动发布文章”的错误方案。

## 背景与真实需求

项目所有者需要在手机、其他电脑或任何地点上传已经编辑好的 Markdown 文件。文章发布不能依赖本机项目目录、GitHub 网络、CI、镜像重建或整站重新部署。目标流程必须是：访问仅项目所有者知道的 URL，输入一个简单访问密码，选择 `.md` 文件并上传，文章立即进入网站列表、详情页和 sitemap。

## 决策

1. 管理入口默认是 `https://getwiseoracle.com/165131`，后缀由服务器环境变量 `ARTICLE_ADMIN_PATH=165131` 提供，可通过改值使旧链接失效。
2. 页面不加入导航、页面内链、robots 或 sitemap。管理响应统一设置 `X-Robots-Tag: noindex, nofollow, noarchive`、`Cache-Control: no-store` 和 `Referrer-Policy: no-referrer`。
3. 不建立用户系统。项目所有者提交 `ARTICLE_ADMIN_PASSWORD` 后，服务器比较密码并写入由 Flask `SECRET_KEY` 签名的 HttpOnly、Secure、SameSite=Strict Cookie。只做前端密码判断的方案被拒绝，因为攻击者可以绕过页面直接调用上传接口。
4. 上传只接受 UTF-8 `.md`，使用现有 TOML front matter + Markdown schema；必须为 `status = "published"`。原始 HTML、图片、危险链接、非法 slug/日期/字段和超限内容继续拒绝。
5. 文件原子写入独立 Docker volume 的 `/app/content/articles_en`。同 slug 已存在时必须显式勾选覆盖。上传后当前 worker 立即重载；其他 Gunicorn worker 在下一请求通过目录指纹自动发现变化。
6. 页面显示文章数量与当前文章清单，并提供“下载全部文章”按钮。下载内容是按 slug 排序的全部原始 `.md` 文件 ZIP，不包含数据库、密钥、日志或用户内容。
7. GitHub 仅管理程序代码。日常文章上传不触发 Git commit、GitHub Actions、Docker build 或部署。

## 数据流

```text
手机/任意电脑
  -> HTTPS /165131
  -> 简单密码（服务器核对，签名 Cookie）
  -> 选择 Markdown + 可选覆盖确认
  -> schema 安全校验
  -> 同卷临时文件 + fsync + os.replace
  -> ArticleRepository 重载
  -> /articles、详情、sitemap 立即可见

“下载全部文章”
  -> 再次验证签名 Cookie
  -> 只读打包 /app/content/articles_en/*.md
  -> ZIP 下载
```

## 非功能边界

- 单文件上限 512 KiB；不支持图片、附件、富文本、批量上传、在线编辑或删除。
- 所有写入在文章持久卷内完成，路径不可穿越；临时文件与最终文件在同一目录，保证原子替换。
- 上传失败保留旧文章；无半文件状态。覆盖成功前不删除旧文件。
- 文章卷需要纳入服务器备份；管理页 ZIP 是人工导出手段，不取代服务器卷备份。
- 密码或 URL 泄露时，修改 `.env` 中相应值并重启应用即可使旧 Cookie 和旧入口失效。

## 替代方案

### 本机编辑器 + GitHub 自动发布

已否决。它限制设备和地点，每篇文章依赖 GitHub、CI、镜像构建与整站部署，故障面和操作成本过高。

### 纯前端密码拦截

已否决。前端代码和接口地址对访问者可见，无法阻止直接 POST 篡改文章。采用一次服务器密码核对和签名 Cookie，使用体验仍然只有一个密码框。

### Cloudflare Access

暂不采用。安全性更高，但增加第三方登录和配置依赖；当前内容管理风险不需要该复杂度。

## 后果

优点是跨设备、即时发布、与 GitHub 和部署完全解耦，且文章可独立备份。代价是生产容器第一次需要增加文章持久卷和环境变量；管理员 URL 只有六位数字，因此真正的写入保护依赖服务器密码，不能把“没有公开链接”等同于安全认证。
