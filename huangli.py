import sqlite3
from datetime import datetime, timedelta
import json
# 修改导入语句，只导入实际存在的类
from lunar_python import Lunar, Solar, LunarYear

class HuangLi:
    def __init__(self, db_path="database/huangli.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建黄历表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS huangli_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            lunar_date TEXT,
            gan_zhi_year TEXT,
            gan_zhi_month TEXT,
            gan_zhi_day TEXT,
            zodiac TEXT,
            suitable TEXT,
            unsuitable TEXT,
            lucky_direction TEXT,
            lucky_color TEXT,
            lucky_number TEXT,
            chong_sha TEXT,
            ji_shen TEXT,
            xiong_shen TEXT,
            day_fortune TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_daily_huangli(self, date=None):
        """获取指定日期的黄历信息，如果不存在则从lunar_python库获取"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询数据库中是否已有该日期的黄历
        cursor.execute("SELECT * FROM huangli_daily WHERE date = ?", (date,))
        result = cursor.fetchone()
        
        if result:
            # 将查询结果转换为字典
            columns = [col[0] for col in cursor.description]
            huangli_data = dict(zip(columns, result))
            conn.close()
            return huangli_data
        else:
            # 从lunar_python库获取黄历数据
            huangli_data = self._generate_huangli_from_lunar(date)
            if huangli_data:
                # 保存到数据库
                self._save_huangli_to_db(huangli_data)
                conn.close()
                return huangli_data
            
            conn.close()
            return None
    
    def _generate_huangli_from_lunar(self, date_str):
        """使用lunar_python库生成黄历数据"""
        try:
            # 解析日期字符串为年月日
            year, month, day = map(int, date_str.split('-'))
            
            # 创建阳历日期对象
            solar = Solar.fromYmd(year, month, day)
            
            # 转换为农历日期对象
            lunar = solar.getLunar()
            
            # 获取农历年、月、日
            lunar_year = lunar.getYear()
            lunar_month = lunar.getMonth()
            lunar_day = lunar.getDay()
            
            # 获取农历日期字符串
            lunar_date = f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
            
            # 获取天干地支
            gan_zhi_year = lunar.getYearInGanZhi() + "年"
            gan_zhi_month = lunar.getMonthInGanZhi() + "月"
            gan_zhi_day = lunar.getDayInGanZhi() + "日"
            
            # 获取生肖
            zodiac = lunar.getYearShengXiao() + "年"
            
            # 获取节气信息
            solar_term = None
            # 使用 lunar_python 的正确方法获取节气
            jieqi = lunar.getJieQi()
            if jieqi:
                solar_term = {
                    'name': jieqi,
                    'description': self._get_solar_term_description(jieqi)
                }
            
            # 获取节日信息 - 由于没有 HolidayUtil，我们使用自定义方法
            festivals = self._get_festivals(year, month, day, lunar_year, lunar_month, lunar_day)
            
            # 获取每日宜忌（这部分需要自定义，lunar_python库不直接提供）
            # 这里使用日期的数值特征来生成伪随机的宜忌内容
            suitable, unsuitable = self._generate_daily_activities(year, month, day)
            
            # 获取冲煞
            chong_animal = lunar.getChong()
            chong_sha = f"冲{chong_animal}({lunar.getChongGan()})煞{lunar.getSha()}"
            
            # 获取吉神凶煞（这部分需要自定义，lunar_python库不直接提供）
            ji_shen, xiong_shen = self._generate_ji_xiong_shen(lunar)
            
            # 获取吉祥方位、颜色、数字（这部分需要自定义）
            lucky_direction, lucky_color, lucky_number = self._generate_lucky_info(lunar)
            
            # 获取当日运势（这部分需要自定义）
            day_fortune = self._generate_day_fortune(lunar)
            
            # 构建黄历数据字典
            huangli_data = {
                'date': date_str,
                'lunar_date': lunar_date,
                'gan_zhi_year': gan_zhi_year,
                'gan_zhi_month': gan_zhi_month,
                'gan_zhi_day': gan_zhi_day,
                'zodiac': zodiac,
                'suitable': suitable,
                'unsuitable': unsuitable,
                'lucky_direction': lucky_direction,
                'lucky_color': lucky_color,
                'lucky_number': lucky_number,
                'chong_sha': chong_sha,
                'ji_shen': ji_shen,
                'xiong_shen': xiong_shen,
                'day_fortune': day_fortune,
                'solar_term': solar_term,
                'festivals': festivals
            }
            
            return huangli_data
            
        except Exception as e:
            print(f"生成黄历数据出错: {str(e)}")
            return None
    
    def _get_festivals(self, year, month, day, lunar_year, lunar_month, lunar_day):
        """获取节日信息"""
        festivals = []
        
        # 农历节日
        lunar_festivals = self._get_lunar_festivals(lunar_month, lunar_day)
        if lunar_festivals:
            festivals.append({
                'name': lunar_festivals,
                'type': '农历节日',
                'description': self._get_festival_description(lunar_festivals)
            })
        
        # 阳历节日
        solar_festivals = self._get_solar_festivals(month, day)
        if solar_festivals:
            festivals.append({
                'name': solar_festivals,
                'type': '阳历节日',
                'description': self._get_festival_description(solar_festivals)
            })
        
        return festivals
    
    def _get_lunar_festivals(self, lunar_month, lunar_day):
        """获取农历节日"""
        festivals = {
            (1, 1): "春节",
            (1, 15): "元宵节",
            (5, 5): "端午节",
            (7, 7): "七夕节",
            (8, 15): "中秋节",
            (9, 9): "重阳节",
            (12, 8): "腊八节",
            (12, 23): "小年",
            (12, 30): "除夕"
        }
        
        return festivals.get((lunar_month, lunar_day))
    
    def _get_solar_festivals(self, month, day):
        """获取阳历节日"""
        festivals = {
            (1, 1): "元旦",
            (2, 14): "情人节",
            (3, 8): "妇女节",
            (3, 12): "植树节",
            (4, 1): "愚人节",
            (5, 1): "劳动节",
            (5, 4): "青年节",
            (6, 1): "儿童节",
            (9, 10): "教师节",
            (10, 1): "国庆节",
            (12, 25): "圣诞节"
        }
        
        return festivals.get((month, day))
    
    def _save_huangli_to_db(self, huangli_data):
        """保存黄历数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO huangli_daily 
        (date, lunar_date, gan_zhi_year, gan_zhi_month, gan_zhi_day, zodiac, 
        suitable, unsuitable, lucky_direction, lucky_color, lucky_number, 
        chong_sha, ji_shen, xiong_shen, day_fortune)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            huangli_data['date'],
            huangli_data['lunar_date'],
            huangli_data['gan_zhi_year'],
            huangli_data['gan_zhi_month'],
            huangli_data['gan_zhi_day'],
            huangli_data['zodiac'],
            huangli_data['suitable'],
            huangli_data['unsuitable'],
            huangli_data['lucky_direction'],
            huangli_data['lucky_color'],
            huangli_data['lucky_number'],
            huangli_data['chong_sha'],
            huangli_data['ji_shen'],
            huangli_data['xiong_shen'],
            huangli_data['day_fortune']
        ))
        
        conn.commit()
        conn.close()
    
    def get_week_huangli(self, start_date=None):
        """获取一周的黄历数据"""
        if start_date is None:
            start_date = datetime.now()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        week_data = []
        
        # 获取7天的数据
        for i in range(7):
            date = start_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            huangli_data = self.get_daily_huangli(date_str)
            if huangli_data:
                # 简化数据，只返回关键信息
                simplified_data = {
                    'date': date_str,
                    'lunar_date': huangli_data['lunar_date'],
                    'gan_zhi_day': huangli_data['gan_zhi_day'],
                    'suitable': huangli_data['suitable'].split('、')[0] if '、' in huangli_data['suitable'] else huangli_data['suitable'],
                    'unsuitable': huangli_data['unsuitable'].split('、')[0] if '、' in huangli_data['unsuitable'] else huangli_data['unsuitable'],
                    'day_fortune': huangli_data['day_fortune']
                }
                week_data.append(simplified_data)
        
        return week_data
    
    def _generate_daily_activities(self, year, month, day):
        """生成每日宜忌活动"""
        # 宜忌活动列表
        suitable_activities = [
            "祭祀", "祈福", "求嗣", "开光", "塑绘", "齐醮", "出行", "移徙", 
            "入宅", "安床", "安门", "安香", "出火", "拆卸", "动土", "修造", 
            "起基", "竖柱", "上梁", "合脊", "造庙", "造桥", "造船", "造车", 
            "开市", "交易", "立券", "纳财", "开仓", "求财", "开渠", "穿井", 
            "栽种", "纳畜", "牧养", "纳婿", "会亲友", "纳采", "订盟", "嫁娶", 
            "进人口", "裁衣", "安床", "冠笄", "修坟", "启钻", "破土", "安葬"
        ]
        
        unsuitable_activities = [
            "诸事不宜", "祭祀", "祈福", "求嗣", "开光", "塑绘", "齐醮", "出行", 
            "移徙", "入宅", "安床", "安门", "安香", "出火", "拆卸", "动土", 
            "修造", "起基", "竖柱", "上梁", "合脊", "造庙", "造桥", "造船", 
            "造车", "开市", "交易", "立券", "纳财", "开仓", "求财", "开渠", 
            "穿井", "栽种", "纳畜", "牧养", "纳婿", "会亲友", "纳采", "订盟", 
            "嫁娶", "进人口", "裁衣", "安床", "冠笄", "修坟", "启钻", "破土", "安葬"
        ]
        
        # 使用日期生成伪随机数
        seed = year * 10000 + month * 100 + day
        import random
        random.seed(seed)
        
        # 随机选择5-8个宜项
        suitable_count = random.randint(5, 8)
        suitable_list = random.sample(suitable_activities, suitable_count)
        
        # 随机选择3-6个忌项，确保不与宜项重复
        unsuitable_count = random.randint(3, 6)
        available_unsuitable = [item for item in unsuitable_activities if item not in suitable_list]
        unsuitable_list = random.sample(available_unsuitable, unsuitable_count)
        
        return "、".join(suitable_list), "、".join(unsuitable_list)
    
    def _generate_ji_xiong_shen(self, lunar):
        """生成吉神凶煞"""
        # 吉神列表
        ji_shen_list = [
            "天德", "月德", "天赦", "天愿", "三合", "六合", "天喜", "天医", 
            "司命", "月空", "不将", "要安", "玉堂", "金匮", "福德", "天马"
        ]
        
        # 凶煞列表
        xiong_shen_list = [
            "月煞", "月虚", "月害", "月刑", "月厌", "月忌", "月破", "大时", 
            "天吏", "天贼", "天刑", "天兵", "天狱", "天棒", "五墓", "八专"
        ]
        
        # 使用农历日期生成伪随机数
        seed = lunar.getYear() * 10000 + lunar.getMonth() * 100 + lunar.getDay()
        import random
        random.seed(seed)
        
        # 随机选择2-4个吉神
        ji_shen_count = random.randint(2, 4)
        ji_shen = random.sample(ji_shen_list, ji_shen_count)
        
        # 随机选择1-3个凶煞
        xiong_shen_count = random.randint(1, 3)
        xiong_shen = random.sample(xiong_shen_list, xiong_shen_count)
        
        return "、".join(ji_shen), "、".join(xiong_shen)
    
    def _generate_lucky_info(self, lunar):
        """生成吉祥方位、颜色、数字"""
        # 方位列表
        directions = ["东", "南", "西", "北", "东北", "东南", "西南", "西北", "中"]
        
        # 颜色列表
        colors = ["红色", "橙色", "黄色", "绿色", "青色", "蓝色", "紫色", "黑色", "白色", "金色", "银色"]
        
        # 使用农历日期生成伪随机数
        seed = lunar.getYear() * 10000 + lunar.getMonth() * 100 + lunar.getDay()
        import random
        random.seed(seed)
        
        # 随机选择1-2个方位
        direction_count = random.randint(1, 2)
        lucky_direction = random.sample(directions, direction_count)
        
        # 随机选择1-2个颜色
        color_count = random.randint(1, 2)
        lucky_color = random.sample(colors, color_count)
        
        # 随机选择1-3个数字
        numbers = list(range(1, 10))
        number_count = random.randint(1, 3)
        lucky_number = random.sample(numbers, number_count)
        lucky_number_str = "、".join([str(num) for num in lucky_number])
        
        return "、".join(lucky_direction), "、".join(lucky_color), lucky_number_str
    
    def _generate_day_fortune(self, lunar):
        """生成当日运势"""
        # 运势列表
        fortunes = [
            "诸事皆宜，顺利吉祥",
            "上午吉，下午平",
            "上午平，下午吉",
            "早晚吉，中午平",
            "吉中有凶，宜谨慎行事",
            "平平淡淡，无灾无难",
            "小凶小吉，宜守不宜进",
            "宜静不宜动，守成不宜进取",
            "诸事不宜，宜修身养性"
        ]
        
        # 使用农历日期生成伪随机数
        seed = lunar.getYear() * 10000 + lunar.getMonth() * 100 + lunar.getDay()
        import random
        random.seed(seed)
        
        # 随机选择一条运势
        return random.choice(fortunes)
    
    def _get_solar_term_description(self, term_name):
        """获取节气描述"""
        descriptions = {
            "立春": "立春是二十四节气之首，标志着新一年春季的开始。万物始发芽，新的一年开始了。",
            "雨水": "雨水节气意味着降水开始增多，空气湿度逐渐加大，雨雪交加。",
            "惊蛰": "惊蛰是指春雷乍动，惊醒了蛰伏在土中冬眠的昆虫。",
            "春分": "春分表示昼夜平分，冬去春来，草木萌动。",
            "清明": "清明节气，是踏青、扫墓、祭祖的日子，也是万物生长的季节。",
            "谷雨": "谷雨是春季最后一个节气，雨生百谷，雨量充足而及时，谷类作物能茁壮成长。",
            "立夏": "立夏表示告别春天，是夏天的开始，万物繁茂。",
            "小满": "小满意味着夏熟作物的籽粒开始灌浆饱满，但还未成熟。",
            "芒种": "芒种表示麦类等有芒作物成熟，可以收获，同时可以播种晚谷。",
            "夏至": "夏至是一年中白昼最长、黑夜最短的一天，也是北半球一年中太阳高度最高的一天。",
            "小暑": "小暑表示炎热的夏天开始，但还没到最热的时候。",
            "大暑": "大暑是一年中最热的节气，正值中伏前后，是一年中气温最高、最热的时期。",
            "立秋": "立秋表示秋天的开始，暑气逐渐消退。",
            "处暑": "处暑意味着炎热的夏天结束，暑气渐消。",
            "白露": "白露表示天气转凉，露水开始凝结。",
            "秋分": "秋分表示昼夜平分，秋季的中间。",
            "寒露": "寒露表示天气更加寒冷，露水更加寒冷。",
            "霜降": "霜降表示天气寒冷，开始有霜冻出现。",
            "立冬": "立冬表示冬季的开始，万物收藏。",
            "小雪": "小雪表示天气寒冷，开始降雪，但雪量不大。",
            "大雪": "大雪表示降雪量增多，天气更加寒冷。",
            "冬至": "冬至是一年中白昼最短、黑夜最长的一天，也是北半球一年中太阳高度最低的一天。",
            "小寒": "小寒表示天气寒冷，但还没到最冷的时候。",
            "大寒": "大寒是一年中最冷的节气，正值三九前后，是一年中气温最低、最冷的时期。"
        }
        
        return descriptions.get(term_name, "")
    
    def _get_festival_description(self, festival_name):
        """获取节日描述"""
        descriptions = {
            "春节": "春节是中国最重要的传统节日，标志着新年的开始，家人团聚，共庆新春。",
            "元宵节": "元宵节是春节之后的第一个重要节日，人们赏花灯、猜灯谜、吃元宵。",
            "清明节": "清明节是中国传统的祭祖节日，人们扫墓祭祖，缅怀先人。",
            "端午节": "端午节是纪念屈原的节日，人们吃粽子、赛龙舟、挂艾草。",
            "七夕节": "七夕节是中国传统的情人节，纪念牛郎织女的爱情故事。",
            "中秋节": "中秋节是中国传统的团圆节，人们赏月、吃月饼，寄托思念之情。",
            "重阳节": "重阳节是中国传统的敬老节，人们登高、赏菊、饮菊花酒。",
            "腊八节": "腊八节是佛教传统节日，人们喝腊八粥，祈求来年平安。",
            "小年": "小年是春节前的准备日，人们开始大扫除，准备年货。",
            "除夕": "除夕是农历一年的最后一天，家人团聚吃年夜饭，守岁迎新年。",
            "元旦": "元旦是公历新年的第一天，人们庆祝新的一年开始。",
            "情人节": "情人节是西方传统节日，恋人之间互送礼物表达爱意。",
            "妇女节": "妇女节是为了纪念妇女争取平等权利的节日。",
            "植树节": "植树节是为了提高人们爱林、造林的意识而设立的节日。",
            "愚人节": "愚人节是西方传统节日，人们互相开玩笑和恶作剧。",
            "劳动节": "劳动节是为了纪念工人阶级争取权益的节日。",
            "青年节": "青年节是为了纪念中国青年运动的节日。",
            "儿童节": "儿童节是为了保障儿童权益、关注儿童成长而设立的节日。",
            "教师节": "教师节是为了尊重教师、弘扬尊师重教传统而设立的节日。",
            "国庆节": "国庆节是为了庆祝中华人民共和国成立而设立的节日。",
            "圣诞节": "圣诞节是西方传统节日，庆祝耶稣基督诞生。"
        }
        
        return descriptions.get(festival_name, "")
        
    def get_solar_term(self, date_str):
        """获取指定日期的节气信息"""
        try:
            year, month, day = map(int, date_str.split('-'))
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            
            jieqi = lunar.getJieQi()
            if jieqi:
                return {
                    'name': jieqi,
                    'description': self._get_solar_term_description(jieqi)
                }
            return None
        except Exception as e:
            print(f"获取节气信息出错: {str(e)}")
            return None
    
    def get_festivals(self, date_str):
        """获取指定日期的节日信息"""
        try:
            year, month, day = map(int, date_str.split('-'))
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            
            lunar_year = lunar.getYear()
            lunar_month = lunar.getMonth()
            lunar_day = lunar.getDay()
            
            return self._get_festivals(year, month, day, lunar_year, lunar_month, lunar_day)
        except Exception as e:
            print(f"获取节日信息出错: {str(e)}")
            return []