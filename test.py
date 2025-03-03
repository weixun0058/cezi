from lunming import LunMing

lunming = LunMing()

# 获取流式分析生成器
result_stream = lunming.analyze_bazi("张三", "男", "1990-01-01", "12:00")

print("开始测试流式输出:")
print("-" * 50)

# 遍历生成器获取每个字符
result_text = ""
for char in result_stream:
    result_text += char
    print(char, end="", flush=True)  # 实时打印每个字符

print("\n" + "-" * 50)
print("流式输出完成")
print(f"总字符数: {len(result_text)}")


