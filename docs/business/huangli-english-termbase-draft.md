# 英文黄历术语表草稿（6tail 候选词抽取）

> **文档定位**：W1.1 产出。从 `frontend/static/js/lunar.js` 的 6tail I18n 英文 messages 抽取候选词，供人工审校。
> **创建日期**：2026-06-30
> **状态**：草稿，待人工审校定稿
> **硬约束引用**：D6（神煞采用音译+解释）
> **注意**：本草稿只抽取候选，不直接上线。定稿后再写入项目英文黄历词表，不改 `lunar.js`。

---

## 一、命名空间含义对照（纠正执行计划注释错误）

> 执行计划 W1.1 列出的 6 个命名空间（sx/yj/jq/sn/ps/bg）含义正确，但注释有误，已纠正：
> - `sx.*` = 生肖（非十神）
> - `ss.*` = 十神（en 完全缺失）
> - `ps.*` = 方位（非彭祖百忌）
> - `bg.*` = 八卦（非拜功）

| 前缀 | 含义 | chs 条目数 | en 条目数 | en 完整度 |
| --- | --- | --- | --- | --- |
| `bg.*` | 八卦 (Eight Trigrams) | 8 | 8 | ✅ 完整 |
| `d.*` | 农历日 (Lunar Days) | 30 | 0 | ❌ en 完全缺失 |
| `ds.*` | 十二长生 (Twelve Life Stages) | 12 | 0 | ❌ en 完全缺失 |
| `dw.*` | 动物 (Animals, 28宿对应) | 28 | 21 | ⚠️ en 部分缺失（缺 7 条） |
| `dz.*` | 地支 (Earthly Branches) | 12 | 12 | ✅ 完整 |
| `h.*` | 候 (Phenology, 72物候) | 75 | 0 | ❌ en 完全缺失 |
| `jq.*` | 节气 (Solar Terms) | 24 | 24 | ✅ 完整 |
| `jr.*` | 节日 (Festivals) | 26 | 24 | ⚠️ en 部分缺失（缺 2 条） |
| `jz.*` | 六十甲子 (Sixty Jiazi) | 60 | 60 | ✅ 完整 |
| `ly.*` | 六曜 (Rokuyō) | 6 | 6 | ✅ 完整 |
| `m.*` | 农历月 (Lunar Months) | 12 | 0 | ❌ en 完全缺失 |
| `n.*` | 数字 (Numbers) | 13 | 13 | ✅ 完整 |
| `ny.*` | 纳音 (Nayin / Melodic Elements) | 29 | 29 | ✅ 完整 |
| `od.*` | 孟仲季 (Meng/Zhong/Ji) | 3 | 0 | ❌ en 完全缺失 |
| `ps.*` | 方位 (Directions) | 16 | 14 | ⚠️ en 部分缺失（缺 2 条） |
| `s.*` | 杂项 (Misc: 黄道/吉凶/阴阳/颜色) | 14 | 12 | ⚠️ en 部分缺失（缺 2 条） |
| `sn.*` | 神煞 (Spirits / Deities) | 148 | 11 | ⚠️ en 部分缺失（缺 137 条） |
| `ss.*` | 十神 (Ten Gods) | 10 | 0 | ❌ en 完全缺失 |
| `sx.*` | 生肖 (Chinese Zodiac) | 12 | 12 | ✅ 完整 |
| `sz.*` | 四季 (Four Seasons) | 4 | 4 | ✅ 完整 |
| `tg.*` | 天干 (Heavenly Stems) | 10 | 10 | ✅ 完整 |
| `ts.*` | 占方 (Divination Directions) | 17 | 17 | ✅ 完整 |
| `w.*` | 星期 (Weekdays) | 7 | 7 | ✅ 完整 |
| `wx.*` | 五行+日月 (Five Elements + Sun/Moon) | 7 | 7 | ✅ 完整 |
| `xx.*` | 28宿 (Twenty-Eight Mansions) | 28 | 28 | ✅ 完整 |
| `xz.*` | 星座 (Western Zodiac) | 12 | 12 | ✅ 完整 |
| `yj.*` | 宜忌 (Favorable/Unfavorable Activities) | 141 | 141 | ✅ 完整 |
| `yx.*` | 月相 (Moon Phases) | 23 | 16 | ⚠️ en 部分缺失（缺 7 条） |
| `zx.*` | 十二值日 (Twelve Duty Officers) | 12 | 12 | ✅ 完整 |

---

## 二、易误读词审校清单（W1.1 第 5 条）

以下词汇需人工审校，避免文化误读：

| 待审校词 | 审校要点 |
| --- | --- |
| Yellow Calendar | 黄历的误译，应使用 Daily Chinese Almanac |
| Auspicious | 宜的翻译，需检查是否过度宗教化 |
| Evil Spirit | 神煞的误译，D6 已确认用音译+解释（Shén Shà） |
| Consecretion | yj.kaiGuang 的拼写错误，应为 Consecration |
| Paint sculptural | yj.suHui 的生硬翻译，需审校 |

---

## 三、各命名空间候选词详情

> 每个命名空间列出：key、中文源词、6tail 英文候选、产品英文候选（待人工填写）、使用场景、是否可直接用于 UI、风险备注。
> - **产品英文候选**：留空表示沿用 6tail 候选；填入表示建议替换。
> - **是否可直接用于 UI**：✅ 可直接用 / ⚠️ 需审校 / ❌ 不建议（将回退到中文或需重译）。

### `bg.*` — 八卦 (Eight Trigrams)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `bg.dui` | 兑 | Dui |  |  | ⚠️ 需审校 |  |
| `bg.gen` | 艮 | Gen |  |  | ⚠️ 需审校 |  |
| `bg.kan` | 坎 | Kan |  |  | ⚠️ 需审校 |  |
| `bg.kun` | 坤 | Kun |  |  | ⚠️ 需审校 |  |
| `bg.li` | 离 | Li |  |  | ⚠️ 需审校 |  |
| `bg.qian` | 乾 | Qian |  |  | ⚠️ 需审校 |  |
| `bg.xun` | 巽 | Xun |  |  | ⚠️ 需审校 |  |
| `bg.zhen` | 震 | Zhen |  |  | ⚠️ 需审校 |  |

### `d.*` — 农历日 (Lunar Days)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `d.eight` | 初八 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.eighteen` | 十八 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.eleven` | 十一 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.fifteen` | 十五 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.five` | 初五 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.four` | 初四 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.fourteen` | 十四 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.nighteen` | 十九 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.nine` | 初九 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.one` | 初一 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.seven` | 初七 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.seventeen` | 十七 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.six` | 初六 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.sixteen` | 十六 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.ten` | 初十 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.thirteen` | 十三 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.thirty` | 三十 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.three` | 初三 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twelve` | 十二 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twenty` | 二十 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyEight` | 廿八 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyFive` | 廿五 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyFour` | 廿四 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyNine` | 廿九 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyOne` | 廿一 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentySeven` | 廿七 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentySix` | 廿六 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyThree` | 廿三 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.twentyTwo` | 廿二 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `d.two` | 初二 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `ds.*` — 十二长生 (Twelve Life Stages)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `ds.bing` | 病 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.changSheng` | 长生 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.diWang` | 帝旺 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.guanDai` | 冠带 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.jue` | 绝 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.linGuan` | 临官 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.mu` | 墓 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.muYu` | 沐浴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.shuai` | 衰 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.si` | 死 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.tai` | 胎 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ds.yang` | 养 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `dw.*` — 动物 (Animals, 28宿对应)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `dw.bao` | 豹 | Leopard |  |  | ⚠️ 需审校 |  |
| `dw.fu` | 蝠 | Bat |  |  | ⚠️ 需审校 |  |
| `dw.gou` | 狗 | Dog |  |  | ⚠️ 需审校 |  |
| `dw.han` | 犴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.he` | 貉 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.hou` | 猴 | Monkey |  |  | ⚠️ 需审校 |  |
| `dw.hu` | 虎 | Tiger |  |  | ⚠️ 需审校 |  |
| `dw.huLi` | 狐 | Fox |  |  | ⚠️ 需审校 |  |
| `dw.ji` | 鸡 | Rooster |  |  | ⚠️ 需审校 |  |
| `dw.jiao` | 蛟 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.lang` | 狼 | Wolf |  |  | ⚠️ 需审校 |  |
| `dw.long` | 龙 | Dragon |  |  | ⚠️ 需审校 |  |
| `dw.lu` | 鹿 | Deer |  |  | ⚠️ 需审校 |  |
| `dw.ma` | 马 | Horse |  |  | ⚠️ 需审校 |  |
| `dw.niu` | 牛 | Ox |  |  | ⚠️ 需审校 |  |
| `dw.she` | 蛇 | Snake |  |  | ⚠️ 需审校 |  |
| `dw.shu` | 鼠 | Rat |  |  | ⚠️ 需审校 |  |
| `dw.tu` | 兔 | Rabbit |  |  | ⚠️ 需审校 |  |
| `dw.wu` | 乌 | Crow |  |  | ⚠️ 需审校 |  |
| `dw.xie` | 獬 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.xu` | 獝 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.yan` | 燕 | Swallow |  |  | ⚠️ 需审校 |  |
| `dw.yang` | 羊 | Goat |  |  | ⚠️ 需审校 |  |
| `dw.yin` | 蚓 | Earthworm |  |  | ⚠️ 需审校 |  |
| `dw.yuan` | 猿 | Ape |  |  | ⚠️ 需审校 |  |
| `dw.zhang` | 獐 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.zhi` | 彘 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `dw.zhu` | 猪 | Pig |  |  | ⚠️ 需审校 |  |

