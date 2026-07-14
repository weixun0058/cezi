# 诸葛神算 V4 项目问题清单与真假问题判定

> 审查日期：2026-07-14
> 审查对象：`codex/i18n-commercialization` 当前工作区，以及远端最新提交 `47ba334`
> 审查性质：审查与修复记录；本轮已修改业务代码、测试、依赖和工程格式。
> 目的：区分真实缺陷、契约变更、过时测试、格式债务、环境误报和尚未完成的产品工作。

## 0. 2026-07-14 产品决策更新

本清单已按以下三项正式产品决策重新判定：

1. **简体中文不做后端删除，只从前端公开入口中移除。** `/zh-hans/*` 路由、简体数据和兼容 API 暂时保留；公开语言切换器只展示繁体中文和英文。
2. **英文四柱采用新契约。** 显示格式统一为“阴阳 + 五行 + 生肖”，例如 `庚午 -> Yang Metal Horse`，不再以 `Geng-Wu` 拼音模式作为对外显示契约。
3. **英文黄历采用十日视图。** `Ten-Day Almanac` 和 10 条返回记录是正式规格，不再保留九日断言。

对第 1 项的审查意见：**作为降低改造风险的过渡方案是合适的**，但必须把它定义为“前端隐藏、后端兼容”，不能把共享的后端默认语言一起改掉。当前 `DEFAULT_LANG = "zh-hant"` 同时改变了无语言参数 API、领域服务默认文案和旧短链接重定向，已经越过“只改前端”的范围。推荐保留后端兼容默认值 `zh-hans`，由前端切换器独立把“中”按钮指向 `/zh-hant/*`。

按以上决策，22 个失败重新归类为：

| 处理方式 | 失败数 | 根因数 | 结论 |
| --- | ---: | ---: | --- |
| 修改业务代码 | 16 | 3 | 默认语言改动越界 2 项、Prompt/Flask 耦合 13 项、英文黄历中文泄漏 1 项 |
| 修改测试条件 | 6 | 3 | 英文四柱新契约 4 项、十日黄历 1 项、197-200 签旧 fallback 假设 1 项 |
| **合计** | **22** | **6** | 不应通过统一“改代码”或统一“改测试”处理 |

## 0.1 2026-07-14 修复执行结果

本轮已完成所有不需要进一步产品决策的修改：

- pytest：**280 passed / 0 failed**。修复前的 22 个失败已全部处理，并新增笔画持久化、权威源同步和 `LunMing` 显式语言测试。
- Black：**75 个受检文件全部通过**。修复前报告的 39 个文件已格式化。
- Ruff：**0 项问题**。修复前的 124 项已通过安全自动修复、Black 和人工整理清零。
- Click：从 `8.2.1` 升级到 `8.3.3`；`pip check` 通过，`pip-audit` 报告 **No known vulnerabilities found**。
- Node：CI 中的 `huangli.js`、`lunming.js`、`main.js`，以及本次涉及的 `daily_almanac.js`、`birth_chart_en.js`、`lang_switcher.js` 均通过 `node --check`。
- Docker：生产镜像构建成功，容器内部健康检查为 `healthy`，`/readyz` 返回 200。Windows 宿主端口转发在本机返回连接失败，但容器日志确认 Gunicorn 正常监听 `0.0.0.0:8000`，属于本机 Docker Desktop 转发层问题。
- `git diff --check`：通过；仅有 Git 的 LF/CRLF 转换提示，无空白错误。

当前唯一仍会阻塞完整 CI 的已知项是数据库可重建性：

| 数据库 | `hanzi` 数量 |
| --- | ---: |
| 当前 `data/reference/reference.db` | 18,751 |
| 从权威源重新构建 | 18,620 |
| 差异 | 0（131 条已纳入汉典补充权威源） |

用户已经决定 131 个新增汉字全部进入权威源。现已增加可读、可审查的
`data/reference/hanzi_strokes_zdic.csv`，构建脚本会在原始康熙库之后合并该补充源；
重新构建后的逻辑导出已与当前 `reference.db` 完全一致。

## 1. 结论摘要

修复前出现的“22 个 pytest 失败、39 个 Black 文件、124 个 Ruff 问题、CI #12 Failure”不是同一类问题，也不能简单理解成“项目有 185 个功能 Bug”。

