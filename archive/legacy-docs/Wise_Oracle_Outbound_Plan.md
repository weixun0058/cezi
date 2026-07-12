> **⚠️ 已废止文档（2026-06-30）**
>
> 本文档已废止，仅保留作历史参考。其内容与当前 W0 定稿文档（D13-D17 硬约束）全面冲突，**不得作为执行依据**。
>
> 主要冲突项：
> - 自由提问输入模式（已取消，改为 Three Words + Three Numbers）
> - New Age / cosmic energy 包装（与文化表达指南冲突）
> - Ask the Oracle 付费 Guidance / Future 3-Month Forecast（与 D17 interpretation 定位冲突）
> - Daoist Auspicious Calendar（产品规格禁用，仅解释文章谨慎使用）
> - 文本提问法哈希映射（已废止，改为 A=1..Z=26 字母求和 + stroke_digit）
>
> 当前执行依据：`docs/business/wise-oracle-english-product-spec.md` 等 W0 定稿文档。

---

# "Wise Oracle" 东方命理海外独立站出海落地全景指南与实操手册
> **域名资产**：`getwiseoracle.com`
> **版本**：v1.0 (2026年6月)
> **定位**：将传统东方命理（诸葛神算、黄历、八字）本地化包装，面向欧美及全球神秘学（New Age）受众的自动化变现平台。

---

## 🗺️ 全景路线图概览
本指南共分为四个核心执行阶段。作为独立开发者，建议采取 **“先跑通闭环，再补充内容，最后放大流量”** 的精益创业（MVP）策略：

```
【第一阶段】核心重构（第1-2周） --> 解决“老外怎么玩”与“结果怎么看”的问题
【第二阶段】合规与低保（第3-4周） --> 搭建内容缓冲带，搞定 Google AdSense 审核
【第三阶段】财务闭环（第5周）    --> 对接全球收款渠道（打赏 + 自动化高级报告付费）
【第四阶段】增长与裂变（第6周+）   --> 盘活私域与公域流量，建立内容变现正循环
```

---

## 🛠️ 第一阶段：核心交互重构与“文化翻译”（第 1 - 2 周）
**核心目标**：把中文的“汉字笔画算命”平替为西方用户无门槛使用的“灵数/文本起卦”，并完成384签诗的本地化。

### 🔘 步骤 1.1：前端交互与后端算法重构（算事/诸葛神算）
西方人无法理解汉字，必须改造输入源。

* **执行动作 1**：在英文版“算事（Zhuge Oracle）”页面提供两种输入交互：
    * *交互 A（自由提问）*：一个文本框，引导语：`"Formulate a clear question in your mind and type it below (e.g., 'Will my investment succeed this month?')."`
    * *交互 B（随机数字）*：三个独立的输入框，引导语：`"Close your eyes, breathe deeply, and enter 3 random numbers between 000 and 999."`
* **执行动作 2（后端算法平替）**：
    * 如果是*数字法*：直接透传用户输入的三个数字，带入你原有的诸葛神算数学公式（求和/求余等），计算出最终的签号（1-384）。
    * 如果是*文本提问法*：为了让用户“同一句话得到同一个签”，在后端用一段轻量级代码处理：
        ```python
        import re

        def text_to_sign_number(user_input_text):
            # 1. 清理文本：只保留小写字母
            clean_text = re.sub(r'[^a-z]', '', user_input_text.lower())
            if not clean_text:
                return 1 # 兜底签号
            
            # 2. 计算所有字母在26个字母中的位置总和 (a=1, b=2... z=26)
            total_sum = sum(ord(char) - ord('a') + 1 for char in clean_text)
            
            # 3. 映射到诸葛神算384签 (求余数加1)
            sign_number = (total_sum % 384) + 1
            return sign_number
        ```

### 🔘 步骤 1.2：利用大模型批量重写 384 签诗（New Age 风格）
切忌直译中国历史典故（如刘备、关公、曹操），必须转化为西方神秘学圈子崇尚的“宇宙能量、行动启示”风格。

* **执行动作**：编写一个 Python 脚本或直接在网页端使用大模型（如 Gemini / ChatGPT），将你的 384 签诗数据库批量导出并结构化翻译。
* **标准 Prompt 模板**：
    > "You are an expert in both ancient Chinese I Ching / Zhuge Oracle and Western New Age mysticism (Tarot/Oracle cards). Please translate and localize the following Chinese oracle sign into a poetic, mysterious, yet psychology-grounded English reading. 
    > 
    > Format the output exactly into 3 parts:
    > 1. [The Oracle]: A poetic, short title summarizing the energy (e.g., 'The Stagnant Stream', 'The Rising Dawn').
    > 2. [The Message]: A deep analysis of their current energy situation. Frame it as reflection rather than fatalism. (Avoid historical Chinese names).
    > 3. [The Guidance]: Practical, concrete advice on what to do next.
    > 
    > Chinese Original Sign: [在此处输入你的古文签诗]"
