# OPS-001 生产环境配置与域名/HTTPS 验收

**验收日期：** 2026-07-16
**正式域名：** `https://getwiseoracle.com`
**任务状态：** 已完成
**关联证据：** `docs/reviews/2026-07-16-seo-001-003-acceptance.md`、`docs/reviews/2026-07-16-trust-001-acceptance.md`

## 1. 完成定义

OPS-001 只有在以下各项同时满足时才能完成：

1. 正式域名可通过有效 TLS 访问，HTTP 和 `www` 入口统一跳转到 HTTPS apex，路径与查询参数不丢失。
2. 生产必填环境变量存在，公开值正确，密钥只核对存在性、不输出原文；Compose 配置可解析。
3. 首页、关键静态资源、sitemap、robots、404、`healthz` 和 `readyz` 符合生产契约。
4. 安全响应头存在，canonical/OG 不受请求 Host 污染，不泄漏 localhost 或占位域名。
5. AI 上游异常有稳定降级，不向用户返回内部异常细节。

## 2. 域名、HTTPS 与跳转

使用不跟随跳转和跟随跳转两种请求方式验收：

| 请求 | 首次响应 | `Location` / 最终地址 | 跳转次数 | TLS 校验 |
| --- | ---: | --- | ---: | ---: |
| `https://getwiseoracle.com/` | 200 | `https://getwiseoracle.com/` | 0 | 0 |
| `http://getwiseoracle.com/ask-oracle?source=ops001` | 301 | `https://getwiseoracle.com/ask-oracle?source=ops001` | 1 | 0 |
| `https://www.getwiseoracle.com/daily-almanac?source=ops001` | 301 | `https://getwiseoracle.com/daily-almanac?source=ops001` | 1 | 0 |
| `http://www.getwiseoracle.com/terms?source=ops001` | 301 | `https://getwiseoracle.com/terms?source=ops001` | 1 | 0 |

`ssl_verify_result=0`，说明客户端完成了证书链和主机名校验。所有旧入口均一次跳到正式 HTTPS origin，并保留原路径与查询参数。

## 3. 生产配置核对

本地真实 `.env` 与当前生产 Compose 按脱敏方式核对：

| 变量 | 结果 |
| --- | --- |
| `APP_ENV` | 已配置为 `production` |
| `APP_DEBUG` | 已配置为 `false` |
| `SITE_BASE_URL` | 已配置为 `https://getwiseoracle.com` |
| `CONTACT_EMAIL` | 已配置为 `5siwei@gmail.com` |
| `TRUSTED_PROXY_HOPS` | 已配置为 `1` |
| `SECRET_KEY` | 已配置；原文未输出 |
| `AI_API_KEY` | 已配置；原文未输出 |
| `AI_GLOBAL_DAILY_LIMIT` | 已配置为正整数；具体运营值不写入验收记录 |

`docker-compose --env-file .env -f deploy/compose.prod.yml config --quiet` 通过。生产配置测试覆盖无效 `SITE_BASE_URL`、无效/占位 `CONTACT_EMAIL`、弱 `SECRET_KEY`、缺失 AI key、缺失全局额度和 debug 开启等拒绝路径。

正式站 `/readyz` 返回 200，进一步证明当前运行实例已通过 AI key、全局额度、reference/runtime SQLite 与 AI 使用策略数据库的 readiness 检查。此结论来自应用公开检查行为，不读取或记录生产密钥。

## 4. 页面、静态资源与健康接口

| 路径 | HTTP | Content-Type / 结果 |
| --- | ---: | --- |
| `/` | 200 | `text/html; charset=utf-8` |
| `/static/css/wise_oracle.css` | 200 | `text/css; charset=utf-8`，32,319 bytes |
| `/static/js/wise_oracle_common.js` | 200 | `text/javascript; charset=utf-8`，7,108 bytes |
| `/sitemap.xml` | 200 | `application/xml; charset=utf-8` |
| `/robots.txt` | 200 | `text/plain; charset=utf-8` |
| `/ops001-not-found-8f4d9171` | 404 | 未知页面不是 soft-404 |
| `/healthz` | 200 | `status=ok`，版本 `4.1` |
| `/readyz` | 200 | `status=ready`，版本 `4.1` |

