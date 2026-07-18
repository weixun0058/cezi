# Wise Oracle 每日自动备份与 Cloudflare R2 异机副本手册

- **对应任务：** OPS-002 持续运维
- **脚本：** `scripts/production_backup.sh`
- **定时器：** `deploy/wise-oracle-backup.service`、`deploy/wise-oracle-backup.timer`
- **当前状态（2026-07-19）：** 本地自动化已实现；R2订阅、私有bucket、专用token和生产定时器待外部配置与验收

## 1. 备份内容与边界

每日快照包含：

- runtime SQLite：运行时缓存、AI聚合用量和限流状态；
- article-content：服务器管理页上传的 Markdown 文章；
- 两份 SHA-256；
- 私有 manifest：时间、镜像标识、卷名和文件大小。

不包含 `.env`、API key、Cookie、支付凭据或用户原始输入。源码由 GitHub 保存，镜像由不可变
标签和发布追溯管理，不重复打进数据备份。

## 2. 安全特性

脚本执行前必须精确匹配两个生产卷；不匹配立即退出。它不会执行 `docker compose down -v`，
不会删除生产卷。应用只在生成一致时间点快照时短暂停止，退出保护负责重新启动并检查本机
health/readiness。有效快照完成后再恢复流量检查和R2上传。

本地策略：

- 最近7份日快照；
- 最近4份周快照（UTC星期日）；
- 不完整快照移入 `backups/failed/`；
- 同一时间只允许一个备份进程；
- R2上传使用 `--immutable`，拒绝覆盖同路径对象；
- 首阶段不自动删除R2对象，避免错误保留规则同时删除本地与异机副本。

## 3. R2账户和计费确认门

2026-07-19 登录态页面显示R2尚未启用。启用页面当前显示 Standard 每月10GB、100万Class A、
1000万Class B免费额度，超额按量计费；立即及固定月费均为0。但点击启用会：

1. 使用账户内已有付款方式；
2. 创建自动续订的用量计费订阅；
3. 同意Cloudflare条款和隐私政策；
4. 超出免费额度时产生费用。

因此必须由项目所有者明确确认后再点击，自动化执行者不得把“预计0美元”理解成无需授权的
财务操作。官方价格以 [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
为准。

## 4. R2资源最小权限

启用后：

1. 创建一个 **Standard、Private** bucket，不配置公开访问或自定义域名。
2. 创建仅限该bucket的R2专用token，只授予对象读写，不授予账户其他资源权限。
3. token只在服务器交互式配置，不粘贴到聊天、Git、systemd unit或shell历史。
4. Cloudflare默认提供传输和静态加密；推荐再使用rclone crypt进行客户端加密，使对象名和内容
   在上传前加密。Cloudflare静态加密说明见
   [R2 Data Security](https://developers.cloudflare.com/r2/reference/data-security/)。

## 5. 服务器交互式配置

在服务器安装rclone后，以root运行：

```bash
rclone config
```

依次建立：

1. `wise-oracle-r2`：类型S3、provider选择Cloudflare、填写专用access key/secret和账户R2 endpoint；
2. `wise-oracle-crypt`：类型crypt，remote指向 `wise-oracle-r2:<private-bucket>`；
3. 文件名和目录名加密选择standard；
4. 让rclone生成crypt密码和salt，并把恢复所需值单独保存到密码管理器；
5. 确认 `/root/.config/rclone/rclone.conf` 权限为`600`。

不要在聊天或命令行参数中传递token。若crypt密码丢失，即使R2对象存在也无法恢复。

## 6. 安装和启用定时器

代码到达生产服务器后执行：

```bash
cd /root/zhugeshensuan
chmod 700 scripts/production_backup.sh
install -m 644 deploy/wise-oracle-backup.service /etc/systemd/system/
install -m 644 deploy/wise-oracle-backup.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now wise-oracle-backup.timer
systemctl list-timers wise-oracle-backup.timer
```

定时器每天UTC 19:15触发并增加最多15分钟随机延迟，即北京时间约03:15–03:30。服务器时区变化
不会改变UTC计划；如果该时段出现真实高峰，再通过一次受控变更调整。

## 7. 首次验收

先手工执行一次：

```bash
systemctl start wise-oracle-backup.service
systemctl status wise-oracle-backup.service --no-pager
journalctl -u wise-oracle-backup.service -n 100 --no-pager
rclone lsf wise-oracle-crypt:production/daily --dirs-only
curl --fail http://127.0.0.1:8000/readyz
curl --fail https://getwiseoracle.com/readyz
```

然后把最新异机快照复制到新建的隔离临时目录，执行：

- `sha256sum --check`；
- runtime `PRAGMA quick_check`；
- 文章 `tar -tzf`；
- 与服务器本地manifest的时间戳和大小核对。

验收不得在生产卷上执行恢复，也不得公开bucket、endpoint、token、完整hash或环境指纹。

## 8. 告警与恢复

systemd任务失败时，本地有效快照仍保留；先确认应用ready，再处理R2。应为
`wise-oracle-backup.service`失败配置管理员通知，不能仅依赖网站UptimeRobot，因为R2上传失败时
网站可能仍然正常。

每月至少执行一次隔离恢复演练。任何恢复都继续遵守
`docs/operations/backup-restore-runbook.md`，不得为了测试直接替换生产数据。
