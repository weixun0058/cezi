import sqlite3
from datetime import datetime, timedelta
from lunar_python import Lunar, Solar

class HuangLi:
    def __init__(self, db_path="database/huangli.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建黄历表，存储已查询过的黄历数据
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS huangli_daily (
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
        ''')
        
        # 检查表结构，如果缺少字段则添加
        cursor.execute("PRAGMA table_info(huangli_daily)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 检查并添加缺失的字段
        if 'peng_zu_bai_ji' not in columns:
            print("添加彭祖百忌字段")
            cursor.execute("ALTER TABLE huangli_daily ADD COLUMN peng_zu_bai_ji TEXT")
        
        if 'xi_shen' not in columns:
            print("添加喜神字段")
            cursor.execute("ALTER TABLE huangli_daily ADD COLUMN xi_shen TEXT")
        
        if 'fu_shen' not in columns:
            print("添加福神字段")
            cursor.execute("ALTER TABLE huangli_daily ADD COLUMN fu_shen TEXT")
        
        if 'cai_shen' not in columns:
            print("添加财神字段")
            cursor.execute("ALTER TABLE huangli_daily ADD COLUMN cai_shen TEXT")
        
        if 'gan_zhi_hour' not in columns:
            print("添加时辰干支字段")
            cursor.execute("ALTER TABLE huangli_daily ADD COLUMN gan_zhi_hour TEXT")
        
        conn.commit()
        conn.close()
    
    def get_daily_huangli(self, date=None):
        """获取指定日期的黄历信息，如果不存在则从lunar_python库获取"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"获取黄历数据: {date}")
        
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
            print(f"从数据库获取黄历数据: {date}")
            return huangli_data
        else:
            # 从lunar_python库获取黄历数据
            huangli_data = self._generate_huangli_data(date)
            if huangli_data:
                # 保存到数据库
                self._save_huangli_to_db(huangli_data)
                conn.close()
                print(f"生成并保存黄历数据: {date}")
                return huangli_data
            
            conn.close()
            print(f"无法获取黄历数据: {date}")
            return None
    
    def _generate_huangli_data(self, date_str):
        """使用lunar_python库生成黄历数据"""
        try:
            print(f"开始生成黄历数据: {date_str}")
            # 解析日期字符串为年月日
            year, month, day = map(int, date_str.split('-'))
            
            # 创建阳历日期对象
            solar = Solar.fromYmd(year, month, day)
            
            # 转换为农历日期对象
            lunar = solar.getLunar()
            
            # 获取农历日期字符串
            lunar_date = f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
            
            # 获取天干地支
            gan_zhi_year = lunar.getYearInGanZhi() + "年"
            gan_zhi_month = lunar.getMonthInGanZhi() + "月"
            gan_zhi_day = lunar.getDayInGanZhi() + "日"
            gan_zhi_hour = lunar.getTimeInGanZhi() + "时"
            
            # 获取生肖
            zodiac = lunar.getYearShengXiao() + "年"
            
            # 获取宜忌
            try:
                suitable = "、".join(lunar.getDayYi())
                unsuitable = "、".join(lunar.getDayJi())
            except Exception as e:
                print(f"获取宜忌出错: {str(e)}")
                suitable = "无"
                unsuitable = "无"
            
            # 获取冲煞
            try:
                chong_animal = lunar.getChong()
                sha = lunar.getSha()
                chong_sha = f"冲{chong_animal}({lunar.getChongGan()})煞{sha}"
            except Exception as e:
                print(f"获取冲煞出错: {str(e)}")
                chong_sha = "无"
            
            # 获取吉神凶煞
            try:
                ji_shen = "、".join(lunar.getDayJiShen())
                xiong_shen = "、".join(lunar.getDayXiongSha())
            except Exception as e:
                print(f"获取吉神凶煞出错: {str(e)}")
                ji_shen = "无"
                xiong_shen = "无"
            
            # 获取彭祖百忌
            try:
                print(f"获取彭祖百忌...")
                peng_zu_gan = lunar.getPengZuGan()
                peng_zu_zhi = lunar.getPengZuZhi()
                peng_zu_bai_ji = f"{peng_zu_gan}，{peng_zu_zhi}"
                print(f"彭祖百忌: {peng_zu_bai_ji}")
            except Exception as e:
                print(f"获取彭祖百忌出错: {str(e)}")
                import traceback
                traceback.print_exc()
                peng_zu_bai_ji = "无"
            
            # 获取喜神、福神、财神方位
            try:
                print(f"获取喜神方位...")
                xi_shen_desc = lunar.getDayPositionXiDesc()
                xi_shen_pos = lunar.getDayPositionXi()
                xi_shen = f"{xi_shen_desc}({xi_shen_pos})"
                print(f"喜神方位: {xi_shen}")
                
                print(f"获取福神方位...")
                fu_shen_desc = lunar.getDayPositionFuDesc()
                fu_shen_pos = lunar.getDayPositionFu()
                fu_shen = f"{fu_shen_desc}({fu_shen_pos})"
                print(f"福神方位: {fu_shen}")
                
                print(f"获取财神方位...")
                cai_shen_desc = lunar.getDayPositionCaiDesc()
                cai_shen_pos = lunar.getDayPositionCai()
                cai_shen = f"{cai_shen_desc}({cai_shen_pos})"
                print(f"财神方位: {cai_shen}")
            except Exception as e:
                print(f"获取神煞方位出错: {str(e)}")
                import traceback
                traceback.print_exc()
                xi_shen = "无"
                fu_shen = "无"
                cai_shen = "无"
            
            # 获取节气
            solar_term = lunar.getJieQi() or "无"
            
            # 获取节日
            festivals = []
            lunar_festivals = lunar.getFestivals()
            if lunar_festivals:
                for festival in lunar_festivals:
                    festivals.append({"name": festival, "type": "农历节日"})
            
            solar_festivals = solar.getFestivals()
            if solar_festivals:
                for festival in solar_festivals:
                    festivals.append({"name": festival, "type": "阳历节日"})
            
            # 构建黄历数据字典
            huangli_data = {
                'date': date_str,
                'lunar_date': lunar_date,
                'gan_zhi_year': gan_zhi_year,
                'gan_zhi_month': gan_zhi_month,
                'gan_zhi_day': gan_zhi_day,
                'gan_zhi_hour': gan_zhi_hour,
                'zodiac': zodiac,
                'suitable': suitable,
                'unsuitable': unsuitable,
                'chong_sha': chong_sha,
                'ji_shen': ji_shen,
                'xiong_shen': xiong_shen,
                'peng_zu_bai_ji': peng_zu_bai_ji,
                'xi_shen': xi_shen,
                'fu_shen': fu_shen,
                'cai_shen': cai_shen,
                'solar_term': solar_term,
                'festivals': festivals
            }
            
            print(f"成功生成黄历数据: {date_str}")
            return huangli_data
            
        except Exception as e:
            print(f"生成黄历数据出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_huangli_to_db(self, huangli_data):
        """保存黄历数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 将节日列表转换为JSON字符串
            import json
            festivals_json = json.dumps(huangli_data['festivals'], ensure_ascii=False)
            
            # 检查数据中是否包含所有必要字段
            fields = ['peng_zu_bai_ji', 'xi_shen', 'fu_shen', 'cai_shen']
            for field in fields:
                if field not in huangli_data or not huangli_data[field]:
                    print(f"警告: 数据中缺少{field}字段或为空，设置为默认值'无'")
                    huangli_data[field] = "无"
            
            print(f"保存数据到数据库: 彭祖百忌={huangli_data['peng_zu_bai_ji']}, 喜神={huangli_data['xi_shen']}, 福神={huangli_data['fu_shen']}, 财神={huangli_data['cai_shen']}")
            
            cursor.execute('''
            INSERT OR REPLACE INTO huangli_daily 
            (date, lunar_date, gan_zhi_year, gan_zhi_month, gan_zhi_day, gan_zhi_hour, 
            zodiac, suitable, unsuitable, chong_sha, ji_shen, xiong_shen, 
            peng_zu_bai_ji, xi_shen, fu_shen, cai_shen, solar_term, festivals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                huangli_data['date'],
                huangli_data['lunar_date'],
                huangli_data['gan_zhi_year'],
                huangli_data['gan_zhi_month'],
                huangli_data['gan_zhi_day'],
                huangli_data['gan_zhi_hour'],
                huangli_data['zodiac'],
                huangli_data['suitable'],
                huangli_data['unsuitable'],
                huangli_data['chong_sha'],
                huangli_data['ji_shen'],
                huangli_data['xiong_shen'],
                huangli_data['peng_zu_bai_ji'],
                huangli_data['xi_shen'],
                huangli_data['fu_shen'],
                huangli_data['cai_shen'],
                huangli_data['solar_term'],
                festivals_json
            ))
            
            conn.commit()
            conn.close()
            print(f"黄历数据已保存到数据库: {huangli_data['date']}")
            return True
        except Exception as e:
            print(f"保存黄历数据到数据库出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_week_huangli(self):
        """获取一周的黄历数据"""
        try:
            today = datetime.now()
            week_data = []
            
            # 获取前2天、今天和未来6天的数据，共9天
            for i in range(-2, 7):
                date = today + timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                huangli_data = self.get_daily_huangli(date_str)
                if huangli_data:
                    # 简化数据，但包含更多传统黄历元素
                    simplified_data = {
                        'date': date_str,
                        'lunar_date': huangli_data.get('lunar_date', ''),
                        'gan_zhi_day': huangli_data.get('gan_zhi_day', ''),
                        'gan_zhi_hour': huangli_data.get('gan_zhi_hour', ''),
                        'suitable': huangli_data.get('suitable', ''),
                        'unsuitable': huangli_data.get('unsuitable', ''),
                        'chong_sha': huangli_data.get('chong_sha', ''),
                        'peng_zu_bai_ji': huangli_data.get('peng_zu_bai_ji', ''),
                        'xi_shen': huangli_data.get('xi_shen', ''),
                        'fu_shen': huangli_data.get('fu_shen', ''),
                        'cai_shen': huangli_data.get('cai_shen', ''),
                        'solar_term': huangli_data.get('solar_term', '')
                    }
                    week_data.append(simplified_data)
            
            return week_data
        except Exception as e:
            print(f"获取一周黄历数据出错: {str(e)}")
            return [] 