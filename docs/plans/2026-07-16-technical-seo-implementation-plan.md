# Technical SEO Foundations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 `https://getwiseoracle.com` 建立可审计、可测试、可回滚的技术 SEO 基础，覆盖固定生产域名、canonical、hreflang、sitemap、robots、页面元数据、Open Graph 和结构化数据。

**Architecture:** 以应用配置中的唯一 `SITE_BASE_URL` 作为所有公开绝对 URL 的可信源，不从请求 `Host` 推导搜索引擎标签。新增集中式 SEO 元数据与 URL 构建模块，由英文和中文页面共用；sitemap 与 robots 由 Flask 端点生成，并以测试锁定公开路由、索引边界和输出格式。

**Tech Stack:** Python 3.13、Flask、Jinja2、pytest、BeautifulSoup、XML、HTML、JSON-LD、Open Graph、Docker/Gunicorn。

---

## 1. 文档用途与评审方式

本文档同时服务三类读者：

1. **项目所有者：** 知道 SEO-001/002/003 实际会改变什么、如何证明完成、哪些事情暂时不会做。
2. **实施工程师：** 可以按任务顺序直接施工，不需要从旧计划猜测约束。
3. **外部评审人员：** 可以审查 URL 策略、索引范围、hreflang 对应关系、结构化数据类型、测试和上线验收是否合理。

实施者不得仅以“页面源码中出现了标签”作为完成证据。每项必须同时具备：自动测试、渲染结果检查、全量质量门禁；涉及真实域名的部分还要有生产环境 HTTP 证据。

### 1.1 2026-07-16 外部评审意见核实记录

| 评审意见 | 仓库核实结果 | 处置 |
| --- | --- | --- |
| `.env.example` 不存在 | 不成立。根目录 `.env.example` 已存在、已被 Git 跟踪，`.gitignore` 还用 `!.env.example` 明确保留它 | 继续写“Modify”，不创建重复文件；补充其用途说明 |
| `deploy/gunicorn.conf.py` 不存在 | 不成立。该文件已存在、已被 Git 跟踪；`deploy/Dockerfile` 的 `CMD` 明确以 `gunicorn --config deploy/gunicorn.conf.py app:app` 启动 | 保留 Black/Ruff 路径；补充 Docker 与 Gunicorn 的关系 |
| JS 只检查 4 个存在盲区 | 成立。`frontend/static/js/` 当前共有 14 个 `.js` 文件，且均可能被现有页面直接或间接使用 | 改为递归检查 14/14；实施时数量如变化，以目录实际枚举为准 |
| 旧生产配置测试可能受新校验干扰 | “必然匹配失败”不成立，因为当前校验器汇总错误后统一抛出；但测试应隔离目标 | 接受改进：旧测试显式传入合法 `SITE_BASE_URL`，另建独立非法 URL 测试 |
| 占位文章 200 测试与未知 slug 404 冲突 | 成立 | 采用选项 B：从 200 集合移出占位 slug，新增明确的未知/未发布 slug 404 测试，不减少覆盖 |
| JSON-LD 可能受 CSP 影响 | 值得实测，但不能据此加入 `'unsafe-inline'`。JSON-LD 是非可执行数据块，Google 推荐嵌入页面 | 增加响应头、浏览器控制台和搜索工具验证；如出现兼容问题优先 nonce/hash，不削弱整站 CSP |
| 应先盘点现有 metadata | 成立 | 在 Task 3 前加入逐模板迁移基线 |
| `og:locale` 映射不够明确 | 成立 | 固化 `en → en_US`、`zh-Hans → zh_CN`、`zh-Hant → zh_TW` 单一映射 |
| 蓝图注册步骤不够明确 | 成立 | 明确导入 `seo_bp` 并加入 `ALL_BLUEPRINTS` |
| 路径注入测试不够明确 | 成立 | 外部 scheme、network-path、query、fragment 四类全部显式测试并拒绝 |

`.env` 与 `.env.example` 的职责不同：真实 `.env` 供当前环境运行，包含真实密钥并被 Git 忽略；`.env.example` 是无密钥的配置契约，告诉新服务器、CI、维护人员和审计人员“有哪些变量必须配置”。它不直接提高 SEO，也不是应用运行的第二份配置，但能防止漏配 `SITE_BASE_URL` 和误把真实 `.env` 交给第三方。

Docker 与 Gunicorn 也不是替代关系：Docker 负责封装、隔离和启动容器，Gunicorn 是容器内部实际运行 Flask 应用的生产 WSGI 服务器。当前 Dockerfile 已明确依赖 `deploy/gunicorn.conf.py`，所以该文件和质量检查都应保留。

## 2. 已确认的业主决策

| 项目 | 已确认值 | 在本方案中的作用 |
| --- | --- | --- |
| 正式站点根 URL | `https://getwiseoracle.com` | canonical、hreflang、Open Graph、JSON-LD、sitemap、robots 的唯一 origin |
| 主机名策略 | 以无 `www` 域名为主 | `www.getwiseoracle.com` 的重定向在 OPS-001 上线验收时核对 |
| 对外联系与隐私邮箱 | `5siwei@gmail.com` | 解锁 TRUST-001；不属于 SEO 代码，但会在信任页同步 |
| 英文文章存储 | 仓库内 Markdown + 受控元数据 | 解锁 ART-001；文章详情的动态 SEO 在 ART-002 接入 |

配置中使用不带末尾斜杠的 `https://getwiseoracle.com`。首页 URL 仍输出为 `https://getwiseoracle.com/`。