| 类别 | 数量/状态 | 结论 |
| --- | ---: | --- |
| 当前工作区 pytest | 280 passed / 0 failed | 已修复并全量验证通过 |
| 当前工作区 Black | 0 个文件 | 75 个受检文件全部符合格式要求 |
| 当前工作区 Ruff | 0 项 | 124 项已全部处理 |
| 远端 `47ba334` Black | 34 个文件 | CI #12 的确定性首个失败点 |
| 远端 `47ba334` Ruff | 110 项 | CI 若通过 Black，下一步仍会失败 |
| 远端 `47ba334` pytest | 1 failed | 197-200 签已补齐，但测试仍期待 fallback，属于过时测试 |
| GitHub CI #12 | Failure | 不是 GitHub 环境偶发误报；干净快照可以稳定复现失败 |

判定标签：

- **[真问题]**：代码行为违背当前已确认契约，或会造成数据泄漏、运行异常。
- **[测试需更新]**：产品契约已经确认，当前实现方向正确，但旧测试仍断言历史行为。
- **[过时测试]**：产品数据或行为已经合法更新，只有旧断言仍期待历史状态。
- **[工程债务]**：不一定影响当前功能，但会阻塞 CI、降低可维护性。
- **[环境误报]**：本机命令环境造成，不是源文件语法错误。

## 2. 修复前工作区的 22 个 pytest 失败

### 2.1 失败总表

| 根因 | 失败数 | 判定 | 是否需要处理 |
| --- | ---: | --- | --- |
| A. 默认语言从 `zh-hans` 改为 `zh-hant` | 2 | [真问题：实施越界/兼容回归] | 恢复后端兼容默认值；繁体入口由前端独立控制 |
| B. 英文四柱从拼音改为描述式英文 | 4 | [测试需更新] | 保留新格式，修改 4 个旧契约测试 |
| C. Prompt 模板加载依赖 Flask `current_app` | 13 | [真问题：架构/测试回归] | 建议修复依赖注入，不建议给 13 个测试机械套 app context |
| D. 英文黄历 `next_favored_date.lunar_date` 泄漏中文 | 1 | [真问题] | 必须修复 |
| E. 九日黄历改成十日黄历 | 1 | [测试需更新] | 保留 10 日实现，修改旧测试并同步英文 API 文档 |
| F. 197-200 签已经补齐但测试仍期待 fallback | 1 | [过时测试] | 删除或改写旧断言 |
| **合计** | **22** |  |  |

### 2.2 A 组：默认语言变化导致的 2 个失败

#### A1. `tests/test_api.py::test_pzbj_explanation`

- 现象：期望 HTTP 200，实际 HTTP 404。
- 直接原因：`zhugeshensuan/i18n_utils.py` 将 `DEFAULT_LANG` 从 `zh-hans` 改成 `zh-hant`。
- 调用链：无 `lang` 的 `/api/pzbj_explanation` -> `g.lang` 使用繁体默认值 -> `database.get_pzbj()` 选择繁体字典 -> 测试传入简体彭祖百忌文本 -> 查找失败 -> `EXPLANATION_NOT_FOUND` 404。
- 这不是路由丢失，路由仍存在；是默认数据字典改变。
- 判定：**[真问题：实施越界/兼容回归]**。产品决策已经明确为“只在前端移除简体入口”，因此不应顺带改变所有无语言参数 API、领域服务和旧短链接的默认语言。这 2 个测试的原有简体兼容断言应保留，不应改成繁体来迁就当前实现。

建议方案：

1. 将“后端兼容默认值”和“中文入口偏好”拆开：
   - `DEFAULT_LANG = "zh-hans"` 继续作为兼容 API 默认值；
   - `lang_switcher.js` 已经直接把“中”按钮指向 `zh-hant`，不需要通过修改后端 `DEFAULT_LANG` 实现；也可增加独立的 `DEFAULT_CHINESE_UI_LANG = "zh-hant"`，但不得被 API/领域服务复用。
2. 所有中文页面发 API 请求时显式传递 `lang=zh-hans` 或 `lang=zh-hant`，不要依赖全局默认值。
3. 旧短链接 `/huangli`、`/suanshi`、`/lunming` 属于公开页面入口，应显式 301 到对应繁体页面；这个前端路由偏好使用独立常量或固定映射，不再复用 API 默认语言常量。
4. 新增两组测试：同一简/繁文本在对应 `lang` 下都能返回解释；语言不匹配时返回明确错误。
5. 新增前端契约测试：切换器不出现 `zh-hans` 按钮，英文页的“中”固定跳到 `/zh-hant/*`，而 `/zh-hans/*` 仍可直接访问。

验收：

```powershell
pytest tests/test_api.py::test_pzbj_explanation -q
```

#### A2. `tests/test_lunming.py::test_full_analysis_consumes_json_stream_into_structured_result`

