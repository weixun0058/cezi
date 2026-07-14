# 架构决策：签文与彭祖百忌数据源迁移

> 决策日期：2026-07-13
> 状态：已实施
> 决策人：项目维护者
> 影响范围：后端数据层、部署流程、数据维护流程

## 一、决策摘要

**签文（gua/gua_hant）和彭祖百忌（pzbj/pzbj_hant）数据源从 SQLite 数据库（reference.db）迁移为 JSON 文件内存加载。**

reference.db 从运行时的"签文+彭祖百忌+汉字笔画"三合一数据库，降级为运行时仅用于汉字笔画查询的数据库。为保持历史构建产物可重建，文件中仍保留 `gua/gua_hant/pzbj/pzbj_hant` 表，但应用运行时不读取这些表。

## 二、背景与问题

### 原架构

```
权威数据源                          运行时数据源
CSV签文诗 ──┐
reinterpreted.json ──┤── backfill_reinterpreted_to_db.py ──→ reference.db ──→ 内存索引
pzbj.json ──┘                                                      (gua/gua_hant/pzbj/pzbj_hant)
```

签文和彭祖百忌的权威数据在 JSON 文件中，运行时却从 reference.db 读取。需要 `backfill_reinterpreted_to_db.py` 脚本将 JSON 同步到数据库。

### 暴露的问题

1. **数据不一致**：JSON 修改后未及时 backfill，导致数据库内容过时。第 120 签重跑后新解读只在 JSON 中，数据库仍是旧解读，用户看到的繁体签文是过时内容。

2. **字段结构不匹配**：reinterpreted.json 已删除 fortune/gua_type 字段（9 字段），数据库 gua 表仍是 11 字段（fortune/gua_type 为 NOT NULL），backfill 脚本无法正常运行。

3. **维护成本高**：改签文需要"改 JSON → 跑 backfill → 重启"三步，多一步导进导出纯属冗余。

4. **数据源混淆**：数据库被误认为"原始数据源"，实际权威数据在 JSON/CSV 中。已有文档反复强调"数据库是派生物"，但仍发生混淆。

## 三、决策方案

### 新架构

```
权威数据源                          运行时数据源
CSV签文诗（异体字）──┐
reinterpreted.json（简体）──┤── build_hant_json.py（离线）──→ reinterpreted_hant.json ──┐
                         │                                                        ├──→ 内存索引
                         └──→ pzbj_hant.json ←── build_hant_json.py ←── pzbj.json ──┘    (gua_index/gua_hant_index/pzbj/pzbj_hant)

reference.db（运行时仅读取 hanzi）──→ get_stroke_count()
```

### 分层数据源

| 数据 | 运行时数据源 | 权威来源 | 加载方式 |
|------|------------|---------|---------|
| 简体签文 | `oracle_signs_reinterpreted.json` | 同左（DeepSeek 生成） | 启动时 JSON → 内存 |
| 繁体签文 | `oracle_signs_reinterpreted_hant.json` | sign_text 从 CSV 取，解读从简体 OpenCC s2t 转换 | 启动时 JSON → 内存 |
| 简体彭祖百忌 | `pzbj.json` | 同左 | 启动时 JSON → 内存 |
| 繁体彭祖百忌 | `pzbj_hant.json` | 从 pzbj.json OpenCC s2t 转换 | 启动时 JSON → 内存 |
| 汉字笔画 | `reference.db` hanzi 表 | kanxi_dict.db（构建时导入） | 运行时 SQLite 只读查询 |
| 英文签文 | `oracle_signs_en.json` | 同左（DeepSeek 翻译） | 启动时 JSON → 内存 |

### 繁体签文的特殊处理

**关键约束**：`oracle_signs_authoritative_tc.csv` 是权威繁体签文，包含异体字（如奥/别/説/踪/团/钩等），不能用 OpenCC s2t 转换（会破坏异体字）。

**解决方案**：
- `sign_text` 字段：从 CSV 权威繁体读取（保留异体字）
- 其他字段（interpretation1/career/wealth/love/health/study/general）：用 OpenCC s2t 从简体 JSON 转换

**验证**：384/384 签 sign_text 与 CSV 权威完全一致，异体字全部保留。

## 四、涉及代码变更

| 文件 | 变更 |
|------|------|
| `scripts/build_hant_json.py` | 新建：离线生成繁体签文和彭祖百忌 JSON |
| `zhugeshensuan/config.py` | 新增 SIGNS_SIMP_PATH / SIGNS_HANT_PATH / PZBJ_SIMP_PATH / PZBJ_HANT_PATH 配置 |
| `zhugeshensuan/database.py` | `_load_gua_index` → `_load_signs_from_json`；`_load_pzbj` → `_load_pzbj_from_json`；移除 GUA_COLUMNS |
| `zhugeshensuan/app.py` | Database 初始化传入 JSON 路径配置 |

## 五、数据维护流程

### 修改签文解读

```
1. 修改 oracle_signs_reinterpreted.json（简体）
2. 运行 python scripts/build_hant_json.py（同步繁体）
3. 重启应用即生效
```

无需 backfill 到数据库。

### 修改签文诗 sign_text

```
1. 修改 oracle_signs_authoritative_sc.csv（简体）和 oracle_signs_authoritative_tc.csv（繁体）
2. 修改 oracle_signs_reinterpreted.json 中的 sign_text（简体）
3. 运行 python scripts/build_hant_json.py（繁体 sign_text 从 CSV 取）
4. 重启应用即生效
```

## 六、reference.db 的角色变化

| 变化前 | 变化后 |
|--------|--------|
| 签文 + 彭祖百忌 + 汉字笔画均参与运行时读取 | 运行时仅读取汉字笔画；旧内容表只为可重建兼容保留 |
| 运行时必读 | 运行时仅笔画查询使用 |
| 改签文需 backfill | 改签文无需操作数据库 |
| 11 字段（含 fortune/gua_type） | 字段结构不变，但签文数据不再被读取 |

**部署注意**：reference.db 仍需打包到 Docker 镜像中（汉字笔画查询依赖），但签文和彭祖百忌数据不再依赖它。

## 七、禁止事项

1. **禁止将 reference.db 作为签文/彭祖百忌的数据源**。权威数据在 JSON 文件中。
2. **禁止用 OpenCC s2t 转换 sign_text**。繁体签文 sign_text 必须从 CSV 权威读取，保留异体字。
3. **禁止在运行时使用 OpenCC**。OpenCC 仅用于离线构建脚本 `build_hant_json.py`。
4. **禁止恢复 backfill_reinterpreted_to_db.py 作为签文同步手段**。该脚本已废弃，保留仅用于历史参考。
5. **禁止在 GUA_COLUMNS 或任何运行时代码中恢复 fortune/gua_type 字段**。

## 八、验证记录

2026-07-13 验证通过：
- 简体算卦：78 签正常，无 fortune/gua_type 字段
- 繁体算卦：78 签正常，异体字保留（動静兩三番，終朝事必嘆）
- 黄历彭祖百忌：繁体文本正常显示
- sign_text 一致性：384/384 与 CSV 权威完全一致
- 无 JS 错误