## 3. 当前事实与本批次修复点

### 3.1 当前事实

- 英文公开首页为 `/`；核心英文工具页为 `/ask-oracle`、`/daily-almanac`、`/birth-chart-reading`。
- 中文页面有 `/zh-hans/*` 和 `/zh-hant/*` 两套路由，公开中文默认入口为繁体 `zh-hant`。
- 旧入口 `/huangli`、`/suanshi`、`/lunming` 已 301 到繁体页面。
- 英文基础模板当前通过 `request.base_url` 生成 canonical，会受到请求 host 的影响。
- 四个中文模板目前没有统一 canonical、hreflang、description、Open Graph 或 JSON-LD。
- `/articles/<slug>` 仍是占位路由，任意 slug 都可能返回占位内容；正式文章系统尚未实施。
- 项目当前没有 `/sitemap.xml` 和 `/robots.txt`。
- 根目录已有受 Git 跟踪的 `.env.example`；本批次是在其中增加变量，不是新建第二份真实配置。
- 当前生产镜像由 `deploy/Dockerfile` 构建，并在容器内使用 `deploy/gunicorn.conf.py` 启动 Gunicorn。
- `docker compose --env-file .env` 只为 Compose 提供变量替换，不会自动把所有变量注入容器；`SITE_BASE_URL` 还必须显式加入 `deploy/compose.prod.yml` 的 `environment`。

### 3.2 本批次必须修复

- 生产绝对 URL 不得读取任意请求 `Host`。
- 每个可索引页面只能有一个自指 canonical。
- 只有内容真正对应的页面才能互设 hreflang。
- 未发布文章、任意占位 slug、API、健康检查、旧重定向入口不得进入 sitemap。
- title 和 description 必须按页面唯一，不得以“准确预测”“保证结果”等措辞吸引点击。
- JSON-LD 必须与用户可见内容一致，不虚构评分、作者、组织资质或服务结果。

### 3.3 本批次不做

- 不保证搜索排名、流量或收录时间。
- 不进行关键词堆砌、批量生成薄内容或购买外链。
- 不在 robots 中放置秘密路径，也不把 robots 当访问控制。
- 不为尚未发布的文章生成假 `Article` 结构化数据。
- 不在本批次接入 Google Search Console；该工作属于 OPS-004。
- 不自动创建 `www` DNS 或修改生产反向代理；该工作属于 OPS-001。

## 4. 目标架构

### 4.1 单一 URL 信任链

```text
.env / deployment environment
        |
        v
SITE_BASE_URL=https://getwiseoracle.com
        |
        v
config validation -> SEO URL builder -> page metadata / sitemap / robots / JSON-LD
```

`SITE_BASE_URL` 必须满足：

- 是绝对 `https` URL；测试和开发环境可显式使用 `http://localhost`。
- 不含用户名、密码、query、fragment。
- 生产环境不允许为空，不允许 `.example`，不允许 localhost/IP。
- 规范化后不带末尾 `/`。
- 请求头 `Host`、`X-Forwarded-Host` 只用于正常请求路由，不参与 SEO 绝对 URL 生成。

### 4.2 URL 与语言对应矩阵

只有下列四组页面是语义等价的语言版本：

| 页面组 | English | 简体中文 | 繁體中文 | `x-default` |
| --- | --- | --- | --- | --- |
| 首页 | `/` | `/zh-hans` | `/zh-hant` | `/` |
| 求签 | `/ask-oracle` | `/zh-hans/divination` | `/zh-hant/divination` | `/ask-oracle` |
| 黄历 | `/daily-almanac` | `/zh-hans/almanac` | `/zh-hant/almanac` | `/daily-almanac` |
| 八字 | `/birth-chart-reading` | `/zh-hans/bazi` | `/zh-hant/bazi` | `/birth-chart-reading` |

生成的 hreflang 代码必须使用标准语言值 `en`、`zh-Hans`、`zh-Hant`、`x-default`，并且每组互相返回完整对应关系。Privacy、Terms、Disclaimer、About、Contact 和暂未发布的 Articles 没有等价中文内容，因此不得伪造中文 hreflang。

### 4.3 canonical 规则

- 所有 canonical 均为绝对 URL，scheme 和 host 固定为 `https://getwiseoracle.com`。
- canonical 不包含 query、fragment 或追踪参数。
- `/` 保留结尾 `/`；其他现有路由使用无结尾 `/` 的形式。
- 英文、简体和繁体是不同语言内容，分别使用自指 canonical，不互相 canonical 到另一语言。
- 旧路由只保留 301，不输出独立 canonical，也不进 sitemap。
- 404、API 和健康检查响应不输出 canonical。

### 4.4 索引策略

当前 sitemap 只主动提交英文主站与繁体中文公开工具页，遵守主台账既定范围。简体页面保留自指 canonical 和 hreflang，但暂不写入 sitemap；这表示“不主动提交”，不是 `noindex`。外部评审若建议正式推广简体站，应另开计划修订，不能在实施时悄悄扩大范围。

第一版 sitemap 精确包含：

```text
/
/ask-oracle
/daily-almanac
/birth-chart-reading
/about
/zh-hant
/zh-hant/divination
/zh-hant/almanac
/zh-hant/bazi
```

暂不包含：