- 现象：测试期望简体标题 `五行气象`，实际返回繁体标题 `五行氣象`。
- 根因与 A1 相同：测试不在请求上下文中，`get_current_lang()` 落到新的繁体默认值。
- 判定：**[真问题：默认语言改动越界]**，不是 AI 输出错误。当前测试期望简体默认值符合“后端保留简体兼容”的决策，应修代码而不是修改该断言。

建议方案：

- 让 `LunMing` 服务显式接收 `lang`，不要在领域服务内部隐式读取 Flask `g`。
- 测试分别覆盖 `zh-hans` 和 `zh-hant`，避免依赖进程级默认值。

### 2.3 B 组：英文四柱显示格式变化导致的 4 个失败

涉及测试：

1. `tests/test_birth_chart_english.py::TestPillarToEnglish::test_basic`
2. `tests/test_birth_chart_english.py::TestBuildEnglishChartSummary::test_pillars_english_pinyin_format`
3. `tests/test_birth_chart_english.py::TestBuildEnglishChartSummary::test_day_master_english`
4. `tests/test_birth_chart_english.py::TestBirthChartEnApiContract::test_stream_chart_event_english`

旧契约：

- `甲子 -> Jia-Zi`
- `庚午 -> Geng-Wu`
- Day Master 为 `Jia/Yi/Bing/...`

当前未提交代码的新契约：

- `甲子 -> Yang Wood Rat`
- `庚午 -> Yang Metal Horse`
- Day Master 为 `Yang Fire` 等描述式英文。

判定：**[测试需更新]**。产品已经明确采用“阴阳 + 五行 + 生肖”新契约，当前业务实现方向正确；4 个失败都来自旧测试仍期待拼音格式，不应回滚代码。

修改测试条件：

- `test_basic`：将 `甲子` 的期望值改为 `Yang Wood Rat`，并补充阴干/阴支样例，确认 `Yin` 分支也正确。
- `test_pillars_english_pinyin_format`：重命名为描述新契约的测试，例如 `test_pillars_use_yin_yang_element_zodiac_format`；四柱均断言新格式，不再出现 `Jia-Zi`、`Geng-Wu`。
- `test_day_master_english`：日主只包含“阴阳 + 五行”，例如 `Yang Fire`；生肖只属于完整柱，不应错误加入日主字段。
- `test_stream_chart_event_english`：SSE `chart` 事件断言 `Yang Metal Horse` 等新文本，并增加“不含旧拼音连字符格式”的负向断言。
- API 文档和示例响应同步为新契约；旧拼音映射可以作为内部计算辅助保留，但不得继续作为英文页面或公开 API 的显示契约。

建议为每个输出字段增加结构约束，而不是只测单个固定样例：完整四柱应匹配 `^(Yin|Yang) (Wood|Fire|Earth|Metal|Water) (Rat|Ox|...|Pig)$`；日主应匹配前两段。这样能验证契约结构，又不会把测试绑定到旧拼音实现。

### 2.4 C 组：Prompt 模板依赖 Flask 上下文导致的 13 个失败

涉及测试：

`TestBuildEnglishPrompt` 4 项：

1. `test_contains_red_lines`
2. `test_contains_chart_data`
3. `test_requests_json_structure`
4. `test_excludes_responsible_use_from_ai_output`

`TestBirthChartEnglishService` 9 项：

5. `test_analyze_returns_responsible_use`
6. `test_analyze_returns_chart_summary_dict`
7. `test_analyze_returns_reflection_points`
8. `test_analyze_no_fortune_no_gua_type`
9. `test_analyze_no_raw_chart_leak`
10. `test_analyze_stream_event_sequence`
11. `test_analyze_stream_chart_event_english`
12. `test_analyze_stream_responsible_use_event`
13. `test_ai_client_uses_json_object_response_format`

共同异常：

```text
RuntimeError: Working outside of application context.
```

根因：`birth_chart_english._load_prompt_template()` 新增了：

```python
template_path_str = current_app.config.get("BIRTH_CHART_PROMPT_PATH")
```

原先 `build_english_prompt()` 和 `BirthChartEnglish` 可以作为普通 Python 服务独立测试；现在隐式依赖 Flask application context。API 请求中通常有 context，所以不一定立刻造成线上请求失败，但后台任务、CLI、独立脚本和单元测试会失败。

判定：**[真问题：架构/可测试性回归]**。13 个失败是一个根因，不是 13 个独立 Bug。

推荐修复：

1. 在 `create_app()` 中读取 `BIRTH_CHART_PROMPT_PATH`。
2. 构造服务时注入：

```python
BirthChartEnglish(
    lunming,
    default_timezone=...,
    prompt_path=app.config["BIRTH_CHART_PROMPT_PATH"],
)
```

