## 译文审核发现：系统性偏差说明

在对 24 条签文进行深度审核后，发现了一个**极其严重的系统性数据对齐问题**：
在 **22 条签文**（第 141、143-145、147-164 签）中，DeepSeek **完全没有翻译** 中文 JSON 中提供的现代、心理学/疗愈风格的解读文本（如“你当下的事业运势像走在薄雾笼罩的山路上...”）。相反，它基于签文诗句（`sign_text`）和其内部知识库，**自行重新撰写** 了一套高度技术化、包含大量易经传统术语（如“Zhen Palace”、“Pi to Wu Wang”、“Xun wood element”等）的英文解读。

整套数据中，**仅有第 142 签和第 146 签** 是对中文原文的真实、忠实翻译。这两签的翻译质量极高，达到了出版级水准。

因此，在以下单签审核中，对于存在“重写”问题的 22 条签文，其**语义忠实度**均被判定为 **D（不及格）**，并将其列为 [Critical] 级系统性漏译/增译问题。不过，针对其诗歌翻译（`sign_text`）以及英文文本本身的语言质量，我们依然进行了客观评估，以便为后续整改提供参考。

---

## 签文逐条审核

### ## 第 141 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文完全脱离了中文原文中“薄雾山路、黎明破晓”的现代疗愈系解读，自行植入了“Li hexagram（离卦）”等中文原文中完全没有的易经学术背景，属于**系统性重写**（非翻译）。
2. [Medium] career 字段 → "recognition will come after the clouds clear." 包含对求签人未来状态的直接预测，属于“真绝对化” will，建议软化。

#### 亮点

- `sign_text` 翻译极佳：“Guard against thunder in the dark, / Suspicion and worry leave no mark. / In a blink the black clouds clear, / Ushering forth the sun on Fusang's arc.” 节奏优美，双行押韵自然，且保留了“扶桑日”这一中国神话意象（Fusang's arc）。

#### 修改建议

- **整改方案**：必须根据中文原文重新翻译。
- **原英文 Career 节选**：The 'thunder in the dark' suggests hidden conflicts...
- **应修改为（忠实翻译原中文）**：Your current career fortune is like walking on a misty mountain road, seemingly peaceful but requiring caution for loose pebbles underfoot. Those hidden dangers causing you unease may be mere projections of your inner anxiety.

---

### ## 第 142 签审核

#### 评分

- 语义忠实度：A
- 文化传达：A
- 诗歌韵律：A
- 语言质量：B
- 一致性：A
- 综合：A-（优秀翻译，仅有少量 will 需软化）

#### 问题清单

1. [Medium] career 字段 → "...your career landscape will gradually open up." 属于直接预测的 will。建议改为 "...is poised to gradually open up"。
2. [Medium] love 字段 → "...things that once seemed distant will flow naturally to you..." 属于直接预测的 will。建议改为 "...are likely to flow naturally..."；此外，"Some fates require you..." 中 "fates" 过于绝对和宿命论，建议改为 "Some connections/destinies"。
3. [Medium] health 字段 → "...you will naturally harvest a radiance of well-being..." 属于直接预测。建议改为 "...you are poised to naturally harvest..."。
4. [Medium] study 字段 → "...These small accumulations will eventually gather into a torrent... those seemingly boring exercises will become the edge..." 属于直接预测。建议改为 "...are poised to eventually gather..." 以及 "...may become the edge..."。
5. [Medium] general 字段 → "...pressure will become the force... you will reach an important transition... The final harvest will exceed expectations..." 均属直接预测。建议分别改为 "may become", "are likely to reach", "is likely to exceed"。

#### 亮点

- `sign_text` 翻译极其精准、考究：“获丑”准确地翻译为历史学意义上的 "capture the enemy"（古汉语中“丑”指敌人/俘虏）；“丹诏”译为 "crimson edict"，极具古典威仪。
- 散文部分翻译极富文学美感，完美传达了中文如“living water that you must actively grasp（活水）”和“lest you become drifting duckweed（浮萍）”的精妙比喻。

#### 修改建议

- 针对 will 进行软化（见问题清单），其余文本保持不变。

---

