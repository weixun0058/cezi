# Wise Oracle 四周运营观察模板

- **对应任务：** MET-001、MET-002
- **周期：** 连续四个完整自然周
- **数据边界：** 只记录聚合数字，不保存姓名、出生资料、IP、设备标识、原问题或结果文本

## 使用方法

1. 每周固定一天填写一次，不因数字小而补造或估算访问量。
2. Cloudflare Web Analytics 填页面浏览和访问；Search Console 填自然搜索数据。
3. 应用聚合数据使用 `scripts/weekly_metrics_report.py` 导出。
4. AI单位成本没有可靠账单时填 `0` 并在备注说明，不把未知成本写成零成本。
5. 打赏、广告或订单尚未启用时填 `未启用`，不要填虚构的 `0% 转化率`。

## 固定隐私检查

- [ ] 本周记录未包含姓名或联系信息。
- [ ] 未包含出生日期、出生时间、性别或时区组合。
- [ ] 未包含IP、Cookie、设备ID或哈希主体。
- [ ] 未包含用户原问题、三个词、签文结果或AI报告正文。
- [ ] 未从Cloudflare/Search Console导出可识别个人的明细。

## 周度记录

每周复制一份本节。

### 第 __ 周：____-__-__ 至 ____-__-__

| 类别 | 指标 | 本周值 | 上周值 | 说明/来源 |
| --- | --- | ---: | ---: | --- |
| 流量 | Cloudflare page views |  |  | Web Analytics |
| 流量 | Cloudflare visits |  |  | Web Analytics |
| 搜索 | Search Console impressions |  |  | Performance |
| 搜索 | Search Console clicks |  |  | Performance |
| 搜索 | CTR |  |  | Performance |
| 搜索 | 平均排名 |  |  | Performance |
| 产品 | Oracle results |  |  | 聚合导出 |
| 产品 | Almanac results |  |  | 聚合导出 |
| 产品 | AI requests accepted |  |  | 聚合导出 |
| 内容 | 当前已发布文章数 |  |  | 聚合导出/文章管理页 |
| 成本 | 估算AI成本（USD） |  |  | 单位成本 × 聚合请求数 |
| 成本 | 服务器及外部服务成本（USD） |  |  | 账单，不含沉没成本 |
| 商业化 | Support clicks | 未启用 | 未启用 | 启用前保持“未启用” |
| 商业化 | Ad impressions/revenue | 未启用 | 未启用 | AdSense启用后填写 |
| 商业化 | Orders/refunds/net revenue | 未启用 | 未启用 | 付费产品启用后填写 |

#### 本周事件

- 新增/更新内容：
- 搜索或流量异常：
- UptimeRobot/应用故障：
- 备份与恢复演练：
- 用户主动反馈：
- 政策或平台变化：

#### 本周判断

- 哪个入口或内容出现真实信号：
- 哪个功能成本高但使用少：
- 下周只做的一项小实验：
- 明确不做的事项：

## 四周汇总决策

四周完成后填写：

- [ ] 四周数据完整，缺失处已说明。
- [ ] 生产备份和异机副本稳定，没有以商业化换取运维风险。
- [ ] 已核验项目所有者所在地、收款主体和提现条件。
- [ ] 已重新核验候选平台官方政策。
- [ ] 已审查公共内容页是否达到 AdSense 准备度。
- [ ] 已确认广告不会进入出生资料输入或个性化结果页。

选择一个结论：

- [ ] 继续观察，商业化保持关闭。
- [ ] 只试运行外部自愿打赏链接。
- [ ] 准备并提交 AdSense 审核。
- [ ] 同时试运行打赏与公共内容页广告。
- [ ] 研究付费产品，但仍不接真实支付。
- [ ] 解冻最小付费产品，进入独立设计和风险审查。

决策依据：

```text
在此写明真实数据、风险、成本和下一次复核日期。
```

## 聚合导出示例

```bash
python scripts/weekly_metrics_report.py \
  --runtime-db /var/lib/docker/volumes/zhugeshensuan_runtime-data/_data/runtime.db \
  --articles-path /var/lib/docker/volumes/zhugeshensuan_article-content/_data/articles_en \
  --start 2026-07-20 \
  --end 2026-07-26 \
  --ai-unit-cost-usd 0
```

输出 JSON 可以保存在站长私有目录；若要提交公开仓库，只提交本模板和不含环境指纹的汇总，
不提交 runtime 数据库、原始日志、账户截图或任何访问凭据。
