# 诸葛神算 V4

诸葛神算 V4 是一个可部署的 Flask Web 项目，提供黄历、诸葛神算、论命解读等传统文化娱乐功能。项目已按运行边界整理为后端、前端、数据、部署和归档目录，根目录只保留入口、依赖、配置模板和项目说明。

> 本项目内容仅用于传统文化娱乐参考，不构成医疗、投资或人生决策建议。

## 目录结构

- `zhugeshensuan/`：Flask 后端包，包含应用工厂、蓝图、业务服务、配置和数据库访问。
- `frontend/templates/`：Jinja 页面模板。
- `frontend/static/`：CSS、JavaScript、图片和字体等前端静态资源。
- `data/reference/`：只读参考数据，`reference.db` 可由 `scripts/build_reference_db.py` 重建。
- `scripts/`：维护脚本和数据构建脚本。
- `tests/`：后端、接口、数据和前端契约测试。
- `deploy/`：Dockerfile、Compose、Gunicorn 和 Nginx 示例配置。
- `docs/`：当前文档、部署说明、API 文档、计划和商业材料。
- `archive/`：旧实验、旧文档和历史构建产物，不参与生产运行。
- `app.py`：兼容入口，保留 `python app.py` 和 `gunicorn app:app` 的使用方式。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe app.py
```

默认访问 `http://127.0.0.1:8000`。如需 AI 解读，在项目根目录 `.env` 中配置 `AI_API_KEY`；不要提交真实密钥。

## 验证

```powershell
.\.venv\Scripts\python.exe -m black --check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
.\.venv\Scripts\python.exe -m ruff check app.py zhugeshensuan deploy/gunicorn.conf.py scripts tests
.\.venv\Scripts\python.exe -m pytest -W error::ResourceWarning
node --check frontend\static\js\huangli.js
node --check frontend\static\js\lunming.js
node --check frontend\static\js\main.js
```

## 数据重建

```powershell
.\.venv\Scripts\python.exe scripts\build_reference_db.py
```

该命令会读取 `data/reference/kanxi_dict.db`、汉典补充权威源
`data/reference/hanzi_strokes_zdic.csv`、`data/reference/zhugeshenshuan_jq.xlsx`
、`data/content/oracle_signs_reinterpreted.json`、
`data/content/oracle_signs_reinterpreted_hant.json` 和 `data/reference/pzbj.json`，
生成 `data/reference/reference.db`。

汉字笔画查询顺序固定为：先查本地数据库，缺字时再查询汉典。汉典成功返回的
新字会写入 `runtime.db`，在可写的本地环境还会同步到 `reference.db`。发布前运行
以下命令，将所有新增字纳入可审查、可重建的权威补充源：

```powershell
.\.venv\Scripts\python.exe scripts\sync_stroke_to_hanzi.py
.\.venv\Scripts\python.exe scripts\build_reference_db.py
```

## 部署

生产部署资产位于 `deploy/`：

```powershell
docker build -f deploy/Dockerfile -t zhugeshensuan:local .
docker compose --env-file .env -f deploy/compose.prod.yml up -d --build

```

详细服务器部署流程见 [docs/部署指南.md](docs/部署指南.md)，接口说明见 [docs/API文档.md](docs/API文档.md)。