### ## 第 143 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文完全脱离了中文原文中“内外拉扯、独自过独木桥、整理抽屉”的疗愈内容，自行引入了“Innocence hexagram（无妄卦）”、“Xun wood element（巽木）”等原文中没有的技术词汇，属于重写。

#### 亮点

- `sign_text` 翻译精炼：“Sigh for worries outside, / Lament for turmoil within the door.” 句式对称，完美对应“堪叹外边忧，更嗟门里闹”。

#### 修改建议

- 必须根据中文原文重新翻译，去除所有未授权引入的易经卦象术语。

---

### ## 第 144 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文脱离中文关于“层层关卡、不透水的闷葫芦、蓄水养生”的描述，自行加入了“Great Possession to Li（大有变离）”等复杂的卦变分析。

#### 亮点

- `sign_text` 翻译极具意境：“Beyond the vase, there is another sky.” 传神地翻译了中国道家文化中的“壶中别有天”。

#### 修改建议

- 必须对照中文关于“翻山渡河、闷葫芦”的原意重新翻译。

---

### ## 第 145 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 现代散文未予翻译，译文自行引入了“Da You to Da Xu（大有变大畜）”及“Qian Palace（乾宫）”等复杂的卦理。

#### 亮点

- `sign_text` 的押韵非常流畅自然：fret/regret, crown/hand，节奏轻快，符合原诗“咫尺青云路”的欢快基调。

#### 修改建议

- 重新翻译，保留中文原版关于“草头人未必是姓氏、带着泥土气的温度”等生动细腻的现代疗愈表述。

---

### ## 第 146 签审核

#### 评分

- 语义忠实度：A
- 文化传达：A
- 诗歌韵律：A
- 语言质量：A
- 一致性：A
- 综合：A（全套签文中质量最高的一篇，达到出版级）

#### 问题清单

1. [Low] wealth 字段 → "The fog will clear to show the path forward." 虽属比喻，但为了追求绝对的非预言感，可微调为 "The fog is poised to clear..."。

#### 亮点

- **神来之笔**：`sign_text` 的第一句 "The boat races through the midstream rapids" 极富动感，完美还原了“船棹中流急”的紧迫画面。
- 译文用词精妙，如将“与无常共处”译为 "coexistence with impermanence"，“将焦虑拧成审视风险的准绳”译为 "Turn anxiety into a rope for assessing risk"，文学造诣极高，且完全忠实于中文原文的每一个意象。
- will 的用法控制得极其得体，全部符合“假绝对化”准则（描述自然规律或文学画面）。

#### 修改建议

- 无需强制修改，可直接作为标杆译文保留。

---

### ## 第 147 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 现代解读部分未予翻译。译文植入了“Zhen Palace”、“Sui hexagram”、“Wu Wang”等中文原文完全不存在的内容。

#### 亮点

- `sign_text` 翻译极其工整：“A chip of jade, a tiny pearl.” 完美对应了“片玉寸珠”，用词高雅。

#### 修改建议

- 重新翻译，还原中文关于“给老座钟上发条、蓄雨水、修补古瓷”等质朴且极具生活化智慧的现代比喻。

---

### ## 第 148 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文脱离中文关于“积蓄养分的幼苗、灶台里的火星、花谢的必然周期”的疗愈视角，重写为包含“Li Palace”、“Ding to Lu hexagram”等易学专业词汇的文本。

#### 亮点

- `sign_text` 翻译具有强烈的预言史诗感：“Flowers fade, yet seeds form—the harvest is blessed.” 极具文学张力。

#### 修改建议

- 重新对照中文原文翻译。

---

### ## 第 149 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译中文原文关于“手里攥着两颗种子、枯荣对照、新旧交替”的现代阐述，而重写为“Da Guo to Heng”等易学分析。

#### 亮点

- `sign_text` 翻译极其干练且语义高度对称：“One mind on two things, one thing with two minds;” 堪称对“一心两事，一事两心”的最佳英译。

#### 修改建议

- 重新翻译，恢复中文原稿中对多方向徘徊的细腻心理描写。

---

### ## 第 150 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译中文关于“进退两难的泥潭、褪色的绸缎、蒲公英”的文学疗愈叙事，而强行植入“Kun changes into Song”等专业易卦论述。

#### 亮点