* **转化对比示例**：
    * *原签诗*：“毫无滋味，实要费心，防有小人夺，倒要费心神。”
    * *出海版输出*：
        * **The Oracle**: *"The Drained Oasis"* (干涸的绿洲)
        * **Message**: *"You are entering a temporary phase of low cosmic resonance where current pursuits may feel flavorless and uninspiring. Your spiritual radar detects subtle resistance. Be Mindful of energy vampires or misalignments in your immediate circle who may try to misdirect your focus."*
        * **Guidance**: *"Protect your energetic boundaries. This is a time for conservation, not aggressive expansion. Meditate daily, decline draining social obligations, and wait for the transit to pass."*

---

## 📝 第二阶段：内容缓冲带建设与 AdSense 申请（第 3 - 4 周）
**核心目标**：通过补充高价值文本内容，绕过 Google 对纯工具站的“低价值内容”拒信，顺利拿下 AdSense 广告低保。

### 🔘 步骤 2.1：开辟 `/blog` 资讯目录并批量填充内容
* **执行动作 1**：在你的独立站下新建目录 `getwiseoracle.com/blog` 或 `getwiseoracle.com/insights`。
* **执行动作 2**：批量生成 **25 - 30 篇** 高质量英文原创文章。文章必须通顺、有深度，每篇字数控制在 **1000 - 1500 字** 之间。
* **黄金选题推荐**（直接使用大模型撰写，确保包含正确的神秘学SEO关键词）：
    1.  *The Beginner’s Guide to I Ching: History, Philosophy, and Oracle Reading.*
    2.  *How Chinese Numerology Differs from Western Astrology.*
    3.  *Understanding the Lunar Calendar: How to Find Your Auspicious Days.* (联动你的黄历板块)
    4.  *Who was the Sage Zhuge Liang? The Story Behind the 384 Divine Numbers.* (讲好品牌故事)
    5.  *Tarot vs. Zhuge Oracle: Choosing the Right Divination Method for Your Question.*

### 🔘 步骤 2.2：补齐出海三大硬性合规页面
确保网站所有页面脚部（Footer）有明显的英文链接导航：
1.  **Privacy Policy（隐私政策）**：必须包含符合 GDPR 和 CCPA 的合规条款。明确写明：“本站包含第三方广告联盟（如 Google AdSense），其会使用 Cookie 收集非敏感数据以展示个性化广告。”
2.  **Terms of Service & Disclaimer（服务条款与免责声明）**：**极其重要！** 必须包含以下法务免责：
    > *"Disclaimer: All readings, forecasting, and calendar alignments provided by GetWiseOracle.com are for traditional cultural appreciation and entertainment purposes only. They do not constitute legal, financial, medical, or psychological advice."*
3.  **About Us & Contact Us（关于与联系）**：写一段真诚的作者/团队简介，树立专业度（E-E-A-T），并留下一个可真实联系的邮箱（如 `support@getwiseoracle.com`）。

### 🔘 步骤 2.3：配置 Google Search Console 并提交 AdSense 审核
* **执行动作 1**：将网站注册到 Google Search Console，提交 `sitemap.xml`，确保你发的所有博客文章都被 Google 成功建立索引。
* **执行动作 2**：在 Google 搜索框输入 `site:getwiseoracle.com`，确认至少能搜到 20 个以上的页面结果。
* **执行动作 3**：登录 Google AdSense 后台，添加网站，将广告验证代码粘贴至你网站前端 HTML 的 `<head>` 标签中，提交等待人工审核（通常需要 3 - 14 天）。

---

## 💳 第三阶段：多级财务链路打通（第 5 周）
**核心目标**：告别国内个人收款的合规困境，用最低的摩擦力接入海外美金收款。

### 🔘 步骤 3.1：低门槛配置——客户主动打赏（冷启动）
利用海外非常成熟的赞助文化，给免费用户一个表达感谢的通道。
* **执行动作 1**：前往 **Buy Me a Coffee (BMC)** 或 **Ko-fi** 注册个人创作者账号，绑定你的个人 PayPal 账号。
* **执行动作 2**：在其后台定制一个专属按钮，文案写：`"Buy the Oracle a Coffee"`（给神谕买杯咖啡）。
* **执行动作 3**：将 Widget 悬浮代码或按钮 HTML 嵌入到你的“算事结果页”和“博客文章末尾”。