- `/articles`：仍是 Coming soon 薄页面；发布首篇文章后由 ART-002 解除 `noindex` 并加入 sitemap。
- `/articles/<slug>`：ART-002 前应对未知或未发布 slug 返回 404，不得形成无限占位 URL。
- `/privacy`、`/terms`、`/disclaimer`、`/contact`：继续允许正常访问和自指 canonical，但不作为搜索落地页主动提交。
- `/zh-hans/*`：按当前“英文 + 繁体公开收录”契约不主动提交。
- `/api/*`、`/healthz`、`/readyz`、旧 301 路由、静态资源、调试或管理端点。

不得编造 `lastmod`。只有能从受控内容元数据或真实部署记录取得变更日期时才输出。

### 4.5 页面元数据与结构化数据

建立集中式页面注册表，每个公开页面最少定义：

```python
SEOPage(
    title="...",
    description="...",
    canonical_path="...",
    indexable=True,
    og_type="website",
    alternates={...},
    schema_types=("WebPage",),
)
```

所有页面输出：

- 唯一 `<title>`。
- 唯一 `<meta name="description">`。
- 唯一绝对 canonical。
- 适用时输出完整 hreflang 组。
- `meta name="robots"`，默认 `index,follow`；文章占位页为 `noindex,follow`。
- Open Graph：`og:title`、`og:description`、`og:type`、`og:url`、`og:site_name`、`og:locale`。
- 有真实分享图后输出 `og:image` 及尺寸/alt；没有合格的 1200×630 资产前不使用错误尺寸图片凑数。

结构化数据采用保守类型：

- 首页：`WebSite` + `WebPage`。
- 工具页与信任页：`WebPage`；有层级关系时可加 `BreadcrumbList`。
- 文章详情：仅 ART-002 读取到已发布 Markdown 元数据后输出 `Article`。
- 暂不使用 `Organization`、`MedicalWebPage`、评分、评论、价格或 `FAQPage`，除非页面具备真实、可见且符合搜索引擎要求的数据。

JSON-LD 必须通过 Jinja `tojson` 序列化，不拼接未经转义的字符串。

## 5. 计划文件范围

### 新建

- `zhugeshensuan/seo.py`
- `zhugeshensuan/blueprints/seo.py`
- `frontend/templates/sitemap.xml`
- `frontend/templates/robots.txt`
- `frontend/templates/partials/seo_head.html`
- `tests/test_seo_urls.py`
- `tests/test_sitemap.py`
- `tests/test_robots.py`
- `tests/test_seo_metadata.py`
- `docs/reviews/2026-07-16-seo-001-003-acceptance.md`（实施完成时建立）

### 修改

- `zhugeshensuan/config.py`
- `zhugeshensuan/app.py`
- `zhugeshensuan/blueprints/__init__.py`
- `zhugeshensuan/blueprints/pages.py`
- `zhugeshensuan/blueprints/pages_en.py`
- `frontend/templates/en/base.html`
- `frontend/templates/index.html`
- `frontend/templates/huangli.html`
- `frontend/templates/suanshi.html`
- `frontend/templates/lunming.html`
- `frontend/templates/en/articles.html`
- `.env.example`
- `deploy/compose.prod.yml`
- `.github/workflows/ci.yml`
- `docs/部署指南.md`
- `docs/plans/2026-07-15-project-completion-master-ledger.md`
- 必要时更新 `tests/test_english_frontend_contract.py`，但不得删除现有断言来迁就新实现。

### 条件性文件

- `frontend/static/images/wise-oracle-og-1200x630.png`：只有获得真实品牌分享图并完成人工预览后才加入。
- 文章 Markdown、文章加载器和动态 `Article` schema 属于 ART-001/002，不在本 SEO 批次提前实现。

## 6. 分步实施方案

### Task 1: 锁定配置和 URL 安全边界（SEO-001）

**Files:**
- Modify: `zhugeshensuan/config.py`
- Modify: `.env.example`
- Modify: `deploy/compose.prod.yml`
- Modify: `.github/workflows/ci.yml`
- Create: `tests/test_seo_urls.py`
- Modify: `tests/test_config.py`

**Step 1: 写失败测试**

测试至少覆盖：

```python
def test_canonical_uses_configured_origin_not_request_host(client):
    response = client.get("/ask-oracle", headers={"Host": "attacker.example"})
    assert 'href="https://getwiseoracle.com/ask-oracle"' in response.get_data(as_text=True)
    assert "attacker.example" not in response.get_data(as_text=True)


def test_production_requires_https_site_base_url():
    # production + http/empty/.example/localhost 均应触发 RuntimeError
    ...


@pytest.mark.parametrize(
    "path",
    ["https://evil.example/x", "//evil.example/x", "/x?a=1", "/x#fragment"],
)
def test_absolute_public_url_rejects_untrusted_path_forms(path):
    with pytest.raises(ValueError):
        absolute_public_url("https://getwiseoracle.com", path)
```

同时覆盖根路径斜杠规范化以及非法配置错误信息。外部 scheme、`//host`、query 和 fragment 一律拒绝，不静默剥离；调用者只能传入注册表中受控的纯路径。

现有 `tests/test_config.py` 两个生产配置测试分别只验证 `SECRET_KEY` 和 `AI_GLOBAL_DAILY_LIMIT`。给这两个配置 dict 都补入：

```python
"SITE_BASE_URL": "https://getwiseoracle.com",
```

这样新增 URL 校验不会污染旧测试的目标；另用新测试专门验证 URL 配置错误。

**Step 2: 运行测试确认失败**

Run:

```powershell
python -m pytest tests/test_config.py tests/test_seo_urls.py -q
```

