# API 文档

## 通用响应

非流式接口统一返回：

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

错误响应中的 `error` 包含稳定的 `code` 和可展示的 `message`。算事旧接口在一个兼容周期内同时保留原顶层字段。

## 健康检查

### `GET /healthz`

返回服务状态和版本，不检查外部模型可用性。

### `GET /readyz`

检查生产必填配置、只读基础库和运行时数据库。未就绪返回 HTTP 503 和错误码 `NOT_READY`。

## 黄历

### `GET /api/huangli`

参数：

- `date`：可选，`YYYY-MM-DD`，默认今天。
- `scenario`：可选，`结婚`、`搬家`、`开业`、`出行`、`签约`、`理发`。

场景结果只匹配原始宜忌条目，不生成额外吉凶结论。

### `GET /api/week_huangli`

返回前两天、今天和后六天，共九天。支持相同的 `scenario` 参数。

### `GET /api/pzbj_explanation?text=...`

查询彭祖百忌原文解释，文本最长 100 字。

## 算事

### `POST /get_strokes`

```json
{"character": "明"}
```

### `POST /calculate_sign`

```json
{"strokes": [8, 10, 12]}
```

签号范围为 1 至 383。

### `POST /get_gua_info`

```json
{"sign_number": 123}
```

返回 `sign_text`、`gua_type`、`fortune`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study` 和 `general` 命名字段。

## 论命

### `POST /api/lunming/analyze`

返回完整结构化命盘和模型解读。

### `POST /api/lunming/stream`

请求头：`Content-Type: application/json`，响应类型：`text/event-stream`。

```json
{
  "name": "称呼",
  "gender": "男",
  "birth_date": "1990-01-01",
  "birth_time": "午",
  "birth_place": "北京",
  "timezone": "Asia/Shanghai",
  "use_true_solar_time": true,
  "longitude": 116.4
}
```

`birth_time` 可使用 `HH:MM`、十二地支或 `未知`。启用真太阳时必须提供经度，且时辰不能未知。

事件数据类型：

- `chart`：确定性历法结果。
- `text`：模型返回的文本块。
- `error`：流式错误。
- `done`：流结束。

只支持 POST；`GET /api/lunming/stream` 返回 HTTP 405。

## 英文 API（Wise Oracle）

英文 API 统一走 `/api/en/*` 前缀（D12 已确认）。返回 9 字段结构，不含 `fortune`/`gua_type`（D14 已确认）。

### `POST /api/en/oracle/ask`

英文算事，支持两种输入模式：

```json
// Three Words 模式
{"mode": "words", "words": ["love", "work", "fate"]}

// Three Numbers 模式（每位 0-9）
{"mode": "numbers", "numbers": [3, 1, 4]}
```

返回 9 字段：`sign_number`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`。

错误码：`INVALID_JSON`、`INVALID_ORACLE_MODE`、`ORACLE_WORDS_INSUFFICIENT`、`INVALID_ORACLE_NUMBER`、`ORACLE_NUMBERS_ALL_ZERO`、`CONTENT_NOT_FOUND`。

### `POST /api/en/birth-chart/analyze`

同步返回基础盘 + AI 报告。

### `POST /api/en/birth-chart/stream`

SSE 流式分析，事件类型：`chart`、`report`、`responsible_use`、`error`、`done`。

## AI 额度与限流

- 每设备每天免费 3 次，按北京时间重置。
- 每设备和每 IP 每分钟最多 3 次。
- 每设备并发 1 次，全站并发默认 4 次。
- 生产环境必须设置 `AI_GLOBAL_DAILY_LIMIT`。

超限统一返回 HTTP 429、稳定错误码和 `Retry-After` 响应头。预留奖励额度扩展点，当前版本未接入广告、支付或会员。
