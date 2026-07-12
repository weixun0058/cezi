# 诸葛神算 V3 上线前改造实施计划

## 执行顺序

1. 首先创建并保存本计划文件。
2. 确认计划文件内容完整后，单独提交：`docs: add production readiness plan`。
3. 再按以下阶段实施，每阶段独立测试和提交。

## 阶段一：数据层

- 创建只读 `data/reference/reference.db`，统一存储汉字笔画、383 条签文和彭祖百忌。
- 创建 `instance/runtime.db`，存储黄历缓存、联网笔画缓存和 AI 额度。
- 增加数据构建脚本，保留 Excel、JSON 等编辑源。
- 修复所有 SQLite 连接泄漏，配置 WAL、事务和并发超时。
- 限制黄历有效日期，旧缓存不迁移。

## 阶段二：AI 保护

- 每设备每天免费 3 次，按北京时间重置。
- 每设备/IP 每分钟 3 次、每设备并发 1 次、全站并发默认 4 次。
- `AI_GLOBAL_DAILY_LIMIT` 作为生产必填配置。
- 所有限制由 SQLite 事务原子执行。
- 超限返回 HTTP 429、稳定错误码和 `Retry-After`。
- 删除旧 `GET /api/lunming/stream`，只保留 POST。
- 预留广告奖励额度扩展点，本轮不接广告、支付或会员。

## 阶段三：安全与依赖

- 升级 Flask、Werkzeug、requests 和 python-dotenv 到漏洞修复版本。
- 撤销 Git 历史中 3 个旧模型密钥。
- 新增 `/readyz` 生产就绪检查。
- 补充 CSP、Permissions-Policy 等安全响应头。
- CI 增加依赖漏洞审计、Docker 构建和容器健康检查。
- 日志禁止记录请求体和论命输入。

## 阶段四：Docker 上线

- 使用 Python 3.13 slim 和非 root 用户。
- 根文件系统只读，仅 `/app/instance` 挂载持久化卷。
- 增加生产 Compose 配置和必填环境变量校验。
- 外部 Nginx/CDN 负责 HTTPS 和 SSE 代理。
- 使用版本镜像发布，支持健康检查和上一版本回滚。
- 更新部署指南、API 文档和综合优化计划。

## 验收

- Black、Ruff、pytest、JavaScript 语法和 pip-audit 通过。
- 测试中不存在 SQLite 连接警告。
- 数据构建完整且可重复。
- 第 4 次每日论命请求正确返回 429。
- 多进程额度扣减不超发。
- Docker 镜像成功构建并通过 `/healthz` 和 `/readyz`。
- 完成真实模型、SSE 代理、数据卷恢复和版本回滚测试。

## 明确约束

- 保留姓名、出生地点和真太阳时现有表单及行为。
- 不新增任何隐私政策、第三方处理说明或提示。
- 删除 README 中现有“隐私”描述。
- 实施前必须先保存并提交本计划文件。
