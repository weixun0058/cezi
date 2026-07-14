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

中文接口的 `lang` 支持 `zh-hans` 和 `zh-hant`；未显式传入时为兼容旧调用默认使用 `zh-hans`。公开语言切换器只提供繁体中文和英文，但 `/zh-hans/*` 路由仍可直接访问。

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

签号范围为 1 至 384。

### `POST /get_gua_info`

```json
{"sign_number": 123}
```

返回 9 字段：`sign_number`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`。

**数据源**：简体从 `data/content/oracle_signs_reinterpreted.json` 内存加载，繁体从 `data/content/oracle_signs_reinterpreted_hant.json` 内存加载（详见 `docs/architecture/data-source-migration-2026-07-13.md`）。不再包含 `fortune`/`gua_type` 字段。

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

## 英文 API 概览（Wise Oracle）

英文 API 统一走 `/api/en/*` 前缀（D12 已确认）。返回 9 字段结构，不含 `fortune`/`gua_type`（D14 已确认）。

英文站提供算事、单日/十日黄历和四柱论命接口。具体请求参数、返回字段与 SSE 事件契约统一见下方“英文站 API”，避免在同一文档中维护两份定义。

## AI 额度与限流

- 每设备每天免费 3 次，按北京时间重置。
- 每设备和每 IP 每分钟最多 3 次。
- 每设备并发 1 次，全站并发默认 4 次。
- 生产环境必须设置 `AI_GLOBAL_DAILY_LIMIT`。

超限统一返回 HTTP 429、稳定错误码和 `Retry-After` 响应头。预留奖励额度扩展点，当前版本未接入广告、支付或会员。

## 英文站 API

英文站 API 统一使用 `/api/en/*` 前缀，错误响应使用 `error_codes.py` 中的中英文双语错误码。

### `POST /api/en/oracle/ask`

英文算事接口，支持三词和三数字两种模式。

```json
{"mode": "words", "words": ["LOVE", "WORK", "FATE"]}
```

```json
{"mode": "numbers", "numbers": [3, 1, 4]}
```

返回 9 个字段：`sign_number`、`sign_text`、`interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general`，不含 `fortune`/`gua_type`（D14 硬约束）。三词模式按 A=1..Z=26 字母求和 + stroke_digit 映射签号；三数字模式按九位种子合成。

错误码：`INVALID_JSON`、`INVALID_ORACLE_MODE`、`ORACLE_WORDS_INSUFFICIENT`、`INVALID_ORACLE_NUMBER`、`ORACLE_NUMBERS_ALL_ZERO`、`CONTENT_NOT_FOUND`。

### `GET /api/en/daily-almanac`

参数：

- `date`：可选，`YYYY-MM-DD`，默认今天。
- `scenario`：可选，`wedding`、`moving`、`business_opening`、`travel`、`signing`、`haircut`。
- `debug`：可选，设为 `1` 返回 `_missing` 审计字段。

返回结构化英文黄历数据，包含农历日期、干支、生肖、节气、宜忌活动、神煞、方位、冲煞、彭祖百忌和场景评估。所有展示值均为英文，无中文泄漏。

### `GET /api/en/week-almanac`

返回以今天为基准的 10 条英文黄历记录，日期升序且不重复。支持相同的 `scenario` 参数。端点中的 `week` 是兼容名称，不代表固定七日或九日。

### `POST /api/en/birth-chart/analyze`

同步返回英文命盘和 AI 文化反思报告。

```json
{
  "name": "John",
  "gender": "male",
  "birth_date": "1990-01-01",
  "birth_time": "12:00",
  "birth_time_unknown": false,
  "timezone": "America/New_York"
}
```

`birth_time` 支持 `HH:MM` 或省略（`birth_time_unknown` 为 `true` 时）。AI 报告遵循 W0.3 prompt 边界：禁止医疗/法律/财务/预测建议，定位为 cultural self-reflection。

### `POST /api/en/birth-chart/stream`

SSE 流式版本，响应类型 `text/event-stream`。事件序列：

- `chart`：英文基础命盘。完整四柱采用“阴阳 + 五行 + 生肖”，例如 `Yang Metal Horse`；日主采用“阴阳 + 五行”。不再输出 `Geng-Wu` 等拼音四柱契约。
- `report`：AI 文化反思报告（JSON 结构）。
- `responsible_use`：底线提示。
- `error`：流式错误。
- `done`：流结束。

复用 AI 用量配额控制，限流规则与中文论命一致。
