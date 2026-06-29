# 英文产品规格

> **文档定位**：W0.1 / W0.2 / W0.3 / W0.4 / W0.6 产出。定义英文版的 URL 信息架构、三大工具页交互、上线范围。
> **创建日期**：2026-06-30
> **状态**：W0 定稿，待用户审阅
> **硬约束引用**：D13（沿用 GUA_COLUMNS）、D14（剔除 fortune/gua_type）、D15（JSON 内存加载）、D16（卦属/吉凶不展示）、D17（解签定位为 interpretation）

---

## 一、英文信息架构（W0.1）

### 1.1 URL 总表

| 页面 | URL | SEO 标题 | meta description |
| --- | --- | --- | --- |
| 首页 | `/` | Wise Oracle — Chinese Cultural Divination & Almanac | Draw an oracle sign, read the daily Chinese almanac, and reflect on your birth chart through traditional Chinese cultural wisdom. |
| 算事 | `/ask-oracle` | Ask the Oracle — Free Chinese Oracle Sign Reading | Hold a question in mind and draw a Zhuge Oracle sign for cultural reflection. Not fortune telling — a mirror for self-examination. |
| 黄历 | `/daily-almanac` | Daily Chinese Almanac — Favorable Activities & Solar Terms | Today's Chinese almanac: favorable and unfavorable activities, lunar date, solar term, and zodiac. |
| 论命 | `/birth-chart-reading` | Birth Chart Reading — BaZi Cultural Self-Reflection | Explore your BaZi birth chart as a cultural framework for self-reflection. Not destiny prediction. |
| 文章列表 | `/articles` | Articles — Chinese Divination Culture & Almanac Traditions | Essays on Chinese oracle signs, almanac traditions, and cultural self-reflection practices. |
| 文章详情 | `/articles/<slug>` | （按文章标题） | （按文章摘要） |
| 隐私政策 | `/privacy` | Privacy Policy — Wise Oracle | How Wise Oracle handles your data. |
| 使用条款 | `/terms` | Terms of Use — Wise Oracle | Terms governing use of Wise Oracle. |
| 免责声明 | `/disclaimer` | Disclaimer — Wise Oracle | Wise Oracle is for entertainment and cultural exploration only. |
| 关于 | `/about` | About — Wise Oracle | The story and mission behind Wise Oracle. |
| 联系 | `/contact` | Contact — Wise Oracle | Get in touch with the Wise Oracle team. |

### 1.2 路由兼容策略

- `/` 作为英文首页（D2 已确认）
- 旧中文路由 `/huangli`、`/suanshi`、`/lunming` 保持 301 到 `/zh-hans/almanac`、`/zh-hans/divination`、`/zh-hans/bazi`
- 英文 API 统一走 `/api/en/*` 前缀（D12 已确认）
- 英文前端路由使用 `/ask-oracle`、`/daily-almanac`、`/birth-chart-reading`（不复用中文拼音路径）

### 1.3 每页定义

#### 首页 `/`

- **页面目的**：英文入口，介绍三大工具，引导用户进入
- **主按钮**：Ask the Oracle（→ `/ask-oracle`）
- **次级按钮**：Daily Almanac、Birth Chart Reading
- **responsible-use 位置**：页面底部

#### 算事 `/ask-oracle`

- **页面目的**：用户心中持一问题，输入三个词或三个数字，获取签文与诠释
- **主按钮**：Draw My Sign
- **次级按钮**：Draw Another Sign（重新测算）
- **responsible-use 位置**：解签内容下方

#### 黄历 `/daily-almanac`

- **页面目的**：展示当日黄历宜忌、农历日期、节气、生肖
- **主按钮**：View This Week
- **次级按钮**：View Details（场景详情）
- **responsible-use 位置**：页面底部

#### 论命 `/birth-chart-reading`

- **页面目的**：输入出生信息，生成八字命盘，AI 诠释
- **主按钮**：Generate My Chart
- **次级按钮**：Ask About This（追问，付费功能待定——Deep Reading 暂时冻结）
- **responsible-use 位置**：结果下方
- **注意**：D11 已确认保留完整入口（2026-06-30）

#### 文章列表 `/articles`

- **页面目的**：展示英文 SEO 文章列表，引导用户了解中国文化背景
- **主按钮**：Browse Articles
- **次级按钮**：无
- **responsible-use 位置**：页面底部

