import json
from datetime import datetime
import requests
import traceback
from openai import OpenAI
import time

class LunMing:
    """论命功能类，处理八字命理分析"""
    
    def __init__(self):
        """初始化论命功能"""
        # 可以在这里添加初始化代码，如加载配置等
        pass
    
    def generate_prompt(self, name, gender, birth_date, birth_time):
        """
        生成提示词
        
        参数:
        name (str): 用户姓名
        gender (str): 性别，'男'或'女'
        birth_date (str): 出生日期，格式为'YYYY-MM-DD'
        birth_time (str): 出生时间，可能是'HH:MM'或地支字符如'子'
        
        返回:
        str: 生成的提示词
        """
        try:
            # 地支到时间段的映射
            time_map = {
                '子': '23:00-01:00',
                '丑': '01:00-03:00',
                '寅': '03:00-05:00',
                '卯': '05:00-07:00',
                '辰': '07:00-09:00',
                '巳': '09:00-11:00',
                '午': '11:00-13:00',
                '未': '13:00-15:00',
                '申': '15:00-17:00',
                '酉': '17:00-19:00',
                '戌': '19:00-21:00',
                '亥': '21:00-23:00'
            }
            
            # 检查birth_time是否为地支字符
            time_display = birth_time
            if birth_time in time_map:
                time_display = f"{birth_time}时 ({time_map[birth_time]})"
            
            # 这里不再尝试解析日期时间，而是直接使用原始的日期和时间值
            print(f"生成提示词：日期={birth_date}, 时间={birth_time}, 显示时间={time_display}")
            
            # 格式化提示词
            prompt = f"""
            请根据以下信息，进行八字命理分析：
            
            姓名：{name}
            性别：{gender}
            出生日期：{birth_date}
            出生时辰：{time_display}
            
            # 请根据以下原则进行分析：
            # 1. 以传统八字命理为基础，结合现代命理学，利用传统文化中既有的象征体系建立信任感。
            # 2. 通过星座/生肖性格模板，调用跨文化原型数据库，组合不同体系的共性描述
            # 3. 结合社会学数据，对特定年龄层共性经历进行推测
            # 4. 利用巴纳姆效应、正例谬误等心理学效应，增加分析的可信度
            # 5. 运用开放性话术工程，增加分析的趣味性
            # 6. 结合个性化故事算法，增加分析的个性化
            # 7. 使用"你"作为第一人称，增加亲和力


            请提供以下内容：
            1. 八字命盘：年柱、月柱、日柱、时柱的天干地支
            2. 命理特征：五行分析、日主强弱、喜用神
            3. 大运走势：十年大运分析
            4. 性格特点：根据八字看性格优缺点
            5. 事业财运：适合的事业方向和财运分析
            6. 健康状况：可能的健康隐患和保健建议
            7. 人际关系：家庭、朋友和社交关系分析
            8. 建议：根据命理特点的生活建议和注意事项
            
            请用专业但通俗易懂的语言进行分析，避免过于迷信的表述，强调命运可以通过自身努力改变。
            """
            
            return prompt.strip()
            
        except Exception as e:
            print(f"生成提示词时出错: {str(e)}")
            return "生成提示词时出错，请检查输入信息是否正确。"
    
    def analyze_bazi(self, name, gender, birth_date, birth_time):
        """
        流式输出八字分析结果
        
        参数:
        name (str): 用户姓名
        gender (str): 性别，'男'或'女'
        birth_date (str): 出生日期，格式为'YYYY-MM-DD'
        birth_time (str): 出生时辰，地支字符如'子'、'丑'等
        
        返回:
        generator: 生成器对象，用于流式输出分析结果
        """
        try:
            print(f"开始分析八字：姓名={name}, 性别={gender}, 日期={birth_date}, 时辰={birth_time}")
            
            # 生成提示词
            prompt = self.generate_prompt(name, gender, birth_date, birth_time)
            print(f"准备进行流式分析，提示词长度: {len(prompt)}")
            print(f"提示词内容: {prompt[:100]}...")  # 打印提示词的前100个字符
            
            # 调用AI模型进行流式输出
            print("尝试连接AI API...")
            
            # 使用全局导入的OpenAI
            print(f"检查全局OpenAI是否已导入")
            
            # 尝试创建客户端
            try:
                print("创建OpenAI客户端...")
                client = OpenAI(
                    api_key="sk-7021b97fae804957ae20727a3f1fd95a",
                    base_url="https://api.deepseek.com"
                )
                print("成功创建OpenAI客户端")
            except Exception as ce:
                print(f"创建OpenAI客户端失败: {str(ce)}")
                import traceback
                print(f"堆栈跟踪: {traceback.format_exc()}")
                # 返回错误信息
                error_msg = f"创建API客户端失败: {str(ce)}"
                for char in error_msg:
                    yield char
                return
            
            # 尝试发送请求
            try:
                print("开始发送API请求...")
                print(f"使用模型: deepseek-chat")
                print(f"温度设置: 0.7")
                print(f"提示词长度: {len(prompt)}")
                start_time = time.time()
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ],
                    temperature=0.7,
                    stream=True
                )
                print("API请求已发送，等待响应...")
                first_response_time = time.time()
                print(f"初始响应耗时: {first_response_time - start_time}秒")
            except Exception as se:
                print(f"发送API请求失败: {str(se)}")
                error_msg = f"API请求失败: {str(se)}"
                for char in error_msg:
                    yield char
                
                import traceback
                print(f"API请求失败详细错误: {traceback.format_exc()}")
                return
                
            print("开始流式输出...")
            output_started = False
            try:
                for chunk in stream:
                    if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                        if chunk.choices[0].delta.content:
                            output_started = True
                            content = chunk.choices[0].delta.content
                            # 一个字符一个字符地返回
                            for char in content:
                                yield char
            except Exception as e:
                print(f"处理API响应时出错: {str(e)}")
                error_msg = f"\n处理API响应出错: {str(e)}"
                for char in error_msg:
                    yield char
                        
                import traceback
                print(f"处理API响应失败详细错误: {traceback.format_exc()}")
        except Exception as e:
            print(f"流式分析八字命理时出错: {str(e)}")
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            error_msg = f"分析出错: {str(e)}"
            for char in error_msg:
                yield char

    def call_ai_model(self, user_message,system_prompt=None,temperature: float = 1.0):
        bailian={'API_KEY': "sk-790941ba780748ec88e4f5145760fbae",'base_url':'https://dashscope.aliyuncs.com/compatible-mode/v1','model_name':"deepseek-r1"}
        siliconflow={'API_KEY': 'sk-euvzhodijzncpfdjgecohoviqiomawrmrxottyokhlmnxzcp','base_url':'https://api.siliconflow.cn/v1','model_name':"deepseek-ai/DeepSeek-R1"}
        deepseek={
            'API_KEY': 'sk-7021b97fae804957ae20727a3f1fd95a',
            'base_url':'https://api.deepseek.com',
            'model_name':"deepseek-reasoner"
}
        organations={'bailian':bailian,'siliconflow':siliconflow,'deepseek':deepseek}
        organation=deepseek
        client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=organation['API_KEY'],
        base_url=organation['base_url'],)

        reasoning_content = ""  # 定义完整思考过程
        answer_content = ""     # 定义完整回复
        is_answering = False   # 判断是否结束思考过程并开始回复
        # 逐步获取响应内容
        stream = client.chat.completions.create(
            model=organation['model_name'],
            messages=[
                # {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            temperature=temperature,
            stream=True,
            # 解除以下注释会在最后一个chunk返回Token使用量
            stream_options={
                "include_usage": True
            }
        )
        print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

        for chunk in stream:
            # 处理usage信息
            if not getattr(chunk, 'choices', None):
                print("\n" + "=" * 20 + "Token 使用情况" + "=" * 20 + "\n")
                print(chunk.usage)
                continue

            delta = chunk.choices[0].delta

            # 检查是否有reasoning_content属性
            if not hasattr(delta, 'reasoning_content'):
                continue

            # 处理空内容情况
            if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None):
                continue

            # 处理开始回答的情况
            if not getattr(delta, 'reasoning_content', None) and not is_answering:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True

            # 处理思考过程
            if getattr(delta, 'reasoning_content', None):
                print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            # 处理回复内容
            elif getattr(delta, 'content', None):
                print(delta.content, end='', flush=True)
                answer_content += delta.content


        # 如果需要打印完整内容，解除以下的注释
        # print("=" * 20 + "完整思考过程" + "=" * 20 + "\n")
        # print(reasoning_content)
        # print("=" * 20 + "完整回复" + "=" * 20 + "\n")
        # print(answer_content)

        return answer_content