首页 canonical 与 `og:url` 均为 `https://getwiseoracle.com/`；响应中无 localhost 和 `.example`。SEO 与联系方式的更完整生产证据分别保存在关联验收记录中。

## 5. 安全响应头

正式首页确认返回：

- `Content-Security-Policy`: 默认和脚本仅允许同源；object 禁止；base/form/frame 均受限。
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options: SAMEORIGIN`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Cross-Origin-Opener-Policy: same-origin`

Cloudflare 当前未返回 `Strict-Transport-Security`。这不阻塞 OPS-001，因为 HTTP 强制跳转与 TLS 已通过；HSTS 属于可选的后续强化，启用前应先确认所有子域长期支持 HTTPS，避免错误配置造成浏览器长期锁定。

## 6. AI 超时/上游失败降级

未在生产环境制造真实上游故障或消耗用户配额。新增两条 mock 回归测试验证现有行为：

- 同步 `/api/en/birth-chart/analyze` 遇到上游超时返回 502 + `ANALYSIS_FAILED`，不泄漏内部异常文本。
- 流式 `/api/en/birth-chart/stream` 遇到上游超时保留基础盘事件，随后返回 `error_code=ANALYSIS_FAILED` 和 `done`，不泄漏内部异常文本。

`tests/test_birth_chart_english.py` 共 63/63 通过；生产环境无需为了验证失败路径而主动中断 AI 服务。

## 7. 质量门禁

| 检查 | 结果 |
| --- | --- |
| OPS 定向测试 | config/API/SEO URL/Birth Chart：100/100 通过 |
| 全量 pytest | 391/391 通过 |
| Black | 83 个 Python 文件通过 |
| Ruff | 全部通过 |
| JavaScript 语法 | 14/14 通过 |
| pip-audit | No known vulnerabilities found |
| Compose 配置 | 通过 |
| `git diff --check` | 通过；仅有 Git 的 CRLF 转换提示 |

## 8. 结论与后续

正式域名、HTTPS、生产配置、静态资源、健康/readiness、安全响应头和 AI 异常降级均满足 OPS-001 完成定义，任务标记为“已完成”。

OPS-001 完成后：

- OPS-002 可开始备份、恢复和镜像回滚演练。
- OPS-004 解除阻塞，可进行 Google Search Console 所有权验证与 sitemap 提交。
- OPS-003 已于 2026-07-18 完成：UptimeRobot 公开状态页、Down 告警和恢复（UP）邮件均已验收。

## 9. OPS-006 Cloudflare Web Analytics 验收

2026-07-16 已在下一发布版本中把脚本 CSP 从 `script-src 'self'` 精确调整为
`script-src 'self' https://static.cloudflareinsights.com`，并保持 `connect-src 'self'` 不变。
没有增加脚本 `'unsafe-inline'`、`'unsafe-eval'` 或通配域名。

历史上代码门禁通过时生产采集尚未完成；当时 `/cdn-cgi/rum` 的 GET 探测返回 404，且首页
源码未出现 Cloudflare beacon。2026-07-18 已完成以下生产验收：

1. 正式响应头包含最小 `script-src` 放行。
2. 浏览器实际加载 `beacon.min.js`。
3. Resource Timing 出现同源 `/cdn-cgi/rum?` 请求；没有依赖 GET 200 误判。
4. Cloudflare Web Analytics 显示 `getwiseoracle.com` Automatic setup，最近 24 小时
   7 page views、2 visits。
5. 没有增加额外 `connect-src`、`unsafe-inline` 或 `unsafe-eval`。

完整证据见 `docs/operations/ops-006-cloudflare-web-analytics-acceptance.md`；OPS-006 已完成。