#### 文章详情 `/articles/<slug>`

- **页面目的**：展示单篇英文文章，提供文化背景、工具使用指引、内链到工具页
- **主按钮**：无（内容页）
- **次级按钮**：Try Ask the Oracle / View Today's Almanac（内链到工具页）
- **responsible-use 位置**：文章末尾

#### 隐私政策 `/privacy`

- **页面目的**：说明数据收集、Cookie、AI 输入处理、用户权利
- **主按钮**：无
- **次级按钮**：无
- **responsible-use 位置**：N/A（本页即合规页）

#### 使用条款 `/terms`

- **页面目的**：说明服务条款、免责声明、禁止滥用
- **主按钮**：无
- **次级按钮**：无
- **responsible-use 位置**：N/A（本页即合规页）

#### 免责声明 `/disclaimer`

- **页面目的**：明确不提供医疗/法律/财务/心理治疗建议
- **主按钮**：无
- **次级按钮**：无
- **responsible-use 位置**：N/A（本页即合规页）

#### 关于 `/about`

- **页面目的**：建立信任，说明网站聚焦东方传统文化，说明算法与 AI 的关系
- **主按钮**：Try Ask the Oracle
- **次级按钮**：Contact
- **responsible-use 位置**：页面底部

#### 联系 `/contact`

- **页面目的**：提供联系方式，收集用户反馈
- **主按钮**：Send Message
- **次级按钮**：无
- **responsible-use 位置**：页面底部

---

## 二、Ask the Oracle 交互（W0.2）

### 2.1 两种输入模式

> **设计原则**：用户不在输入框中键入问题文本，显著减少敏感问题文本的收集和定向回答风险（三个词仍可能组成敏感表达，不能宣称完全消除风险），同时保留诸葛神算"三字起卦"的"三"母题与神秘仪式感。原"自由提问"模式已取消。

#### 引导语

引导语分为公共前半句和两套模式文案。

**公共前半句（两种模式共用）**：

```text
Hold one question quietly in mind. Do not type it. Take a slow breath.
```

**Three Words 模式文案**：

```text
Then enter the first three words that come to you. They may be connected to your question—or not. Do not overthink them.
```

**Three Numbers 模式文案**：

```text
Then enter three numbers between 0 and 999. Let them come freely—the first ones that appear are the right ones. Do not overthink them.
```

#### 模式一：三个词（Three Words）

- 用户心中持一问题（不输入），再输入三个英文词
- 每个词按 A=1..Z=26 对字母求和，复用源书 `stroke_digit` 规则（和对 10 取模，余 0 则取 1）得到数字 d1、d2、d3（均 1-9），对应中文"三字→笔画数→笔画位"的神秘变换
- 系统组合成三位数 N = 100×d1 + 10×d2 + d3（即源书 `compose_three_character_number`）
- 映射到 1-384：r = ((N-1) mod 384) + 1（即源书 `reduce_to_start_index`）
- **示例**：LOVE=12+15+22+5=54→4，WORK=23+15+18+11=67→7，FATE=6+1+20+5=32→2 → N=472 → Sign #88
- **校验规则**：
  - 必须输入三个词（以空白分隔）
  - 每词至少含 1 个字母
  - 词数不足返回 `ORACLE_WORDS_INSUFFICIENT`
  - 空输入返回 `INVALID_INPUT`
- **算法实现**：复用 `scripts/derive_original_oracle_signs.py` 的 `stroke_digit` + `compose_three_character_number` + `reduce_to_start_index`

#### 模式二：三个数字（Three Numbers）

- 用户输入三个 0-999 的数字，作为无词汇门槛的起卦方式
- 系统拼接为九位数种子 seed = d1×1,000,000 + d2×1,000 + d3（即 `compose_english_three_number_seed`，英文产品专用，非源书方法）
- 映射到 1-384：r = ((seed-1) mod 384) + 1
- **页面输入约束**：
  - 页面明确提示"三组数字不能全为 0"
- **校验规则**：
  - 每个数字范围 0-999
  - 三组数字不能全为 0
  - 超范围返回 `INVALID_ORACLE_NUMBER`
  - 全零返回 `ORACLE_NUMBERS_ALL_ZERO`
- **算法实现**：`scripts/derive_original_oracle_signs.py` 的 `compose_english_three_number_seed` + `reduce_to_start_index`

