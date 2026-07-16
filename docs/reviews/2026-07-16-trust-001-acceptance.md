# TRUST-001 联系方式实施验收记录

**日期：** 2026-07-16
**任务：** TRUST-001 确定并配置真实联系与隐私邮箱
**当前状态：** 已完成
**项目所有者决定：** Contact 与 Privacy 统一使用 `5siwei@gmail.com`

## 1. 实施范围

- 新增非敏感配置 `CONTACT_EMAIL`，生产环境拒绝空值、无效格式和 `.example` 占位域名。
- `frontend/templates/en/contact.html` 的 General Inquiries 与 Privacy Inquiries 统一显示 `5siwei@gmail.com`，并提供 `mailto:` 链接。
- Privacy、Terms、Disclaimer 同步公开同一联系方式，修订日期更新为 2026-07-16。
- `.env.example`、真实本地 `.env`、生产 Compose 和部署指南同步增加 `CONTACT_EMAIL=5siwei@gmail.com`。
- 新增回归测试，确保所有公开模板不再出现 `.example`，四个信任页面均输出配置邮箱和 `mailto:` 链接。

## 2. 自动化与静态门禁

| 检查 | 结果 |
| --- | --- |
| TRUST 定向测试 | `tests/test_config.py tests/test_english_frontend_contract.py`：66/66 通过 |
| 全量测试 | 388/388 通过 |
| Black | 83 个 Python 文件检查通过 |
| Ruff | 全部检查通过 |
| JavaScript 语法 | 14/14 通过 |
| 依赖审计 | `pip-audit`：No known vulnerabilities found |
| Compose 配置 | `docker-compose --env-file .env -f deploy/compose.prod.yml config --quiet` 通过 |
| Git diff | `git diff --check` 通过；仅有 Git 的 CRLF 转换提示 |
| 模板占位域名 | `frontend/templates/**/*.html` 中无 `.example` |

`pip-audit` 首次启动时因 Windows 中文工作路径的子进程输出编码发生 `UnicodeDecodeError`；使用 UTF-8 code page、`PYTHONUTF8=1` 和 `PYTHONIOENCODING=utf-8` 重跑后正常完成，结果为无已知漏洞。

## 3. Docker 生产路径验收

- 镜像：`zhugeshensuan:local`
- 版本标签：`2026.07.16-trust`
- 镜像 ID：`sha256:9e1818fd71ab087bd68951e27bc3914a7ad19e26edea7b5ae7e6e5319b4404cb`
- 导出工件：`zhugeshensuan-2026.07.16-trust.tar`（122,463,232 bytes）
- tar SHA-256：`03119D97DD55DFC6028E2858BDCF62DD2A412903D0A0E1D3466DE1EA3D00FB16`

镜像以生产配置、非 root、只读文件系统、`cap-drop ALL` 和 `no-new-privileges` 启动成功。容器内实测：

| 路径 | HTTP | 真实邮箱 | `mailto:` | `.example` |
| --- | ---: | --- | --- | --- |
| `/contact` | 200 | 有 | 有 | 无 |
| `/privacy` | 200 | 有 | 有 | 无 |
| `/terms` | 200 | 有 | 有 | 无 |
| `/disclaimer` | 200 | 有 | 有 | 无 |
| `/healthz` | 200 | — | — | — |
| `/readyz` | 200 | — | — | — |

## 4. 正式域名验收

项目所有者完成新镜像部署后，直接请求 `https://getwiseoracle.com` 验收：

| 路径 | HTTP | Cloudflare 解码后的邮箱 | `.example` | 修订日期 |
| --- | ---: | --- | --- | --- |
| `/contact` | 200 | `5siwei@gmail.com` | 无 | — |
| `/privacy` | 200 | `5siwei@gmail.com` | 无 | 2026-07-16 |
| `/terms` | 200 | `5siwei@gmail.com` | 无 | 2026-07-16 |
| `/disclaimer` | 200 | `5siwei@gmail.com` | 无 | 2026-07-16 |
| `/healthz` | 200 | — | — | — |
| `/readyz` | 200 | — | — | — |

Cloudflare 对公开邮箱启用了 Email Address Obfuscation：响应源码中的邮箱和 `mailto:` 会被改写为同源 `/cdn-cgi/l/email-protection` 链接及 `data-cfemail`，浏览器再通过同源 `email-decode.min.js` 恢复。四页的 `data-cfemail` 解码结果均为 `5siwei@gmail.com`；脚本受现有 `script-src 'self'` CSP 允许。这是防止简单爬虫收集邮箱的保护，不是占位地址或部署错误。

## 5. 人工收信验收

项目所有者已完成实际收信确认：

- [x] 正式域名四个信任页面发布 `5siwei@gmail.com`，无 `.example`，Cloudflare 邮箱保护可解码回真实地址。
- [x] 项目所有者向该地址发送测试邮件并确认实际收到；该邮件进入 Gmail 垃圾箱，但收件链路有效。

垃圾箱结果不阻塞 TRUST-001：网站只提供收件地址和 `mailto:`，邮件是否进入垃圾箱由 Gmail 结合实际发送方、邮件内容和信誉进行过滤；单封测试邮件不足以判断所有访客来信都会进入垃圾箱。项目所有者应先对本次邮件执行“不是垃圾邮件”，并在运营初期定期检查垃圾箱；若来自多个正常发送方的来信持续被误判，再单独评估邮箱运营方案。

## 6. 回滚

若新容器无法正常启动，使用上一版 SEO 工件恢复原镜像并重新启动 Compose。回滚只影响新联系方式显示；不要删除服务器原有 `.env`、Compose 文件或运行数据卷。问题修复后再重新部署 TRUST 工件。
