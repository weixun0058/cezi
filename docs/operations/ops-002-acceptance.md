# OPS-002 备份、恢复与镜像回滚验收记录

- **任务：** OPS-002
- **日期：** 2026-07-16
- **执行环境：** Windows 开发机 + Docker Desktop Linux Engine
- **演练开始时间：** 2026-07-16 13:29:47（Asia/Shanghai）
- **生产服务器：** 未连接、未修改
- **生产数据卷：** `zhugeshensuan_runtime-data` 未挂载、未写入、未删除

## 1. 产出

- `docs/operations/backup-restore-runbook.md`：生产备份、隔离恢复、生产恢复、失败撤回和镜像回滚步骤。
- `scripts/ops002_rehearsal.ps1`：只允许操作 `zhugeshensuan-ops002-` 前缀资源的本地演练脚本。
- `tests/test_ops002_runbook.py`：锁定数据边界、安全护栏和验收证据。

## 2. 演练镜像

| 角色 | 标签 | 不可变 image ID | 结果 |
| --- | --- | --- | --- |
| 当前镜像 | `zhugeshensuan:local` | `sha256:9e1818fd71ab087bd68951e27bc3914a7ad19e26edea7b5ae7e6e5319b4404cb` | 使用隔离源卷启动，`readyz` 成功 |
| 回滚镜像 | `zhugeshensuan:final-audit` | `sha256:f4d1d96b52b878754a329cf7aa13020aba142b0785e7465ab8d80abf0f6fabb1` | 使用隔离恢复卷启动，`readyz` 成功 |

两者 image ID 不同，因此本次确实验证了镜像切换，不是同一镜像的不同标签。

## 3. 备份与恢复证据

演练使用两个自动生成的临时卷：源卷和恢复卷。二者名称均以 `zhugeshensuan-ops002-` 开头，完成后已删除。

| 检查项 | 结果 |
| --- | --- |
| 当前镜像初始化 `runtime.db` | 通过 |
| 备份前标记 | `present-in-backup` |
| 备份文件大小 | 65,536 bytes |
| 备份 SHA-256 | `50be86d7405843d1b7a12c553ad1da752dcd9f80ffd6cabeaeb998b80fd57c09` |
| 备份 `PRAGMA quick_check` | `ok` |
| 备份后仅在源卷新增标记 | `created-after-backup` |
| 恢复卷 `PRAGMA quick_check` | `ok` |
| 恢复卷最终标记 | 只有 `present-in-backup` |
| 当前镜像 `/readyz` | `success=true`, `status=ready`, `version=4.1` |
| 旧镜像 + 恢复卷 `/readyz` | `success=true`, `status=ready`, `version=4.1` |

恢复卷没有出现备份后才写入源卷的 `created-after-backup`，证明恢复内容来自备份快照，而不是错误复用了演练源卷。

## 4. 生产隔离与清理证据

| 检查项 | 结果 |
| --- | --- |
| 演练前生产卷存在 | 是 |
| 演练前后生产卷身份 | 一致 |
| 脚本挂载生产卷 | 否 |
| 删除生产卷 | 否 |
| 残留 `zhugeshensuan-ops002-` 容器 | 0 |
| 残留 `zhugeshensuan-ops002-` 卷 | 0 |

脚本的删除函数会先检查资源名；不带 `zhugeshensuan-ops002-` 前缀时直接拒绝。生产卷名另有显式拒绝分支。

## 5. 验收结论与限制

OPS-002 要求的三个技术路径均已完成本地安全演练：

1. 停止应用后从数据卷复制 `runtime.db` 并计算 SHA-256。
2. 把备份恢复到独立卷，验证 SQLite 完整性和快照语义。
3. 用不同 image ID 的旧镜像挂载恢复卷，验证应用 readiness。

生产服务器依照任务约束没有被连接或修改，因此本记录不声称“已取得一份真实生产数据库备份”。正式生产备份的首次执行仍应由有服务器权限的操作者按 runbook 第 3、4 节完成；该动作不影响本次恢复与回滚机制验收，但完成后应把脱敏的文件名、大小、SHA-256 和 `quick_check=ok` 追加到运维记录。

## 6. 自动化验证

```text
pytest tests/test_ops002_runbook.py tests/test_documentation_contract.py -q
10 passed

ruff check tests/test_ops002_runbook.py
All checks passed!

PowerShell parser: passed
git diff --check: passed
```

脚本实跑后再次检查 Docker：残留 OPS-002 临时容器为 0，残留 OPS-002 临时卷为 0，生产卷仍存在。

## 7. 回滚

- 文档和演练脚本只新增文件，不改变应用运行路径。
- 删除这些新增文件即可回滚本批代码；不得删除 `zhugeshensuan_runtime-data`。
- 演练资源已自动清理，无需对 Docker 生产资源做任何回滚操作。