### 2.2 结果字段（D13 已确认：沿用 GUA_COLUMNS）

英文 API 响应字段（D14 已确认：剔除 fortune/gua_type，共 9 字段）：

| 字段 | 英文标签 | 说明 |
| --- | --- | --- |
| sign_number | Sign Number | 签号 1-384 |
| sign_text | Oracle Sign Text | 签文诗句（英文翻译） |
| interpretation1 | Overall Interpretation | 总体诠释 |
| career | Career | 事业视角 |
| wealth | Wealth | 财富视角 |
| love | Relationships | 感情视角 |
| health | Well-being | 健康视角 |
| study | Learning | 学业视角 |
| general | General Guidance | 综合指引 |

**不展示的字段**（D14/D16 硬约束）：

- `fortune`（吉凶分级）：加载时剔除
- `gua_type`（卦属）：加载时剔除

### 2.3 未译签文 fallback

若 `interpretation1` 含 CJK 字符或必填字段为空：

```text
This sign's English translation is under review.
```

### 2.4 交互流程

```
1. 显示引导语（Hold one question quietly in mind...）
2. 用户选择输入模式（Three Words / Three Numbers）
3. 输入并提交
4. 【Three Words】依次动画展示变换过程：LOVE → 54 → 4 / WORK → 67 → 7 / FATE → 32 → 2，
   再显示 "The three words form 472. Oracle Sign #88"
4a. 【Three Numbers】动画展示数字拼接过程：314 | 159 | 265 → 314159265，
    再显示 "The three numbers form 314159265. Oracle Sign #33"
5. 显示签号（"Oracle Sign #N"）
6. 逐字显现签文（typeWriter 动画，复用 main.js）
7. 显示 "View Interpretation" 按钮
8. 点击后显示总体诠释 + 6 个分项
9. 显示 "Draw Another Sign" 按钮（重新测算）
```

**变换过程透明度**：输入前不展示公式，保留仪式感；提交后动画展示变换过程（Three Words 展示每词的字母求和与取位；Three Numbers 展示三组数字拼接为九位种子）；旁边提供折叠项 "How were these numbers formed?" 供好奇用户展开复算。

### 2.5 数据加载（D15 已确认）

- 英文签文从 `data/content/oracle_signs_en.json` 加载到内存字典
- 启动时加载一次，运行期只读
- 加载时剔除 fortune/gua_type 字段（D14）
- 不入数据库，中文仍走 `database.py`
- 内存字典键为 `sign_number`（int），值为 9 字段 dict

---

## 三、Birth Chart Reading 边界（W0.3）

### 3.1 页面命名与定位

- **页面名**：Birth Chart Reading
- **定位**：BaZi-inspired cultural self-reflection
- **不用**：fate guarantee、life prediction、destiny reading

### 3.2 功能边界

1. **基础盘生成**：现有八字计算仅作基础盘生成（天干地支、五行、十神）
2. **AI 解释层**：AI 仅作解释层，不输出确定性结论
3. **免费/付费边界**：基础盘免费；AI 深度诠释为 `Wise Oracle Deep Reading`（付费，待 D8 定价）

### 3.3 AI prompt 边界

详见 `docs/business/wise-oracle-ai-prompt-boundaries.md`。核心红线：

- 不输出医疗、法律、财务、心理治疗、生育、死亡、灾难、重大人生决策的确定性结论
- 定位为 reflection prompt，不是 advice

### 3.4 D11 待确认

是否弱化 Birth Chart Reading 入口（隐私合规复杂度）。若弱化：

- 首页不直接展示入口，改为文章页引导
- 第一轮上线仅做基础盘，不做 AI 深度诠释

---

## 四、Daily Chinese Almanac 边界（W0.4）

### 4.1 页面命名

- **页面名**：Daily Chinese Almanac
- **禁用**：Yellow Calendar
- **谨慎使用**：Daoist Auspicious Calendar（仅在解释文章中使用）

### 4.2 标签

| 中文 | 英文标签 |
| --- | --- |
| 宜 | Favorable Activities |
| 忌 | Unfavorable Activities |
| 农历日期 | Lunar Date |
| 节气 | Solar Term |
| 生肖 | Chinese Zodiac |

### 4.3 场景

第一轮支持的黄历场景：