3. `_load_prompt_template(path)` 只接收普通 `Path`，不导入 `flask.current_app`。
4. 测试可使用临时模板路径验证文件加载、缓存、文件缺失 fallback。

不推荐的“假修复”：给 13 个测试全部套 `with app.app_context()`。这样会让测试通过，但保留了领域服务对 Flask 全局状态的耦合。

### 2.5 D 组：英文黄历中文泄漏导致的 1 个失败

测试：

- `tests/test_huangli_english.py::test_daily_api_contract_and_no_chinese_leak`

现象：`/api/en/daily-almanac?date=2026-07-01&scenario=wedding` 返回体仍含 CJK。

根因：新增 `find_next_favored_date()` 后，返回值直接写入：

```python
"lunar_date": record.get("lunar_date", "")
```

主黄历记录会走 `translate_lunar_date()`，但新增的 `next_favored_date.lunar_date` 绕过了翻译层。

判定：**[真问题]**。英文 API 的明确契约是不能泄漏中文。

推荐修复（二选一）：

1. 最小改动：`next_favored_date` 只返回 ISO 日期和 `days_ahead`，删除非必要的农历字段。
2. 如果 UI 必须显示农历日期，则在 `HuangLiEnglish` 内统一翻译后再返回，且将缺失翻译纳入 `_missing` 审计。

验收：

```powershell
pytest tests/test_huangli_english.py::test_daily_api_contract_and_no_chinese_leak -q
pytest tests/test_huangli_english.py::test_2026_full_year_no_chinese_leak -q
```

### 2.6 E 组：九日改十日导致的 1 个失败

测试：

- `tests/test_huangli_english.py::test_week_api_contract`

现象：期望 9 条，实际 10 条。

代码变化：英文 API 显式调用 `get_week_huangli(days=10)`，前端标题也从 `Nine-Day Almanac` 改为 `Ten-Day Almanac`。

判定：**[测试需更新]**。英文页面十日黄历已经是正式规格；当前返回 10 条和 `Ten-Day Almanac` 标题是正确实现，失败来自测试仍断言 9 条。

修改测试条件：

- 将 `test_week_api_contract` 的数量断言从 9 改为 10。
- 继续断言 10 个日期按升序排列、日期不重复、首尾范围符合接口定义，而不只检查 `len(data)`。
- 增加英文前端契约断言：标题为 `Ten-Day Almanac`，不再出现 `Nine-Day Almanac`。
- 在英文 API 文档中说明：历史端点名 `week-almanac` 为兼容名称，固定返回 10 日。端点可暂不重命名，避免制造新的 URL 兼容问题。
- 中文页面现有“九天黄历”文案是否调整不在本次英文规格决策范围内，不能据此自动修改中文契约。

### 2.7 F 组：197-200 签 fallback 测试过时导致的 1 个失败

测试：

- `tests/test_oracle_english.py::TestLoadEnglishSigns::test_known_empty_general_gets_fallback`

现象：测试仍要求 197-200 签的 `general` 等于 `FALLBACK_TEXT`，但这些字段已在提交 `57af639` 中补齐。

判定：**[过时测试]**，产品数据补齐是正确进展。

推荐修复：

- 删除“已知为空”的历史假设。
- 改成通用质量契约：384 条全部字段非空、不含 CJK、不触发 fallback。
- 可增加单独构造的空记录单元测试，继续验证 fallback 机制本身。

## 3. Black：修复前 39 个文件是什么问题

### 3.1 Black 的性质

Black 报告的是代码格式不符合统一格式，不代表这些文件都有功能错误。主要变化通常是：

- 长参数或长表达式换行；
- 字典、列表和函数调用的缩进；
- import/空行布局；
- 尾逗号带来的稳定换行。

因此 Black 问题属于 **[工程债务/CI 阻塞]**，不是 39 个业务 Bug。但 CI 明确执行 `black --check`，所以不处理就无法得到绿色构建。

### 3.2 当前工作区 39 个文件完整清单

生产包与蓝图（13）：

1. `zhugeshensuan/ai_usage.py`
2. `zhugeshensuan/app.py`
3. `zhugeshensuan/birth_chart_english.py`
4. `zhugeshensuan/config.py`
5. `zhugeshensuan/database.py`
6. `zhugeshensuan/huangli_english.py`
7. `zhugeshensuan/huangli_i18n.py`
8. `zhugeshensuan/i18n_utils.py`
9. `zhugeshensuan/blueprints/birth_chart_en_api.py`
10. `zhugeshensuan/blueprints/huangli_en_api.py`
11. `zhugeshensuan/blueprints/oracle_en_api.py`
12. `zhugeshensuan/blueprints/pages.py`
13. `zhugeshensuan/blueprints/pages_en.py`

