# 黄历英文改造后续指导

## 当前结论

黄历英文不在本轮上线。本轮只完成繁体动态数据闭环，并为英文阶段留下可复用的术语来源和实现路线。

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