### `dz.*` — 地支 (Earthly Branches)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `dz.chen` | 辰 | Chen |  |  | ⚠️ 需审校 |  |
| `dz.chou` | 丑 | Chou |  |  | ⚠️ 需审校 |  |
| `dz.hai` | 亥 | Hai |  |  | ⚠️ 需审校 |  |
| `dz.mao` | 卯 | Mao |  |  | ⚠️ 需审校 |  |
| `dz.shen` | 申 | Shen |  |  | ⚠️ 需审校 |  |
| `dz.si` | 巳 | Si |  |  | ⚠️ 需审校 |  |
| `dz.wei` | 未 | Wei |  |  | ⚠️ 需审校 |  |
| `dz.wu` | 午 | Wu |  |  | ⚠️ 需审校 |  |
| `dz.xu` | 戌 | Xu |  |  | ⚠️ 需审校 |  |
| `dz.yin` | 寅 | Yin |  |  | ⚠️ 需审校 |  |
| `dz.you` | 酉 | You |  |  | ⚠️ 需审校 |  |
| `dz.zi` | 子 | Zi |  |  | ⚠️ 需审校 |  |

### `h.*` — 候 (Phenology, 72物候)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `h.baiLu` | 白露降 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.banXia` | 半夏生 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.biSe` | 闭塞而成冬 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.caiNai` | 豺乃祭兽 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.cangGeng` | 仓庚鸣 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.caoMuHuangLuo` | 草木黄落 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.caoMuMengDong` | 草木萌动 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.daYu` | 大雨行时 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.daiSheng` | 戴胜降于桑 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.diShi` | 地始冻 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.dongFeng` | 东风解冻 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.fanShe` | 反舌无声 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.first` | 初候 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.fuCao` | 腐草为萤 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.hanChan` | 寒蝉鸣 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.heDan` | 鹖鴠不鸣 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.heNai` | 禾乃登 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.hongCang` | 虹藏不见 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.hongShi` | 虹始见 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.hongYanLai` | 鸿雁来 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.hongYanLaiBin` | 鸿雁来宾 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.houYan` | 候雁北 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.huShi` | 虎始交 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.jiShi` | 鸡始乳 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.juShi` | 鵙始鸣 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.juYou` | 菊有黄花 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.kuCai` | 苦菜秀 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.leiNai` | 雷乃发声 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.leiShi` | 雷始收声 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.liTing` | 荔挺出 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.liangFeng` | 凉风至 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.louGuo` | 蝼蝈鸣 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.luJia` | 鹿角解 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.maiQiu` | 麦秋至 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.miCao` | 靡草死 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.miJiao` | 麋角解 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.mingJiu` | 鸣鸠拂奇羽 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.pingShi` | 萍始生 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.qiuYinChu` | 蚯蚓出 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.qiuYinJie` | 蚯蚓结 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.queRu` | 雀入大水为蛤 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.queShi` | 鹊始巢 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.qunNiao` | 群鸟养羞 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.second` | 二候 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.shiDian` | 始电 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.shuiQuan` | 水泉动 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.shuiShiBing` | 水始冰 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.shuiShiHe` | 水始涸 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.shuiZe` | 水泽腹坚 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.taJi` | 獭祭鱼 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tangLang` | 螳螂生 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.taoShi` | 桃始华 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.third` | 三候 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tianDi` | 天地始肃 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tianQi` | 天气上升地气下降 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tianShu` | 田鼠化为鴽 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tiaoShi` | 蜩始鸣 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tongShi` | 桐始华 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.tuRun` | 土润溽暑 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.wangGua` | 王瓜生 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.wenFeng` | 温风至 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.xiShuai` | 蟋蟀居壁 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.xuanNiaoGui` | 玄鸟归 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.xuanNiaoZhi` | 玄鸟至 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.yanBei` | 雁北乡 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.yingHua` | 鹰化为鸠 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.yingNai` | 鹰乃祭鸟 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.yingShi` | 鹰始挚 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.yuZhi` | 鱼陟负冰 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.zheChongPiHu` | 蛰虫坯户 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.zheChongShiZhen` | 蛰虫始振 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.zheChongXianFu` | 蛰虫咸俯 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.zhengNiao` | 征鸟厉疾 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.zhiRu` | 雉入大水为蜃 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `h.zhiShi` | 雉始雊 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `jq.*` — 节气 (Solar Terms)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `jq.baiLu` | 白露 | White Dew |  |  | ⚠️ 需审校 |  |
| `jq.chuShu` | 处暑 | End of Heat |  |  | ⚠️ 需审校 |  |
| `jq.chunFen` | 春分 | Spring Equinox |  |  | ⚠️ 需审校 |  |
| `jq.daHan` | 大寒 | Great Cold |  |  | ⚠️ 需审校 |  |
| `jq.daShu` | 大暑 | Greater Heat |  |  | ⚠️ 需审校 |  |
| `jq.daXue` | 大雪 | Heavy Snow |  |  | ⚠️ 需审校 |  |
| `jq.dongZhi` | 冬至 | Winter Solstice |  |  | ⚠️ 需审校 |  |
| `jq.guYu` | 谷雨 | Grain Rain |  |  | ⚠️ 需审校 |  |
| `jq.hanLu` | 寒露 | Cold Dew |  |  | ⚠️ 需审校 |  |
| `jq.jingZhe` | 惊蛰 | Awakening from Hibernation |  |  | ⚠️ 需审校 |  |
| `jq.liChun` | 立春 | Spring Beginning |  |  | ⚠️ 需审校 |  |
| `jq.liDong` | 立冬 | Beginning of Winter |  |  | ⚠️ 需审校 |  |
| `jq.liQiu` | 立秋 | Beginning of Autumn |  |  | ⚠️ 需审校 |  |
| `jq.liXia` | 立夏 | Beginning of Summer |  |  | ⚠️ 需审校 |  |
| `jq.mangZhong` | 芒种 | Grain in Ear |  |  | ⚠️ 需审校 |  |
| `jq.qingMing` | 清明 | Fresh Green |  |  | ⚠️ 需审校 |  |
| `jq.qiuFen` | 秋分 | Autumnal Equinox |  |  | ⚠️ 需审校 |  |
| `jq.shuangJiang` | 霜降 | First Frost |  |  | ⚠️ 需审校 |  |
| `jq.xiaZhi` | 夏至 | Summer Solstice |  |  | ⚠️ 需审校 |  |
| `jq.xiaoHan` | 小寒 | Lesser Cold |  |  | ⚠️ 需审校 |  |
| `jq.xiaoMan` | 小满 | Lesser Fullness |  |  | ⚠️ 需审校 |  |
| `jq.xiaoShu` | 小暑 | Lesser Heat |  |  | ⚠️ 需审校 |  |
| `jq.xiaoXue` | 小雪 | Light Snow |  |  | ⚠️ 需审校 |  |
| `jq.yuShui` | 雨水 | Rain Water |  |  | ⚠️ 需审校 |  |

