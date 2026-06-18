# 诸葛神算 V3

诸葛神算 V3 是一个传统文化主题的 Flask Web 应用，提供黄历、三字起卦和八字文化解读。黄历与四柱基础数据由确定性历法库计算，语言模型只负责解释结构化结果。

> 传统文化娱乐参考，不构成医疗、投资或人生决策建议。

## 功能

- 黄历：单日详情、九天比较、场景筛选、收藏、复制、分享和打印。
- 算事：问题确认、重复提醒、三字笔画起卦、分类解签和本地记录。
- 论命：四柱、生肖、五行、纳音、大运、时辰未知、时区和真太阳时修正。
- 隐私：论命使用 POST 流传输；收藏、起卦记录和报告只保存在浏览器本地。

## 技术栈

- Python 3.13、Flask 3、Gunicorn
- SQLite、openpyxl、pandas
- lunar-python
- OpenAI 兼容模型接口
- HTML、CSS、原生 JavaScript、Server-Sent Events
- pytest、Black、Ruff、GitHub Actions、Docker

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe app.py
```

默认访问 `http://127.0.0.1:8000`。如需 AI 解读，在 `.env` 中配置新的 `AI_API_KEY`；不要把密钥提交到仓库。

## 验证

```powershell
.\.venv\Scripts\python.exe -m black --check app.py api_utils.py config.py logging_config.py database.py huangli.py lunming.py bazi_service.py bailian.py gunicorn.conf.py blueprints tests
.\.venv\Scripts\python.exe -m ruff check app.py api_utils.py config.py logging_config.py database.py huangli.py lunming.py bazi_service.py bailian.py gunicorn.conf.py blueprints tests
.\.venv\Scripts\python.exe -m pytest
node --check static\js\huangli.js
node --check static\js\lunming.js
node --check static\js\main.js
```

## 目录边界

- `blueprints/`：HTTP 路由。
- `database.py`、`huangli.py`、`lunming.py`、`bazi_service.py`：业务服务。
- `instance/`：运行时数据库和本地备份，不进入版本控制。
- `日历/`：早期独立 JavaScript 日历实验及其上游测试，不由 Flask 引用，不进入 Docker 镜像；归档或删除需另行确认。

接口细节见 `API文档.md`，部署见 `部署指南.md`。