Expected: FAIL，原因应是 `SITE_BASE_URL` 尚未实现，且当前 canonical 仍来自请求 host。

**Step 3: 实现最小配置与 URL 构建器**

在 `Config` 增加：

```python
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://localhost:8000").rstrip("/")
```

该开发默认值与当前 `APP_PORT=8000` 的默认值一致；若开发者覆盖端口，也应同步覆盖 `SITE_BASE_URL`。生产环境不得使用该 localhost 默认值。

在生产 `validate_config` 中验证上述第 4.1 节规则。在 `zhugeshensuan/seo.py` 提供纯函数：

```python
def absolute_public_url(base_url: str, path: str) -> str:
    normalized_path = "/" if path == "/" else "/" + path.strip("/")
    return f"{base_url.rstrip('/')}{normalized_path}"
```

真实实现必须按 Step 1 的四类测试拒绝 path 中的外部 scheme、`//host`、query 和 fragment，避免把该函数变成 URL 注入入口。

`.env.example` 增加：

```dotenv
SITE_BASE_URL=https://getwiseoracle.com
```

`deploy/compose.prod.yml` 的 `app.environment` 显式增加：

```yaml
SITE_BASE_URL: "${SITE_BASE_URL:?SITE_BASE_URL is required}"
```

不能假设 `docker compose --env-file .env` 会把未列出的变量自动传入容器。`.github/workflows/ci.yml` 的生产容器 `docker run` 同时增加：

```text
-e SITE_BASE_URL=https://getwiseoracle.com
```

否则新增生产配置校验后，CI 容器会因使用 localhost 默认值而启动失败。

**Step 4: 运行定向测试**

```powershell
python -m pytest tests/test_config.py tests/test_seo_urls.py -q
```

Expected: PASS。

**Step 5: 提交检查点**

```powershell
git add zhugeshensuan/config.py zhugeshensuan/seo.py .env.example deploy/compose.prod.yml .github/workflows/ci.yml tests/test_config.py tests/test_seo_urls.py
git commit -m "feat: establish trusted public site URLs"
```

### Task 2: 建立页面 SEO 注册表和模板上下文（SEO-001）

**Files:**
- Modify: `zhugeshensuan/seo.py`
- Modify: `zhugeshensuan/blueprints/pages.py`
- Modify: `zhugeshensuan/blueprints/pages_en.py`
- Create: `tests/test_seo_metadata.py`

**Step 1: 写失败测试**

用参数化矩阵锁定：每条公开 HTML 路由的 title、description、canonical、robots 策略，以及四组核心页面的 hreflang 对应 URL。测试应解析 DOM，不以脆弱的整段字符串比较代替语义断言。

```python
@pytest.mark.parametrize(
    ("path", "canonical_path"),
    [("/", "/"), ("/ask-oracle", "/ask-oracle"), ("/zh-hant", "/zh-hant")],
)
def test_page_has_one_absolute_self_canonical(client, path, canonical_path):
    ...
```

**Step 2: 运行测试确认失败**

```powershell
python -m pytest tests/test_seo_metadata.py -q
```

Expected: FAIL，指出中文页面缺少 SEO 标签、英文 canonical 仍不受集中注册表控制。

**Step 3: 实现不可变页面注册表**

在 `seo.py` 定义 `SEOPage` 数据类和页面 key，例如：

```python
CORE_ALTERNATES = {
    "home": {"en": "/", "zh-Hans": "/zh-hans", "zh-Hant": "/zh-hant", "x-default": "/"},
    "oracle": {"en": "/ask-oracle", "zh-Hans": "/zh-hans/divination", "zh-Hant": "/zh-hant/divination", "x-default": "/ask-oracle"},
    "almanac": {"en": "/daily-almanac", "zh-Hans": "/zh-hans/almanac", "zh-Hant": "/zh-hant/almanac", "x-default": "/daily-almanac"},
    "bazi": {"en": "/birth-chart-reading", "zh-Hans": "/zh-hans/bazi", "zh-Hant": "/zh-hant/bazi", "x-default": "/birth-chart-reading"},
}
```

注册表必须保存路径和文案，不保存由请求产生的绝对 URL。渲染前使用 `SITE_BASE_URL` 统一展开 canonical、alternates、Open Graph URL 和 JSON-LD URL。

**Step 4: 路由显式注入页面 key**

英文 `_render_en()` 与中文 `render_template()` 都传入 `seo` 上下文。未知 page key 应在测试/启动阶段失败，不能静默退回首页 metadata。

**Step 5: 运行测试**

```powershell
python -m pytest tests/test_seo_urls.py tests/test_seo_metadata.py -q
```

Expected: 在模板标签尚未接入前，注册表单元测试 PASS，渲染测试仍 FAIL；失败原因应准确指向模板。

**Step 6: 提交检查点**

```powershell
git add zhugeshensuan/seo.py zhugeshensuan/blueprints/pages.py zhugeshensuan/blueprints/pages_en.py tests/test_seo_metadata.py
git commit -m "feat: centralize page SEO metadata"
```

### Task 3: 英文和中文模板统一输出 SEO head（SEO-001/003）

**Files:**
- Create: `frontend/templates/partials/seo_head.html`
- Modify: `frontend/templates/en/base.html`
- Modify: `frontend/templates/index.html`
- Modify: `frontend/templates/huangli.html`
- Modify: `frontend/templates/suanshi.html`
- Modify: `frontend/templates/lunming.html`
- Modify: `frontend/templates/en/articles.html`
- Modify: `tests/test_english_frontend_contract.py`
- Test: `tests/test_seo_metadata.py`

