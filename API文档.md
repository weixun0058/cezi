# 诸葛神算微信小程序 API 文档

根据提供的源代码，以下是完整的 API 文档，包含所有端点、参数和响应格式。

## 目录

1. [基础信息](#基础信息)
2. [黄历相关 API](#黄历相关-api)
   - [获取每日黄历](#获取每日黄历)
   - [获取九天黄历](#获取九天黄历)
   - [获取彭祖百忌解释](#获取彭祖百忌解释)
3. [算事相关 API](#算事相关-api)
   - [获取汉字笔画数](#获取汉字笔画数)
   - [计算签号](#计算签号)
   - [获取卦象信息](#获取卦象信息)
4. [论命相关 API](#论命相关-api)
   - [分析八字命理](#分析八字命理)
   - [流式输出八字分析](#流式输出八字分析)

## 基础信息

- **基础 URL**: `https://您的服务器地址`
- **请求方式**: 主要使用 GET 和 POST 方法
- **响应格式**: 所有 API 返回 JSON 格式数据
- **错误处理**: 错误返回时会包含 `success` 和 `message` 字段

## 黄历相关 API

### 获取每日黄历

获取指定日期的黄历信息，包括宜忌、神煞、彭祖百忌等。

- **URL**: `/api/huangli`
- **方法**: `GET`
- **参数**:
  
  | 参数 | 类型 | 必填 | 描述 |
  |-----|-----|-----|-----|
  | date | string | 否 | 日期，格式为 YYYY-MM-DD，不提供则使用当前日期 |

- **成功响应**:
  ```json
  {
    "success": true,
    "data": {
      "date": "2023-05-01",
      "lunar_date": "三月十二",
      "gan_zhi_year": "癸卯年",
      "gan_zhi_month": "乙巳月",
      "gan_zhi_day": "丙午日",
      "gan_zhi_hour": "丁巳时",
      "zodiac": "兔年",
      "suitable": "祭祀、祈福、求嗣、开光、出行、解除、伐木、作梁",
      "unsuitable": "嫁娶、动土、安葬、入宅、开市、破土",
      "chong_sha": "冲鼠(甲子)煞北",
      "ji_shen": "天德、月德、天赦、天巫",
      "xiong_shen": "月煞、土府、月建、天刑",
      "peng_zu_bai_ji": "丙不修灶必见灾殃，午不苫盖屋主更张",
      "xi_shen": "东南(巳)",
      "fu_shen": "正北(子)",
      "cai_shen": "正南(午)",
      "solar_term": "立夏",
      "prev_solar_term": "谷雨",
      "prev_solar_term_days": 15,
      "next_solar_term": "小满",
      "next_solar_term_days": 15,
      "formatted_solar_term_info": "谷雨(15天前) --- 立夏(今日) --- 小满(还有15天)",
      "festivals": [
        {"name": "国际劳动节", "type": "阳历节日"}
      ]
    }
  }
  ```

- **错误响应**:
  ```json
  {
    "success": false,
    "message": "日期格式无效，请使用YYYY-MM-DD格式"
  }
  ```

### 获取九天黄历

获取包括前2天、今天和后6天的黄历概要信息，共9天数据。

- **URL**: `/api/week_huangli`
- **方法**: `GET`
- **参数**: 无

- **成功响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "date": "2023-04-29",
        "lunar_date": "三月十",
        "gan_zhi_day": "甲辰日",
        "gan_zhi_hour": "丁巳时",
        "suitable": "祭祀、沐浴、理发、整手足甲、解除",
        "unsuitable": "嫁娶、入宅、安床、上梁、作灶",
        "chong_sha": "冲猴(戊申)煞北",
        "peng_zu_bai_ji": "甲不开仓财物耗散，辰不哭泣必主重丧",
        "xi_shen": "西南(申)",
        "fu_shen": "正南(午)",
        "cai_shen": "正北(子)",
        "solar_term": "无"
      },
      // ... 更多天数数据
    ]
  }
  ```

- **错误响应**:
  ```json
  {
    "success": false,
    "message": "获取一周黄历数据时出错: 具体错误信息"
  }
  ```

### 获取彭祖百忌解释

获取彭祖百忌文本的详细解释。

- **URL**: `/api/pzbj_explanation`
- **方法**: `GET`
- **参数**:
  
  | 参数 | 类型 | 必填 | 描述 |
  |-----|-----|-----|-----|
  | text | string | 是 | 彭祖百忌文本，如"丙不修灶必见灾殃" |

- **成功响应**:
  ```json
  {
    "success": true,
    "explanation": "丙日不宜修灶，传统认为会带来灾祸。修灶在古代是一件重要的家事，灶王爷是司命之神，丙日火旺，若在此日修灶可能引发火灾或其他不幸。"
  }
  ```

- **错误响应**:
  ```json
  {
    "success": false,
    "message": "未找到对应解释"
  }
  ```

## 算事相关 API

### 获取汉字笔画数

获取单个汉字的康熙笔画数。

- **URL**: `/get_strokes`
- **方法**: `POST`
- **参数** (JSON):
  ```json
  {
    "character": "诸"
  }
  ```

- **成功响应**:
  ```json
  {
    "strokes": 10
  }
  ```

### 计算签号

根据三个汉字的笔画数计算对应的签号。

- **URL**: `/calculate_sign`
- **方法**: `POST`
- **参数** (JSON):
  ```json
  {
    "strokes": [10, 15, 8]
  }
  ```

- **成功响应**:
  ```json
  {
    "sign_number": 158
  }
  ```

### 获取卦象信息

根据签号获取对应的卦象信息和解释。

- **URL**: `/get_gua_info`
- **方法**: `POST`
- **参数** (JSON):
  ```json
  {
    "sign_number": 158
  }
  ```

- **成功响应**:
  ```json
  {
    "sign_text": "同心之言，信者必从。疑者必拒，好事多磨，耐守以成。",
    "gua_type": "大有卦",
    "fortune": "上上",
    "interpretation1": "初起亨通，因事多波折，最后圆满成功。",
    "career": "你的事业正处于发展阶段，虽有阻力，但最终能获得成功。",
    "wealth": "财运顺利，收入稳定，但要提防意外支出。",
    "love": "感情上遇到阻碍，需要耐心沟通，共同克服困难。",
    "health": "身体状况良好，但注意劳逸结合，避免过度疲劳。",
    "study": "学习上需要加倍努力，克服困难后会有好成绩。",
    "general": "整体运势良好，但需要耐心和坚持，不要轻易放弃。"
  }
  ```

- **错误响应**:
  ```json
  {
    "error": "未找到对应的卦象信息",
    "sign_text": "暂无签文",
    "gua_type": "未知",
    "fortune": "未知",
    "interpretation1": "暂无解签",
    "career": "暂无解签",
    "wealth": "暂无解签",
    "love": "暂无解签",
    "health": "暂无解签",
    "study": "暂无解签",
    "general": "暂无解签"
  }
  ```

## 论命相关 API

### 分析八字命理

根据用户生辰信息进行八字命理分析。

- **URL**: `/api/lunming/analyze`
- **方法**: `POST`
- **参数** (JSON):
  ```json
  {
    "name": "张三",
    "gender": "男",
    "birth_date": "1990-05-01",
    "birth_time": "子"
  }
  ```
  > 注意：birth_time 可以是地支字符如"子"、"丑"等，也可以是"unknown"表示未知

- **成功响应**:
  ```json
  {
    "success": true,
    "data": {
      "prompt": "生成的提示词内容",
      "analysis": "完整的八字分析结果"
    }
  }
  ```

- **错误响应**:
  ```json
  {
    "success": false,
    "message": "请提供完整的姓名、性别、出生日期和时间"
  }
  ```

### 流式输出八字分析

使用 Server-Sent Events (SSE) 方式流式输出八字分析结果，适用于长文本生成场景。

- **URL**: `/api/lunming/stream`
- **方法**: `GET`
- **参数**:
  
  | 参数 | 类型 | 必填 | 描述 |
  |-----|-----|-----|-----|
  | name | string | 否 | 用户姓名 |
  | gender | string | 否 | 性别，默认为"男" |
  | birth_date | string | 是 | 出生日期，格式为 YYYY-MM-DD |
  | birth_time | string | 否 | 出生时辰，地支字符如"子"，或"unknown" |

- **成功响应**: 
  使用 Server-Sent Events 流式返回文本内容，客户端需要使用对应的 EventSource 接收。

  每个事件格式为：
  ```
  data: {"text": "分析内容片段"}
  ```

  分析完成时会发送：
  ```
  data: {"done": true}
  ```

- **错误响应**:
  ```
  data: {"error": "分析过程没有产生任何结果，请重试"}
  data: {"done": true}
  ```

## 使用示例

### 微信小程序获取黄历数据

```javascript
// 获取当日黄历
wx.request({
  url: 'https://您的服务器地址/api/huangli',
  method: 'GET',
  success(res) {
    if (res.data.success) {
      const huangliData = res.data.data;
      // 处理黄历数据
      console.log(huangliData);
    } else {
      wx.showToast({
        title: res.data.message,
        icon: 'none'
      });
    }
  },
  fail(err) {
    console.error('请求失败', err);
  }
});
```

### 微信小程序进行算事

```javascript
// 步骤1：获取三个汉字的笔画
function getStrokes(characters) {
  const promises = characters.map(char => {
    return new Promise((resolve) => {
      wx.request({
        url: 'https://您的服务器地址/get_strokes',
        method: 'POST',
        data: { character: char },
        success(res) {
          resolve(res.data.strokes);
        },
        fail() {
          resolve(1); // 失败时默认为1
        }
      });
    });
  });
  
  return Promise.all(promises);
}

// 步骤2：计算签号
function calculateSign(strokes) {
  return new Promise((resolve) => {
    wx.request({
      url: 'https://您的服务器地址/calculate_sign',
      method: 'POST',
      data: { strokes: strokes },
      success(res) {
        resolve(res.data.sign_number);
      },
      fail() {
        resolve(null);
      }
    });
  });
}

// 步骤3：获取卦象信息
function getGuaInfo(signNumber) {
  return new Promise((resolve) => {
    wx.request({
      url: 'https://您的服务器地址/get_gua_info',
      method: 'POST',
      data: { sign_number: signNumber },
      success(res) {
        resolve(res.data);
      },
      fail() {
        resolve(null);
      }
    });
  });
}

// 组合使用
async function calculateDivination(name) {
  const characters = name.split('').slice(0, 3);
  if (characters.length < 3) {
    wx.showToast({
      title: '请输入至少三个汉字',
      icon: 'none'
    });
    return;
  }
  
  try {
    // 获取笔画数
    const strokes = await getStrokes(characters);
    // 计算签号
    const signNumber = await calculateSign(strokes);
    if (!signNumber) {
      wx.showToast({
        title: '计算签号失败',
        icon: 'none'
      });
      return;
    }
    
    // 获取卦象解释
    const guaInfo = await getGuaInfo(signNumber);
    if (!guaInfo) {
      wx.showToast({
        title: '获取卦象信息失败',
        icon: 'none'
      });
      return;
    }
    
    // 展示结果
    displayResult(guaInfo);
  } catch (error) {
    console.error('占卜过程出错', error);
  }
}
```

### 微信小程序进行论命分析

```javascript
// 使用流式API进行八字分析
function streamBaziAnalysis(name, gender, birthDate, birthTime) {
  // 构建URL
  const url = `https://您的服务器地址/api/lunming/stream?name=${encodeURIComponent(name)}&gender=${encodeURIComponent(gender)}&birth_date=${encodeURIComponent(birthDate)}&birth_time=${encodeURIComponent(birthTime)}`;
  
  let buffer = '';
  let analysisResult = '';
  
  // 创建结果显示函数
  function updateAnalysisContent(content) {
    // 在小程序中更新内容
    // 例如：this.setData({ analysisContent: content });
    console.log('分析内容更新:', content);
  }
  
  // 微信小程序没有原生的EventSource，需要使用自定义实现
  // 这里使用轮询方式模拟
  function fetchNextChunk(url, offset) {
    wx.request({
      url: `${url}&offset=${offset}`,
      method: 'GET',
      success(res) {
        if (res.data && res.data.text) {
          analysisResult += res.data.text;
          updateAnalysisContent(analysisResult);
          
          // 如果没有完成，继续获取下一段
          if (!res.data.done) {
            fetchNextChunk(url, offset + res.data.text.length);
          }
        } else if (res.data && res.data.done) {
          console.log('分析完成');
        } else if (res.data && res.data.error) {
          wx.showToast({
            title: res.data.error,
            icon: 'none'
          });
        }
      },
      fail(err) {
        console.error('获取分析结果失败', err);
      }
    });
  }
  
  // 开始获取第一段
  fetchNextChunk(url, 0);
}

// 调用示例
streamBaziAnalysis('张三', '男', '1990-05-01', '子');
```

## 注意事项

1. 所有请求应该添加合适的错误处理
2. 流式输出API需要特殊处理，微信小程序需要自行实现类似EventSource的功能
3. 在微信小程序中，需要在app.json中配置服务器域名为可信任域名
4. 可能需要考虑用户授权、登录等微信特有功能
5. 响应较大的数据时可能需要分页或压缩处理