- `sign_text` 翻译精准、凝练、悲凉：“Great matters may be hard to achieve; / Withered blossoms bloom no more.” 完美传递了原诗的宿命感。

#### 修改建议

- 对照中文原稿中“老木匠不劈断锯、考古学家清理文物”等极佳现代比喻进行忠实重译。

---

### ## 第 151 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文完全忽略了中文原文“悬在迷雾里的灯、踩着潮水涨退的滩涂、月圆月缺的警示”等极美现代比喻，而是重写为一整套“Xian to Cui”的易学学术报告。

#### 亮点

- `sign_text` 将“桂轮”巧妙译为 "The cassia wheel"，准确保留了中国古典文学中月亮上种有桂树的神话背景，文化传达极为出色。

#### 修改建议

- 必须基于中文关于“反复擦拭镜面、进退试探、量变催生质变”的原文进行重译。

---

### ## 第 152 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 现代解读部分被重写，强行加入了“Kan to Kun hexagram”及“肾、膀胱、下肢水肿”等原文完全没有的中医与易学技术信息，丢失了中文原稿关于“长竿钓鱼、水面折射碎金”等现代心理引导。

#### 亮点

- `sign_text` 韵律极佳：“Do not sigh that matters delay; / Do not say they will never reach their end...” 叹息与结束的语调抓得非常精准。

#### 修改建议

- 重新翻译，保留中文原版“别被‘终’字骗了、再续三寸坚持”等充满生命智慧和温润抚慰的现代金句。

---

### ## 第 153 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译原文中“站在薄冰边缘、鞋跟总被杂草勾缠、崴脚冲顶”等现代生动隐喻，自行植入了“Cui to Pi hexagram”、“Dui as Lake”等易经卦理。

#### 亮点

- `sign_text` 第二行“Take no hasty step, lest you fall before you.”（未为恐先踬）翻译得非常地道，节奏紧凑。

#### 修改建议

- 重新翻译，忠实还原原文中关于“别强求结果、种子总要等春雨”的现代意向。

---

### ## 第 154 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 现代散文未予翻译。译稿自行写成了“Kun to Cui hexagram”、“Zusanli and Yongquan points（足三里和涌泉穴）”等高度具体的中医穴位和易学信息。

#### 亮点

- `sign_text` 翻译对仗优美：“The foot is unsteady, the cart is unsteady, / Two matters come together, / Worry comes, yet turns to joy.” 完美再现了原诗民谣风的轻快感。

#### 修改建议

- 重新翻译，保留中文关于“走钢丝保持平衡、太极阴阳鱼、竹笋顶破冻土”等精妙的现代解读。

---

### ## 第 155 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文忽略了中文关于“歪了脚的鼎、断裂处新生的骨痂、老屋榫卯”等现代修复心理学隐喻，硬套了“Ding to Gu”、“Li Palace”等传统卦变分析。

#### 亮点

- `sign_text` “车脱辐”准确译为 "the cart loses its spoke"（spoke 为车轮辐条，用词极为严谨）。

#### 修改建议

- 对照中文重新翻译，聚焦于现代重整、不将就和寻找人生新状态的疗愈语境。

---

### ## 第 156 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译中文中“刚沸的水、老树盘根、煮一锅老汤”等优美比喻，重写为了“Cui to Bi hexagram”和传统口舌诉讼分析。

#### 亮点

- `sign_text` 对“波涛扬沸”的处理极佳："waves boil and rise"，极具画面张力。

#### 修改建议

- 重新翻译，恢复中文原稿中对在纷扰和时间逆境中“稳住呼吸、当个清醒观察者”的现代积极心态引导。

---

### ## 第 157 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译中文原文中“手气旺得像刚开封的汽水、春天急着开尽所有花、考场上的德就是底子”等极具现代感和趣味性的比喻，重写为干瘪的传统卦象说明。

#### 亮点

- `sign_text` “功名唾手成”直译为 "Fame and rank come as easy as spitting"，虽然略显粗俗，但保留了中文俗语“唾手可得”的生动肉体感。

#### 修改建议

- 重新翻译，重点保留现代语境下对“唾手可得之物”保持清醒和每天存下健康元气的哲理。

---