**Step 1: 盘点并冻结现有 metadata 迁移基线**

实施前以当前模板建立下表；迁移不是趁机重写文案。任何文案优化必须在 diff 中单独说明，不能与“移动到注册表”混在一起。

| 页面/模板 | 当前 title | 当前 description |
| --- | --- | --- |
| `/` / `en/index.html` | Wise Oracle — Chinese Cultural Divination & Almanac | Draw an oracle sign, read the daily Chinese almanac, and reflect on your birth chart through traditional Chinese cultural wisdom. |
| `/ask-oracle` | Ask the Oracle — Free Chinese Oracle Sign Reading | Hold a question in mind and draw a Zhuge Oracle sign for cultural reflection. Not fortune telling — a mirror for self-examination. |
| `/daily-almanac` | Daily Chinese Almanac — Favorable Activities & Solar Terms | Explore the daily Chinese almanac: traditional activity indications, lunar date, solar terms, zodiac, directions, and cultural context. |
| `/birth-chart-reading` | Birth Chart Reading — BaZi Cultural Self-Reflection | Explore your BaZi birth chart as a cultural framework for self-reflection. Not destiny prediction. |
| `/articles` | Articles — Chinese Divination Culture & Almanac Traditions | Essays on Chinese oracle signs, almanac traditions, and cultural self-reflection practices. |
| `/articles/<slug>` 占位 | Article — Wise Oracle | An article on Chinese divination culture and self-reflection. |
| `/privacy` | Privacy Policy — Wise Oracle | How Wise Oracle handles your data: oracle queries, birth chart input, AI processing, cookies, and your rights. |
| `/terms` | Terms of Service — Wise Oracle | Terms of service for Wise Oracle: acceptable use, no warranty, limitation of liability, and AI content disclaimer. |
| `/disclaimer` | Disclaimer — Wise Oracle | Wise Oracle disclaimer: all readings are for entertainment, cultural exploration, and self-reflection only. Not professional advice. |
| `/about` | About — Wise Oracle | Wise Oracle offers traditional Chinese oracle signs, almanac references, and BaZi birth chart reflections for cultural self-examination. |
| `/contact` | Contact — Wise Oracle | Contact Wise Oracle for questions, feedback, privacy inquiries, or support. |
| `/zh-*/` / `index.html` | 诸葛神算 | 当前无服务端 description |
| `/zh-*/almanac` / `huangli.html` | 诸葛神算 - 传统黄历 | 当前无服务端 description |
| `/zh-*/divination` / `suanshi.html` | 诸葛神算 - 算事 | 当前无服务端 description |
| `/zh-*/bazi` / `lunming.html` | 诸葛神算 - 论命 | 当前无服务端 description |

英文 `base.html` 的默认 title/description 仅是兜底，不作为独立公开页面。中文繁简两种 description 需要在注册表中分别补齐并由项目所有者/评审人员检查文字准确性。

**Step 2: 在共享 partial 中输出统一标签**

目标结构：

```jinja2
<title>{{ seo.title }}</title>
<meta name="description" content="{{ seo.description }}">
<meta name="robots" content="{{ seo.robots }}">
<link rel="canonical" href="{{ seo.canonical_url }}">
{% for language, url in seo.alternates.items() %}
<link rel="alternate" hreflang="{{ language }}" href="{{ url }}">
{% endfor %}
<meta property="og:title" content="{{ seo.title }}">
<meta property="og:description" content="{{ seo.description }}">
<meta property="og:type" content="{{ seo.og_type }}">
<meta property="og:url" content="{{ seo.canonical_url }}">
<meta property="og:site_name" content="Wise Oracle">
<meta property="og:locale" content="{{ seo.og_locale }}">
{% for graph in seo.json_ld %}
<script type="application/ld+json">{{ graph|tojson }}</script>
{% endfor %}
```

实际实现需保证属性转义，JSON-LD 不得使用 `safe` 直接放入手拼 JSON。

**Step 3: 接入英文基础模板**

移除 `request.base_url` canonical。各英文子模板现有 title/description block 要么迁移到注册表，要么只作为显示文案来源；不得保留两套相互漂移的元数据权威源。

**Step 4: 接入四个中文独立模板**

在每个 `<head>` 中 include 同一 partial。保留 `data-i18n` 的可见交互文案，但服务端首屏 title/description 必须已经与当前 URL 语言匹配，不能依赖 JavaScript 执行后才纠正搜索标签。

现有中文模板的 `<html lang="{{ html_lang|default('zh-Hans') }}">` 已通过 `html_lang_for()` 输出 `zh-Hans`/`zh-Hant`，与 hreflang 使用的 BCP 47 值一致；本任务只补充 head 元数据，不改变这项语言语义。

**Step 5: 处理文章占位页并更新旧契约测试**

- `/articles` 输出 `noindex,follow`，直到 ART-002 至少存在一篇 published 文章。
- `/articles/<slug>` 在 ART-002 前对任何 slug 返回 404，避免 soft-404 和无限 URL；不保留 `how-oracle-signs-work` 特例。
- 将 `tests/test_english_frontend_contract.py` 中 `/articles/how-oracle-signs-work` 从“全部返回 200”的参数集合移出，并新增 `test_unpublished_article_slug_returns_404`。这是公开路由契约从占位 200 到正确 404 的必要更新，不是删除测试迁就代码。

**Step 6: 运行定向测试**