### `jr.*` — 节日 (Festivals)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `jr.chongYang` | 重阳节 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `jr.chuXi` | 除夕 | Chinese New Year's Eve |  |  | ⚠️ 需审校 |  |
| `jr.chunJie` | 春节 | Luna New Year |  |  | ⚠️ 需审校 |  |
| `jr.duanWu` | 端午节 | Dragon Boat Festival |  |  | ⚠️ 需审校 |  |
| `jr.erTong` | 儿童节 | Children's Day |  |  | ⚠️ 需审校 |  |
| `jr.fuNv` | 妇女节 | Women's Day |  |  | ⚠️ 需审校 |  |
| `jr.guoQing` | 国庆节 | National Day |  |  | ⚠️ 需审校 |  |
| `jr.jianDang` | 建党节 | Party's Day |  |  | ⚠️ 需审校 |  |
| `jr.jianJun` | 建军节 | Army Day |  |  | ⚠️ 需审校 |  |
| `jr.jiaoShi` | 教师节 | Teachers' Day |  |  | ⚠️ 需审校 |  |
| `jr.laBa` | 腊八节 | Laba Festival |  |  | ⚠️ 需审校 |  |
| `jr.longTou` | 龙头节 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `jr.pingAn` | 平安夜 | Christmas Eve |  |  | ⚠️ 需审校 |  |
| `jr.qiXi` | 七夕节 | Begging Festival |  |  | ⚠️ 需审校 |  |
| `jr.qingNian` | 青年节 | Youth Day |  |  | ⚠️ 需审校 |  |
| `jr.qingRen` | 情人节 | Valentine's Day |  |  | ⚠️ 需审校 |  |
| `jr.shengDan` | 圣诞节 | Christmas Day |  |  | ⚠️ 需审校 |  |
| `jr.wanSheng` | 万圣节 | All Saints' Day |  |  | ⚠️ 需审校 |  |
| `jr.wanShengYe` | 万圣节前夜 | All Saints' Eve |  |  | ⚠️ 需审校 |  |
| `jr.wuYi` | 劳动节 | International Worker's Day |  |  | ⚠️ 需审校 |  |
| `jr.xiaoFei` | 消费者权益日 | Consumer Rights Day |  |  | ⚠️ 需审校 |  |
| `jr.yuRen` | 愚人节 | April Fools' Day |  |  | ⚠️ 需审校 |  |
| `jr.yuanDan` | 元旦节 | New Year's Day |  |  | ⚠️ 需审校 |  |
| `jr.yuanXiao` | 元宵节 | Lantern Festival |  |  | ⚠️ 需审校 |  |
| `jr.zhiShu` | 植树节 | Arbor Day |  |  | ⚠️ 需审校 |  |
| `jr.zhongQiu` | 中秋节 | Mid-Autumn Festival |  |  | ⚠️ 需审校 |  |

### `jz.*` — 六十甲子 (Sixty Jiazi)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `jz.bingChen` | 丙辰 | BingChen |  |  | ⚠️ 需审校 |  |
| `jz.bingShen` | 丙申 | BingShen |  |  | ⚠️ 需审校 |  |
| `jz.bingWu` | 丙午 | BingWu |  |  | ⚠️ 需审校 |  |
| `jz.bingXu` | 丙戌 | BingXu |  |  | ⚠️ 需审校 |  |
| `jz.bingYin` | 丙寅 | BingYin |  |  | ⚠️ 需审校 |  |
| `jz.bingZi` | 丙子 | BingZi |  |  | ⚠️ 需审校 |  |
| `jz.dingChou` | 丁丑 | DingChou |  |  | ⚠️ 需审校 |  |
| `jz.dingHai` | 丁亥 | DingHai |  |  | ⚠️ 需审校 |  |
| `jz.dingMao` | 丁卯 | DingMao |  |  | ⚠️ 需审校 |  |
| `jz.dingSi` | 丁巳 | DingSi |  |  | ⚠️ 需审校 |  |
| `jz.dingWei` | 丁未 | DingWei |  |  | ⚠️ 需审校 |  |
| `jz.dingYou` | 丁酉 | DingYou |  |  | ⚠️ 需审校 |  |
| `jz.gengChen` | 庚辰 | GengChen |  |  | ⚠️ 需审校 |  |
| `jz.gengShen` | 庚申 | GengShen |  |  | ⚠️ 需审校 |  |
| `jz.gengWu` | 庚午 | GengWu |  |  | ⚠️ 需审校 |  |
| `jz.gengXu` | 庚戌 | GengXu |  |  | ⚠️ 需审校 |  |
| `jz.gengYin` | 庚寅 | GengYin |  |  | ⚠️ 需审校 |  |
| `jz.gengZi` | 庚子 | GengZi |  |  | ⚠️ 需审校 |  |
| `jz.guiChou` | 癸丑 | GuiChou |  |  | ⚠️ 需审校 |  |
| `jz.guiHai` | 癸亥 | GuiHai |  |  | ⚠️ 需审校 |  |
| `jz.guiMao` | 癸卯 | GuiMao |  |  | ⚠️ 需审校 |  |
| `jz.guiSi` | 癸巳 | GuiSi |  |  | ⚠️ 需审校 |  |
| `jz.guiWei` | 癸未 | GuiWei |  |  | ⚠️ 需审校 |  |
| `jz.guiYou` | 癸酉 | GuiYou |  |  | ⚠️ 需审校 |  |
| `jz.jiChou` | 己丑 | JiChou |  |  | ⚠️ 需审校 |  |
| `jz.jiHai` | 己亥 | JiHai |  |  | ⚠️ 需审校 |  |
| `jz.jiMao` | 己卯 | JiMao |  |  | ⚠️ 需审校 |  |
| `jz.jiSi` | 己巳 | JiSi |  |  | ⚠️ 需审校 |  |
| `jz.jiWei` | 己未 | JiWei |  |  | ⚠️ 需审校 |  |
| `jz.jiYou` | 己酉 | JiYou |  |  | ⚠️ 需审校 |  |
| `jz.jiaChen` | 甲辰 | JiaChen |  |  | ⚠️ 需审校 |  |
| `jz.jiaShen` | 甲申 | JiaShen |  |  | ⚠️ 需审校 |  |
| `jz.jiaWu` | 甲午 | JiaWu |  |  | ⚠️ 需审校 |  |
| `jz.jiaXu` | 甲戌 | JiaXu |  |  | ⚠️ 需审校 |  |
| `jz.jiaYin` | 甲寅 | JiaYin |  |  | ⚠️ 需审校 |  |
| `jz.jiaZi` | 甲子 | JiaZi |  |  | ⚠️ 需审校 |  |
| `jz.renChen` | 壬辰 | RenChen |  |  | ⚠️ 需审校 |  |
| `jz.renShen` | 壬申 | RenShen |  |  | ⚠️ 需审校 |  |
| `jz.renWu` | 壬午 | RenWu |  |  | ⚠️ 需审校 |  |
| `jz.renXu` | 壬戌 | RenXu |  |  | ⚠️ 需审校 |  |
| `jz.renYin` | 壬寅 | RenYin |  |  | ⚠️ 需审校 |  |
| `jz.renZi` | 壬子 | RenZi |  |  | ⚠️ 需审校 |  |
| `jz.wuChen` | 戊辰 | WuChen |  |  | ⚠️ 需审校 |  |
| `jz.wuShen` | 戊申 | WuShen |  |  | ⚠️ 需审校 |  |
| `jz.wuWu` | 戊午 | WuWu |  |  | ⚠️ 需审校 |  |
| `jz.wuXu` | 戊戌 | WuXu |  |  | ⚠️ 需审校 |  |
| `jz.wuYin` | 戊寅 | WuYin |  |  | ⚠️ 需审校 |  |
| `jz.wuZi` | 戊子 | WuZi |  |  | ⚠️ 需审校 |  |
| `jz.xinChou` | 辛丑 | XinChou |  |  | ⚠️ 需审校 |  |
| `jz.xinHai` | 辛亥 | XinHai |  |  | ⚠️ 需审校 |  |
| `jz.xinMao` | 辛卯 | XinMao |  |  | ⚠️ 需审校 |  |
| `jz.xinSi` | 辛巳 | XinSi |  |  | ⚠️ 需审校 |  |
| `jz.xinWei` | 辛未 | XinWei |  |  | ⚠️ 需审校 |  |
| `jz.xinYou` | 辛酉 | XinYou |  |  | ⚠️ 需审校 |  |
| `jz.yiChou` | 乙丑 | YiChou |  |  | ⚠️ 需审校 |  |
| `jz.yiHai` | 乙亥 | YiHai |  |  | ⚠️ 需审校 |  |
| `jz.yiMao` | 乙卯 | YiMao |  |  | ⚠️ 需审校 |  |
| `jz.yiSi` | 乙巳 | YiSi |  |  | ⚠️ 需审校 |  |
| `jz.yiWei` | 乙未 | YiWei |  |  | ⚠️ 需审校 |  |
| `jz.yiYou` | 乙酉 | YiYou |  |  | ⚠️ 需审校 |  |

