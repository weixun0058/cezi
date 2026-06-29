# 错误码策略定稿

> **文档定位**：W1.2 产出。定义全后端 API 错误码的稳定 `code`、中英文消息映射、HTTP status 对应关系。
> **创建日期**：2026-06-30
> **状态**：W1 定稿，待用户审阅
> **前置关系**：W3.2 产出 `zhugeshensuan/error_codes.py` 代码必须引用本文档；W4/W5/W6 后端实现必须使用本文档定义的 code
> **关联文档**：`wise-oracle-copy-style-guide.md`（英文消息文案）、`wise-oracle-english-product-spec.md`（英文 API 错误响应示例）

---

## 一、设计原则

1. **code 优先于 message**：前端按 `error.code` 做差异化处理（如限流倒计时、404 友好提示），message 仅作展示兜底
2. **code 稳定不变**：一旦定义，code 字符串不随 message 文案调整而改变
3. **中英文双语**：每个 code 同时有中文和英文消息；前端按语言切换展示
4. **HTTP status 与 code 对应**：同一 code 对应固定 status，不混用
5. **中文页面保持兼容**：现有中文前端只读 message，不读 code，不影响现有行为

---

## 二、现有错误码清单（21 个，来自代码扫描）

> 来源：`zhugeshensuan/api_utils.py` 的 `failure(code, message, status)` 调用点全量扫描（2026-06-30）。

### 2.1 通用错误（app.py）

| code | HTTP status | 触发场景 | 中文消息 | 英文消息 |
| --- | --- | --- | --- | --- |
| `NOT_READY` | 503 | 服务健康检查未通过（启动期） | 服务尚未就绪 | The service is not ready yet. Please try again later. |
| `PAYLOAD_TOO_LARGE` | 413 | 请求体超过 MAX_CONTENT_LENGTH | 请求内容过大 | The request payload is too large. |
| `NOT_FOUND` | 404 | /api/ 前缀路径不存在 | 接口不存在 | The requested API endpoint does not exist. |

### 2.2 黄历 API（huangli_api.py）

| code | HTTP status | 触发场景 | 中文消息 | 英文消息 |
| --- | --- | --- | --- | --- |
| `INVALID_DATE` | 400 | 日期格式非 YYYY-MM-DD | 日期格式无效，请使用 YYYY-MM-DD | Invalid date format. Please use YYYY-MM-DD. |
| `INVALID_DATE` | 400 | 日期超出 1900-2100 范围 | 日期必须在 1900-01-01 到 2100-12-31 之间 | The date must be between 1900-01-01 and 2100-12-31. |
| `INVALID_SCENARIO` | 400 | 场景码不支持 | 不支持的场景筛选 | The selected scenario is not supported. |
| `HUANGLI_NOT_FOUND` | 404 | 无法获取黄历数据 | 无法获取黄历数据 | Could not retrieve almanac data for this date. |
| `INVALID_TEXT` | 400 | 彭祖百忌文本空或超 100 字 | 彭祖百忌文本不能为空且不能超过 100 字 | The text must not be empty and must not exceed 100 characters. |
| `EXPLANATION_NOT_FOUND` | 404 | 未找到对应解释 | 未找到对应解释 | No explanation was found for this item. |

### 2.3 算事 API（divination.py，中文版现有）

| code | HTTP status | 触发场景 | 中文消息 | 英文消息 |
| --- | --- | --- | --- | --- |
| `INVALID_JSON` | 400 | 请求体非 JSON 对象 | 请求体必须是 JSON 对象 | The request body must be a JSON object. |
| `INVALID_CHARACTER` | 400 | 中文算事：未输入汉字 | 请输入一个汉字 | Please enter a single Chinese character. |
| `STROKE_NOT_FOUND` | 404 | 笔画查询失败 | 暂时无法查询该字笔画 | Could not determine the stroke count. Please try a different character. |
| `INVALID_STROKES` | 400 | 中文算事：笔画非三个 1-100 整数 | 笔画必须是三个 1 到 100 的整数 | Strokes must be three integers between 1 and 100. |
| `INVALID_SIGN` | 400 | 签号非 1-383 整数 | 签号必须是 1 到 383 的整数 | The sign number must be an integer between 1 and 383. |
| `SIGN_NOT_FOUND` | 404 | 未找到对应签文 | 未找到对应签文 | This oracle sign could not be found. |

### 2.4 论命 API（lunming_api.py + ai_usage.py）

