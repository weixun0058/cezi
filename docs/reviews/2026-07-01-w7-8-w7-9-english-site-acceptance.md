# W7.8 / W7.9 英文站响应式与可访问性验收

日期：2026-07-01

## 结论

W7.8 响应式与可访问性实现通过；W7.9 页面、交互和错误状态验收通过。
英文签文数据另有一项跨工作包内容风险，需回到 W2 内容审校处理，不能依赖前端裁剪。

## 本轮修复

- 全英文页增加 `Skip to main content` 和可聚焦正文锚点
- 为链接、按钮、表单控件和 `summary` 增加统一 `:focus-visible` 样式
- Ask the Oracle 模式切换补齐 tab/tabpanel 关联、roving tabindex 和方向键/Home/End 操作
- Birth Chart 性别控件改为 `fieldset/legend`，加载状态补 `role=status`
- Daily Almanac 日期和场景使用显式 label，错误状态使用 `role=alert` 和 `Error:` 文本
- 390px 下三词、三数字输入改为单列；按钮、标签和选项卡触摸高度至少 44px
- 修复 Birth Chart 英文流中的中文农历日期和未知时辰限制说明泄漏

## 浏览器矩阵

桌面 1440×900 与移动 390×844 均检查以下路由：

- `/`
- `/ask-oracle`
- `/daily-almanac`
- `/birth-chart-reading`
- `/articles`
- `/articles/how-oracle-signs-work`
- `/privacy`
- `/terms`
- `/disclaimer`
- `/about`
- `/contact`

所有页面满足：HTTP 200、唯一 H1、`lang=en`、无重复 ID、无未标记表单控件、
无横向溢出、无正文裁切、存在正文跳转链接。

## 交互验收

- Ask the Oracle / Three Words：`LOVE / WORK / FATE` 返回 Sign No. 88
- Ask the Oracle / Three Numbers：`314 / 159 / 265` 返回 Sign No. 33
- Oracle 选项卡：ArrowLeft/ArrowRight 键可切换并移动焦点
- Daily Almanac：日期切换成功；wedding、moving、business_opening、travel、signing、haircut 六场景均成功返回英文状态
- Birth Chart：出生时间未知会禁用时间输入；英文基础盘不再泄漏中文农历日期或限制说明
- API 断开：Daily Almanac 显示 `Error: Failed to fetch`，并使用 `role=alert`

## 自动化验证

- `tests/test_english_frontend_contract.py` 新增跳转链接、控件标签、tab/tabpanel、
  fieldset/legend、焦点和移动端契约
- `tests/test_birth_chart_english.py` 新增英文农历日期和限制说明回归测试
- 计划中原命令引用的 `tests/test_english_routes.py` 不存在；实际使用现有英文前端契约测试和完整测试套件

## 跨工作包内容风险

`data/content/oracle_signs_en.json` 的 384 条签文中：

- 358 条仍包含 `hexagram` 表述
- 143 条仍包含 favorable/unfavorable/auspicious sign 等吉凶分级表述
- 308 条匹配具体健康建议关键词

这些内容与 D16 及非专业建议边界冲突。字段级 `fortune/gua_type` 已被 API 剔除，但正文仍会展示。
建议建立 W2.8“384 条英文签文边界重审”任务，通过数据层审校解决，不在前端做脆弱的字符串过滤。