### `ly.*` — 六曜 (Rokuyō)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `ly.chiKou` | 赤口 | Chikagoro |  |  | ⚠️ 需审校 |  |
| `ly.daAn` | 大安 | Great safety |  |  | ⚠️ 需审校 |  |
| `ly.foMie` | 佛灭 | Buddhism's demise |  |  | ⚠️ 需审校 |  |
| `ly.xianFu` | 先负 | Lose first |  |  | ⚠️ 需审校 |  |
| `ly.xianSheng` | 先胜 | Win first |  |  | ⚠️ 需审校 |  |
| `ly.youYin` | 友引 | Friend's referral |  |  | ⚠️ 需审校 |  |

### `m.*` — 农历月 (Lunar Months)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `m.eight` | 八 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.eleven` | 冬 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.five` | 五 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.four` | 四 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.nine` | 九 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.one` | 正 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.seven` | 七 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.six` | 六 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.ten` | 十 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.three` | 三 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.twelve` | 腊 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `m.two` | 二 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `n.*` — 数字 (Numbers)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `n.eight` | 八 | 8 |  |  | ⚠️ 需审校 |  |
| `n.eleven` | 十一 | 11 |  |  | ⚠️ 需审校 |  |
| `n.five` | 五 | 5 |  |  | ⚠️ 需审校 |  |
| `n.four` | 四 | 4 |  |  | ⚠️ 需审校 |  |
| `n.nine` | 九 | 9 |  |  | ⚠️ 需审校 |  |
| `n.one` | 一 | 1 |  |  | ⚠️ 需审校 |  |
| `n.seven` | 七 | 7 |  |  | ⚠️ 需审校 |  |
| `n.six` | 六 | 6 |  |  | ⚠️ 需审校 |  |
| `n.ten` | 十 | 10 |  |  | ⚠️ 需审校 |  |
| `n.three` | 三 | 3 |  |  | ⚠️ 需审校 |  |
| `n.twelve` | 十二 | 12 |  |  | ⚠️ 需审校 |  |
| `n.two` | 二 | 2 |  |  | ⚠️ 需审校 |  |
| `n.zero` | 〇 | 0 |  |  | ⚠️ 需审校 |  |

### `ny.*` — 纳音 (Nayin / Melodic Elements)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `ny.baiLa` | 白蜡 | Wax |  |  | ⚠️ 需审校 |  |
| `ny.biShang` | 壁上 | Wall |  |  | ⚠️ 需审校 |  |
| `ny.chaiChuan` | 钗钏 | Ornaments |  |  | ⚠️ 需审校 |  |
| `ny.changLiu` | 长流 | Flows |  |  | ⚠️ 需审校 |  |
| `ny.chengTou` | 城头 | City |  |  | ⚠️ 需审校 |  |
| `ny.daHai` | 大海 | Ocean |  |  | ⚠️ 需审校 |  |
| `ny.daLin` | 大林 | Forest |  |  | ⚠️ 需审校 |  |
| `ny.daXi` | 大溪 | Stream |  |  | ⚠️ 需审校 |  |
| `ny.daYi` | 大驿 | Post |  |  | ⚠️ 需审校 |  |
| `ny.fuDeng` | 覆灯 | Light |  |  | ⚠️ 需审校 |  |
| `ny.haiZhong` | 海中 | Sea |  |  | ⚠️ 需审校 |  |
| `ny.jianFeng` | 剑锋 | Blade |  |  | ⚠️ 需审校 |  |
| `ny.jianXia` | 涧下 | Valleyn |  |  | ⚠️ 需审校 |  |
| `ny.jinBo` | 金箔 | Foil |  |  | ⚠️ 需审校 |  |
| `ny.luPang` | 路旁 | Roadside |  |  | ⚠️ 需审校 |  |
| `ny.luZhong` | 炉中 | Stove |  |  | ⚠️ 需审校 |  |
| `ny.piLi` | 霹雳 | Thunderbolt |  |  | ⚠️ 需审校 |  |
| `ny.pingDi` | 平地 | Land |  |  | ⚠️ 需审校 |  |
| `ny.quanZhong` | 泉中 | Spring |  |  | ⚠️ 需审校 |  |
| `ny.sangZhe` | 桑柘 | Cudrania |  |  | ⚠️ 需审校 |  |
| `ny.shaZhong` | 沙中 | Sand |  |  | ⚠️ 需审校 |  |
| `ny.shanTou` | 山头 | Hilltop |  |  | ⚠️ 需审校 |  |
| `ny.shanXia` | 山下 | Piedmont |  |  | ⚠️ 需审校 |  |
| `ny.shiLiu` | 石榴 | Pomegranate |  |  | ⚠️ 需审校 |  |
| `ny.songBo` | 松柏 | Coniferin |  |  | ⚠️ 需审校 |  |
| `ny.tianHe` | 天河 | River |  |  | ⚠️ 需审校 |  |
| `ny.tianShang` | 天上 | Sky |  |  | ⚠️ 需审校 |  |
| `ny.wuShang` | 屋上 | Roof |  |  | ⚠️ 需审校 |  |
| `ny.yangLiu` | 杨柳 | Willow |  |  | ⚠️ 需审校 |  |

### `od.*` — 孟仲季 (Meng/Zhong/Ji)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `od.first` | 孟 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `od.second` | 仲 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `od.third` | 季 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `ps.*` — 方位 (Directions)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `ps.bei` | 北 | North |  |  | ⚠️ 需审校 |  |
| `ps.center` | 中 | Center |  |  | ⚠️ 需审校 |  |
| `ps.dong` | 东 | East |  |  | ⚠️ 需审校 |  |
| `ps.dongBei` | 东北 | Northeast |  |  | ⚠️ 需审校 |  |
| `ps.dongNan` | 东南 | Southeast |  |  | ⚠️ 需审校 |  |
| `ps.fangNei` | 房内 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ps.nan` | 南 | South |  |  | ⚠️ 需审校 |  |
| `ps.wai` | 外 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ps.xi` | 西 | West |  |  | ⚠️ 需审校 |  |
| `ps.xiBei` | 西北 | Northwest |  |  | ⚠️ 需审校 |  |
| `ps.xiNan` | 西南 | Southwest |  |  | ⚠️ 需审校 |  |
| `ps.zhengBei` | 正北 | North |  |  | ⚠️ 需审校 |  |
| `ps.zhengDong` | 正东 | East |  |  | ⚠️ 需审校 |  |
| `ps.zhengNan` | 正南 | South |  |  | ⚠️ 需审校 |  |
| `ps.zhengXi` | 正西 | West |  |  | ⚠️ 需审校 |  |
| `ps.zhong` | 中宫 | Center |  |  | ⚠️ 需审校 |  |

### `s.*` — 杂项 (Misc: 黄道/吉凶/阴阳/颜色)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `s.badLuck` | 凶 | Bad luck |  |  | ⚠️ 需审校 |  |
| `s.black` | 黑 | Black |  |  | ⚠️ 需审校 |  |
| `s.blue` | 碧 | Blue |  |  | ⚠️ 需审校 |  |
| `s.goodLuck` | 吉 | Good luck |  |  | ⚠️ 需审校 |  |
| `s.green` | 绿 | Green |  |  | ⚠️ 需审校 |  |
| `s.heiDao` | 黑道 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `s.huangDao` | 黄道 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `s.none` | 无 | None |  |  | ⚠️ 需审校 |  |
| `s.purple` | 紫 | Purple |  |  | ⚠️ 需审校 |  |
| `s.red` | 赤 | Red |  |  | ⚠️ 需审校 |  |
| `s.white` | 白 | White |  |  | ⚠️ 需审校 |  |
| `s.yang` | 阳 | Yang |  |  | ⚠️ 需审校 |  |
| `s.yellow` | 黄 | Yellow |  |  | ⚠️ 需审校 |  |
| `s.yin` | 阴 | Yin |  |  | ⚠️ 需审校 |  |

