# 管理员统计 API

项目现在提供一个只读的管理员统计接口，用于查询 Cloudflare 边缘访问和
Google Search Console 搜索表现。接口不会把任何第三方 Token 返回到浏览器。

## 地址与认证

接口挂载在文章管理路径下。生产环境默认地址为：

```text
https://getwiseoracle.com/165131/analytics
https://getwiseoracle.com/165131/analytics/status
https://getwiseoracle.com/165131/analytics/overview
https://getwiseoracle.com/165131/analytics/search-console
```

先在 `https://getwiseoracle.com/165131` 输入文章管理密码，统计面板和接口复用同一个管理员
Session。没有设置 `ARTICLE_ADMIN_PASSWORD` 时，统计接口会返回 503，避免统计数据
意外公开。

打开不带后缀的 `/analytics` 地址可查看人类可读的统计面板；`overview` 和
`search-console` 是供面板及其他程序调用的 JSON 接口。

## 接口参数

`overview` 和 `search-console` 接受：

- `from=YYYY-MM-DD`：开始日期（包含）
- `to=YYYY-MM-DD`：结束日期（包含）
- 默认查询当前时区最近 30 天
- 单次最多查询 `ANALYTICS_MAX_RANGE_DAYS` 天，默认 31 天

示例：

```text
/165131/analytics/overview?from=2026-08-01&to=2026-08-31
/165131/analytics/search-console?from=2026-08-01&to=2026-08-31&dimensions=date,page
```

`overview` 返回：

- `totals`：筛选后的 GET 请求、Cloudflare visits、响应字节数
- `daily`：按 `Asia/Shanghai`（或 `DEFAULT_TIMEZONE`）汇总的每日数据
- `pages`：访问路径排名，排除了 `/static/`、`/api/`、`/cdn-cgi/`、健康检查和 sitemap
- `referrers`：来源网站；没有 Referer 的访问归入 `(direct or hidden)`
- `countries`：来源国家

这里的 `requests` 是边缘请求，不等同于点击；`visits` 使用 Cloudflare 的访问定义。
Cloudflare Free/Pro 计划的 HTTP Analytics API 通常只保留约 7 天历史数据；如果请求范围
更早，接口会返回可用日期的数据，并在 `notes` 中说明被跳过的日期。要查询更长的
Cloudflare 历史范围，需要升级计划或改用其他持久化日志来源。
如需 Google 搜索词、点击、展示、CTR 和平均排名，使用 `search-console` 接口。

## Cloudflare 配置

在 Cloudflare 控制台：

1. 进入右上角个人菜单 → **My Profile → API Tokens**，选择 **Create Token**。
2. 选择 **Custom token**。
3. 权限选择 **Account → Account Analytics → Read**。
4. Zone Resources 只选择 `getwiseoracle.com` 所在的 Zone。
5. 创建后只复制一次显示的 Token，并保存到服务器 `.env`。
6. 打开域名的 **Overview**，滚动到 API 区域，复制 **Zone ID**。

```dotenv
CLOUDFLARE_ANALYTICS_TOKEN=这里填Token
CLOUDFLARE_ZONE_ID=这里填ZoneID
CLOUDFLARE_ANALYTICS_HOSTNAME=getwiseoracle.com
```

不要把 Token 提交到 Git、文章、截图或前端代码中。

## Search Console 配置

项目采用 OAuth 2.0 refresh token。Google Search Console API 要求 OAuth 授权，且
调用账号必须对对应资源拥有读取权限。

1. 在 Google Cloud Console 创建一个项目。
2. 启用 **Google Search Console API**。
3. 配置 OAuth consent screen。
4. 创建 OAuth Client ID（Desktop app 或 Web application）。保存 Client ID 和
   Client Secret。
5. 用 OAuth 2.0 Playground 或自己的 OAuth 流程申请只读 scope：
   `https://www.googleapis.com/auth/webmasters.readonly`。
6. 同意访问后换取 refresh token，并确认该 Google 账号有
   `sc-domain:getwiseoracle.com` 的 Search Console 权限。

```dotenv
GSC_SITE_URL=sc-domain:getwiseoracle.com
GSC_CLIENT_ID=你的ClientID
GSC_CLIENT_SECRET=你的ClientSecret
GSC_REFRESH_TOKEN=你的RefreshToken
```

`GSC_ACCESS_TOKEN` 仅用于短期测试；它会过期，不应作为生产配置。

## 验证

部署后，先登录管理员页面，再访问：

```text
/165131/analytics/status
```

确认返回：

```json
{
  "cloudflare": {"configured": true},
  "search_console": {"configured": true}
}
```

随后访问 `overview`。如果 Cloudflare 返回查询错误，优先检查 Zone ID、Token 的
`Account Analytics: Read` 权限和 Zone Resources 范围；如果 Search Console 返回
403，检查 OAuth 账号是否被添加到对应资源。
