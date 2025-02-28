import sqlite3

def cale_character_count(num1, num2, num3):
    """
    计算三个数字对应的签号
    Args:
        num1: 第一个汉字的康熙笔画数
        num2: 第二个汉字的康熙笔画数
        num3: 第三个汉字的康熙笔画数
    Returns:
        返回1-383之间的签号
    """
    # 方法1：简单相加后取余
    last_digit1 = num1 % 10 or 1
    last_digit2 = num2 % 10 or 1
    last_digit3 = num3 % 10 or 1
    
    # 使用383作为最大签号
    new_number = last_digit1 * 100 + last_digit2 * 10 + last_digit3
    
    result = new_number % 384
    
    
    print(f"笔画数: {num1}, {num2}, {num3}")
    print(f"笔画组成数: {new_number}")
    print(f"计算结果: {result}")
    return result


def num_to_chinese_upper(num):
    if not 0 <= num < 100:
        raise ValueError("此函数仅支持0到99之间的数字")

    # 定义0-9对应的大写汉字
    chinese_upper_digits = {
        0: '〇', 1: '一', 2: '二', 3: '三', 4: '四',
        5: '五', 6: '六', 7: '七', 8: '八', 9: '九'
    }
    
    # 十位的表示
    chinese_tens = '十'

    if num < 10:
        return chinese_upper_digits[num]
    elif num < 20:
        return '十' + ('' if num == 10 else chinese_upper_digits[num - 10])
    else:
        tens = num // 10
        ones = num % 10
        result = chinese_upper_digits[tens] + chinese_tens
        if ones == 0:
            return result
        else:
            return result + chinese_upper_digits[ones]
if __name__ == "__main__":
    # 使用示例
    for i in range(0, 100):  # 测试一些边界情况
        print(f"{i}: {num_to_chinese_upper(i)}")