### `sn.*` — 神煞 (Spirits / Deities)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `sn.baFeng` | 八风 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.baLong` | 八龙 | Eight Dragon |  |  | ⚠️ 需审校 |  |
| `sn.baZhuan` | 八专 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.baiHu` | 白虎 | White Tiger |  |  | ⚠️ 需审校 |  |
| `sn.baoGuang` | 宝光 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.buJiang` | 不将 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.chengRi` | 成日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.chongRi` | 重日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.chuShen` | 除神 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.chuShuiLong` | 触水龙 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.chunYang` | 纯阳 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.chunYin` | 纯阴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.daBai` | 大败 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.daHao` | 大耗 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.daHui` | 大会 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.daSha` | 大煞 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.daShi` | 大时 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.danYin` | 单阴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.diHuo` | 地火 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.diNang` | 地囊 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.fourHit` | 四击 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.fuDe` | 福德 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.fuRi` | 复日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.fuSheng` | 福生 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.gouChen` | 勾陈 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.guChen` | 孤辰 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.guYang` | 孤阳 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.guanRi` | 官日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.guiJi` | 归忌 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.heKui` | 河魁 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jiQi` | 吉期 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jieChu` | 解除 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jieSha` | 劫煞 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jieShen` | 解神 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jinKui` | 金匮 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jinTang` | 金堂 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jingAn` | 敬安 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jiuHu` | 九虎 | Nine Tiger |  |  | ⚠️ 需审校 |  |
| `sn.jiuJiao` | 九焦 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jiuKan` | 九坎 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jiuKong` | 九空 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jueYang` | 绝阳 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.jueYin` | 绝阴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.liaoLi` | 了戾 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.linRi` | 临日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.liuHe` | 六合 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.liuShe` | 六蛇 | Six Snake |  |  | ⚠️ 需审校 |  |
| `sn.liuYi` | 六仪 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.minRi` | 民日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.mingFei` | 鸣吠 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.mingFeiDui` | 鸣吠对 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.mingTang` | 明堂 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.muCang` | 母仓 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.puHu` | 普护 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.qiFu` | 七符 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.qiNiao` | 七鸟 | Seven Bird |  |  | ⚠️ 需审校 |  |
| `sn.qingLong` | 青龙 | Azure Dragon |  |  | ⚠️ 需审校 |  |
| `sn.sanHe` | 三合 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.sanYin` | 三阴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.shengQi` | 生气 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.shengXin` | 圣心 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.shiDe` | 时德 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.shiYang` | 时阳 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.shiYin` | 时阴 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.shouRi` | 守日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siFei` | 四废 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siHao` | 四耗 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siJi` | 四忌 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siMing` | 司命 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siQi` | 死气 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siQiong` | 四穷 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.siShen` | 死神 | Death |  |  | ⚠️ 需审校 |  |
| `sn.siXiang` | 四相 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.suiBo` | 岁薄 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianCang` | 天仓 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianDe` | 天德 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianDeHe` | 天德合 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianEn` | 天恩 | Serene Grace |  |  | ⚠️ 需审校 |  |
| `sn.tianFu` | 天符 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianGang` | 天罡 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianGou` | 天狗 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianHou` | 天后 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianHuo` | 天火 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianLao` | 天牢 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianLi` | 天吏 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianMa` | 天马 | Pegasus |  |  | ⚠️ 需审校 |  |
| `sn.tianShe` | 天赦 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianWu` | 天巫 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianXi` | 天喜 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianXing` | 天刑 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianYi` | 天医 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianYuan` | 天愿 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tianZei` | 天贼 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tuFu` | 土符 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.tuHu` | 土府 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wangRi` | 王日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wangWang` | 往亡 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wuFu` | 五富 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wuHe` | 五合 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wuLi` | 五离 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wuMu` | 五墓 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.wuXu` | 五虚 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xianChi` | 咸池 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xiangRi` | 相日 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xiaoHao` | 小耗 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xiaoHui` | 小会 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xiaoShi` | 小时 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xingHen` | 行狠 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xuShi` | 续世 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xuanWu` | 玄武 | Black Tortoise |  |  | ⚠️ 需审校 |  |
| `sn.xueJi` | 血忌 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.xueZhi` | 血支 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yanDui` | 厌对 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yangCuo` | 阳错 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yangCuoYinChong` | 阳错阴冲 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yangDe` | 阳德 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yangPoYinChong` | 阳破阴冲 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yaoAn` | 要安 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yiHou` | 益后 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yiMa` | 驿马 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinCuo` | 阴错 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinDaoChongYang` | 阴道冲阳 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinDe` | 阴德 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinShen` | 阴神 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinWei` | 阴位 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinYangJiChong` | 阴阳击冲 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinYangJiaoPo` | 阴阳交破 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yinYangJuCuo` | 阴阳俱错 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.youHuo` | 游祸 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yuTang` | 玉堂 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yuYu` | 玉宇 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yuanWu` | 元武 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueDe` | 月德 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueDeHe` | 月德合 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueEn` | 月恩 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueHai` | 月害 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueJian` | 月建 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueKong` | 月空 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yuePo` | 月破 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueSha` | 月煞 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueXing` | 月刑 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueXu` | 月虚 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.yueYan` | 月厌 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.zaiSha` | 灾煞 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.zhaoYao` | 招摇 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.zhiSi` | 致死 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `sn.zhuQue` | 朱雀 | Rosefinch |  |  | ⚠️ 需审校 |  |
| `sn.zhuZhen` | 逐阵 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `ss.*` — 十神 (Ten Gods)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `ss.biJian` | 比肩 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.jieCai` | 劫财 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.pianCai` | 偏财 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.pianYin` | 偏印 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.qiSha` | 七杀 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.shangGuan` | 伤官 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.shiShen` | 食神 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.zhengCai` | 正财 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.zhengGuan` | 正官 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `ss.zhengYin` | 正印 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `sx.*` — 生肖 (Chinese Zodiac)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `sx.dog` | 狗 | Dog |  |  | ⚠️ 需审校 |  |
| `sx.dragon` | 龙 | Dragon |  |  | ⚠️ 需审校 |  |
| `sx.goat` | 羊 | Goat |  |  | ⚠️ 需审校 |  |
| `sx.horse` | 马 | Horse |  |  | ⚠️ 需审校 |  |
| `sx.monkey` | 猴 | Monkey |  |  | ⚠️ 需审校 |  |
| `sx.ox` | 牛 | Ox |  |  | ⚠️ 需审校 |  |
| `sx.pig` | 猪 | Pig |  |  | ⚠️ 需审校 |  |
| `sx.rabbit` | 兔 | Rabbit |  |  | ⚠️ 需审校 |  |
| `sx.rat` | 鼠 | Rat |  |  | ⚠️ 需审校 |  |
| `sx.rooster` | 鸡 | Rooster |  |  | ⚠️ 需审校 |  |
| `sx.snake` | 蛇 | Snake |  |  | ⚠️ 需审校 |  |
| `sx.tiger` | 虎 | Tiger |  |  | ⚠️ 需审校 |  |

### `sz.*` — 四季 (Four Seasons)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `sz.chun` | 春 | Spring |  |  | ⚠️ 需审校 |  |
| `sz.dong` | 冬 | Winter |  |  | ⚠️ 需审校 |  |
| `sz.qiu` | 秋 | Autumn |  |  | ⚠️ 需审校 |  |
| `sz.xia` | 夏 | Summer |  |  | ⚠️ 需审校 |  |

### `tg.*` — 天干 (Heavenly Stems)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `tg.bing` | 丙 | Bing |  |  | ⚠️ 需审校 |  |
| `tg.ding` | 丁 | Ding |  |  | ⚠️ 需审校 |  |
| `tg.geng` | 庚 | Geng |  |  | ⚠️ 需审校 |  |
| `tg.gui` | 癸 | Gui |  |  | ⚠️ 需审校 |  |
| `tg.ji` | 己 | Ji |  |  | ⚠️ 需审校 |  |
| `tg.jia` | 甲 | Jia |  |  | ⚠️ 需审校 |  |
| `tg.ren` | 壬 | Ren |  |  | ⚠️ 需审校 |  |
| `tg.wu` | 戊 | Wu |  |  | ⚠️ 需审校 |  |
| `tg.xin` | 辛 | Xin |  |  | ⚠️ 需审校 |  |
| `tg.yi` | 乙 | Yi |  |  | ⚠️ 需审校 |  |

### `ts.*` — 占方 (Divination Directions)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `ts.cang` | 仓 | Depot |  |  | ⚠️ 需审校 |  |
| `ts.cangKu` | 仓库 | Depot |  |  | ⚠️ 需审校 |  |
| `ts.ce` | 厕 | Toilet |  |  | ⚠️ 需审校 |  |
| `ts.chu` | 厨 | Kitchen |  |  | ⚠️ 需审校 |  |
| `ts.chuang` | 床 | Bed |  |  | ⚠️ 需审校 |  |
| `ts.daMen` | 大门 | Gate |  |  | ⚠️ 需审校 |  |
| `ts.dui` | 碓 | Pestle |  |  | ⚠️ 需审校 |  |
| `ts.fang` | 房 | Room |  |  | ⚠️ 需审校 |  |
| `ts.hu` | 户 | Household |  |  | ⚠️ 需审校 |  |
| `ts.lu` | 炉 | Stove |  |  | ⚠️ 需审校 |  |
| `ts.men` | 门 | Door |  |  | ⚠️ 需审校 |  |
| `ts.mo` | 磨 | Mill |  |  | ⚠️ 需审校 |  |
| `ts.tang` | 堂 | Hall |  |  | ⚠️ 需审校 |  |
| `ts.win` | 窗 | Window |  |  | ⚠️ 需审校 |  |
| `ts.xi` | 栖 | Habitat |  |  | ⚠️ 需审校 |  |
| `ts.zao` | 灶 | Cooker |  |  | ⚠️ 需审校 |  |
| `ts.zhan` | 占 | At |  |  | ⚠️ 需审校 |  |