```powershell
python -m pytest tests/test_seo_metadata.py tests/test_english_frontend_contract.py tests/test_frontend_contract.py -q
```

Expected: PASS；每页恰好一个 title、description、canonical，核心页面 hreflang 完整且互返。

**Step 7: 提交检查点**

```powershell
git add frontend/templates zhugeshensuan/blueprints/pages_en.py tests/test_seo_metadata.py tests/test_english_frontend_contract.py tests/test_frontend_contract.py
git commit -m "feat: render canonical metadata and language alternates"
```

### Task 4: 实现 sitemap.xml（SEO-002）

**Files:**
- Create: `zhugeshensuan/blueprints/seo.py`
- Create: `frontend/templates/sitemap.xml`
- Modify: `zhugeshensuan/blueprints/__init__.py`
- Create: `tests/test_sitemap.py`

**Step 1: 写失败测试**

断言：

- `GET /sitemap.xml` 返回 200。
- `Content-Type` 为 `application/xml` 或 `application/xml; charset=utf-8`。
- XML 可解析，使用标准 `http://www.sitemaps.org/schemas/sitemap/0.9` namespace。
- 精确包含第 4.4 节 9 个 URL，且全部使用正式 origin。
- 不出现 `.example`、测试 host、query、fragment、重复 URL。
- 不出现 API、健康检查、旧路由、简体路由、占位文章或未发布文章。

**Step 2: 运行测试确认失败**

```powershell
python -m pytest tests/test_sitemap.py -q
```

Expected: FAIL with 404。

**Step 3: 实现 sitemap 端点**

使用受控常量或已发布内容 manifest 生成列表，不遍历 Flask `url_map`，因为自动遍历会把 API、动态占位和兼容路由带入 sitemap。

```python
@seo_bp.get("/sitemap.xml")
def sitemap():
    urls = build_sitemap_urls(current_app.config["SITE_BASE_URL"])
    return Response(render_template("sitemap.xml", urls=urls), mimetype="application/xml")
```

在 `zhugeshensuan/blueprints/__init__.py` 中显式：

1. `from .seo import seo_bp`；
2. 把 `seo_bp` 加入 `ALL_BLUEPRINTS` 元组；
3. 通过测试确认 `/sitemap.xml` 和 `/robots.txt` 都只注册一次。

**Step 4: 运行测试**

```powershell
python -m pytest tests/test_sitemap.py -q
```

Expected: PASS。

**Step 5: 提交检查点**

```powershell
git add zhugeshensuan/blueprints/seo.py zhugeshensuan/blueprints/__init__.py frontend/templates/sitemap.xml tests/test_sitemap.py
git commit -m "feat: publish controlled XML sitemap"
```

### Task 5: 实现 robots.txt（SEO-002）

**Files:**
- Modify: `zhugeshensuan/blueprints/seo.py`
- Create: `frontend/templates/robots.txt`
- Create: `tests/test_robots.py`

**Step 1: 写失败测试**

断言 200、`text/plain`、只有一个正式 sitemap URL，并覆盖以下语义：

```text
User-agent: *
Allow: /
Disallow: /api/
Disallow: /healthz
Disallow: /readyz
Sitemap: https://getwiseoracle.com/sitemap.xml
```

不得禁止 CSS/JS/图片；不得列出任何密钥、后台真实路径或用户数据路径。

**Step 2: 运行测试确认失败**

```powershell
python -m pytest tests/test_robots.py -q
```

Expected: FAIL with 404。

**Step 3: 实现并测试**

```powershell
python -m pytest tests/test_robots.py tests/test_sitemap.py -q
```

Expected: PASS。

**Step 4: 提交检查点**

```powershell
git add zhugeshensuan/blueprints/seo.py frontend/templates/robots.txt tests/test_robots.py
git commit -m "feat: publish crawler directives"
```

### Task 6: 完成 Open Graph 与 JSON-LD（SEO-003）

**Files:**
- Modify: `zhugeshensuan/seo.py`
- Modify: `frontend/templates/partials/seo_head.html`
- Modify: `tests/test_seo_metadata.py`
- Conditional create: `frontend/static/images/wise-oracle-og-1200x630.png`

**Step 1: 写失败测试**

测试每个 indexable 页面：

- `og:url` 等于 canonical。
- `og:title`/`og:description` 与页面元数据一致。
- `og:locale` 与当前语言一致：`en_US`、`zh_CN`、`zh_TW`。
- 每个 JSON-LD script 都可由 `json.loads()` 解析。
- JSON-LD 的 `url` 使用正式 origin，类型在批准白名单内。
- 不出现虚构评分、评论、医疗/金融资质、价格或保证性措辞。

`seo.py` 只保留一份显式映射，不在模板中分散判断：

```python
OG_LOCALES = {
    "en": "en_US",
    "zh-Hans": "zh_CN",
    "zh-Hant": "zh_TW",
}
```

**Step 2: 实现保守 schema graph**

首页示意：

```python
{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Wise Oracle",
    "url": "https://getwiseoracle.com/",
    "inLanguage": "en",
}
```

工具页使用 `WebPage`，并通过 `isPartOf` 指向站点。页面没有真实可见面包屑时不输出虚构 `BreadcrumbList`。

同时增加 CSP 兼容验证：