### ## 第 158 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 现代散文部分未予翻译。译文自行引入了“Guai to Da Zhuang hexagram”及“脾胃运化、气机淤滞”等医学易理。

#### 亮点

- `sign_text` 翻译节奏感强，句式凝练：“In laughter and talk lies hidden peril; / With united hearts, matters bring joy.” 极其精准。

#### 修改建议

- 重新对照中文翻译，保留“玩笑里藏着隐形的刺、走钢丝般的交际、背靠背的同心合力”等现代职场与人际心理学分析。

---

### ## 第 159 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 现代解读被重写，植入了“Gen Palace, Lu to Kui”等易理及“肝郁脾湿”等原文完全没有的中医病理，丢失了中文“月亮穿透云层、擦拭过的镜面、无克剥即无损耗”等现代解读。

#### 亮点

- `sign_text` 翻译极具画面感，"ink-black clouds" 对应 “墨云”，"sky's heart" 对应 “天心”，忠实且具诗意。

#### 修改建议

- 重新对照中文原文翻译。

---

### ## 第 160 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文强行植入了“Shi Ke to Jin hexagram”以及“肝胆郁结、虚火上扰”等硬性中医信息，完全颠覆了中文原文中“卸下必须立刻成功的包袱、每天能握住的刻度、在迷雾中种下自己的灯”等极美的心理疗愈和自我调节语境。

#### 亮点

- `sign_text` 翻译行云流水：“One leans on the tower, burdened with sorrow. / With calm and steady steps, / Matters first become free of worry.” 极具中国古典山水画中孤身凭栏的寂寥感。

#### 修改建议

- 必须根据中文极其温柔且富有哲理的原文进行重译。

---

### ## 第 161 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文偏离了中文原文关于“枯枝发芽需沉住钝劲、不贪多的智慧、熬中药文火慢炖”等绝佳的心理学与哲学建议，重写为了“Zhong Fu to Huan hexagram”等传统易学。

#### 亮点

- `sign_text` 极度对称，韵律极其自然（warmth/meets, anew/two），是整套签文中诗歌翻译的顶尖之作。

#### 修改建议

- 针对散文部分进行全盘忠实重新翻译。

---

### ## 第 162 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 译文完全忽略了中文原文中关于“踩在未化的积雪里、老茶农焙茶守着火候、雨水冲刷岩石”等极美的现代文学隐喻，擅自重写为了“Ge to Sui hexagram”和传统脏腑医学（肾、膀胱、耳鸣、尿浑浊等）。

#### 亮点

- `sign_text` 简洁凝练，极其耐读：“The road is long and far, / The gate and courtyard sealed; / Mists gather thick then pass, / Clouds part to see the sun.”

#### 修改建议

- 对照中文原文重新翻译。

---

### ## 第 163 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译中文原文中“丝线绷紧快要断、摸清鱼性、加固根基、弓弦绷紧”等极佳现代解读，自行撰写了“Sui to Zhun hexagram”、“Zhen Palace”等卦象信息。

#### 亮点

- `sign_text` 翻译精准无误：“The fish has taken the hook, / But the fishing line is weak; / To land it is no easy task, / Apply more strength and technique.”

#### 修改建议

- 必须对照中文原文重译，恢复“该使巧劲别光用蛮力、绷得太紧反而容易折断”等极具指导意义的现代格言。

---

### ## 第 164 签审核

#### 评分

- 语义忠实度：D
- 文化传达：B
- 诗歌韵律：A
- 语言质量：B
- 一致性：D
- 综合：D

#### 问题清单

1. [Critical] 全文 → 未翻译原文“藤蔓相互缠绕着生长、揉皱的纸团、春蚕吐丝”等温暖现代的生机词汇，而将其重写为了带有“Pi to Wu Wang hexagram”等易学阐释的内容。

#### 亮点

- `sign_text` 的情感传达极其温润，"Warm and sincere, joy comes naturally" 译出了“殷勤喜自然”的真诚与纯粹。

#### 修改建议

- 重新对照中文原文翻译。

---

## 整体总结报告

### 1. 总体评分：D（不及格）

