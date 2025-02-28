from flask import Flask, request, jsonify, render_template,url_for
from database import Database
from utils import cale_character_count, num_to_chinese_upper
from huangli import HuangLi
from datetime import datetime, timedelta

app = Flask(__name__)
db = Database()
huangli = HuangLi()

@app.route('/')
def index():
    """主页 - 黄历页面"""
    return render_template('huangli.html')

@app.route('/suanshi')
def suanshi_page():
    """算事页面 - 原诸葛神算功能"""
    return render_template('suanshi.html')

@app.route('/lunming')
def lunming_page():
    """论命页面 - 待开发功能"""
    return render_template('lunming.html')

@app.route('/get_strokes', methods=['POST'])
def get_strokes():
    try:
        char = request.json['character']
        print(f"收到笔画查询请求: {char}")
        
        strokes = db.get_stroke_count(char)
        print(f"查询到的笔画数: {strokes}")
        
        if strokes is None or strokes < 1:
            print(f"笔画数无效，使用默认值1")
            strokes = 1
            
        return jsonify({'strokes': strokes})
    except Exception as e:
        print(f"笔画查询出错: {str(e)}")
        return jsonify({'strokes': 1})

@app.route('/calculate_sign', methods=['POST'])
def calculate_sign():
    strokes = request.json['strokes']
    sign_number = cale_character_count(*strokes)
    return jsonify({'sign_number': sign_number})

@app.route('/get_gua_info', methods=['POST'])
def get_gua_info():
    try:
        sign_number = request.json['sign_number']
        print(f"接收到签号: {sign_number}")
        
        if not isinstance(sign_number, int) or sign_number < 1 or sign_number > 383:
            print(f"签号 {sign_number} 超出有效范围")
            return jsonify({
                'error': '无效的签号',
                'sign_text': '暂无签文',
                'gua_type': '未知',
                'fortune': '未知',
                'interpretation1': '暂无解签',
                'career': '暂无解签',
                'wealth': '暂无解签',
                'love': '暂无解签',
                'health': '暂无解签',
                'study': '暂无解签',
                'general': '暂无解签'
            })
        
        gua_info = db.get_gua_info(sign_number)
        print(f"获取到卦象信息: {gua_info}")
        
        if gua_info is None:
            return jsonify({
                'error': '未找到对应的卦象信息',
                'sign_text': '暂无签文',
                'gua_type': '未知',
                'fortune': '未知',
                'interpretation1': '暂无解签',
                'career': '暂无解签',
                'wealth': '暂无解签',
                'love': '暂无解签',
                'health': '暂无解签',
                'study': '暂无解签',
                'general': '暂无解签'
            })
        
        response = {
            'sign_text': gua_info[4],    # 签文
            'gua_type': gua_info[3],     # 卦属
            'fortune': gua_info[2],      # 吉凶
            'interpretation1': gua_info[5],  # 解签一
            'career': gua_info[6],       # 事业
            'wealth': gua_info[7],       # 财运
            'love': gua_info[8],         # 情感
            'health': gua_info[9],       # 健康
            'study': gua_info[10],       # 学业
            'general': gua_info[11]      # 泛泛
        }
        print(f"返回数据: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"处理卦象信息时出错: {str(e)}")
        return jsonify({
            'error': '处理卦象信息时出错',
            'sign_text': '暂无签文',
            'gua_type': '未知',
            'fortune': '未知',
            'interpretation1': '暂无解签',
            'career': '暂无解签',
            'wealth': '暂无解签',
            'love': '暂无解签',
            'health': '暂无解签',
            'study': '暂无解签',
            'general': '暂无解签'
        })
    

# @app.route('/image-url')
# def image_url():
#     # 使用 url_for 函数生成图片的 URL
#     image_url = url_for('static', filename='static/images/ancient-bg.jpg')
#     return f'The URL of the image is: <a href="{image_url}">{image_url}</a>'

@app.route('/huangli')
def huangli_page():
    """黄历页面 - 为了兼容旧链接"""
    return render_template('huangli.html')

@app.route('/api/huangli', methods=['GET'])
def get_huangli():
    """获取黄历API"""
    date_str = request.args.get('date')
    
    # 如果没有提供日期，使用当前日期
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 验证日期格式
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # 获取黄历数据
        huangli_data = huangli.get_daily_huangli(date_str)
        
        if not huangli_data:
            return jsonify({'error': '无法获取黄历数据'}), 404
        
        # 获取节气信息
        solar_term = huangli.get_solar_term(date_str)
        
        # 获取节日信息
        festivals = huangli.get_festivals(date_str)
        
        # 直接返回黄历数据，添加节气和节日信息
        huangli_data['solar_term'] = solar_term
        huangli_data['festivals'] = festivals
        
        return jsonify(huangli_data)
        
    except ValueError:
        return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
    except Exception as e:
        return jsonify({'error': f'获取黄历数据时出错: {str(e)}'}), 500

@app.route('/api/huangli/week', methods=['GET'])
def get_week_huangli():
    """获取一周黄历数据"""
    try:
        today = datetime.now()
        week_data = []
        
        # 获取今天和未来6天的数据
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            huangli_data = huangli.get_daily_huangli(date_str)
            if huangli_data:
                # 简化数据，只返回关键信息
                simplified_data = {
                    'date': date_str,
                    'lunar_date': huangli_data['lunar_date'],
                    'suitable': huangli_data['suitable'],
                    'unsuitable': huangli_data['unsuitable'],
                    'day_fortune': huangli_data['day_fortune']
                }
                week_data.append(simplified_data)
        
        return jsonify(week_data)
        
    except Exception as e:
        return jsonify({'error': f'获取一周黄历数据时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)