### `w.*` — 星期 (Weekdays)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `w.fri` | 五 | Friday |  |  | ⚠️ 需审校 |  |
| `w.mon` | 一 | Monday |  |  | ⚠️ 需审校 |  |
| `w.sat` | 六 | Saturday |  |  | ⚠️ 需审校 |  |
| `w.sun` | 日 | Sunday |  |  | ⚠️ 需审校 |  |
| `w.thur` | 四 | Thursday |  |  | ⚠️ 需审校 |  |
| `w.tues` | 二 | Tuesday |  |  | ⚠️ 需审校 |  |
| `w.wed` | 三 | Wednesday |  |  | ⚠️ 需审校 |  |

### `wx.*` — 五行+日月 (Five Elements + Sun/Moon)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `wx.huo` | 火 | Fire |  |  | ⚠️ 需审校 |  |
| `wx.jin` | 金 | Metal |  |  | ⚠️ 需审校 |  |
| `wx.mu` | 木 | Wood |  |  | ⚠️ 需审校 |  |
| `wx.ri` | 日 | Sun |  |  | ⚠️ 需审校 |  |
| `wx.shui` | 水 | Water |  |  | ⚠️ 需审校 |  |
| `wx.tu` | 土 | Earth |  |  | ⚠️ 需审校 |  |
| `wx.yue` | 月 | Moon |  |  | ⚠️ 需审校 |  |

### `xx.*` — 28宿 (Twenty-Eight Mansions)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `xx.bi` | 毕 | Finish |  |  | ⚠️ 需审校 |  |
| `xx.can` | 参 | Join |  |  | ⚠️ 需审校 |  |
| `xx.di` | 氐 | Foundation |  |  | ⚠️ 需审校 |  |
| `xx.dou` | 斗 | Fight |  |  | ⚠️ 需审校 |  |
| `xx.fang` | 房 | House |  |  | ⚠️ 需审校 |  |
| `xx.gui` | 鬼 | Ghost |  |  | ⚠️ 需审校 |  |
| `xx.ji` | 箕 | Sieve |  |  | ⚠️ 需审校 |  |
| `xx.jiao` | 角 | Horn |  |  | ⚠️ 需审校 |  |
| `xx.jing` | 井 | Well |  |  | ⚠️ 需审校 |  |
| `xx.kang` | 亢 | Kang |  |  | ⚠️ 需审校 |  |
| `xx.kui` | 奎 | Qui |  |  | ⚠️ 需审校 |  |
| `xx.liu` | 柳 | Willow |  |  | ⚠️ 需审校 |  |
| `xx.lou` | 娄 | Weak |  |  | ⚠️ 需审校 |  |
| `xx.mao` | 昴 | Mao |  |  | ⚠️ 需审校 |  |
| `xx.niu` | 牛 | Ox |  |  | ⚠️ 需审校 |  |
| `xx.nv` | 女 | Female |  |  | ⚠️ 需审校 |  |
| `xx.qiang` | 壁 | Wall |  |  | ⚠️ 需审校 |  |
| `xx.shi` | 室 | Room |  |  | ⚠️ 需审校 |  |
| `xx.tail` | 尾 | Tail |  |  | ⚠️ 需审校 |  |
| `xx.vei` | 胃 | Stomach |  |  | ⚠️ 需审校 |  |
| `xx.wei` | 危 | Danger |  |  | ⚠️ 需审校 |  |
| `xx.xin` | 心 | Heart |  |  | ⚠️ 需审校 |  |
| `xx.xing` | 星 | Star |  |  | ⚠️ 需审校 |  |
| `xx.xu` | 虚 | Virtual |  |  | ⚠️ 需审校 |  |
| `xx.yi` | 翼 | Wing |  |  | ⚠️ 需审校 |  |
| `xx.zhang` | 张 | Chang |  |  | ⚠️ 需审校 |  |
| `xx.zhen` | 轸 | Cross-bar |  |  | ⚠️ 需审校 |  |
| `xx.zi` | 觜 | Mouth |  |  | ⚠️ 需审校 |  |

### `xz.*` — 星座 (Western Zodiac)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `xz.aquarius` | 水瓶 | Aquarius |  |  | ⚠️ 需审校 |  |
| `xz.aries` | 白羊 | Aries |  |  | ⚠️ 需审校 |  |
| `xz.cancer` | 巨蟹 | Cancer |  |  | ⚠️ 需审校 |  |
| `xz.capricornus` | 摩羯 | Capricornus |  |  | ⚠️ 需审校 |  |
| `xz.gemini` | 双子 | Gemini |  |  | ⚠️ 需审校 |  |
| `xz.leo` | 狮子 | Leo |  |  | ⚠️ 需审校 |  |
| `xz.libra` | 天秤 | Libra |  |  | ⚠️ 需审校 |  |
| `xz.pisces` | 双鱼 | Pisces |  |  | ⚠️ 需审校 |  |
| `xz.sagittarius` | 射手 | Sagittarius |  |  | ⚠️ 需审校 |  |
| `xz.scorpio` | 天蝎 | Scorpio |  |  | ⚠️ 需审校 |  |
| `xz.taurus` | 金牛 | Taurus |  |  | ⚠️ 需审校 |  |
| `xz.virgo` | 处女 | Virgo |  |  | ⚠️ 需审校 |  |