虽然诗歌翻译（`sign_text`）表现极其亮眼（达到了 **A 级**），且在唯一的两篇真翻译（第 142、146 签）中展现出了极高的翻译水准（**A 级**），但由于 **高达 92%（22/24 条）** 的签文解读、事业、财运、情感等字段出现了**彻底的系统性偏离与未授权重写**，本套英文翻译从“翻译忠实度”维度来看，综合评级为 **D**，无法直接在生产环境中作为翻译成果使用。

### 2. 共性问题分析

- **系统性上下文漂移（Massive Hallucination/Rewrite）**：译者模型在处理第 141、143-145、147-164 签时，完全忽略了 JSON 输入中对应的中文解读字段，而是根据 `sign_text` 诗句直接触发了其内部知识库中的“传统周易六十四卦卦变、八宫卦属、中医五行脏腑理论”。这导致了严重的语义不对齐。中文原本是极具温度的**“现代心理/疗愈系咨询”**，而英文却变成了**“硬核传统命理与中医诊断”**，完全偏离了产品定位。
- **真绝对化 "will" 的使用**：在第 142 签等翻译中，出现了一些对用户状态和结果的直接宿命论预测（如 "will open up", "will eventually gather"），这些违反了无绝对化预测的硬性规定，但由于数量不多，极易通过轻度后期润色（如改为 `is poised to` 或 `may`）进行修复。
- **违禁词/宿命论表述**：在第 142 签中出现了 "fates" 用于指代因缘，稍显生硬，需微调。

### 3. 优先修改项（按签号排列）

- **[Critical] 第 141、143、144、145、147-164 签**：上述 22 条签文的 `interpretation1`、`career`、`wealth`、`love`、`health`、`study`、`general` 字段需要**全部退回重新翻译**。
- **[High] 第 142 签**：
  - `career`：将 "...will gradually open up" 软化为 "...is poised to gradually open up"。
  - `love`：将 "...will flow naturally..." 改为 "...are likely to flow naturally..."；将 "fates" 替换为 "connections"。
  - `health`：将 "will naturally harvest" 软化为 "is poised to naturally harvest"。
  - `study`：将 "will eventually gather" 软化为 "are poised to eventually gather"；"will become" 改为 "may become"。
  - `general`：将 "will become", "will reach", "will exceed" 分别软化为 "may become", "are likely to reach", "is likely to exceed"。

### 4. 可接受项（免修项）

- **所有 24 条签文的 `sign_text`（签文诗）字段**：翻译质量极其高超，音律和谐，用词典雅，精准传神（如“壶中天”译为 "Another sky in the vase"，“片玉寸珠”译为 "A chip of jade, a tiny pearl"）。建议予以**全盘保留，无需任何修改**。
- **第 146 签的全部字段**：属于大师级翻译，完全忠实且极富文学色彩，可直接用作优秀样板。

### 5. 建议重译项（重译签号）

- **第 141, 143, 144, 145, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164 签**（共 22 条，仅需重译除 `sign_number` 和 `sign_text` 外的解读性散文字段）。

### 6. 改进建议（针对翻译流程和 Prompt 调试）

1. **隔离输入源，防止大模型“自作聪明”**：大模型（如 DeepSeek）内部拥有极其丰富的《易经》及占卜知识储备。当它看到“卦名”或“签号”时，会极易触发其内在记忆而忽略你给的输入文本。在重新运行翻译时，**强烈建议在 Prompt 中加入以下强约束**：
   
   > *"WARNING: You are a pure TRANSLATOR. Do NOT write your own interpretations of the signs based on I Ching, hexagrams, or TCM. You MUST ONLY translate the provided Chinese text in each field (career, wealth, love, etc.) sentence-by-sentence into English. Do not add any hexagram or palace terms (like Qian Palace, Xun wood, etc.) if they are not explicitly present in the Chinese source text."*
2. **分批次/逐字段翻译**：如果 JSON 整体输入导致模型逻辑过载，可以尝试将 `sign_text`（诗歌体）与现代散文解读字段分流翻译。对于散文部分，使用严格的、低创造性的学术翻译指令；而对于诗歌部分，则使用高创造性的文学翻译指令。
3. **提供标准软化示例**：在 Prompt 中明确规定，将中文的“必然、会、将”一律对应翻译为 `may`, `is likely to`, `is poised to`, `suggests potential to`，从而在源头上彻底解决 True Absolutist "will" 的问题。
