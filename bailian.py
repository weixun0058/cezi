import os
from openai import OpenAI
import time

bailian={'API_KEY': "sk-790941ba780748ec88e4f5145760fbae",'base_url':'https://dashscope.aliyuncs.com/compatible-mode/v1','model_name':"deepseek-r1"}
siliconflow={'API_KEY': 'sk-euvzhodijzncpfdjgecohoviqiomawrmrxottyokhlmnxzcp','base_url':'https://api.siliconflow.cn/v1','model_name':"deepseek-ai/DeepSeek-R1"}
deepseek={
    'API_KEY': 'sk-7021b97fae804957ae20727a3f1fd95a',
    'base_url':'https://api.deepseek.com',
    'model_name':"deepseek-reasoner"
}
organations={'bailian':bailian,'siliconflow':siliconflow,'deepseek':deepseek}

def get_completion(organation, system_prompt, user_message, temperature=0.7):

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
            {'role': 'system', 'content': system_prompt},
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

    print("=" * 20 + "完整思考过程" + "=" * 20 + "\n")
    print(reasoning_content)
    print("=" * 20 + "完整回复" + "=" * 20 + "\n")
    print(answer_content)

    return answer_content

def main():
    organation = organations['deepseek']
    a=time.time()
    system_prompt='你是寺庙里的一位很有修为的长老，精通命理学和心理学方面的知识，特别擅长解签及通过签文分析人的事业方面的运势。并具有很高的情商及专业素养。并由非常正面的心态，总能正面角度考虑任何问题。'
    use_prompt='在别人抽到了以下签文："炉中火，沙里金，功力到，丹鼎成。"希望你帮他解签。要求：\n1. 先写思考过程（用【思考】开头）\n2. 再写最终解签结果（用【解签】开头）\n3. 根据签文内在意涵分析事业运势\n4. 用自然通俗的语言，避免条理化格式'
    answer = get_completion(organation, system_prompt, use_prompt)
    print(f'解签用时{time.time()-a}秒')
if __name__ == "__main__":
    main()



