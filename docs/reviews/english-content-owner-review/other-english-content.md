# 非签文极端问题清单

> 英文黄历、四柱 Prompt/fallback、文章占位和公开定位页面均已检查。本册只保留 2 个可能直接影响医疗或法律行动时机的问题。

## OTHER-HUANGLI-001：医疗事项日期判断

- 初筛结论：**达到极端候选阈值，倾向修改**
- 风险规则：`MED-02`
- 内容位置：`data/content/huangli_terms_en.json / $.activity_categories.medical_care`
- 极端点：黄历会对求医、针灸、治病给出宜忌日期，可能让用户按占卜结果选择或推迟医疗时机。

**当前内容**

> "label": "Medical Care"
> "sources": ["针灸", "求医", "治病", "求医疗病"]

**我的建议**

更稳健的做法是不对医疗事项输出宜忌；至少必须明确“不得因黄历推迟或改变医疗安排”。

**项目所有者决定**

- [ ] 按建议方向修改
- [ ] 保留原文并接受风险
- [x] 删除该分类
- [ ] 另行指定修改方式

**修改结论**

从 `huangli_terms_en.json` 的 `activity_categories` 中移除 `medical_care` 分类（含 `label` 与 `sources`），黄历宜忌不再对医疗事项输出宜忌日期。

**实施结果**

已从 `huangli_activities_curated.json` 人工审校源删除并重新生成 `huangli_terms_en.json`；正式词表不再包含 `medical_care`。

---

## OTHER-HUANGLI-002：法律事项日期判断

- 初筛结论：**达到极端候选阈值，倾向修改**
- 风险规则：`LEG-01`
- 内容位置：`data/content/huangli_terms_en.json / $.activity_categories.legal_matters`
- 极端点：黄历会对诉讼事项给出日期宜忌，可能影响具有法定期限的现实法律行动。

**当前内容**

> "label": "Legal Matters"
> "sources": ["词讼"]

**我的建议**

若保留，应明确不能替代律师意见、法定期限或程序安排；不得预测案件结果。

**项目所有者决定**

- [x] 按建议方向修改
- [ ] 保留原文并接受风险
- [ ] 删除该分类
- [ ] 另行指定修改方式

**修改结论**

保留 `legal_matters` 分类，但在黄历输出此分类时附加免责声明：「本黄历内容仅供文化参考，不得替代律师意见、法定期限或程序安排；亦不得据以预测案件结果。」

**实施结果**

API 与结果页实际显示：

> Traditional almanac references to legal matters are cultural context only. They are not legal advice or a prediction of any case outcome. Consult a qualified legal professional for decisions about your situation.

## 已检查并排除

- 一般求财、开业、经营、购买、签约、婚礼和搬家等传统黄历分类。
- 四柱 Prompt/fallback 的严格限制。
- Terms 与 Birth Chart 的文化自我反思定位。
- 英文文章占位页。
