# 项目结构说明

本项目按运行边界整理：

- `zhugeshensuan/` 是后端包，生产入口为 `zhugeshensuan.app:create_app`，根目录 `app.py` 只做兼容转发。
- `frontend/` 只放浏览器可见资源，Flask 在应用工厂中显式绑定模板和静态目录。
- `data/reference/` 只放可重建或只读参考数据；运行期 SQLite 放在 `instance/`，不提交仓库。
- `deploy/` 只放部署配置；Docker 构建仍以仓库根目录为上下文。
- `archive/` 不参与运行，包含旧日历实验、微信小程序历史文档、旧日志、旧 notebook 和历史镜像包。

判断文件是否应进入归档的标准：

- 当前 Flask 应用没有引用。
- 文档内容明确描述早期实现或其他端形态。
- 文件是一次性构建产物、调试产物或历史备份。