测试（3）：

14. `tests/test_frontend_contract.py`
15. `tests/test_huangli_i18n.py`
16. `tests/test_oracle_english.py`

维护脚本（23）：

17. `scripts/adjudicate_single_sign.py`
18. `scripts/apply_review_fixes_signs_13_32.py`
19. `scripts/backfill_hanzi_strokes.py`
20. `scripts/backfill_reinterpreted_to_db.py`
21. `scripts/build_gemini_review_prompt.py`
22. `scripts/build_hant_db.py`
23. `scripts/build_huangli_terms_en.py`
24. `scripts/build_reference_db.py`
25. `scripts/check_variants.py`
26. `scripts/compare_oracle_signs.py`
27. `scripts/extract_lunar_en_candidates.py`
28. `scripts/gemini_prompt_builder.py`
29. `scripts/generate_authoritative_signs.py`
30. `scripts/reinterpret_oracle_signs.py`
31. `scripts/reprocess_single_sign.py`
32. `scripts/retranslate_signs_by_numbers.py`
33. `scripts/sort_reinterpreted_output.py`
34. `scripts/sync_gua_hant_sign_text.py`
35. `scripts/sync_review_status.py`
36. `scripts/sync_stroke_to_hanzi.py`
37. `scripts/translate_oracle_signs.py`
38. `scripts/update_xlsx_signs.py`
39. `scripts/verify_db.py`

其中远端干净提交 `47ba334` 是 34 个；当前工作区新增的 5 个是：

- `scripts/backfill_hanzi_strokes.py`
- `scripts/sync_stroke_to_hanzi.py`
- `zhugeshensuan/blueprints/huangli_en_api.py`
- `zhugeshensuan/birth_chart_english.py`
- `zhugeshensuan/huangli_english.py`

推荐处理方式：

```powershell
python -m black app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
git diff --check
python -m pytest
```

注意：先修功能和契约，再统一跑 Black，避免格式化噪声干扰功能 diff 审查。

## 4. Ruff：修复前 124 项是什么问题

### 4.1 按规则统计和真假判断

| 规则 | 数量 | 含义 | 风险判断 | 推荐动作 |
| --- | ---: | --- | --- | --- |
| `E501` | 70 | 行长度超过 100 | 基本是格式问题 | Black 后手工处理 Black 不覆盖的长字符串/注释 |
| `F541` | 24 | f-string 没有占位符 | 无功能影响，但表达多余 | 去掉字符串前的 `f` |
| `I001` | 13 | import 未排序 | 无功能影响 | `ruff check --fix` 或手工排序 |
| `F401` | 5 | import 后未使用 | 多数无功能影响，可能暗示残留代码 | 确认无副作用后删除 |
| `E402` | 3 | 模块 import 不在文件顶部 | 脚本中常因 `sys.path` 注入产生；不是自动 Bug | 重构脚本入口或加有说明的局部豁免 |
| `UP045` | 3 | `Optional[X]` 可写成 `X | None` | 纯现代化建议 | 自动修复即可 |
| `B904` | 2 | `except` 内重新抛错未使用 `from` | 错误链会丢失，影响诊断 | 改为 `raise ... from exc` |
| `UP035` | 2 | 类型从 `typing` 导入方式过时 | 纯现代化建议 | 改从 `collections.abc` 导入 |
| `B007` | 1 | 循环变量 `fname` 未使用 | 当前逻辑仍使用 start/end，偏代码味道 | 改名 `_fname`，同时确认未漏用文件名 |
| `B905` | 1 | `zip()` 未显式给 `strict=` | 当前两个列表源自同一数据，实际长度一致，风险低 | 写 `strict=True` 锁定假设 |
| **合计** | **124** |  |  |  |

整体判断：

- 107 项（E501/F541/I001）是明显的格式/风格债务。
- 8 项（UP045/UP035/F401 中的一部分）是现代化或清理建议。
- 9 项需要人工看一下上下文，但当前没有证据表明它们已造成线上功能错误。
- 没有发现 `F821` 未定义变量、语法错误或明显的危险异常吞噬类规则。
- 所以“Ruff 124”不是“124 个真实 Bug”，但它是确定的 CI 门禁失败。

### 4.2 生产代码和测试中的 22 项