### `yj.*` — 宜忌 (Favorable/Unfavorable Activities)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `yj.DingHun` | 订婚 | Engagement |  |  | ⚠️ 需审校 |  |
| `yj.TiTou` | 剃头 | Shave |  |  | ⚠️ 需审校 |  |
| `yj.anChuang` | 安床 | Bed placing |  |  | ⚠️ 需审校 |  |
| `yj.anDuiWei` | 安碓磑 | Build rub |  |  | ⚠️ 需审校 |  |
| `yj.anJi` | 安机 | Install machine |  |  | ⚠️ 需审校 |  |
| `yj.anJiXie` | 安机械 | Build machine |  |  | ⚠️ 需审校 |  |
| `yj.anMen` | 安门 | Door placing |  |  | ⚠️ 需审校 |  |
| `yj.anXiang` | 安香 | Incenst placement |  |  | ⚠️ 需审校 |  |
| `yj.anZang` | 安葬 | Burial |  |  | ⚠️ 需审校 |  |
| `yj.buYuan` | 补垣 | Mending |  |  | ⚠️ 需审校 |  |
| `yj.buZhuo` | 捕捉 | Catch |  |  | ⚠️ 需审校 |  |
| `yj.caiYi` | 裁衣 | Dressmaking |  |  | ⚠️ 需审校 |  |
| `yj.chaiXie` | 拆卸 | Smash house |  |  | ⚠️ 需审校 |  |
| `yj.chengChuan` | 乘船 | Ride boat |  |  | ⚠️ 需审校 |  |
| `yj.chengFu` | 成服 | Formation of clothes |  |  | ⚠️ 需审校 |  |
| `yj.chouShen` | 酬神 | Reward gods |  |  | ⚠️ 需审校 |  |
| `yj.chuFu` | 除服 | Mourning clothes removal |  |  | ⚠️ 需审校 |  |
| `yj.chuHuo` | 出火 | Expel the flame |  |  | ⚠️ 需审校 |  |
| `yj.chuHuoCai` | 出货财 | Delivery |  |  | ⚠️ 需审校 |  |
| `yj.chuXing` | 出行 | Travel |  |  | ⚠️ 需审校 |  |
| `yj.chuanPing` | 穿屏扇架 | Build door |  |  | ⚠️ 需审校 |  |
| `yj.ciSong` | 词讼 | Litigation |  |  | ⚠️ 需审校 |  |
| `yj.diaoKe` | 雕刻 | Carving |  |  | ⚠️ 需审校 |  |
| `yj.dingMeng` | 订盟 | Make alliance |  |  | ⚠️ 需审校 |  |
| `yj.dingSang` | 定磉 | Fix stone |  |  | ⚠️ 需审校 |  |
| `yj.dongTu` | 动土 | Break ground |  |  | ⚠️ 需审校 |  |
| `yj.duShui` | 渡水 | Cross water |  |  | ⚠️ 需审校 |  |
| `yj.duanYi` | 断蚁 | Block ant hole |  |  | ⚠️ 需审校 |  |
| `yj.faMu` | 伐木 | Lumbering |  |  | ⚠️ 需审校 |  |
| `yj.faMuZuoLiang` | 伐木做梁 | Make beams |  |  | ⚠️ 需审校 |  |
| `yj.fangShui` | 放水 | Drainage |  |  | ⚠️ 需审校 |  |
| `yj.fenJu` | 分居 | Live apart |  |  | ⚠️ 需审校 |  |
| `yj.fenXiang` | 焚香 | Burn incense |  |  | ⚠️ 需审校 |  |
| `yj.fuRen` | 赴任 | Go post |  |  | ⚠️ 需审校 |  |
| `yj.gaiWu` | 盖屋 | Build house |  |  | ⚠️ 需审校 |  |
| `yj.gaiWuHeJi` | 盖屋合脊 | Cover house |  |  | ⚠️ 需审校 |  |
| `yj.geMi` | 割蜜 | Harvest honey |  |  | ⚠️ 需审校 |  |
| `yj.guYong` | 雇佣 | Hire |  |  | ⚠️ 需审校 |  |
| `yj.guZhu` | 鼓铸 | Cast |  |  | ⚠️ 需审校 |  |
| `yj.guaBian` | 挂匾 | Hang plaque |  |  | ⚠️ 需审校 |  |
| `yj.guanJi` | 冠笄 | Crowning adulthood |  |  | ⚠️ 需审校 |  |
| `yj.guiNing` | 归宁 | Visit parents |  |  | ⚠️ 需审校 |  |
| `yj.guiXiu` | 归岫 | Place beam |  |  | ⚠️ 需审校 |  |
| `yj.heJi` | 合脊 | Close ridge |  |  | ⚠️ 需审校 |  |
| `yj.heShouMu` | 合寿木 | Make coffin |  |  | ⚠️ 需审校 |  |
| `yj.heZhang` | 合帐 | Make up accounts |  |  | ⚠️ 需审校 |  |
| `yj.huaiYuan` | 坏垣 | Demolish |  |  | ⚠️ 需审校 |  |
| `yj.huiQinYou` | 会亲友 | Meet friends |  |  | ⚠️ 需审校 |  |
| `yj.huiYou` | 会友 | Meet friends |  |  | ⚠️ 需审校 |  |
| `yj.jiSi` | 祭祀 | Sacrifice |  |  | ⚠️ 需审校 |  |
| `yj.jiaMa` | 架马 | Erect horse |  |  | ⚠️ 需审校 |  |
| `yj.jiaQu` | 嫁娶 | Marriage |  |  | ⚠️ 需审校 |  |
| `yj.jianGui` | 见贵 | Meet noble |  |  | ⚠️ 需审校 |  |
| `yj.jiaoNiuMa` | 教牛马 | Train horse |  |  | ⚠️ 需审校 |  |
| `yj.jiaoYi` | 交易 | Trade |  |  | ⚠️ 需审校 |  |
| `yj.jieChu` | 解除 | Removal |  |  | ⚠️ 需审校 |  |
| `yj.jieWang` | 结网 | Netting |  |  | ⚠️ 需审校 |  |
| `yj.jinRenKou` | 进人口 | Adopt |  |  | ⚠️ 需审校 |  |
| `yj.jingLuo` | 经络 | Build loom |  |  | ⚠️ 需审校 |  |
| `yj.jueJing` | 掘井 | Dig well |  |  | ⚠️ 需审校 |  |
| `yj.kaiCang` | 开仓 | Open depot |  |  | ⚠️ 需审校 |  |
| `yj.kaiCe` | 开厕 | Open toilet |  |  | ⚠️ 需审校 |  |
| `yj.kaiChi` | 开池 | Open pond |  |  | ⚠️ 需审校 |  |
| `yj.kaiGuang` | 开光 | Consecretion |  |  | ⚠️ 需审校 |  |
| `yj.kaiJing` | 开井开池 | Open pond and well |  |  | ⚠️ 需审校 |  |
| `yj.kaiQu` | 开渠 | Canalization |  |  | ⚠️ 需审校 |  |
| `yj.kaiRong` | 开容 | Open face |  |  | ⚠️ 需审校 |  |
| `yj.kaiShengFen` | 开生坟 | Open grave |  |  | ⚠️ 需审校 |  |
| `yj.kaiShi` | 开市 | Opening |  |  | ⚠️ 需审校 |  |
| `yj.kaiZhuYan` | 开柱眼 | Build beam |  |  | ⚠️ 需审校 |  |
| `yj.liBei` | 立碑 | Tombstone erecting |  |  | ⚠️ 需审校 |  |
| `yj.liFa` | 理发 | Haircut |  |  | ⚠️ 需审校 |  |
| `yj.liQuan` | 立券 | Covenant |  |  | ⚠️ 需审校 |  |
| `yj.liQuanJiaoYi` | 立券交易 | Covenant trade |  |  | ⚠️ 需审校 |  |
| `yj.maiChe` | 买车 | Buy car |  |  | ⚠️ 需审校 |  |
| `yj.muYang` | 牧养 | Graze |  |  | ⚠️ 需审校 |  |
| `yj.muYu` | 沐浴 | Bathing |  |  | ⚠️ 需审校 |  |
| `yj.naCai` | 纳采 | Proposing |  |  | ⚠️ 需审校 |  |
| `yj.naChai` | 纳财 | Accept wealth |  |  | ⚠️ 需审校 |  |
| `yj.naChu` | 纳畜 | Feed livestock |  |  | ⚠️ 需审校 |  |
| `yj.naXu` | 纳婿 | Uxorilocal marriage |  |  | ⚠️ 需审校 |  |
| `yj.pingZhi` | 平治道涂 | Repair roads |  |  | ⚠️ 需审校 |  |
| `yj.poTu` | 破土 | Break earth |  |  | ⚠️ 需审校 |  |
| `yj.poWu` | 破屋 | Break house |  |  | ⚠️ 需审校 |  |
| `yj.poWuHuaiYuan` | 破屋坏垣 | Demolish |  |  | ⚠️ 需审校 |  |
| `yj.puDu` | 普渡 | Save soul |  |  | ⚠️ 需审校 |  |
| `yj.qiFu` | 祈福 | Pray |  |  | ⚠️ 需审校 |  |
| `yj.qiJi` | 起基 | Digging |  |  | ⚠️ 需审校 |  |
| `yj.qiJiDongTu` | 起基动土 | Lay foundation |  |  | ⚠️ 需审校 |  |
| `yj.qiJiao` | 齐醮 | Build altar |  |  | ⚠️ 需审校 |  |
| `yj.qiZuan` | 启钻 | Open coffin |  |  | ⚠️ 需审校 |  |
| `yj.qiuCai` | 求财 | Seek wealth |  |  | ⚠️ 需审校 |  |
| `yj.qiuSi` | 求嗣 | Seek heirs |  |  | ⚠️ 需审校 |  |
| `yj.qiuYi` | 求医 | See doctor |  |  | ⚠️ 需审校 |  |
| `yj.qiuYiLiaoBing` | 求医疗病 | Seek treatment |  |  | ⚠️ 需审校 |  |
| `yj.quYu` | 取渔 | Fishing |  |  | ⚠️ 需审校 |  |
| `yj.ruLian` | 入殓 | Body placing |  |  | ⚠️ 需审校 |  |
| `yj.ruXue` | 入学 | Enter school |  |  | ⚠️ 需审校 |  |
| `yj.ruZhai` | 入宅 | Enter house |  |  | ⚠️ 需审校 |  |
| `yj.saiXue` | 塞穴 | Block nest |  |  | ⚠️ 需审校 |  |
| `yj.saoShe` | 扫舍 | Sweep house |  |  | ⚠️ 需审校 |  |
| `yj.shangLiang` | 上梁 | Beam placing |  |  | ⚠️ 需审校 |  |
| `yj.shuZhu` | 竖柱 | Erecting pillars |  |  | ⚠️ 需审校 |  |
| `yj.siZhao` | 祀灶 | Offer kitchen god |  |  | ⚠️ 需审校 |  |
| `yj.suHui` | 塑绘 | Paint sculptural |  |  | ⚠️ 需审校 |  |
| `yj.tanBing` | 探病 | Visiting |  |  | ⚠️ 需审校 |  |
| `yj.tianLie` | 畋猎 | Hunt |  |  | ⚠️ 需审校 |  |
| `yj.wanMian` | 挽面 | Cosmeticsurgery |  |  | ⚠️ 需审校 |  |
| `yj.wenMing` | 问名 | Ask name |  |  | ⚠️ 需审校 |  |
| `yj.xiYi` | 习艺 | Learn |  |  | ⚠️ 需审校 |  |
| `yj.xieTu` | 谢土 | Earth gratitude |  |  | ⚠️ 需审校 |  |
| `yj.xingSang` | 行丧 | Funeral |  |  | ⚠️ 需审校 |  |
| `yj.xiuFen` | 修坟 | Grave repair |  |  | ⚠️ 需审校 |  |
| `yj.xiuMen` | 修门 | Repair door |  |  | ⚠️ 需审校 |  |
| `yj.xiuShi` | 修饰垣墙 | Decorate wall |  |  | ⚠️ 需审校 |  |
| `yj.xiuZao` | 修造 | Repair |  |  | ⚠️ 需审校 |  |
| `yj.yiJiu` | 移柩 | Move coffin |  |  | ⚠️ 需审校 |  |
| `yj.yiXi` | 移徙 | Move |  |  | ⚠️ 需审校 |  |
| `yj.yuShi` | 馀事勿取 | Do nothing else |  |  | ⚠️ 需审校 |  |
| `yj.yunNiang` | 酝酿 | Brew |  |  | ⚠️ 需审校 |  |
| `yj.zaiZhong` | 栽种 | Farming |  |  | ⚠️ 需审校 |  |
| `yj.zaoCang` | 造仓 | Build depot |  |  | ⚠️ 需审校 |  |
| `yj.zaoCangKu` | 造仓库 | Build depot |  |  | ⚠️ 需审校 |  |
| `yj.zaoCheQi` | 造车器 | Build car |  |  | ⚠️ 需审校 |  |
| `yj.zaoChuChou` | 造畜稠 | Livestock thickening |  |  | ⚠️ 需审校 |  |
| `yj.zaoChuan` | 造船 | Build boat |  |  | ⚠️ 需审校 |  |
| `yj.zaoMiao` | 造庙 | Build temple |  |  | ⚠️ 需审校 |  |
| `yj.zaoQiao` | 造桥 | Build bridge |  |  | ⚠️ 需审校 |  |
| `yj.zaoWu` | 造屋 | Build house |  |  | ⚠️ 需审校 |  |
| `yj.zhaiJiao` | 斋醮 | Taoist rites |  |  | ⚠️ 需审校 |  |
| `yj.zhenJiu` | 针灸 | Acupuncture |  |  | ⚠️ 需审校 |  |
| `yj.zhengShou` | 整手足甲 | Manicure |  |  | ⚠️ 需审校 |  |
| `yj.zhiBing` | 治病 | Treat |  |  | ⚠️ 需审校 |  |
| `yj.zhiChan` | 置产 | Buy property |  |  | ⚠️ 需审校 |  |
| `yj.zhuDi` | 筑堤 | Fill |  |  | ⚠️ 需审校 |  |
| `yj.zhuShi` | 诸事不宜 | Everything Sucks |  |  | ⚠️ 需审校 |  |
| `yj.zuoBei` | 作陂放水 | Make pond and fill water |  |  | ⚠️ 需审校 |  |
| `yj.zuoCe` | 作厕 | Build toilet |  |  | ⚠️ 需审校 |  |
| `yj.zuoLiang` | 作梁 | Beam construction |  |  | ⚠️ 需审校 |  |
| `yj.zuoRan` | 作染 | Dye |  |  | ⚠️ 需审校 |  |
| `yj.zuoZhao` | 作灶 | Make stove |  |  | ⚠️ 需审校 |  |

