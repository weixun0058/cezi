# 诸葛神算V2 工作流程

本文档记录诸葛神算V2项目的工作流程、开发过程和使用方法。

## 开发流程

### 1. 黄历功能

黄历功能是本项目的核心模块之一，提供专业的传统黄历查询服务。

#### 1.1 数据获取流程

1. 用户访问黄历页面或通过API请求黄历数据
2. 系统检查数据库中是否已有该日期的黄历数据
   - 如果有，直接从数据库返回数据
   - 如果没有，调用`lunar_python`库生成黄历数据
3. 生成的黄历数据包括：
   - 农历日期、天干地支、生肖
   - 每日宜忌事项（通过`lunar_python`库的`getDayYi`和`getDayJi`方法获取）
   - 彭祖百忌（通过`lunar_python`库的`getPengZuGan`和`getPengZuZhi`方法获取）
   - 神煞信息：
     - 冲煞（通过`getChong`、`getChongGan`和`getSha`方法获取）
     - 喜神（通过`getDayPositionXi`和`getDayPositionXiDesc`方法获取）
     - 福神（通过`getDayPositionFu`和`getDayPositionFuDesc`方法获取）
     - 财神（通过`getDayPositionCai`和`getDayPositionCaiDesc`方法获取）
     - 吉神（通过`getDayJiShen`方法获取）
     - 凶神（通过`getDayXiongSha`方法获取）
   - 节气信息（通过`getJieQi`方法获取）
   - 节日信息（通过`getFestivals`方法获取）
4. 将生成的数据保存到数据库，并返回给用户

#### 1.2 前端展示流程

1. 页面加载时，通过JavaScript获取当前日期
2. 调用API获取当日黄历数据
3. 将数据渲染到页面对应位置
4. 同时获取九天黄历预览数据（前2天、今天和未来6天）
5. 用户可以通过日期选择器或前后按钮切换日期

### 2. 算事功能

算事功能基于传统卜卦方法，为用户提供问事预测服务。

#### 2.1 卜卦流程

1. 用户输入三个汉字
2. 系统查询每个汉字的康熙笔画数
3. 根据笔画数计算签号（1-383之间）
4. 根据签号查询对应的卦象信息
5. 返回卦象解读和多维度运势分析

#### 2.2 前端展示流程

1. 用户在输入框中输入三个汉字
2. 点击"开始测算"按钮
3. 系统显示测算过程动画
4. 显示卦象结果，包括签文、卦属、吉凶等信息
5. 显示多维度解读，包括事业、财运、情感、健康、学业等

### 3. 论命功能

论命功能目前处于开发中，将提供基于生辰八字的命盘分析。

## 数据库结构

### 1. 黄历数据表 (huangli_daily)

