# 黄历英文改造后续指导

## 当前结论

> **更新（2026-07-12）：** 英文黄历已实现并接通 API，本文档从"后续指导"转为"实现参考"。
>
> 英文 Daily Almanac 已在 W5 阶段完成实现：`zhugeshensuan/huangli_english.py` 提供翻译服务，`zhugeshensuan/blueprints/huangli_en_api.py` 提供 `/api/en/daily-almanac` 和 `/api/en/week-almanac` 端点，前端 `daily_almanac.js` 已接通 API（非 Coming soon 降级）。`data/content/huangli_terms_en.json` 和 `huangli_scenarios_en.json` 已生成，覆盖 39 活动类别、6 场景判断、20 个审校神煞。`tests/test_huangli_english.py` 覆盖翻译函数、活动流水线、场景判断和 API 契约，含 2026 全年无中文泄漏回归测试。

英文黄历已上线。本文档保留术语来源和实现路线作为参考。

## 术语来源

项目内 `frontend/static/js/lunar.js` 是 6tail lunar 的 JavaScript 版本，已包含 `I18n` 与英文 messages。后续英文黄历术语应优先从该文件的英文段抽取候选词，再进入人工审校。

可优先抽取的类别：

- `sx.*`：生肖，例如 Rat、Ox、Tiger、Rabbit。
- `yj.*`：宜忌事项，例如 marriage、travel、trading 等候选表达。
- `jq.*`：二十四节气。
- `sn.*`：神煞。
- `ps.*` / `bg.*`：方位与八卦方位。

## 执行路线

1. 编写一次性抽取脚本，从 `frontend/static/js/lunar.js` 的 `I18n` 英文 messages 中提取黄历相关 key。
2. 生成 `docs/business/huangli-english-termbase-draft.md`，字段为：中文源词、6tail 英文候选、产品英文候选、使用场景、备注。
3. 人工审校后，把定稿词表写入项目内黄历本地化层或独立 JSON 词表。
4. 英文 API 上线前，必须统一英文免责声明、产品定位和术语风格，避免直接暴露库级生硬翻译。

## 不采用的方案

- 不把 6tail JS 运行库接入 Flask 后端作为跨进程服务。
- 不直接把 `lunar.js` 英文输出当成最终产品英文。
- 不修改 `site-packages/lunar_python` 或 `frontend/static/js/lunar.js` 来维护项目语言。
