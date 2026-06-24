# 诸葛神算 - CodeBuddy Code 开发指南

这是一个基于传统命理学的Flask Web应用，提供黄历、算事（占卜）和论命（八字分析）三大功能。

## 开发环境和运行

### 基本命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器（默认端口80）
python app.py

# 访问应用
http://localhost:80
```

### 生产环境部署

参考 `部署指南.md` 文档，使用 Nginx + Gunicorn 部署：

```bash
# 使用Gunicorn启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 或使用systemd服务
systemctl start flaskapp
```

## 核心架构

### 应用结构

* **app.py**: 主应用入口，定义路由和API端点
* **数据层**:

  * `database.py`: 汉字笔画数据库和卦象数据管理
  * `database/`: SQLite数据库文件存储
* **功能模块**:

  * `huangli.py`: 黄历数据生成和缓存
  * `lunming.py`: 八字命理分析（集成AI大模型）
  * `utils.py`: 工具函数（笔画计算、数字转换等）
* **前端资源**:

  * `templates/`: HTML模板文件
  * `static/`: CSS、JS和图片资源

### 关键技术栈

* **后端**: Python 3.12 + Flask 2.3.3
* **历法计算**: lunar-python 1.3.1 (基于寿星历算法)
* **数据库**: SQLite (汉字笔画数据、黄历缓存)
* **AI集成**: OpenAI API (用于八字分析)
* **前端**: 原生HTML/CSS/JS，响应式设计
* **数据处理**: pandas (Excel数据读取)

### API架构

应用提供RESTful API和流式API：

* `/api/huangli`: 黄历数据API
* `/api/week\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_huangli`: 九天黄历概览
* `/get\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_strokes`: 汉字笔画查询
* `/calculate\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_sign`: 签号计算
* `/get\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_gua\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_info`: 卦象信息查询
* `/api/lunming/stream`: SSE流式八字分析

## 核心算法

### 签号计算算法

位于 `utils.py:cale\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_character\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_count()`：

1. 获取三个汉字的康熙笔画数
2. 每个笔画数取模10得个位数（0则为1）
3. 组合成三位数，对384取模得到1-383签号

### 黄历数据生成

位于 `huangli.py:\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_generate\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_huangli\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_data()`：

* 使用lunar\_python库进行农历转换
* 计算干支、节气、吉凶宜忌
* 数据缓存到SQLite避免重复计算

### 八字命理分析

位于 `lunming.py`：

* 解析生辰信息，计算四柱干支
* 生成结构化提示词调用AI模型
* 支持流式输出（SSE）实时显示分析结果

## 数据管理

### 汉字笔画数据库

* 文件: `database/kanxi\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_dict.db`
* 优先本地查询，缺失时从汉典网获取并缓存
* 使用康熙字典笔画标准

### 卦象数据

* 文件: `database/zhugeshenshuan\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_jq.xlsx`
* 包含383个签文及对应解释
* 涵盖事业、财运、情感、健康等多维度解签

### 黄历缓存

* 表: `huangli\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_daily`
* 缓存已计算的黄历数据
* 包含干支、宜忌、神煞、节气等完整信息

## 前端特性

### 响应式设计

* 桌面端和移动端分离样式表
* 媒体查询自动适配不同屏幕尺寸
* 移动设备优化的触摸交互

### 日期处理

* 支持阴历阳历互转（`static/js/lunar\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_date\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_handler.js`）
* 闰月处理和日期验证
* 实时联动的日期选择器

### 流式输出处理

* 前端JavaScript处理SSE流式数据
* 智能文本解析（标题、列表、正文）
* 缓冲区处理确保显示连贯性

## 开发注意事项

### AI模型配置

在 `lunming.py` 中配置OpenAI API：

* 需要设置正确的API密钥和base\_url
* 支持流式输出的AI模型
* 建议使用temperature=0.7保持分析的创造性

### 数据库初始化

首次运行时会自动创建必要的数据库表，确保：

* `database/` 目录存在且有写权限
* `database/zhugeshenshuan\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_jq.xlsx` 文件完整

### 部署配置

生产环境需要：

* 禁用Flask的debug模式
* 配置Nginx支持SSE（proxy\_buffering off）
* 设置合适的超时时间（300s）

## 测试和调试

### 本地测试

```bash
# 测试黄历功能
curl "http://localhost:80/api/huangli?date=2023-05-01"

# 测试算事功能
curl -X POST "http://localhost:80/get\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_strokes" -H "Content-Type: application/json" -d '{"character":"诸"}'

# 测试流式分析
curl "http://localhost:80/api/lunming/stream?name=张三\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\&gender=男\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\&birth\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_date=1990-05-01\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\&birth\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_time=子"
```

### 日志查看

* 应用日志: `error.log`
* Gunicorn日志: `journalctl -u flaskapp`
* Nginx日志: `/var/log/nginx/error.log`

