# 需重新翻译的英文签文条目

基于权威简体签文（`oracle_signs_authoritative_sc.csv`）与当前英文翻译（`oracle_signs_en.json`）的比对，筛选出因中文签文修正导致**意义变化很大或产生歧义**的条目。

修正涉及 23 签（A类13 + B类9 + C类1），其中标点修订3签（4/25/26）文字不变，不影响翻译。

---

## 一、必须重新翻译（4签 · 意义反转或根本性变化）

### 第 96 签
- **修正**：`乡聚首` → `他乡聚首`（B类）
- **当前英文**：`Laughing heartily, gathering in the hometown, / Each joyful and healthy.`
- **问题**：英文 `in the hometown`（在故乡）对应旧文「乡聚首」，新文为「他乡聚首」（在异乡聚首），**故乡↔异乡反转**。
- **附加变化**：删除末尾「和」字。

### 第 142 签
- **修正**：`出战时` → `出战征`，`获馈` → `获丑`（B类）
- **当前英文**：`Advantage lies in engaging battle from one's own state, / One is rewarded in the royal court.`
- **问题**：
  - `engaging battle` 对应「出战」，但「时」（时机）→「征」（征伐），语义重心从"出战的时机"变为"出兵征伐"。
  - `rewarded`（获赏）对应旧文「获馈」，新文「获丑」意为"俘获敌人"，**获赏↔俘获反转**。

### 第 146 签
- **修正**：`花开春又离` → `花开春又逢`（A类）
- **当前英文**：`Flowers bloom, yet spring again must go.`
- **问题**：英文 `spring again must go`（春天又离去）对应旧文「春又离」，新文「春又逢」意为"春天又相逢/重来"，**离去↔重逢反转**。

### 第 260 签【已撤销 — 无需重译】
- **原分析（有误）**：曾认为应将 `轮回不能免，永落深坑堑` 改为 `轮回不能永落深坑堑`（去掉「免」字，意为"不会永远沉沦"）。
- **用户决定（2026-07-05）**：**保留「免」字，尊重原文**。权威文本确认为 `轮回不能免，永落深坑堑`（意为"轮回无法避免，永远落入深坑"）。
- **依据**：[generate_authoritative_signs.py:78-81](file:///v:/诸葛神算V4/scripts/generate_authoritative_signs.py#L78-L81) 注释明确"保留「免」字"；CSV、数据库 gua/gua_hant 表均一致。
- **当前英文**（已于 2026-07-05 重译）：`The cycle of rebirth cannot be escaped, / Forever falling into deep pits and trenches.` —— 忠实翻译了"轮回不能免，永落深坑堑"，**正确，无需再改**。

### 第 332 签
- **修正**：`时边多艰` → `时变多艰`（B类）
- **当前英文**：`Times are fraught with hardship;`
- **问题**：英文 `Times are fraught with hardship` 模糊对应，但「时边」（时局边患）→「时变」（时局变化），语义从"边患"变为"变局"，**产生歧义**。

---

## 二、建议重新翻译（7签 · 意义有明显变化）

### 第 192 签
- **修正**：`事苦羁留` → `事若羁留`（A类）
- **当前英文**：`Matters linger, labor in vain,`
- **问题**：「苦」（辛苦地）→「若」（如果），从"辛苦被困"变为"如果被困"，英文 `labor in vain` 需改为条件句。

### 第 212 签
- **修正**：`明月在人间` → `明月出人间`（A类）
- **当前英文**：`The bright moon is here among men.`
- **问题**：「在」（存在于）→「出」（升起/出现于），英文 `is here among men` 需改为 `rises from among men`。

### 第 235 签
- **修正**：`道路狂招呼` → `道路在招呼`（A类）
- **当前英文**：`Loud calls along the road, yet not a ripple of strife.`
- **问题**：「狂」（狂妄地）→「在」（正在），英文 `Loud calls` 带有"狂妄"色彩，需改为中性"正在招呼"。

### 第 263 签
- **修正**：`家食翻嫌太贵` → `家食翻嫌太费`（A类）
- **当前英文**：`Home food seems too costly;`
- **问题**：「贵」（昂贵）→「费」（耗费/浪费），英文 `too costly` 需改为 `too wasteful` 或 `too costly to maintain`。

### 第 302 签
- **修正**：`锦帆前程` → `锦片前程`（A类）
- **当前英文**：`silken sails ahead, a splendid flow.`
- **问题**：「锦帆」（锦缎帆船）→「锦片」（锦绣一片），英文 `silken sails` 需改为 `a splendid prospect`（锦绣前程）。

### 第 320 签
- **修正**：`一掌能着` → `一掌能看`（A类）
- **当前英文**：`The mystic gate's subtle art lies within one palm's light.`
- **问题**：「着」（着落/掌握）→「看」（看透/看穿），英文未直接译出此动词，需补充 `can be seen at a glance`。

### 第 331 签
- **修正**：`遭研妒` → `遭奸妒`（A类）
- **当前英文**：`Every move meets envy and spite.`
- **问题**：「研」（研究？错字）→「奸」（奸诈），英文 `envy and spite` 未体现"奸诈"，需补充 `malicious envy`。

---

## 三、可选重新翻译（4签 · 意义有细微变化）

| 签号 | 修正 | 当前英文要点 | 变化说明 |
|------|------|------------|---------|
| 124 | `新，照两人` → `亲照两人` | `newly polished, Shining on two persons` | 新镜→亲照，需改 `newly` → `intimately` |
| 144 | `山一重水` → `水一重山` + `壸中有别天` → `壶中别有天` | `Mountain after mountain, river after river` + `Beyond the vase` | 山水顺序颠倒；`壸`(宫中路)→`壶`(葫芦) |
| 213 | `重关` → `重门` | `breaks through many passes` | `passes`→`gates`，近义可保留 |
| 226 | `拨云` → `披云` | `Parting the clouds` | `Parting`(拨开)→`Draped in`(披着)，细微差异 |

---

## 四、无需重新翻译（7签 · 异体字/同义替换）

| 签号 | 修正 | 原因 |
|------|------|------|
| 14 | `却藏拙`→`藏却拙`，`蹉`→`嗟` | 语序调整+异体字，英文语义不变 |
| 276 | `无虑`→`无虞` | 同义词，英文 `without worry` 仍准确 |
| 313 | `伏軏`→`伏轭` | 异体字，英文 `yoke` 仍准确 |
| 366 | `却遇见`→`却遇` | 删「见」，英文 `meet` 仍准确 |
| 373 | `火毐`→`火毒` | 异体字，英文 `poison of fire` 仍准确 |
| 380 | `膏梁`→`膏粱` | 异体字，英文 `Rich meats` 仍准确 |
| 382 | `一声雷`→`一声雷轰` | 近义扩充，英文 `thunderclap` 仍准确 |

---

## 汇总

| 优先级 | 签数 | 签号 |
|--------|------|------|
| 必须重新翻译 | 4 | 96, 142, 146, 332 |
| 建议重新翻译 | 7 | 192, 212, 235, 263, 302, 320, 331 |
| 可选重新翻译 | 4 | 124, 144, 213, 226 |
| 无需重新翻译 | 8 | 14, 260, 276, 313, 366, 373, 380, 382 |
