# 中文定场诗右起竖排修复验收

- **日期：** 2026-07-16
- **台账任务：** UI-001
- **状态：** 本地完成，随下一生产镜像部署

## 问题与口径

算事、论命和黄历页面的定场诗原本把模板中的第一句排在最左侧。古典中文竖排应满足两个独立方向：

1. 每一列文字自上而下；
2. 各列从右向左，第一句位于最右侧。

不能给整个页面设置 RTL，否则会影响导航、表单和普通横排正文。本次只调整 `.poetry-container` 的列顺序，`.poem-line` 继续使用 `writing-mode: vertical-rl`。

## 实施范围

- `frontend/static/css/style.css`：桌面端 `.poetry-container` 改为 `flex-direction: row-reverse`。
- `frontend/static/css/style_mobile.css`：移动端采用相同右起列序。
- `frontend/templates/huangli.html`：动画延迟改为第一句先出现，顺着右到左阅读方向展开。
- `tests/test_frontend_contract.py`：覆盖中文首页、算事、论命和黄历共用组件，以及桌面/移动两份样式。

## 验收证据

真实 Chrome 计算布局结果：

| 页面 | 视口 | 第一句 X | 第二句 X | 结果 |
| --- | ---: | ---: | ---: | --- |
| 算事 | 1280px | 868 | 793 | 第一句在右 |
| 论命 | 1280px | 718 | 643 | 第一句在右 |
| 黄历 | 1280px | 718 | 644 | 第一句在右 |
| 算事 | 390px | 271 | 200 | 第一句在右 |
| 论命 | 390px | 271 | 200 | 第一句在右 |
| 黄历 | 390px | 271 | 201 | 第一句在右 |

所有页面的计算样式均为 `flex-direction: row-reverse`，第一句横坐标大于第二句；每句文字自身仍为竖排。

自动化门禁：

- 新增定向契约：1/1 通过。
- `tests/test_frontend_contract.py`：15/15 通过。
- 全量 pytest：448/448 通过，`ResourceWarning` 与 `PytestUnraisableExceptionWarning` 均作为错误处理。
- Black：89 个 Python 文件通过。
- Ruff：通过。
- `git diff --check`：通过。

## 生产验收

本修复会被打入与服务器文章上传功能相同的下一生产镜像。部署后强制刷新算事、论命和黄历页面，确认第一句位于最右侧即可关闭生产验收。
