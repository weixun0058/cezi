# 站长管理手册

- **适用站点：** `https://getwiseoracle.com/`
- **站长联系邮箱：** `5siwei@gmail.com`
- **文档日期：** 2026-07-16
- **目的：** 用已有的外部控制台和服务器工具管理网站，同时保留完整发布、告警和恢复证据

## 1. 你需要的不是一个“万能后台”

当前站点的管理能力分布在几个工具中：搜索表现在 Google Search Console，访问和边缘安全在 Cloudflare，代码与发布在 GitHub，存活告警在 UptimeRobot，真实运行状态在服务器 Docker，备份和恢复则有独立 runbook。

这个分工比把搜索数据、部署密钥和服务器控制全部塞进一个公开后台更容易管理边界。私密文章上传页只负责正式 Markdown 的上传、覆盖和导出，不替代这些站长工具。

## 2. 管理入口与用途

| 入口 | 主要看什么 | 当前状态 | 不在这里做什么 |
| --- | --- | --- | --- |
| Google Search Console | 收录、搜索展示、点击、关键词、页面索引和 sitemap | 网域所有权已验证；sitemap 状态成功；首页已编入 Google 索引 | 不看实时服务存活，不把收录等同于排名保证 |
| Cloudflare Analytics & Logs | 总访问、请求趋势、边缘响应、缓存与安全事件 | 已完成 Web Analytics/CSP 生产验收；Automatic setup 与非零数据均已确认 | 不依赖用户级跟踪；Logs 的粒度和保留期取决于当前套餐，不假定付费功能已开通 |
| 私密文章上传页 | 从手机或任意电脑上传 Markdown、覆盖更新、下载全部文章 ZIP | 默认入口 `/165131`；文章写入独立持久卷并立即生效 | 不经过 GitHub，不重新构建或部署网站；不上传 `.env`、数据库或用户数据 |
| GitHub Actions | 程序代码测试和代码版本记录 | CI 已有；不参与日常文章发布 | 不在 workflow 或日志中显示 production secret |
| UptimeRobot | 从站外每 5 分钟访问公网 `readyz`，下线和恢复时发邮件 | 已完成；公开状态、Down 和恢复邮件均已验收 | 不发送请求体，不监控带出生资料或占卜问题的 URL |
| Docker health/readiness | 容器、本机 `healthz`/`readyz`、应用 JSON 日志 | 生产 Compose 已配置 readiness healthcheck | 不先猜 Cloudflare 或 Google 故障；它是源站真相入口 |
| OPS-002 备份/恢复 | `runtime.db` 与文章卷备份、校验、隔离恢复和镜像回滚 | runtime 本地安全演练已完成；文章卷已加入手册；首次真实生产备份仍需服务器操作者执行 | 不删除任何生产数据卷，不运行 `down -v` |

Search Console 的已验收证据见 `docs/operations/search-console-acceptance.md`。备份、恢复和回滚必须使用 `docs/operations/backup-restore-runbook.md`，不根据本页的概要自行编写生产命令。

## 3. 登录与权限原则

1. Google、Cloudflare、GitHub 和 UptimeRobot 均开启多因素验证；恢复码保存到密码管理器的独立条目。
2. 不共享主账号密码。如需专业人员协助，优先使用平台成员/角色权限，工作结束即撤销。
3. GitHub CI secret、服务器 SSH 私钥、Cloudflare Tunnel token、AI key、文章访问密码和 `.env` 只存在各自的安全边界中，不贴到 Issue、PR、文档、聊天或截图。
4. 请求支持或事故排查时，只分享时间范围、响应码、脱敏的 request_id、聚合数据和已删除用户内容的日志片段。

## 4. 例行管理节奏

### 每日：只处理告警

- 查看 `5siwei@gmail.com` 是否收到 UptimeRobot 下线或恢复邮件。未收到告警时不必每日手工登录所有平台。
- 有告警时按 `docs/operations/monitoring-runbook.md` 的顺序分辨公网、Cloudflare Tunnel、容器和依赖故障。
- 不在没有现场备份和回滚点时边查边升级。

### 每周：一次 20–30 分钟运营复盘

1. **Search Console：** 比较过去 7 天的展示、点击、查询和页面；查看索引和 sitemap 是否出现新错误。数据量小时不做排名结论。
2. **Cloudflare：** 查看请求趋势、国家/地区、响应码和安全事件；核对突增是真实流量、搜索爬虫还是异常请求。
3. **GitHub：** 查看 Actions / Deployments 最后一次成功版本、失败任务和当前生产镜像 SHA；不把未执行的 workflow 当作已发布。
4. **日志：** 检查最近的 5xx、重复异常和高延迟，只保留聚合结果和脱敏样本。
5. **文章：** 通过私密上传页发布后，检查文章 URL 和 sitemap；定期点击“打包下载全部文章”保存副本，并用 Search Console 观察展示和查询。不要因一周波动频繁改标题。

### 每月：可恢复性、依赖与成本

1. 按 OPS-002 手册确认真实生产备份存在、SHA-256 和 SQLite `quick_check` 通过；在隔离卷做恢复抽查，不用生产卷测试。
2. 执行项目依赖安全审计，评估负责人、修复版本、回归范围和回滚方案，不在生产服务器盲目升级。
3. 对照 Cloudflare、GitHub、服务器、域名、AI 上游的账单和配额；对 AI 只记录聚合用量和成本，不保留原始问题或 AI 原文。
4. 复核管理平台成员、多因素验证、恢复方式和不再需要的权限。

## 5. 运营数据的正确理解

- Search Console 告诉你 Google 搜索里发生了什么，不是全站实时访问统计。
- Cloudflare 告诉你经过边缘网络的请求和安全趋势；Web Analytics 验收后再补充页面访问视角。
- UptimeRobot 告诉你“站外能不能完成 readiness 请求”，它不解释故障根因。
- Docker 和应用日志用来找根因；GitHub 发布记录用来判断故障是否与新版本同时出现。
- 一个工具的数字与另一个工具不同并不必然是错误：统计口径、时区、爬虫、拦截和采样都可以导致差异。

## 6. 不得上传或粘贴的数据

下列内容不得上传到 Search Console、Cloudflare 支持工单、GitHub Issue/Actions artifact、UptimeRobot、未批准的第三方错误平台或公开聊天：

- 用户的原始问题、签文请求或 AI 原文。
- 姓名、出生日期、出生时间、出生地点和完整八字/命盘。
- Cookie、Authorization header、会话/设备标识、IP 明文和完整请求体。
- `.env`、API key、SSH 私钥、Cloudflare token、DNS 验证值和 GitHub secret。
- 不应公开的文章草稿、内部编辑备注和业务数据；管理页只上传准备正式发布的 Markdown。

必须寻求外部帮助时，先复制到本地文本，删除上述字段，再检查截图边缘、浏览器地址栏和终端历史中是否有敏感值。

## 7. 站长最小记录

每次发布或事故只需保留以下脱敏记录：

- 开始/结束时间和执行人。
- Git commit SHA、不可变镜像标签与当时的生产版本。
- 受影响的公开 URL、HTTP 状态码和脱敏 request_id。
- 做了哪些检查、是否回滚、`healthz`/`readyz` 结果。
- 备份文件名、大小、SHA-256 和 `quick_check`；不记录备份内容。

真实故障的具体排查和升级步骤见 `docs/operations/monitoring-runbook.md`。