### `yx.*` — 月相 (Moon Phases)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `yx.can` | 残 | Waning |  |  | ⚠️ 需审校 |  |
| `yx.eMei` | 蛾眉 | Waxing |  |  | ⚠️ 需审校 |  |
| `yx.eMeiCan` | 蛾眉残 | Waning waxing |  |  | ⚠️ 需审校 |  |
| `yx.eMeiXin` | 蛾眉新 | New waxing |  |  | ⚠️ 需审校 |  |
| `yx.gengDai` | 更待 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `yx.hui` | 晦 | Obscure |  |  | ⚠️ 需审校 |  |
| `yx.jiShuo` | 既朔 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `yx.jiWang` | 既望 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `yx.jianKuiTu` | 渐亏凸 | Disseminating |  |  | ⚠️ 需审校 |  |
| `yx.jianYingTu` | 渐盈凸 | Gibbous |  |  | ⚠️ 需审校 |  |
| `yx.jiuYe` | 九夜 | Nine night |  |  | ⚠️ 需审校 |  |
| `yx.juDai` | 居待 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `yx.liDai` | 立待 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `yx.night` | 宵 | Night |  |  | ⚠️ 需审校 |  |
| `yx.qinDai` | 寝待 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |
| `yx.shangXian` | 上弦 | First quarter |  |  | ⚠️ 需审校 |  |
| `yx.shuo` | 朔 | New |  |  | ⚠️ 需审校 |  |
| `yx.wang` | 望 | Full |  |  | ⚠️ 需审校 |  |
| `yx.xi` | 夕 | Evening |  |  | ⚠️ 需审校 |  |
| `yx.xiaXian` | 下弦 | Third quarter |  |  | ⚠️ 需审校 |  |
| `yx.xiao` | 晓 | Daybreak |  |  | ⚠️ 需审校 |  |
| `yx.xiaoWang` | 小望 | Little full |  |  | ⚠️ 需审校 |  |
| `yx.youMing` | 有明 |  |  |  | ❌ 缺失（回退中文） | en 未翻译，运行时回退到中文 |

### `zx.*` — 十二值日 (Twelve Duty Officers)

| key | 中文源词 | 6tail 英文候选 | 产品英文候选 | 使用场景 | 可直接用于 UI | 风险备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `zx.bi` | 闭 | Close |  |  | ⚠️ 需审校 |  |
| `zx.cheng` | 成 | Complete |  |  | ⚠️ 需审校 |  |
| `zx.chu` | 除 | Remove |  |  | ⚠️ 需审校 |  |
| `zx.ding` | 定 | Stable |  |  | ⚠️ 需审校 |  |
| `zx.jian` | 建 | Build |  |  | ⚠️ 需审校 |  |
| `zx.kai` | 开 | Open |  |  | ⚠️ 需审校 |  |
| `zx.man` | 满 | Full |  |  | ⚠️ 需审校 |  |
| `zx.ping` | 平 | Flat |  |  | ⚠️ 需审校 |  |
| `zx.po` | 破 | Break |  |  | ⚠️ 需审校 |  |
| `zx.shou` | 收 | Collect |  |  | ⚠️ 需审校 |  |
| `zx.wei` | 危 | Danger |  |  | ⚠️ 需审校 |  |
| `zx.zhi` | 执 | Hold |  |  | ⚠️ 需审校 |  |

---

## 四、en 完全缺失的命名空间（需补译）

以下 6 个命名空间 en 完全缺失，运行时回退到中文显示，需补译：

| 前缀 | 含义 | chs 条目数 | 补译优先级 |
| --- | --- | --- | --- |
| `d.*` | 农历日 (Lunar Days) | 30 | 高 |
| `ds.*` | 十二长生 (Twelve Life Stages) | 12 | 低 |
| `h.*` | 候 (Phenology, 72物候) | 75 | 低 |
| `m.*` | 农历月 (Lunar Months) | 12 | 高 |
| `od.*` | 孟仲季 (Meng/Zhong/Ji) | 3 | 低 |
| `ss.*` | 十神 (Ten Gods) | 10 | 中 |

---

## 五、彭祖百忌说明

彭祖百忌不在 I18n messages 里，而在 `_arrays.LunarUtil.PENGZU_GAN` 和 `PENGZU_ZHI` 数组中（lunar.js 行 8260-8261），通过 `{tg.jia}` 等占位符引用 messages，由 `_updateArray` 渲染。

若需抽取彭祖百忌英文候选，需单独解析这两个数组（本草稿暂不覆盖，待 W5 黄历后端实施时按需处理）。

---

## 六、参考来源

- `frontend/static/js/lunar.js` 行 6876-8471（I18n 模块）
- `docs/plans/2026-06-27-english-site-execution-plan.md` W1.1 任务定义
- `docs/business/wise-oracle-cultural-expression-guide.md` D6 神煞翻译策略
- `docs/business/huangli-english-localization-guidance.md` 黄历英文指导