| 文件 | 位置/规则 |
| --- | --- |
| `zhugeshensuan/app.py` | `1 I001` |
| `zhugeshensuan/blueprints/__init__.py` | `1 I001` |
| `zhugeshensuan/blueprints/pages_en.py` | `21 F401` |
| `zhugeshensuan/database.py` | `311,318 E501` |
| `zhugeshensuan/error_codes.py` | `124,129,130,131,132,133 E501`; `210,211 UP045` |
| `zhugeshensuan/huangli_i18n.py` | `310 E501` |
| `zhugeshensuan/oracle_algorithm.py` | `7 E501`; `24 UP035` |
| `zhugeshensuan/oracle_english.py` | `4 E501`; `24 UP035`; `120 UP045` |
| `tests/test_frontend_contract.py` | `152 E501` |
| `tests/test_oracle_english.py` | `12 I001`; `14 F401` |

### 4.3 维护脚本中的 102 项完整位置清单

| 文件 | 位置/规则 |
| --- | --- |
| `scripts/adjudicate_single_sign.py` | `36 I001`; `346,440,849,853,925,940,941 E501`; `387,388,799 F541` |
| `scripts/apply_review_fixes_signs_13_32.py` | `31,56,79,105 E501` |
| `scripts/backfill_hanzi_strokes.py` | `21,183,184,185,186,255 E501`; `34 E402`; `171,270,275 F541` |
| `scripts/backfill_reinterpreted_to_db.py` | `13,129,130 E501` |
| `scripts/build_gemini_review_prompt.py` | `24,32 I001`; `56,75,76,77,79 F541` |
| `scripts/build_huangli_terms_en.py` | `104,179,186,234,243 E501`; `276,279 F541` |
| `scripts/check_variants.py` | `10 I001`; `57 E501` |
| `scripts/compare_oracle_signs.py` | `19 I001`; `175,192,202,206 F541` |
| `scripts/extract_lunar_en_candidates.py` | `140,144,150,191,193,203,228,246,248 E501`; `203,204 F541` |
| `scripts/generate_authoritative_signs.py` | `221 F541` |
| `scripts/reinterpret_oracle_signs.py` | `27 I001`; `33 F401`; `259 B904` |
| `scripts/reprocess_single_sign.py` | `56 F401`; `63,320 I001`; `320,325 E402`; `330,362,377,378,454,455,458 E501` |
| `scripts/retranslate_signs_by_numbers.py` | `23 E501`; `41 I001` |
| `scripts/sort_reinterpreted_output.py` | `32 B905`; `52,67 E501` |
| `scripts/sync_gua_hant_sign_text.py` | `69 F541` |
| `scripts/sync_review_status.py` | `126,205,279,281,283,296,298,321,322,324,403,410 E501`; `151 B007`; `212 F541` |
| `scripts/sync_stroke_to_hanzi.py` | `52 E501`; `65 F541` |
| `scripts/translate_oracle_signs.py` | `26 I001`; `30 F401`; `202 B904` |
| `scripts/update_xlsx_signs.py` | `65 F541` |

建议修复顺序：

1. 先人工处理 `B904/B007/B905/E402/F401`，避免自动修复掩盖逻辑意图。
2. 执行 `ruff check --fix` 处理 I001、F541、UP035、UP045 等安全自动修复项。
3. 执行 Black。
4. 最后处理残余 E501，尤其是长字符串、SQL 和文档字符串。
5. 重新跑 pytest，避免格式整理时误改字符串内容。

## 5. GitHub CI #12 到底失败在哪里

远端页面：<https://github.com/weixun0058/cezi/actions/runs/29205691754>

公开页面只显示 `Status Failure` 和 job `Process completed with exit code 1`，未登录状态不能读取完整逐步日志。为避免猜测，本次创建了干净的 `47ba334` 本地快照并按 CI 顺序复现。

CI 关键顺序：

1. 安装依赖；
2. `black --check ...`；
3. `ruff check ...`；
4. `pytest ...`；
5. `pip-audit`；
6. 数据库可重建检查；
7. Node 语法检查；
8. Docker 构建与健康检查。

`47ba334` 干净快照复现结果：

| 步骤 | 结果 | 说明 |
| --- | --- | --- |
| Black | **失败** | 34 个文件需要格式化；这是流水线中首个可确定复现的失败点 |
| Ruff（单独绕过 Black 后执行） | **失败** | 110 项：61 E501、20 F541、13 I001、5 F401、3 UP045、2 E402、2 B904、2 UP035、1 B007、1 B905 |
| pytest（单独执行） | **失败 1 项** | 197-200 签 fallback 旧测试 |

结论：

