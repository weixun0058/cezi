from flask import Flask, request, jsonify, render_template,url_for
from database import Database
from utils import cale_character_count, num_to_chinese_upper
from huangli import HuangLi
from datetime import datetime, timedelta
import json

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

@app.route('/huangli')
def huangli_page():
    """黄历页面"""
    return render_template('huangli.html')

@app.route('/api/huangli', methods=['GET'])
def get_huangli():
    """获取黄历API"""
    try:
        date_str = request.args.get('date')
        
        # 如果没有提供日期，使用当前日期
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        print(f"获取黄历数据: {date_str}")
        
        # 验证日期格式
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"日期格式无效: {date_str}")
            return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
        
        # 获取黄历数据
        huangli_data = huangli.get_daily_huangli(date_str)
        
        if not huangli_data:
            print(f"无法获取黄历数据: {date_str}")
            return jsonify({'error': '无法获取黄历数据'}), 404
        
        # 如果festivals是JSON字符串，将其转换为Python对象
        if isinstance(huangli_data.get('festivals'), str):
            try:
                huangli_data['festivals'] = json.loads(huangli_data['festivals'])
            except:
                huangli_data['festivals'] = []
        
        print(f"成功获取黄历数据: {date_str}")
        print(f"彭祖百忌: {huangli_data.get('peng_zu_bai_ji', '无')}")
        print(f"喜神: {huangli_data.get('xi_shen', '无')}")
        print(f"福神: {huangli_data.get('fu_shen', '无')}")
        print(f"财神: {huangli_data.get('cai_shen', '无')}")
        return jsonify(huangli_data)
        
    except Exception as e:
        print(f"获取黄历数据时出错: {str(e)}")
        return jsonify({'error': f'获取黄历数据时出错: {str(e)}'}), 500

@app.route('/api/huangli/week', methods=['GET'])
def get_week_huangli():
    """获取一周黄历数据"""
    try:
        # 获取一周黄历数据
        week_data = huangli.get_week_huangli()
        
        if not week_data:
            print("无法获取一周黄历数据")
            return jsonify({'error': '无法获取一周黄历数据'}), 404
        
        print(f"成功获取一周黄历数据，共{len(week_data)}天")
        return jsonify(week_data)
        
    except Exception as e:
        print(f"获取一周黄历数据时出错: {str(e)}")
        return jsonify({'error': f'获取一周黄历数据时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)