# GOV-003 Git、镜像与导出工件发布追溯记录

- **建立日期：** 2026-07-18
- **任务：** GOV-003
- **结论：** 已完成
- **当前 Git 基线：** `7c99c26be7c80155e8a4f3ee030c72a741e47889`（`main` / `origin/main`）

## 1. 追溯原则

本记录区分三种证据强度：

1. **镜像内嵌提交：** Docker OCI label 直接包含 Git 短 SHA，可建立精确映射。
2. **历史工作树工件：** 验收时从尚未提交的工作树构建；可映射到验收记录、标签、image ID
   和 tar SHA-256，但不能伪称由后续 Git 提交逐字节重建。
3. **首次持久化提交：** 后续提交首次把该批源码和验收记录完整纳入 Git，用于长期审阅，
   不倒推改变历史工件身份。

## 2. Git 基线

| 提交 | 完整 SHA | 时间（Asia/Shanghai） | 作用 |
| --- | --- | --- | --- |
| `f90a852` | `f90a852`（镜像 label 记录的短 SHA） | 2026-07-15 前后基线 | 根目录现存 `zhugeshensuan-local.tar` 的内嵌源码标识 |
| `8c60f4e` | `8c60f4e3b9b1d97ec9b9bedfb1a3f96d797d5b43` | 2026-07-17 00:35:10 +08:00 | 首次完整提交 SAFE、SEO、TRUST、文章上传、OPS 文档及部署代码 |
| `44f6925` | `44f69251a7c2b8a9b45882552975efaaa0100def` | 2026-07-17 01:28:21 +08:00 | 修复生产 Docker CI 冒烟配置；对应 Actions run 20 的代码修复 |
| `7c99c26` | `7c99c26be7c80155e8a4f3ee030c72a741e47889` | 2026-07-17 01:31:53 +08:00 | 记录 run 20 成功；当前远端主分支基线 |

## 3. 镜像与 tar 映射

| 工件/标签 | image ID / 内嵌版本 | tar SHA-256 | Git 映射与判定 |
| --- | --- | --- | --- |
| 根目录 `zhugeshensuan-local.tar`，`zhugeshensuan:local` | config digest `sha256:0b5f24c6c4b68160db71945345c0d36667ed61c7dac05cf39f70baae448fda4c`；OCI version `4.1-local-f90a852` | `753AEE64BC64C1A42079511FA47E029C66036FA95577865909D974F03FD643DC` | 精确映射到内嵌短 SHA `f90a852`；这是 2026-07-15 旧基线，不是 SEO/文章上传最终工件 |
| `2026.07.16-seo` | 历史记录未保存 image ID | `913D4E3D96152F717CFEE5225CC9CB1B9728CCBA3D739584FFDEFC1CEC705C5A` | 从未提交工作树构建；SEO 验收记录是工件身份源，相关源码首次完整持久化于 `8c60f4e`；不声称 tar 可由该提交逐字节复现 |
| `2026.07.16-trust` | `sha256:9e1818fd71ab087bd68951e27bc3914a7ad19e26edea7b5ae7e6e5319b4404cb` | `03119D97DD55DFC6028E2858BDCF62DD2A412903D0A0E1D3466DE1EA3D00FB16` | 从未提交工作树构建；TRUST 验收记录是工件身份源，相关源码首次完整持久化于 `8c60f4e` |
| `zhugeshensuan:2026.07.16-article-upload` | `sha256:077d7e40b6d62768b5bb91483c40ef3b77450bcd9491a6ad3abc35654b97b5e6`；version `server-article-upload-poetry-rtl` | `27403E6DD1F801E2C8DD015BE6C3F8663BC28878E17F32342B6B58AAB478B81A` | 已部署功能工件；文章上传、SEO、TRUST、UI 源码及验收记录首次完整持久化于 `8c60f4e` |

SEO、TRUST 和 article-upload 的历史 tar 当前不在仓库中；本记录只引用当时验收时已经保存的
SHA-256，不捏造重新计算结果。根目录旧 tar 则在 2026-07-18 重新计算 SHA-256，并从其
`manifest.json` 与 config blob 读取 OCI version 完成精确归属。

## 4. CI 与生产关系

- `8c60f4e` 提交了生产上线和文章系统代码，但对应 run 19 的 Docker 冒烟因 CI 未传入
  `CONTACT_EMAIL` 和独立文章卷路径而失败。
- `44f6925` 修复 CI 契约；GitHub Actions run 20 全部通过。
- `7c99c26` 只记录 run 20 成功，不改变应用运行代码。
- 当前生产功能状态已通过正式域名、文章入口、动态 sitemap、`healthz`/`readyz`、UptimeRobot
  和 OPS-005 统一验收确认；本记录不把“CI 通过”误写成一次新的生产部署。

## 5. 后续发布要求

以后构建可部署镜像时应把完整 Git SHA 写入 OCI revision label，并使用不可变标签：

```text
org.opencontainers.image.revision=<full-git-sha>
org.opencontainers.image.version=<release-tag>
```

每次发布至少记录 Git SHA、镜像标签、image ID、导出 tar 文件名与 SHA-256、CI run、部署时间
和回滚标签。不得用可覆盖的 `latest`/`local` 作为唯一生产追溯点。

## 6. 验证与限制

- Git 提交、时间、分支和文件范围由本地仓库只读核验。
- 根目录 tar 的 SHA-256、manifest、config digest 和 OCI version 已只读核验。
- 历史 SEO/TRUST/article tar 不在当前工作区，因此只采用已有验收记录中的哈希。
- 本任务只新增/更新文档，不改镜像、生产服务器或部署状态。
- `git diff --check` 必须通过。

上述记录把“可精确映射的旧 tar”和“历史未提交工作树构建的上线工件”明确分开，同时为后续
发布规定了完整 SHA 规则。GOV-003 的追溯欠债至此关闭。