| code | HTTP status | 触发场景 | 中文消息 | 英文消息 |
| --- | --- | --- | --- | --- |
| `INVALID_BIRTH_DATA` | 400 | 出生信息格式错误 | （来自 BaziInputError，动态） | The birth data provided was invalid. Please check and try again. |
| `MODEL_NOT_CONFIGURED` | 503 | AI 模型未配置 | （来自 ModelConfigurationError，动态） | The analysis service is not configured. Please contact support. |
| `ANALYSIS_FAILED` | 502 | AI 分析失败 | 分析服务暂时不可用 | The analysis service is temporarily unavailable. Please try again later. |
| `AI_DAILY_QUOTA_EXHAUSTED` | 429 | 用户今日免费论命次数用完 | 今日免费论命次数已用完 | Your daily free analysis quota has been used up. Please try again tomorrow. |
| `AI_GLOBAL_QUOTA_EXHAUSTED` | 429 | 全局 AI 额度用完 | 今日分析服务额度已用完 | The analysis service quota has been exhausted today. Please try again tomorrow. |
| `AI_RATE_LIMITED` | 429 | 请求过于频繁 | 请求过于频繁，请稍后再试 | Too many requests. Please slow down. |
| `AI_CONCURRENCY_LIMITED` | 429 | 并发数达上限 | 分析服务繁忙，请稍后再试 | The analysis service is busy. Please try again shortly. |

---

## 三、英文版新增错误码（W4/W6 专用）

> 依据 `wise-oracle-english-product-spec.md` 和 `wise-oracle-copy-style-guide.md`，英文 Ask the Oracle 新增以下错误码。

### 3.1 Ask the Oracle 英文版（W4）

| code | HTTP status | 触发场景 | 英文消息 |
| --- | --- | --- | --- |
| `INVALID_INPUT` | 400 | 空输入或字段缺失 | Some fields were missing or invalid. Please check and try again. |
| `INVALID_ORACLE_MODE` | 400 | mode 非 words/numbers | Invalid input mode. Choose 'three words' or 'three numbers'. |
| `ORACLE_WORDS_INSUFFICIENT` | 400 | 三词词数不足或含非字母 | Please enter exactly three words. |
| `INVALID_ORACLE_NUMBER` | 400 | 三数字超范围（非 0-999） | Each number must be between 0 and 999. |
| `ORACLE_NUMBERS_ALL_ZERO` | 400 | 三数字全为 0 | The three numbers cannot all be zero. |

### 3.2 Birth Chart Reading 英文版（W6）

英文论命复用 `INVALID_BIRTH_DATA` / `MODEL_NOT_CONFIGURED` / `ANALYSIS_FAILED` / `AI_*` 限流码，消息切换为英文。

### 3.3 内容缺失（W2/W7）

| code | HTTP status | 触发场景 | 英文消息 |
| --- | --- | --- | --- |
| `CONTENT_NOT_FOUND` | 404 | 文章/合规页/数据缺失 | The requested content is not available. |
| `SIGN_NOT_FOUND` | 404 | 英文签文未找到（复用现有 code） | This oracle sign could not be found. |

---

## 四、SSE 流错误处理策略

> 现状：`lunming_api.py` L112/L118 的 SSE 流错误返回 `{"type": "error", "error": "字符串"}`，无 code 字段，与 JSON failure 体系割裂。

### 4.1 定稿方案

SSE 流错误**保持现有格式**（`{"type": "error", "error": "字符串"}`），但字符串内容按语言切换：

| 触发场景 | 中文 SSE error | 英文 SSE error |
| --- | --- | --- |
| ModelConfigurationError | （来自异常 str） | The analysis service is not configured. |
| 其他异常兜底 | 分析流意外中断，请重试 | The analysis stream was interrupted. Please try again. |

### 4.2 不统一为 code 的原因

- SSE 是流式输出，前端 `lunming.js` L190 已按 `event.error` 字符串处理，改为 code 需改前端
- 流式错误无需差异化处理（如限流倒计时），字符串足够
- 中文版保持现有行为，英文版只需切换字符串

---

## 五、前端错误码映射策略

> 现状：前端**完全不读 error.code**，只读 `data.error?.message` 或 `data.message`。

### 5.1 中文前端（保持兼容）

- 继续只读 message，不读 code
- 现有行为不变

### 5.2 英文前端（W7 实施）

- **必须读 `error.code`**，按 code 映射英文消息
- 英文消息来源：本文档第三节 + `wise-oracle-copy-style-guide.md` 第 3.3 节
- 兜底：若 code 未识别，展示 `error.message`（后端返回的英文消息）

### 5.3 前端 code 映射表（W7 实施参考）

