# 存活监控、日志排查与事故升级手册

- **适用站点：** `https://getwiseoracle.com/`
- **外部检查目标：** `https://getwiseoracle.com/readyz`
- **告警邮箱：** `5siwei@gmail.com`
- **文档日期：** 2026-07-16
- **当前状态：** 已完成；UptimeRobot monitor、公开 Operational 状态、Down 告警和恢复（UP）邮件均已验收
- **公开状态页：** `https://stats.uptimerobot.com/wOqljyqoWd`

## 1. 第一批监控的范围

第一批只建立一个站外 HTTP monitor：

| 字段 | 值 |
| --- | --- |
| Monitor type | HTTP(s) |
| Friendly name | `Wise Oracle production readiness` |
| URL | `https://getwiseoracle.com/readyz` |
| Monitoring interval | 5 分钟 |
| Alert contact | `5siwei@gmail.com` |
| 预期正常结果 | HTTP 200，JSON 含 `status=ready` |

2026-07-18 公开状态页核验结果：监控对象显示为 `getwiseoracle.com/readyz`，状态为
`Operational`，页面显示 `100.000%` uptime。该证据确认站外 monitor 已建立并正在工作，
项目所有者随后提供同屏截图，确认 `TEST: Monitor is DOWN` 和
`TEST: Monitor is UP` 两封邮件均已送达，目标均为 `getwiseoracle.com/readyz`；OPS-003
验收闭环完成。

选择 `readyz` 而不是首页，是因为它除了进程存活，还检查生产必填配置、reference/runtime SQLite 和 AI 使用策略数据库。这是“能不能正常接受业务请求”的保守信号，不代表 AI 上游的每一次请求都会成功。

UptimeRobot 官方定价页 `https://uptimerobot.com/pricing/` 在核对日期：2026-07-16 显示 Free 方案为 0 美元、50 monitors、5 分钟间隔，并支持 HTTP/port/ping 监控。套餐以后可能变化，创建时必须重新查看官方页面；本手册不承诺付费功能。

## 2. 项目所有者的创建步骤

账号创建、条款接受和邮箱确认必须由项目所有者完成。项目代码不保存 UptimeRobot 密码或 API key。

1. 打开 UptimeRobot 官网，用站长管理账号注册，完成 `5siwei@gmail.com` 邮箱确认并开启多因素验证。
2. 新建 HTTP(s) monitor，逐项填写上表的 friendly name、URL 和 5 分钟间隔。
3. 把 `5siwei@gmail.com` 选为 alert contact。不要把用户内容、生产密钥、Cookie 或 Authorization 放入 monitor 名称、URL、header 或备注。
4. 等待一个完整检查周期，确认 monitor 显示 Up，并从本地自行访问同一 URL 确认 HTTP 200。
5. 验证邮件通道。如当前界面提供通知联系人测试，先使用它；否则在预定窗口建一个临时 HTTP monitor，指向明确不存在的测试路径，收到 Down 后把 URL 改为公网 `readyz`，再确认告警邮件和恢复邮件都送达，最后删除临时 monitor。不为测试停掉生产容器。
6. 记录 monitor 名称、创建时间、检查间隔、告警与恢复邮件时间。截图前隐藏账号、monitor ID 和其他无关信息。

只有正式 monitor 显示 Up，且告警邮件和恢复邮件均验证成功，才能把外部存活监控标记为完成。在此之前不得声称 OPS-003 已完成。

## 3. 告警后的四层排查

先保存告警和当时的发布版本，再按以下顺序检查；不跳过源站直接改 DNS。

### 第 1 层：公网状态

在自己电脑执行：

```powershell
curl.exe --fail --show-error https://getwiseoracle.com/healthz
curl.exe --fail --show-error https://getwiseoracle.com/readyz
```

- 两者都成功：可能是短暂网络或单一监控节点故障；先看 UptimeRobot 后续检查和 Cloudflare 事件。
- `healthz` 成功、`readyz` 失败：进程还在，但配置、SQLite 或 AI 用量数据库未就绪，继续检查服务器。
- 两者都失败：可能是 Cloudflare/Tunnel、服务器、Docker 或网络问题，不根据单一现象下结论。

### 第 2 层：服务器本机和 Docker

SSH 登录服务器后，使用实际部署目录：

```bash
cd ~/zhugeshensuan
docker compose --env-file .env -f compose.prod.yml ps
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
curl --fail https://getwiseoracle.com/readyz
docker compose --env-file .env -f compose.prod.yml logs --tail=200 app
```

- 本机成功、公网失败：检查 Cloudflare Tunnel connector、Published application route 和 DNS，不重建正常容器。
- 本机 `healthz` 也失败：查看容器是否存在、启动循环、端口绑定和最新日志。
- 本机 `healthz` 成功但 `readyz` 失败：从 readiness 响应的脱敏 `checks` 和日志判断是配置还是数据库；不打印 `.env` 或密钥原文。

