# 项目结构说明

本项目按运行边界整理：

- `zhugeshensuan/` 是后端包，生产入口为 `zhugeshensuan.app:create_app`，根目录 `app.py` 只做兼容转发。
- `frontend/` 只放浏览器可见资源，Flask 在应用工厂中显式绑定模板和静态目录。
- `data/reference/` 只放可重建或只读参考数据；运行期 SQLite 放在 `instance/`，不提交仓库。
- `deploy/` 只放部署配置；Docker 构建仍以仓库根目录为上下文。
- `frontend/templates/en/` 是英文站模板目录，包含 `base.html` 共享布局和 11 个英文页面（首页、Ask the Oracle、Daily Almanac、Birth Chart Reading、合规页等）。
- `data/content/` 存放英文内容数据：`oracle_signs_en.json`（384 条英文签文）、`huangli_terms_en.json`（英文黄历词表）、`huangli_scenarios_en.json`（英文场景定义）。英文数据走 JSON 内存加载，不入数据库。
- `zhugeshensuan/` 中的 i18n 相关模块：`huangli_english.py`（英文黄历翻译）、`oracle_english.py`（英文签文服务）、`birth_chart_english.py`（英文论命服务）、`error_codes.py`（中英文错误码映射）、`i18n_utils.py`（国际化工具）、`huangli_i18n.py`（简繁本地化）。英文蓝图（`pages_en.py`、`oracle_en_api.py`、`huangli_en_api.py`、`birth_chart_en_api.py`）统一使用 `/api/en/*` 前缀。
- `archive/` 不参与运行，包含旧日历实验、微信小程序历史文档、旧日志、旧 notebook、已废止的商业计划和历史镜像包。
- `prompts/` 只放 AI 翻译/审查/评定的系统提示词，不参与运行。
- `scripts/` 放数据构建、翻译审查、同步看板等离线脚本，不参与运行。

判断文件是否应进入归档的标准：

- 当前 Flask 应用没有引用。
- 文档内容明确描述早期实现或其他端形态。
- 文件是一次性构建产物、调试产物或历史备份。
- 文档已被新版本取代或明确标记为已废止。
