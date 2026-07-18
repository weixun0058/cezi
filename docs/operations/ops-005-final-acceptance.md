# OPS-005 上线后统一全量验收记录

- **验收日期：** 2026-07-18
- **正式站点：** `https://getwiseoracle.com`
- **任务：** OPS-005 执行上线后统一全量验收
- **结论：** 已完成

## 1. 验收口径

本记录不重新制造生产故障，也不重复消耗 AI 配额，而是汇总已经完成的专项验收、
最新 CI、生产站检查、隔离 Docker 演练和外部监控证据。历史记录中的测试数量随代码增长
而变化；最终自动化基线以提交 `44f6925` 对应的 GitHub Actions run 20 为准。

完成条件是：P0-P1 的 SAFE、SEO、TRUST 与 OPS 前置项均完成；最新代码门禁和生产
Docker 冒烟通过；桌面/移动、AI 失败降级、备份恢复、镜像回滚及站外告警均有可追溯证据。

## 2. 统一验收矩阵

| 范围 | 结果 | 证据 |
| --- | --- | --- |
| 内容安全 | 通过 | SAFE-003/004：74/74 个批准字段写回，黄历医疗分类删除，法律提示进入 API 和页面；1440×900、390×844 验收通过 |
| 正式域名与 HTTPS | 通过 | apex HTTPS、HTTP/`www` 单次 301、路径和 query 保留、TLS 校验通过 |
| 生产配置与安全头 | 通过 | 生产必填配置、可信 URL、CSP、nosniff、Referrer/Frame/Permissions/COOP 策略均已验收；密钥只核对存在性 |
| 健康与就绪 | 通过 | 正式站 `/healthz`、`/readyz` 为 200；最新独立双卷生产 Docker 冒烟同样通过 |
| SEO 与公开路由 | 通过 | canonical、hreflang、Open Graph、JSON-LD、sitemap、robots、未知文章 404 和 Search Console 均通过；文章上线后 sitemap 动态增至 11 URL |
| 联系方式与信任页 | 通过 | Contact/Privacy/Terms/Disclaimer 使用真实邮箱，无 `.example`；Cloudflare 邮箱保护可还原，实际收信成功 |
| 桌面与移动浏览器 | 通过 | 正式站 1440×900、390×844 无横向溢出或 JS exception；中文三页 1280/390 坐标证明定场诗右起竖排 |
| AI/API 失败降级 | 通过 | 受控 mock 超时下，同步 API 返回稳定 `ANALYSIS_FAILED`；流式 API 保留基础盘并正常结束，不泄漏内部异常；未中断生产 AI |
| 备份与恢复 | 通过 | 隔离卷备份 SHA-256、SQLite `quick_check=ok`、快照语义及恢复卷 readiness 均通过；生产卷未挂载或删除 |
| 镜像回滚 | 通过 | 当前镜像与不同 image ID 的旧镜像均成功挂载隔离恢复卷并通过 `/readyz`；回滚不删除数据卷 |
| 外部监控 | 通过 | UptimeRobot 每 5 分钟检查公网 `readyz`；公开状态页 Operational、100% uptime；Down 与恢复（UP）邮件均已送达 |
| 最新 CI 与质量门禁 | 通过 | 提交 `44f6925` 对应 GitHub Actions run 20 成功；pytest 450/450、Black、Ruff、14/14 JavaScript、pip-audit 和独立双卷 Docker 冒烟通过 |

## 3. 关键专项记录

- `docs/reviews/2026-07-15-safe-003-004-acceptance.md`
- `docs/reviews/2026-07-16-seo-001-003-acceptance.md`
- `docs/reviews/2026-07-16-trust-001-acceptance.md`
- `docs/reviews/2026-07-16-chinese-poetry-direction-acceptance.md`
- `docs/reviews/2026-07-16-art-001-002-site-management-acceptance.md`
- `docs/operations/production-acceptance.md`
- `docs/operations/ops-002-acceptance.md`
- `docs/operations/search-console-acceptance.md`
- `docs/operations/monitoring-runbook.md`
- `docs/operations/backup-restore-runbook.md`

## 4. 失败、断网与恢复边界

验收没有为了取证而关闭正式网站或真实 AI 上游。应用失败路径由受控 mock 测试覆盖，
站外告警由临时失败目标触发 Down 后恢复到公网 `readyz` 验证。这样同时证明了应用降级和
邮件告警闭环，且不制造用户可见停机。

数据恢复和镜像回滚使用严格隔离的临时卷；演练没有连接、挂载、覆盖或删除生产数据卷。
事故时应继续遵循监控与备份手册，不把本次验收记录当作可以跳过现场备份的授权。

## 5. 非阻塞遗留项

以下事项不推翻 OPS-005，也不阻塞网站继续运行：

1. **OPS-006（已于 2026-07-18 完成）：** 生产 CSP、beacon、同源 RUM 请求及 Cloudflare 后台非零统计均已验收，见 `docs/operations/ops-006-cloudflare-web-analytics-acceptance.md`。
2. **GOV-003（已于 2026-07-18 完成）：** 历史源码提交、镜像标签和导出 tar SHA-256 的映射见 `docs/operations/release-provenance.md`。
3. **真实生产备份（已于 2026-07-18 完成首次快照）：** runtime 与文章卷的公开验收结论见 `docs/operations/2026-07-18-production-backup-acceptance.md`；精确文件名、大小和 SHA-256 仅保留在服务器侧，加密异机副本属于持续运维。
4. **文章写入链路：** 从手机/其他电脑补一次登录上传、同 slug 覆盖拒绝/确认和 ZIP 下载记录。
5. **可选增强：** HSTS 与合格的 1200×630 `og:image` 仍未启用；启用前应独立验收。
6. **持续运营：** 文章数量不设硬性门槛；指标、四周复盘和商业化继续按台账独立推进。

## 6. 本次汇总后的验证

项目所有者安装 `requirements-dev.txt` 后，工作区 `.venv` 的 Python 3.14.3、pytest、Black
和 Ruff 均可正常运行。两条仍锁定台账 1.17 和 ART-003 硬性 10 篇要求的旧文档契约断言已
同步为当前批准的 1.21 与非硬性内容口径；未修改应用运行代码。

2026-07-18 最终结果：

- `pytest -W error::ResourceWarning`：450 passed；
- Black：90 files would be left unchanged；
- Ruff：All checks passed；
- JavaScript：14/14 通过 `node --check`；
- pip-audit：No known vulnerabilities found；
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 转换提示。

本次仍未重新执行 Docker 或制造生产故障；相关结论继续引用 run 20、隔离 Docker、生产站和
UptimeRobot 的既有实跑证据。

## 7. 回滚与结论

本次汇总不改变应用、数据库、生产配置或容器，无运行时回滚动作。若要撤销本记录，只需回退
本文及主台账状态；不得因此删除生产卷、监控或备份。

SAFE/SEO/TRUST/OPS 的 P0-P1 前置项、最新 CI/Docker 基线、浏览器验收、失败降级、
备份恢复、镜像回滚和外部告警均已有证据，OPS-005 标记为“已完成”。