```sql
CREATE TABLE huangli_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE,
    lunar_date TEXT,
    gan_zhi_year TEXT,
    gan_zhi_month TEXT,
    gan_zhi_day TEXT,
    gan_zhi_hour TEXT,
    zodiac TEXT,
    suitable TEXT,
    unsuitable TEXT,
    chong_sha TEXT,
    ji_shen TEXT,
    xiong_shen TEXT,
    peng_zu_bai_ji TEXT,
    xi_shen TEXT,
    fu_shen TEXT,
    cai_shen TEXT,
    solar_term TEXT,
    festivals TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 2. 卦象数据表

卦象数据存储在数据库中，包含383个卦象的详细信息。

## API接口

### 1. 黄历API

#### 1.1 获取指定日期的黄历数据

- 请求：`GET /api/huangli?date=YYYY-MM-DD`
- 响应：黄历数据JSON对象，包含以下字段：
  - `date`: 阳历日期
  - `lunar_date`: 农历日期
  - `gan_zhi_year`: 年干支
  - `gan_zhi_month`: 月干支
  - `gan_zhi_day`: 日干支
  - `gan_zhi_hour`: 时辰干支
  - `zodiac`: 生肖
  - `suitable`: 宜事项（以"、"分隔）
  - `unsuitable`: 忌事项（以"、"分隔）
  - `chong_sha`: 冲煞信息
  - `ji_shen`: 吉神信息
  - `xiong_shen`: 凶神信息
  - `peng_zu_bai_ji`: 彭祖百忌
  - `xi_shen`: 喜神方位
  - `fu_shen`: 福神方位
  - `cai_shen`: 财神方位
  - `solar_term`: 节气信息
  - `festivals`: 节日信息数组

#### 1.2 获取九天黄历预览数据

- 请求：`GET /api/huangli/week`
- 响应：九天黄历数据JSON数组，每个元素包含简化的黄历信息

### 2. 算事API

#### 2.1 获取汉字笔画数

- 请求：`POST /get_strokes`
- 请求体：`{"character": "汉字"}`
- 响应：`{"strokes": 笔画数}`

#### 2.2 计算签号

- 请求：`POST /calculate_sign`
- 请求体：`{"strokes": [笔画数1, 笔画数2, 笔画数3]}`
- 响应：`{"sign_number": 签号}`

#### 2.3 获取卦象信息

- 请求：`POST /get_gua_info`
- 请求体：`{"sign_number": 签号}`
- 响应：卦象详细信息JSON对象

## 使用方法

### 1. 黄历功能

1. 访问主页 `/` 或 `/huangli`
2. 查看当日黄历信息，包括：
   - 阳历和农历日期
   - 天干地支和生肖
   - 宜忌事项
   - 彭祖百忌
   - 神煞信息（冲煞、喜神、福神、财神、吉神、凶神）
   - 节气和节日信息
3. 使用日期选择器或前后按钮切换日期
4. 查看九天黄历预览，点击任意日期查看详情

### 2. 算事功能

1. 点击主页的"算事"链接或直接访问 `/suanshi`
2. 在输入框中输入三个汉字
3. 点击"开始测算"按钮
4. 查看卦象解读和多维度运势分析

### 3. 论命功能

1. 点击主页的"论命"链接或直接访问 `/lunming`
2. 此功能正在开发中，敬请期待

## 维护与更新

1. 定期检查`lunar_python`库的更新，确保黄历数据的准确性
2. 根据用户反馈优化界面和功能
3. 完善论命功能的开发
4. 考虑添加更多传统命理学内容，如六爻、梅花易数等

## lunar_python库使用说明

本项目使用`lunar_python`库获取准确的中国传统历法数据。以下是主要使用的方法：

1. **创建日期对象**：
   ```python
   from lunar_python import Solar, Lunar
   
   # 创建阳历日期对象
   solar = Solar.fromYmd(2023, 2, 28)
   
   # 转换为农历日期对象
   lunar = solar.getLunar()
   ```

2. **获取基本信息**：
   ```python
   # 获取农历日期
   lunar_month = lunar.getMonthInChinese()  # 返回如"正"、"二"等
   lunar_day = lunar.getDayInChinese()      # 返回如"初一"、"十五"等
   
   # 获取天干地支
   gan_zhi_year = lunar.getYearInGanZhi()   # 返回如"甲子"
   gan_zhi_month = lunar.getMonthInGanZhi() # 返回如"丙寅"
   gan_zhi_day = lunar.getDayInGanZhi()     # 返回如"壬辰"
   gan_zhi_hour = lunar.getTimeInGanZhi()   # 返回如"丙子"
   
   # 获取生肖
   shengxiao = lunar.getYearShengXiao()     # 返回如"鼠"、"牛"等
   ```

3. **获取宜忌信息**：
   ```python
   # 获取宜事项
   yi_list = lunar.getDayYi()               # 返回宜事项列表
   
   # 获取忌事项
   ji_list = lunar.getDayJi()               # 返回忌事项列表
   ```

4. **获取神煞信息**：
   ```python
   # 获取冲煞
   chong = lunar.getChong()                 # 返回冲的生肖
   chong_gan = lunar.getChongGan()          # 返回冲的天干
   sha = lunar.getSha()                     # 返回煞方位
   
   # 获取喜神方位
   xi_position = lunar.getDayPositionXi()   # 返回喜神方位
   xi_desc = lunar.getDayPositionXiDesc()   # 返回喜神方位描述
   
   # 获取福神方位
   fu_position = lunar.getDayPositionFu()   # 返回福神方位
   fu_desc = lunar.getDayPositionFuDesc()   # 返回福神方位描述
   
   # 获取财神方位
   cai_position = lunar.getDayPositionCai() # 返回财神方位
   cai_desc = lunar.getDayPositionCaiDesc() # 返回财神方位描述
   
   # 获取吉神凶煞
   ji_shen = lunar.getDayJiShen()           # 返回吉神列表
   xiong_sha = lunar.getDayXiongSha()       # 返回凶煞列表
   ```

5. **获取彭祖百忌**：
   ```python
   # 获取彭祖百忌
   peng_zu_gan = lunar.getPengZuGan()       # 返回天干百忌
   peng_zu_zhi = lunar.getPengZuZhi()       # 返回地支百忌
   ```

6. **获取节气和节日**：
   ```python
   # 获取节气
   jie_qi = lunar.getJieQi()                # 返回节气名称，如无则返回None
   
   # 获取农历节日
   lunar_festivals = lunar.getFestivals()   # 返回农历节日列表
   
   # 获取阳历节日
   solar_festivals = solar.getFestivals()   # 返回阳历节日列表
   ```
  </rewritten_file> 