如需确认 Docker healthcheck 历史，只输出容器状态，不展开环境变量：

```bash
APP_CONTAINER="$(docker compose --env-file .env -f compose.prod.yml ps -q app)"
docker inspect "$APP_CONTAINER" --format '{{json .State.Health}}'
```

### 第 3 层：日志和请求关联

当前应用日志为 JSON，基础字段是 `time`、`level`、`logger`、`message`；异常时可另有 `exception`。请求结束日志的 `message` 内包含 method、path、HTTP status、耗时和 `request_id`，响应头也返回 `X-Request-ID`。当前请求日志不记录 query string 或请求体。

排查时：

1. 先按告警时间戳缩小范围，再查找 5xx、ERROR 和重复异常。
2. 如用户能提供响应头中的 `X-Request-ID`，只使用这个脱敏 ID 关联日志，不让用户重发占卜问题或出生资料。
3. 分享日志前删除堆栈中可能出现的本机路径、上游 URL 参数和任何意外的用户内容。
4. 现有 Compose 文件未在本任务中承诺集中日志或远程保留。在设计保留/轮转前，不将 Docker 本机日志当作永久审计记录。

### 第 4 层：发布和恢复路径

- 如故障在新部署后立即出现，记录 Git commit SHA、当前与上一个镜像标签，优先按已验证的镜像回滚路径恢复服务。
- 如 `runtime.db` 损坏或恢复后 readiness 失败，严格使用 `docs/operations/backup-restore-runbook.md`；不删除生产数据卷。
- 只在有当前备份、可追溯镜像和验收命令时做生产变更。恢复服务优先，根因修复可在服务稳定后完成。

## 4. 事故升级

| 级别 | 判定 | 立即动作 | 升级条件 |
| --- | --- | --- | --- |
| P1 服务不可用 | 公网 `readyz` 持续失败，或核心功能大面积 5xx | 保存告警时间和版本，完成四层排查；若与新版本同时出现则回滚 | 无服务器权限、无可用回滚镜像、数据库完整性失败，或 30 分钟内未恢复时联系服务器/应用专业人员 |
| P2 部分降级 | 站点可访问，但 AI 或单个工具重复失败 | 保留 request_id 和聚合错误数，查上游与配额；不收集用户原文 | 影响扩大、出现数据泄露迹象，或持续一个工作日时升级为专项故障 |
| P3 单次/观察项 | 短暂告警已自愈、单次 5xx 或统计异常 | 记录时间和证据，在每周复盘查看是否重复 | 重复出现或影响用户时提升为 P2 |

任何疑似密钥、用户输入、出生资料或 Cookie 泄露的情况都不按普通稳定性问题等待：立即保留脱敏证据，限制相关凭据/入口，轮换受影响凭据，并联系安全专业人员。不在 Issue 中公开原始样本。

## 5. 敏感数据禁传清单

无论是 UptimeRobot、Cloudflare、GitHub artifact/Issue，还是未来的日志或错误平台，均不得发送：

- 用户原始问题、签文请求、AI prompt、AI 原文或完整报告。
- 姓名、出生日期、出生时间、出生地点、命盘或可联合识别的个人资料。
- 完整请求体、query string、Cookie、Authorization、session/device ID 和未脱敏 IP。
- `.env`、API key、Cloudflare token、SSH 私钥、GitHub secret 或备份数据库。

可以保留的是：时间、环境、应用版本、路由模板、HTTP 状态码、耗时、错误类型、聚合计数和脱敏 request_id。

## 6. 第三方错误平台检查点

第三方错误上报平台默认关闭。当前第一批只使用现有 JSON 日志和存活监控，不自动上传异常、请求或用户内容。

任何 Sentry 或同类平台的后续启用，都必须先建立独立决策记录，并明确：

1. 服务商和数据区域，包括跨境传输。
2. 事件、堆栈、IP 和用户标识的保留期与删除方式。
3. 采样率、月度限额、费用上限和超额行为。
4. 服务端和客户端 scrubbing 规则，用测试事件证明请求体、Cookie、Authorization、用户原始问题、出生资料和 AI 原文已被删除。
5. 最小团队权限、多因素验证、密钥轮换和停用/导出流程。

未通过上述检查时，保持关闭，不因“排错更方便”就先把生产数据送到第三方。

## 7. 事故结束条件和记录

事故只在以下条件同时满足后关闭：

1. 本机和公网 `healthz`/`readyz` 恢复。
2. UptimeRobot 恢复连续检查并已发送恢复邮件。
3. 核心用户路径已做无敏感数据的冒烟测试。
4. 当前 Git commit/镜像、故障时间线、影响范围、修复/回滚动作和后续任务均已脱敏记录。

记录中不包含用户原文、出生资料、Cookie、Authorization、`.env` 或 AI 原文。