- 响应仍保持 `script-src 'self'`，测试明确禁止为了 JSON-LD 加入 `'unsafe-inline'`。
- 在 Chromium 系浏览器查看控制台，确认 `application/ld+json` 数据块没有产生 CSP violation。
- 用页面原始响应解析 JSON-LD，再使用 Google Rich Results Test 或 Schema.org Validator 检查。
- 如果受支持浏览器确实报告兼容问题，先评估只给该数据块使用按响应生成的 nonce/hash；不得改为全站 `'unsafe-inline'`，也不得假设外部 JSON-LD 文件会被搜索引擎等价识别。

**Step 3: 分享图条件门禁**

只有同时满足以下条件才添加 `og:image`：

- 文件实际存在且为 1200×630。
- 版权和品牌使用明确。
- 绝对 URL 可从生产环境访问，返回正确图片 MIME。
- 桌面和移动分享预览人工检查通过。

未满足时允许本批次没有 `og:image`，并在验收记录列为“后续增强”，不能引用不存在的图片。

**Step 4: 运行测试**

```powershell
python -m pytest tests/test_seo_metadata.py -q
```

Expected: PASS。

**Step 5: 提交检查点**

```powershell
git add zhugeshensuan/seo.py frontend/templates/partials/seo_head.html tests/test_seo_metadata.py frontend/static/images
git commit -m "feat: add social and structured page metadata"
```

如果没有新增图片，不得为使 `git add` 成功而创建空目录或占位文件。

### Task 7: 文档、全量门禁和本地验收（SEO-001/002/003）

**Files:**
- Modify: `docs/部署指南.md`
- Modify: `docs/plans/2026-07-15-project-completion-master-ledger.md`
- Modify: `.github/workflows/ci.yml`
- Create: `docs/reviews/2026-07-16-seo-001-003-acceptance.md`

**Step 1: 更新部署契约**

部署文档必须写清：

- `SITE_BASE_URL=https://getwiseoracle.com` 是生产必填项。
- 反向代理必须把 HTTP 重定向到 HTTPS。
- `www.getwiseoracle.com` 若配置 DNS，必须 301 到无 `www` 主域名，并保留 path/query。
- 应用接受代理头的范围由 `TRUSTED_PROXY_HOPS` 控制，但 SEO URL 不依赖代理 host。
- 环境切换测试不得把 staging host 写入生产 canonical。

**Step 2: 运行 SEO 定向门禁**

```powershell
python -m pytest tests/test_config.py tests/test_seo_urls.py tests/test_sitemap.py tests/test_robots.py tests/test_seo_metadata.py tests/test_english_frontend_contract.py tests/test_frontend_contract.py -q
```

Expected: 全部 PASS，无 warning。

**Step 3: 运行全量质量门禁**

```powershell
python -m pytest -W error::ResourceWarning
python -m black --check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
python -m ruff check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
python -m pip_audit -r requirements.txt --no-deps --progress-spinner off
git diff --check
python -c "import pathlib, subprocess; files=sorted(pathlib.Path('frontend/static/js').rglob('*.js')); assert files; [subprocess.run(['node', '--check', str(path)], check=True) for path in files]; print(f'node --check: {len(files)}/{len(files)} passed')"
```

Expected: 全部退出码 0；当前应输出 `node --check: 14/14 passed`。若后续新增或删除 JS，数量随实际目录变化，但必须保持全量检查。若 `pip-audit` 因网络不可达失败，必须记录为外部阻塞，不能改写成“通过”。

同时把 `.github/workflows/ci.yml` 当前三个单文件 `node --check` 步骤替换为同一递归命令，确保 CI 与本地门禁一致，而不是只在人工验收时全量检查。

**Step 4: 本地 HTML/XML 人工检查**

至少检查：

- 1440px 和 390px 下核心英文/繁体页面仍正常显示。
- 查看源码确认 SEO 标签在服务端响应中存在，不依赖 JavaScript。
- 用伪造 `Host: attacker.example` 请求，源码仍只引用正式 origin。
- `/sitemap.xml` 可由 XML 解析器打开。
- `/robots.txt` 是纯文本，sitemap 地址正确。
- 使用 `/articles/nonexistent-<UUID>` 构造不可能与已发布文章冲突的 slug，确认返回 404，而不是占位 200。

**Step 5: 建立验收记录**

`docs/reviews/2026-07-16-seo-001-003-acceptance.md` 记录：提交号、文件清单、测试数量与结果、人工检查路径、未完成的生产验收、回滚方式和已知限制。没有真实域名证据前，SEO 任务最高只能标记“待验收”，不能标记“已完成”。

**Step 6: 提交检查点**

```powershell
git add docs/部署指南.md docs/plans/2026-07-15-project-completion-master-ledger.md docs/reviews/2026-07-16-seo-001-003-acceptance.md
git commit -m "docs: record technical SEO verification"
```

### Task 8: 生产域名验收（与 OPS-001 协同）

**Files:**
- Modify: `docs/reviews/2026-07-16-seo-001-003-acceptance.md`
- Modify: `docs/operations/production-acceptance.md`

**Step 1: DNS/HTTPS 验证**

确认 `getwiseoracle.com` 解析到预期生产入口，TLS 证书有效且覆盖所使用域名。若 `www` 有 DNS，则验证其 301 到无 `www` 主域名；若未配置 `www`，记录“未启用”，不能声称已重定向。

**Step 2: HTTP 响应验证**

```powershell
curl.exe -I https://getwiseoracle.com/
curl.exe -I https://getwiseoracle.com/sitemap.xml
curl.exe -I https://getwiseoracle.com/robots.txt
curl.exe -I https://getwiseoracle.com/healthz
curl.exe -I https://getwiseoracle.com/readyz
```