### 🔘 步骤 3.2：高转化配置——自动化高级报告付费解锁（现金流主力）
通过分层显示结果，实现“免费引流 + 付费解锁深度报告”的 SaaS 模型。
* **产品逻辑分层**：
    * *免费内容*：展示 `[The Oracle]` 和 `[Message]`。
    * *付费墙（Paywall）遮罩*：将 `[Guidance]`（具体行动指南）和 `[Future 3-Month Transit Forecast]`（未来三个月运势预测）模糊化。
    * *定价策略*：小额微支付，建议定价 **$2.99 或 $4.99**（极易冲动消费）。
* **免开发/低代码接入方案（推荐 Lemon Squeezy）**：
    * **为什么选 Lemon Squeezy / Gumroad**：它们是专门的数字产品销售平台（Merchant of Record），会自动帮你处理欧美各州复杂的消费税，且支持信用卡、Apple Pay、Google Pay 和 PayPal，完美解决个人开发者无海外公司实体的问题。
    * **实操步骤**：
        1. 注册 Lemon Squeezy 账号，创建一个“数字商品”，命名为 `Zhuge Oracle - Full Detailed Strategic Report`。
        2. 获取该商品的“Checkout Link（收银台跳转链接）”。
        3. 在网站的付费遮罩层上放一个高亮按钮：`"Unlock Full Strategic Guidance & Future Forecast for $4.99"`。
        4. **配置 Webhook 自动解锁**：用户付完钱后，Lemon Squeezy 会向你的服务器后端发送一个 Webhook 异步通知。你的后端收到通知后，通过 Session 或临时 Token，在前端为该用户渲染并展示出完整的签诗 Guidance 内容。

---

## 📈 第四阶段：精细化运营与海外流量增长（第 6 周+）
**核心目标**：利用海外对神秘学极度饥渴的自然流量，为你的变现机器持续注入用户。

### 🔘 步骤 4.1：海外社交媒体流量截流（TikTok / Instagram / Pinterest）
占卜类内容在海外社交媒体上是公认的“流量制造机”。
* **执行动作 1（短视频裂变）**：利用 AI 视频工具或 Canva，制作极简风格的神秘学视频。
    * *视频画面*：一张带有东方八卦阵或复古羊皮纸特效的静态/微动背景，中间一行神秘字。
    * *文案文案*：`"Stop scrolling. The universe guided you here for a reason. Pick a number from 1 to 3, then check the link in my bio for your Zhuge Oracle guidance."`
    * *话题标签（Hashtags）*：必须带上 `#WitchTok`、`#spirituality`、`#oracle`、`#iching`、`#fortunetelling`。
* **执行动作 2（Bio引流）**：在你的 TikTok 和 Instagram 账号主页（Bio）挂上你的域名 `http://getwiseoracle.com`。

### 🔘 步骤 4.2：风控避坑指南
1.  **支付账单描述规范**：在 Lemon Squeezy 或 PayPal 后台，将你的“商户账单名称（Statement Descriptor）”配置为 **`WISEORACLE-SERVICE`** 或 **`WISEORACLE-DIGITAL`**。**绝对不要**出现 `Fortune Telling（算命）`、`Suanming`、`Magic（魔法）`、`Witchcraft（巫术）` 等敏感字眼，否则极易触发金融机构风控导致冻结账号。
2.  **黄历板块英文包装**：你网站上的“黄历”是非常独特的资产。不要翻译成 "Yellow Calendar"，请翻译成 **"Daoist Auspicious Calendar"**（道教吉日历）或 **"Daily Cosmic Energy Guide"**（每日宇宙能量指南），把“宜/忌”包装成 "Favorable Activities / Unfavorable Activities"，更符合西方瑜伽、正念圈子的黑话。

---

## 📅 独立开发者今日行动确认清单（Todo List）

- [ ] **Task 1**：登录你的服务器，确认 `getwiseoracle.com` 的 SSL 证书（HTTPS）状态为“已开启”。
- [ ] **Task 2**：写一段后端脚本，将英文字符串/随机数计算映射到 1-384 的数学公式跑通。
- [ ] **Task 3**：用大模型批量翻译并重写前 20 个签诗，测试前端渲染效果。
- [ ] **Task 4**：注册 Buy Me a Coffee 账号，生成你的第一个赞助链接。
