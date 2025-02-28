import sqlite3
import os
import requests
from bs4 import BeautifulSoup

class Database:
    def __init__(self):
        import pandas as pd
        self.hanzi_db = "database/kanxi_dict.db"
        self.gua_data = pd.read_excel('database/zhugeshenshuan_jq.xlsx')
        # 调试用：打印数据库信息
        # self._print_db_info()
        # 移除自动创建表和导入数据的逻辑
        # self._init_db()
        # if not self._check_data_exists():
        #     self._import_data()
    
    def get_gua_info(self, sign_number):
        """获取卦象信息"""
        try:
            print(f"\n=== 查询卦象信息 ===")
            print(f"查询签号: {sign_number}")
            
            # 首先打印列名，帮助调试
            print("Excel文件的列名:", list(self.gua_data.columns))
            
            # 查找对应签号的行
            matching_rows = self.gua_data[self.gua_data['签号'] == sign_number]
            if matching_rows.empty:
                print(f"未找到签号 {sign_number} 的数据")
                return None
            
            row = matching_rows.iloc[0]
            
            # 使用实际的列名
            result = [
                0,  # ID可以是行索引
                row['签号'] if '签号' in row else None,
                row['吉凶'] if '吉凶' in row else None,
                row['卦属'] if '卦属' in row else None,
                row['签文'] if '签文' in row else None,
                row['解签一'] if '解签一' in row else None,
                row['事业'] if '事业' in row else None,  # 注意列名可能不同
                row['财运'] if '财运' in row else None,
                row['情感'] if '情感' in row else None,
                row['健康'] if '健康' in row else None,
                row['学业'] if '学业' in row else None,
                row['泛泛'] if '泛泛' in row else None
            ]
            
            print("字段对应关系:")
            print(f"  签号: {result[1]}")
            print(f"  吉凶: {result[2]}")
            print(f"  卦属: {result[3]}")
            print(f"  签文: {result[4]}")
            print(f"  解签一: {result[5]}")
            print(f"  事业: {result[6]}")
            print(f"  财运: {result[7]}")
            print(f"  情感: {result[8]}")
            print(f"  健康: {result[9]}")
            print(f"  学业: {result[10]}")
            print(f"  泛泛: {result[11]}")
            
            return result
            
        except Exception as e:
            print(f"查询卦象信息时出错: {str(e)}")
            # 打印更详细的错误信息
            import traceback
            print(traceback.format_exc())
            return None

    def _print_available_signs(self):
        """打印所有可用的签号"""
        try:
            conn = sqlite3.connect(self.gua_db)
            cursor = conn.cursor()
            cursor.execute("SELECT 签号 FROM zg_base ORDER BY 签号")
            signs = cursor.fetchall()
            print("数据库中可用的签号:", [sign[0] for sign in signs])
            conn.close()
        except Exception as e:
            print(f"获取签号列表时出错: {str(e)}") 

    def _print_db_info(self):
        """打印数据库信息"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.gua_db):
                print(f"卦象数据库文件不存在: {self.gua_db}")
                return
            
            if not os.path.exists(self.hanzi_db):
                print(f"汉字数据库文件不存在: {self.hanzi_db}")
                return
            
            # 打印汉字数据库信息
            print("\n=== 汉字数据库信息 ===")
            conn_hanzi = sqlite3.connect(self.hanzi_db)
            cursor_hanzi = conn_hanzi.cursor()
            cursor_hanzi.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables_hanzi = cursor_hanzi.fetchall()
            print("汉字数据库中的表:", [table[0] for table in tables_hanzi])
            conn_hanzi.close()
            
            # 打印卦象数据库信息
            print("\n=== 卦象数据库信息 ===")
            conn_gua = sqlite3.connect(self.gua_db)
            cursor_gua = conn_gua.cursor()
            cursor_gua.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables_gua = cursor_gua.fetchall()
            print("卦象数据库中的表:", [table[0] for table in tables_gua])
            conn_gua.close()

            # 检查汉字数据库所有字段
            print("\n=== 汉字数据库所有字段 ===")
            conn_hanzi = sqlite3.connect(self.hanzi_db)
            cursor_hanzi = conn_hanzi.cursor()
            cursor_hanzi.execute("PRAGMA table_info(hanzi)")
            columns_hanzi = cursor_hanzi.fetchall()
            print("汉字数据库中的字段:", [column[1] for column in columns_hanzi])
            conn_hanzi.close()
            
            # 添加：打印一些示例数据
            print("\n=== 汉字数据示例 ===")
            conn_hanzi = sqlite3.connect(self.hanzi_db)
            cursor_hanzi = conn_hanzi.cursor()
            cursor_hanzi.execute("SELECT * FROM hanzi LIMIT 3")
            sample_hanzi = cursor_hanzi.fetchall()
            print("汉字数据示例:", sample_hanzi)
            conn_hanzi.close()
            
            print("\n=== 卦象数据示例 ===")
            conn_gua = sqlite3.connect(self.gua_db)
            cursor_gua = conn_gua.cursor()
            cursor_gua.execute("SELECT * FROM zg_base LIMIT 3")
            sample_gua = cursor_gua.fetchall()
            print("卦象数据示例:", sample_gua)
            
            # 添加：打印签号范围
            cursor_gua.execute("SELECT MIN(签号), MAX(签号), COUNT(*) FROM zg_base")
            sign_range = cursor_gua.fetchone()
            print(f"签号范围: {sign_range[0]} - {sign_range[1]}, 总数: {sign_range[2]}")
            conn_gua.close()
            
        except Exception as e:
            print(f"获取数据库信息时出错: {str(e)}") 

    def get_stroke_count_by_hd(self, character):
        """从汉典网获取汉字的康熙笔画数"""
        try:
            url = f"https://www.zdic.net/hans/{character}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            req = requests.get(url, headers=headers)
            req.encoding = "utf-8"
            html = req.text
            soup = BeautifulSoup(html, "html.parser")
            
            # 先查康熙字典笔画
            kx_path = soup.select("div.kxzd span.res_d a")
            if kx_path:
                return int(kx_path[-1].text)
            
            # 如果没有康熙字典笔画，查简体笔画
            jt_path = soup.select("td.z_bs2 p")
            if jt_path:
                for p in jt_path:
                    if '总笔画' in p.text:
                        return int(p.text.split()[-1])
            
            return 1
            
        except Exception as e:
            print(f"从汉典网获取笔画数时出错: {str(e)}")
            return 1

    def get_stroke_count(self, character):
        """获取汉字的康熙笔画数，如有重复记录取第一个"""
        if not character or len(character) != 1:
            return None
            
        try:
            conn = sqlite3.connect(self.hanzi_db)
            cursor = conn.cursor()
            
            # 添加调试日志
            print(f"查询汉字: {character}")
            cursor.execute("""
                SELECT 简体字总笔画, 繁体字总笔画, 康熙字典笔画
                FROM hanzi 
                WHERE 汉字=? 
                ORDER BY ID 
                LIMIT 1
            """, (character,))
            result = cursor.fetchone()
            print(f"康熙字典笔画查询结果: {result}")
            
            if result:
                # 依次尝试康熙字典笔画、繁体字笔画、简体字笔画
                if result[2] is not None:
                    return result[2]
                elif result[1] is not None:
                    return result[1]
                elif result[0] is not None:
                    return result[0]
            
            conn.close()
            
            # 如果数据库中没有找到，使用汉典网查询
            print(f"未找到康熙字典笔画，使用汉典网查询: {character}")
            stroke_count = self.get_stroke_count_by_hd(character)
            print(f"汉典网查询结果: {stroke_count}")
            
            # 将查询结果保存到数据库中
            try:
                conn = sqlite3.connect(self.hanzi_db)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO hanzi (汉字, 康熙字典笔画)
                    VALUES (?, ?)
                """, (character, stroke_count))
                conn.commit()
                conn.close()
                print(f"已将查询结果保存到数据库: {character}={stroke_count}")
            except Exception as e:
                print(f"保存查询结果时出错: {str(e)}")
            
            return stroke_count
            
        except Exception as e:
            print(f"查询笔画数时出错: {str(e)}")
            return 1