Expected: 首页 200；sitemap 200 + XML MIME；robots 200 + text MIME；health/readiness 与生产配置状态一致；无 HTTP→HTTPS 循环。

**Step 3: 生产源码抽检**

抽检英文首页、三个英文工具页、繁体首页、一个繁体工具页：canonical/hreflang/OG/JSON-LD 均使用正式域名；响应中无 localhost、测试 host 或 `.example`。

**Step 4: 搜索引擎工具验证**

- 使用 Schema.org Validator 或搜索引擎 Rich Results 工具验证 JSON-LD 可解析。
- 在 Search Console 完成所有权后提交 `/sitemap.xml`，属于 OPS-004；记录提交日期和响应，不承诺立即收录。

**Step 5: 状态更新**

只有本地门禁与生产证据均齐全，才能把 SEO-001/002/003 从“待验收”改为“已完成”。

## 7. 测试与验收矩阵

| 风险 | 自动测试 | 人工/生产验收 | 完成标准 |
| --- | --- | --- | --- |
| Host 注入污染 canonical | 伪造 Host 和 Forwarded Host | 生产源码抽检 | 绝对 URL 始终使用配置 origin |
| 多语言映射错误 | 四组互返矩阵测试 | 逐页查看源码 | en/zh-Hans/zh-Hant/x-default 完整且对应 |
| sitemap 混入私有/占位路由 | 精确集合、排除集合、XML 解析 | 生产打开 sitemap | 只有批准的 9 个 URL |
| robots MIME/规则错误 | 响应和文本断言 | 生产 curl | 规则可读且 sitemap 地址唯一 |
| 重复或漂移 metadata | DOM 参数化测试 | 页面源码抽检 | 每页一个 title/description/canonical |
| JSON-LD 无法解析或虚构 | `json.loads` + 类型白名单 | validator 检查 | 0 个解析错误，内容与页面一致 |
| 占位文章形成 soft-404 | 未知 slug 404 测试 | 随机 slug 请求 | 不返回可索引 200 |
| SEO 改动破坏页面 | 全量 pytest + 前端契约 | 1440px/390px | 功能与布局无回归 |
| 本地通过但线上配置错误 | 配置生产校验 | DNS/TLS/curl/源码 | 生产证据写入验收记录 |

## 8. 回滚方案

SEO 代码不迁移数据库，回滚重点是配置和模板：

1. 保留变更前应用镜像/提交号。
2. 若新版本导致 5xx 或模板渲染失败，回滚应用镜像；不得仅删除 `SITE_BASE_URL` 绕过生产校验。
3. 若只有 sitemap/robots 内容错误，可回滚对应应用提交并清除 CDN 缓存。
4. 若 canonical 指向错误域名，应视为高优先级发布事故：立即回滚、修正、重新部署，并在 Search Console 检查影响。
5. 回滚后复测首页、三个核心工具页、sitemap、robots、healthz、readyz。
6. 记录故障窗口、错误 URL、回滚提交和恢复时间。

## 9. 外部专业评审清单

请评审人员重点回答：

1. 固定 `SITE_BASE_URL`、不信任请求 Host 的方案是否正确实现？
2. 四组 hreflang 是否语义等价、互返完整，`x-default` 是否合理？
3. 简体页面“自指 canonical + hreflang 但暂不进 sitemap”的策略是否符合当前市场范围？
4. 第一版 sitemap 的 9 个 URL 是否过少或包含不必要页面？
5. 文章占位页 noindex、未知 slug 404 的过渡策略是否足以避免 soft-404？
6. WebSite/WebPage 的结构化数据是否与可见内容一致，有无不当 schema 类型？
7. robots 是否只承担抓取提示而没有被误用为安全控制？
8. 自动测试能否防止 host 注入、语言映射漂移、重复 metadata 和未发布内容误收录？
9. 生产 DNS、HTTPS、`www`、代理和缓存层是否还有本仓库无法覆盖的风险？

评审意见若改变 URL、语言或索引范围，必须先更新本方案和主台账版本，再实施代码；不得只在代码中临时调整。

## 10. 完成定义

SEO-001/002/003 全部完成必须同时满足：

- `SITE_BASE_URL=https://getwiseoracle.com` 已配置并通过生产校验。
- 所有批准页面 canonical 正确，伪造 Host 不影响输出。
- 四组核心页面 hreflang 完整互返。
- sitemap 精确包含批准 URL，robots 指向正式 sitemap。
- title、description、Open Graph、JSON-LD 通过自动解析和人工抽检。
- 占位文章不形成可索引无限 URL。
- SEO 定向测试、全量测试、Black、Ruff、依赖审计和 JS 语法检查均有真实结果。
- 1440px/390px 页面无回归。
- 真实域名 DNS、HTTPS、HTTP 状态、源码标签均有验收证据。
- 主台账和 SEO 验收记录已更新，已知限制与后续任务明确。

在上述条件全部具备前，状态只能是“进行中”或“待验收”，不能写成“已完成”。

## 11. 规范与官方参考

- W3C HTML 5.2 `script` data block 规则：<https://www.w3.org/TR/2017/REC-html52-20171214/semantics-scripting.html>
- W3C Content Security Policy Level 3：<https://www.w3.org/TR/CSP/>
- Google Search Central — Structured data introduction：<https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data>
- Google Search Central — Generate structured data with JavaScript / server-side rendering：<https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript>
- Google Search Central — General structured data guidelines：<https://developers.google.com/search/docs/appearance/structured-data/sd-policies>
