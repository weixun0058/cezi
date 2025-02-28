# 从“汉典”字典网获取汉字信息

import requests
from bs4 import BeautifulSoup
def get_word_info(word):
    url = f"https://www.zdic.net/hans/{word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('div', class_='zdict').text

word = input("请输入要查询的汉字：")
info = get_word_info(word)
print(info)