- CI #12 不是 GitHub 偶发故障。
- 即使 Black 修完，Ruff 和 pytest 仍会继续让 CI 失败。
- 当前工作区已经达到 Black 0 / Ruff 0 / pytest 0 failed；远端 `47ba334` 仍是 34/110/1，因为本轮修复尚未提交推送。
- 修 CI 时必须针对“准备提交的最终工作区”一次性跑完整门禁，不能只修远端的 34 个 Black 文件。

## 6. 其他应修复或需要决策的问题

### G. `reference.db` 不可从权威源完整重建（已修复）

- 当前工作区数据库 `hanzi`：18,751 条。
- 原始康熙库：18,620 条。
- 汉典补充权威源：131 条。
- 合并权威源重建：18,751 条。
- 判定：**[真问题：数据可重复性，已修复]**。

根因：运行时查询结果已经写入 `runtime.db`，并在本地可写时回写派生的
`reference.db`，但原同步脚本没有更新构建所依赖的权威源，导致派生库多出 131 条。
生产容器只读时，`runtime.db` 位于可写卷中，因此新增字仍会持久保存。

已确认并实施的规则：

- 查询顺序保持不变：先查本地 `reference.db`，再查 `runtime.db`，缺字才查询汉典。
- 汉典成功返回的新字必须写入 `runtime.db`；本地可写时继续回写 `reference.db`。
- `scripts/sync_stroke_to_hanzi.py` 汇总新增记录，写入
  `data/reference/hanzi_strokes_zdic.csv`，解决重新构建丢字问题。
- 权威补充源只新增缺字；若已有权威值发生冲突，保留权威值并报告人工核对，避免缓存覆盖权威数据。
- 构建脚本同时改用运行时相同的简体、繁体签文 JSON 权威源，消除了派生库中
  2 条简体及 156 条繁体签文记录的历史漂移。
- CI 继续保留 logical dump 可重建比较。

### H. 工作区存在临时文件和大体积 tar（已修复）

原未跟踪项包括 `_tmp_test_api.py`、`_tmp_test_db.py`、`_verify_bazi.py`
以及约 122.7 MB 的 `zhugeshensuan-local.tar`；这些临时产物现已删除。

判定：**[工程卫生问题]**。`.dockerignore` 未排除 `*.tar` 和这些临时脚本，而 Dockerfile 使用 `COPY . .`，本地构建可能把它们打进镜像。

建议：

- 有价值的维护脚本已正式保留并补测试；三份纯临时验证脚本已删除。
- `zhugeshensuan-local.tar` 已从工作区删除。
- `.dockerignore` 已增加 `*.tar`、`_tmp_*.py`、`_verify_*.py`、`outputs` 规则。

### I. Click 依赖漏洞（已修复）

- 修复前固定 `click==8.2.1`，`pip-audit` 报 `PYSEC-2026-2132`。
- 当前已升级到 `click==8.3.3`。
- `pip check` 通过；强制 UTF-8 环境后 `pip-audit` 报告 `No known vulnerabilities found`。
- 判定：**[已修复]**。

验证：280 项 pytest 全绿，生产 Docker 镜像成功安装依赖并完成内部健康检查。

### J. 英文签文“翻译审校完成”不等于“产品边界完成”

当前数据扫描按“匹配行”统计：

- `hexagram`：1,334 行；
- `investment`：320 行；
- `doctor`：18 行；
- `blood pressure`：29 行。

其中包含具体投资方向、杠杆/借贷建议、血压/心悸/肝肾等健康指导，以及嵌入正文的宫位/变卦/吉凶语言。

判定：**[真问题：内容边界]**。384/384 代表翻译审校流程完成，不代表已经满足产品对医疗、财务和原典边界的要求。

建议：另建“产品安全审校”状态；直接修改内容数据，不在前端做关键词隐藏。建立自动扫描和人工复核双门禁。

### K. SEO/公开运营/商业化尚未完成

仍缺少或未定稿：

- sitemap、robots、SEO 模块；
- 正式文章系统和首批内容；
- 真实联系邮箱（当前仍是 `.example`）；
- Search Console/域名/上线验收；
- P6-P8 商业化配置、平台核验和运营复盘。

判定：**[未完成工作，不是代码回归]**。不能把它们计入 pytest Bug，但会限制“生产上线完成度”。

### L. Node `CSPRNG` 崩溃属于本机环境问题

在缺少 `SystemRoot/WINDIR` 的 Codex 命令环境中，Node 曾报 `Assertion failed: ncrypto::CSPRNG`。补齐环境变量后，对本次修改涉及的 `main.js`、`daily_almanac.js`、`birth_chart_en.js`、`lang_switcher.js` 单文件 `node --check` 均通过。