```javascript
const ERROR_MESSAGES_EN = {
  INVALID_JSON: "The request format was invalid. Please try again.",
  INVALID_INPUT: "Some fields were missing or invalid. Please check and try again.",
  ORACLE_WORDS_INSUFFICIENT: "Please enter exactly three words.",
  INVALID_ORACLE_NUMBER: "Each number must be between 0 and 999.",
  ORACLE_NUMBERS_ALL_ZERO: "The three numbers cannot all be zero.",
  INVALID_ORACLE_MODE: "Invalid input mode. Choose 'three words' or 'three numbers'.",
  SIGN_NOT_FOUND: "This oracle sign could not be found.",
  STROKE_NOT_FOUND: "Could not determine the stroke count. Please try different characters.",
  INVALID_DATE: "The date provided was invalid.",
  INVALID_SCENARIO: "The selected scenario is not supported.",
  CONTENT_NOT_FOUND: "The requested content is not available.",
  HUANGLI_NOT_FOUND: "Could not retrieve almanac data for this date.",
  EXPLANATION_NOT_FOUND: "No explanation was found for this item.",
  INVALID_BIRTH_DATA: "The birth data provided was invalid. Please check and try again.",
  MODEL_NOT_CONFIGURED: "The analysis service is not configured. Please contact support.",
  ANALYSIS_FAILED: "The analysis service is temporarily unavailable. Please try again later.",
  AI_DAILY_QUOTA_EXHAUSTED: "Your daily free analysis quota has been used up. Please try again tomorrow.",
  AI_GLOBAL_QUOTA_EXHAUSTED: "The analysis service quota has been exhausted today. Please try again tomorrow.",
  AI_RATE_LIMITED: "Too many requests. Please slow down.",
  AI_CONCURRENCY_LIMITED: "The analysis service is busy. Please try again shortly.",
  NOT_READY: "The service is not ready yet. Please try again later.",
  PAYLOAD_TOO_LARGE: "The request payload is too large.",
  NOT_FOUND: "The requested API endpoint does not exist.",
};
```

---

## 六、错误码命名规范

### 6.1 命名规则

- 全大写 + 下划线
- 按域分组：
  - `INVALID_*`：入参校验失败（400）
  - `*_NOT_FOUND`：资源缺失（404）
  - `AI_*`：AI 服务相关（429 限流 / 502 失败 / 503 未配置）
  - `ORACLE_*`：英文算事专用（400）
  - `HUANGLI_*`：黄历专用（404）
- 同一语义不拆分：`INVALID_DATE` 复用于格式错误和范围错误（消息文案区分）

### 6.2 新增 code 规则

- 新增 code 必须先更新本文档，再写代码
- code 一旦上线，不重命名（只增不改）
- message 文案可调整，code 不变

---

## 七、与 W3.2 的关系

> W3.2 产出 `zhugeshensuan/error_codes.py` 代码模块。

### 7.1 error_codes.py 职责

- 定义 code 常量（如 `INVALID_DATE = "INVALID_DATE"`）
- 提供 `get_message(code, lang)` 函数，返回中/英文消息
- 提供 `failure_with_code(code, lang, status, details)` 封装，替代直接调 `failure(code, message, status)`

### 7.2 迁移策略

- W3.2 创建 `error_codes.py`，定义本文档所有 code
- 现有 `failure(code, message, status)` 调用**保持不变**（向后兼容）
- 新增英文 API 调用 `failure_with_code(code, "en", status)`，自动取英文消息
- 中文 API 逐步迁移为 `failure_with_code(code, "zh", status)`（非阻塞，可后续做）

---

## 八、参考来源

- `zhugeshensuan/api_utils.py`：failure 函数签名
- `zhugeshensuan/app.py` L157-167：通用错误码
- `zhugeshensuan/blueprints/huangli_api.py`：黄历错误码
- `zhugeshensuan/blueprints/divination.py`：算事错误码
- `zhugeshensuan/blueprints/lunming_api.py`：论命错误码
- `zhugeshensuan/ai_usage.py` L17-22/L138-170：AI 限流错误码
- `docs/business/wise-oracle-copy-style-guide.md` 第 3.3 节：英文错误消息
- `docs/business/wise-oracle-english-product-spec.md` 第 2.1 节：英文算事校验规则

---

## 九、修订记录

| 日期 | 变更 | 变更人 |
| --- | --- | --- |
| 2026-06-30 | 初稿创建，基于代码扫描（21 个现有 code）+ 英文版新增 5 个 code（INVALID_INPUT/INVALID_ORACLE_MODE/ORACLE_WORDS_INSUFFICIENT/INVALID_ORACLE_NUMBER/ORACLE_NUMBERS_ALL_ZERO）+ CONTENT_NOT_FOUND | 助手起草，待用户审阅 |
