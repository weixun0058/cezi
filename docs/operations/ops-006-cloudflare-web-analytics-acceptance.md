# OPS-006 Cloudflare Web Analytics 与 CSP 验收记录

- **验收日期：** 2026-07-18
- **正式站点：** `https://getwiseoracle.com`
- **任务：** OPS-006
- **结论：** 已完成

## 1. 问题与处置

Cloudflare 自动注入的 Web Analytics beacon 曾被应用的 `script-src 'self'` 拒绝，导致页面
功能和 SEO 正常，但 Browser Insights/Web Analytics 无法采集。项目所有者决定保留
Cloudflare Web Analytics，并采用最小放行方案：

```text
script-src 'self' https://static.cloudflareinsights.com
```

没有加入 `'unsafe-inline'`、`'unsafe-eval'` 或通配脚本域名；`connect-src 'self'` 保持不变，
允许 beacon 向正式站同源 `/cdn-cgi/rum` 上报。

## 2. 代码与自动化证据

- `zhugeshensuan/app.py` 的 CSP 精确允许 `https://static.cloudflareinsights.com`。
- `tests/test_seo_metadata.py` 锁定脚本源，并明确禁止 `'unsafe-inline'` 和 `'unsafe-eval'`。
- 2026-07-18 全量门禁：pytest 450/450、Black 90、Ruff、14/14 JavaScript、pip-audit 和
  `git diff --check` 均通过。

## 3. 正式站公开证据

2026-07-18 对正式首页验收：

1. HTTP 200。
2. 响应头包含 `script-src 'self' https://static.cloudflareinsights.com`。
3. DOM 实际出现并加载 `https://static.cloudflareinsights.com/beacon.min.js/...`。
4. Resource Timing 实际出现同源 `https://getwiseoracle.com/cdn-cgi/rum?` 请求。
5. 页面继续正常加载，CSP 未放宽到 inline/eval。

公开证据证明新 CSP 已部署、beacon 被注入且浏览器已执行上报路径。

## 4. Cloudflare 私有控制台证据

项目所有者在专用登录 Edge 中完成 Cloudflare 登录，执行者只读取可见页面，不读取或导出
Cookie、令牌、密码、API key 或请求授权头。

Cloudflare `Web Analytics → Sites` 在 2026-07-18 显示：

| 项目 | 结果 |
| --- | --- |
| 站点 | `getwiseoracle.com` |
| 设置方式 | Automatic setup |
| 创建状态 | Created 25 days ago |
| Page views（Last 24 hrs） | 7 |
| Visits（Last 24 hrs） | 2 |

这些非零统计证明 Cloudflare 已接收并展示生产访问数据，不再只是“脚本存在但后台无数据”。
数字是验收时快照，会随统计窗口变化，不作为长期流量承诺。

## 5. 隐私与运行边界

- 本任务使用 Cloudflare 的隐私优先 Web Analytics，不新增应用用户数据库或用户级画像。
- 验收没有读取访客 IP、Cookie、出生资料、占卜问题或 AI 内容。
- 不把页面浏览量等同于独立真人数量、转化或收入。
- 若以后增加其他分析脚本、跨域上报或用户标识，必须重新做隐私与 CSP 决策，不能沿用本次授权。

## 6. 回滚

若 Cloudflare beacon 将来引发兼容性、隐私或性能问题，可在 Cloudflare 关闭 Automatic setup，
并把 CSP 恢复为 `script-src 'self'`。回滚后应复测页面、控制台、CSP 和 SEO；不得为了省事
加入更宽泛的脚本源。

## 7. 结论

最小 CSP 已部署，正式浏览器实际加载 beacon 并产生同源 RUM 请求，Cloudflare 后台显示
`getwiseoracle.com` 最近 24 小时的非零 Page views 与 Visits。OPS-006 完成。