判定：**[环境误报]**，不是这些 JS 文件的语法错误。README/本机验证脚本可加入 Windows 环境前置检查，但不应修改 JS 来“修复”它。

## 7. 最终修复清单（建议执行顺序）

### P0：恢复可提交、可验证状态

- [x] 将后端/API/领域服务兼容默认值恢复为 `zh-hans`；不要为了前端繁体入口修改共享 `DEFAULT_LANG`。
- [x] 保持语言切换器只展示繁体中文和英文，并固定把“中”链接指向 `/zh-hant/*`。
- [x] 保留 `/zh-hans/*` 路由、简体数据和显式 `lang=zh-hans` API 能力；新增“隐藏但可访问”的兼容测试。
- [x] 将旧短链接 `/huangli`、`/suanshi`、`/lunming` 显式 301 到繁体对应页，并用路由测试锁定，不再隐式复用 API 默认值。
- [x] 保留英文四柱“阴阳 + 五行 + 生肖”实现，更新 4 个拼音旧契约测试；公开输出不再断言 `Jia-Zi/Geng-Wu`。
- [x] 保留英文十日黄历实现，将 `test_week_api_contract` 改为 10 条并同步英文契约测试。
- [x] 将 Birth Chart prompt 路径通过构造函数注入，移除领域服务对 `current_app` 的隐式依赖。
- [x] 修复 `next_favored_date.lunar_date` 英文 API 中文泄漏。
- [x] 删除/改写 197-200 签 fallback 过时测试。
- [x] 补齐简体兼容、繁体公开入口、旧短链接和英文输出契约测试。
- [x] `LunMing` 领域服务显式接收 `lang`；仅 Web 蓝图读取 Flask 请求语言，业务层不再隐式读取 `g`。
- [x] 全量 pytest 已达到 280 passed / 0 failed。

### P0：恢复质量门禁

- [x] 人工审查 Ruff 的 B904/B007/B905/E402/F401。
- [x] 运行安全的 `ruff check --fix`。
- [x] 运行 Black 格式化 39 个文件。
- [x] 处理剩余 E501。
- [x] 运行 `git diff --check`。
- [x] 推送前已按 CI 顺序完整执行：Black、Ruff、pytest、pip-audit、数据库 logical dump、Node、Docker 构建与健康检查全部通过。
- [ ] 确认 GitHub CI 变绿。

### P1：数据和构建一致性

- [x] 保留现有请求路径的笔画入库行为：先写可写的 `runtime.db`，本地环境同时回写 `reference.db`。
- [x] 将 131 个新增汉字纳入 `hanzi_strokes_zdic.csv` 权威补充源。
- [x] 从权威源重建数据库；18,751 条汉字完整保留，CI 同款 logical dump 比较通过。
- [x] 清理临时脚本和 `zhugeshensuan-local.tar`。
- [x] 加强 `.dockerignore`。
- [x] 升级 Click 到 8.3.3，并通过 `pip check` 与 `pip-audit`。

### P1：产品内容边界

- [ ] 建立独立的英文内容安全审校清单。
- [ ] 清理正文中的具体医疗/财务建议。
- [ ] 清理与产品考据决策冲突的宫位、变卦和吉凶层累内容。
- [ ] 建立内容扫描测试并保留人工复核记录。

### P2：公开上线准备

- [ ] 实现 sitemap、robots、canonical 和 SEO 模块。
- [ ] 替换 `.example` 联系地址。
- [ ] 发布首批人工审校文章。
- [ ] 完成域名、Search Console、监控、备份恢复和上线验收。
- [ ] 在流量和使用数据成立后再解冻支付/商业化。

## 8. 建议验收命令

```powershell
# Python 功能与契约
python -m pytest -W error::ResourceWarning

# 格式与静态检查
python -m black --check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
python -m ruff check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
git diff --check

# 依赖安全
python -m pip_audit -r requirements.txt --no-deps --progress-spinner off

# 关键 JavaScript
node --check frontend/static/js/main.js
node --check frontend/static/js/daily_almanac.js
node --check frontend/static/js/birth_chart_en.js
node --check frontend/static/js/lang/lang_switcher.js

# 数据库可重建性：按 CI 的 logical dump 比较执行
python scripts/build_reference_db.py --output <临时目录>/reference.db

# Docker
docker build -f deploy/Dockerfile --build-arg APP_VERSION=audit -t zhugeshensuan:audit .
```

完成标准：不是“某一项修了”，而是当前最终工作区在同一次验证中通过 pytest、Black、Ruff、pip-audit、数据库可重建、Node 检查、Docker 构建和健康探针。