| 中文场景 | 英文场景 | 场景码 |
| --- | --- | --- |
| 嫁娶 | wedding | wedding |
| 搬家 | moving | moving |
| 开市 | business opening | business_opening |
| 出行 | travel | travel |
| 签约 | signing | signing |
| 理发 | haircut | haircut |

### 4.4 术语来源

- 优先从 `frontend/static/js/lunar.js` 的 6tail 英文 messages 抽取候选（W1.1）
- 人工审校后定稿，不直接使用库级生硬翻译
- 详见 `docs/business/huangli-english-localization-guidance.md`

---

## 五、英文上线范围（W0.6）

### 5.1 第一轮上线

| 类别 | 页面/功能 | 状态 |
| --- | --- | --- |
| 工具页 | `/`（首页） | 上线 |
| 工具页 | `/ask-oracle`（算事） | 上线 |
| 工具页 | `/daily-almanac`（黄历） | 上线（待用户核实黄历上线条件） |
| 工具页 | `/birth-chart-reading`（论命） | 上线（D11 已确认保留完整入口） |
| 内容页 | `/articles` + ≥10 篇文章 | 上线 |
| 合规页 | `/privacy`、`/terms`、`/disclaimer` | 上线 |
| 信息页 | `/about`、`/contact` | 上线 |
| 商业化 | 赞助/付费墙 | 赞助占位；付费墙暂时冻结（Deep Reading 待深度思考） |
| SEO | sitemap.xml、robots.txt | 上线 |

### 5.2 第一轮不上线

| 功能 | 原因 |
| --- | --- |
| 完整会员系统 | 第一阶段不做 |
| 复杂订单管理 | 第一阶段不做 |
| 人工咨询 | 第一阶段不做 |
| 多语言文章 | 第一阶段仅英文 |
| 真实支付 | 等待平台政策核验 |

---

## 六、字段结构定稿（D13/D14）

### 6.1 英文签文字段（D13 已确认：沿用 GUA_COLUMNS）

原始 JSON 字段（11 个）：

```
sign_number, fortune, gua_type, sign_text, interpretation1, career, wealth, love, health, study, general
```

加载到内存后字段（9 个，D14 已确认：剔除 fortune/gua_type）：

```
sign_number, sign_text, interpretation1, career, wealth, love, health, study, general
```

### 6.2 API 响应结构

成功响应：

```json
{
  "success": true,
  "sign_number": 24,
  "sign_text": "Intent and diligent, with a concerned heart, seek peace and guard your comings and goings.",
  "interpretation1": "Traditionally, this sign suggests...",
  "career": "One cultural reading is...",
  "wealth": "...",
  "love": "...",
  "health": "...",
  "study": "...",
  "general": "..."
}
```

错误响应（超范围）：

```json
{
  "success": false,
  "code": "INVALID_ORACLE_NUMBER",
  "message": "Each number must be between 0 and 999.",
  "status": 400
}
```

错误响应（全零）：

```json
{
  "success": false,
  "code": "ORACLE_NUMBERS_ALL_ZERO",
  "message": "The three numbers cannot all be zero.",
  "status": 400
}
```

---

## 七、参考来源

- 总纲第 2.1 节：URL 表格
- 总纲第 2.2 节：英文命名
- 考据文档：`docs/research/zhuge-origin-research.md`
- 英文站执行计划 W0 章节
- `wise-oracle-cultural-expression-guide.md`：文化表达分级

---

## 八、修订记录

| 日期 | 变更 | 变更人 |
| --- | --- | --- |
| 2026-06-30 | 初稿创建，覆盖 W0.1/W0.2/W0.3/W0.4/W0.6 | 助手起草，待用户审阅 |
| 2026-06-30 | 取消自由提问模式，改为 Three Words + Three Numbers；新增引导语；SEO 描述改为"Hold a question in mind..."；重启按钮改为 Draw Another Sign；错误响应示例改用 INVALID_ORACLE_NUMBER | 助手修订，待用户审阅 |
| 2026-06-30 | 算法定稿（依据 scripts/derive_original_oracle_signs.py）：Three Words 改为 A=1..Z=26 字母求和 + stroke_digit（mod 10，余 0 取 1）+ compose_three_character_number，示例 LOVE/WORK/FATE→Sign #88；Three Numbers 改为三个 0-999 数字 + 九位种子 compose_english_three_number_seed；新增 UI 变换动画与折叠项；设计原则措辞改为"显著减少…收集和定向回答风险" | 助手修订，待用户审阅 |
