from flask import Flask, request, jsonify, render_template,url_for, Response
from database import Database
from utils import cale_character_count, num_to_chinese_upper
from huangli import HuangLi
from lunming import LunMing
from datetime import datetime, timedelta
import json
import traceback
import time

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
db = Database()
huangli = HuangLi()
lunming = LunMing()

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
            return jsonify({'success': False, 'message': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
        
        # 获取黄历数据
        huangli_data = huangli.get_daily_huangli(date_str)
        
        if not huangli_data:
            print(f"无法获取黄历数据: {date_str}")
            return jsonify({'success': False, 'message': '无法获取黄历数据'}), 404
        
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
        return jsonify({'success': True, 'data': huangli_data})
        
    except Exception as e:
        print(f"获取黄历数据时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'获取黄历数据时出错: {str(e)}'}), 500

@app.route('/api/week_huangli', methods=['GET'])
def get_week_huangli():
    """获取一周黄历数据"""
    try:
        # 获取一周黄历数据
        week_data = huangli.get_week_huangli()
        
        if not week_data:
            print("无法获取一周黄历数据")
            return jsonify({'success': False, 'message': '无法获取一周黄历数据'}), 404
        
        print(f"成功获取一周黄历数据，共{len(week_data)}天")
        return jsonify({'success': True, 'data': week_data})
        
    except Exception as e:
        print(f"获取一周黄历数据时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'获取一周黄历数据时出错: {str(e)}'}), 500

@app.route('/api/lunming/analyze', methods=['POST'])
def analyze_bazi():
    """分析八字命理API"""
    try:
        data = request.json
        name = data.get('name', '')
        gender = data.get('gender', '男')
        birth_date = data.get('birth_date', '')
        birth_time = data.get('birth_time', '')
        
        print(f"收到八字分析请求: 姓名={name}, 性别={gender}, 出生日期={birth_date}, 出生时间={birth_time}")
        
        # 验证输入
        if not name or not birth_date or not birth_time:
            print("输入数据不完整")
            return jsonify({
                'success': False, 
                'message': '请提供完整的姓名、性别、出生日期和时间'
            }), 400
        
        # 调用论命功能进行分析
        result = lunming.analyze_bazi(name, gender, birth_date, birth_time)
        
        if not result.get('success', False):
            print(f"八字分析失败: {result.get('error', '未知错误')}")
            return jsonify({
                'success': False,
                'message': result.get('error', '分析失败，请稍后再试')
            }), 500
        
        print(f"八字分析成功")
        return jsonify({
            'success': True,
            'data': {
                'prompt': result.get('prompt', ''),
                'analysis': result.get('analysis', '')
            }
        })
        
    except Exception as e:
        print(f"处理八字分析请求时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@app.route('/api/lunming/stream', methods=['GET'])
def stream_bazi_analysis():
    """流式输出八字分析结果API"""
    try:
        # 从查询参数中获取数据
        name = request.args.get('name', '')
        gender = request.args.get('gender', '男')
        birth_date = request.args.get('birth_date', '')
        birth_time = request.args.get('birth_time', '')
        
        print(f"收到八字分析流式请求: 姓名={name}, 性别={gender}, 出生日期={birth_date}, 出生时间={birth_time}")
        
        # 验证输入
        if not name or not birth_date or not birth_time:
            return jsonify({
                'success': False, 
                'message': '请提供完整的姓名、性别、出生日期和时间'
            }), 400
            
        def generate():
            try:
                # 使用全局的lunming实例
                print("开始生成分析结果...")
                
                # 先发送一个开始信号
                print("发送开始信号...")
                yield f"data: {json.dumps({'text': '正在分析，请稍候...'})}\n\n"
                
                # 使用修改后的analyze_bazi方法
                print("开始调用analyze_bazi方法...")
                chars_count = 0
                for char in lunming.analyze_bazi(name, gender, birth_date, birth_time):
                    if char:
                        chars_count += 1
                        # 确保每个字符都被单独发送
                        if chars_count % 10 == 0:  # 每10个字符打印一次日志，减少日志量
                            print(f"已发送{chars_count}个字符", flush=True)
                        json_data = json.dumps({'text': char})
                        yield f"data: {json_data}\n\n"
                        # 强制刷新
                        if hasattr(generate, 'flush'):
                            generate.flush()
                
                # 检查是否有字符输出
                if chars_count == 0:
                    print("警告：没有收到任何字符输出")
                    yield f"data: {json.dumps({'error': '分析过程没有产生任何结果，请重试'})}\n\n"
                else:
                    print(f"成功发送了{chars_count}个字符")
                
                # 发送完成信号
                print("分析完成，发送完成信号")
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                print(f"生成分析结果时出错: {str(e)}")
                import traceback
                error_traceback = traceback.format_exc()
                print(f"错误堆栈: {error_traceback}")
                # 发送错误信息
                detailed_error = f"生成分析结果时出错: {str(e)}"
                yield f"data: {json.dumps({'error': detailed_error})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
        
        # 设置响应头，禁用缓冲
        response = Response(generate(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
        response.headers['Connection'] = 'keep-alive'
        return response
        
    except Exception as e:
        print(f"处理流式请求时出错: {str(e)}")
        traceback.print_exc()  # 打印完整的错误堆栈
        return jsonify({
            'success': False,
            'message': f'处理请求时出错: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)