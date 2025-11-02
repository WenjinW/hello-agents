'''
Author: vinjinwang vinjinwang@tencent.com
Date: 2025-11-01 23:04:57
LastEditors: vinjinwang vinjinwang@tencent.com
LastEditTime: 2025-11-01 23:08:08
FilePath: /hello-agents/examples/travel_thought_action_observation.py
Description: 

Copyright (c) 2025 by Tencent, All Rights Reserved. 
'''
import os
import re
from dotenv import load_dotenv


from models.openai_client import OpenAICompatibleClient
from prompts.travel_prompt import AGENT_SYSTEM_PROMPT
from tools.available_tools import available_tools



load_dotenv()

if __name__ == "__main__":
    # --- 1. 配置LLM客户端 ---
    # 请根据您使用的服务，将这里替换成对应的凭证和地址
    API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = "http://one-api.woa.com/v1"
    MODEL_ID = "gpt-4o"

    llm = OpenAICompatibleClient(
        model=MODEL_ID,
        api_key=API_KEY,
        base_url=BASE_URL
    )

    # --- 2. 初始化 ---
    user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
    prompt_history = [f"用户请求: {user_prompt}"]

    print(f"用户输入: {user_prompt}\n" + "="*40)

    # --- 3. 运行主循环 ---
    for i in range(5): # 设置最大循环次数
        print(f"--- 循环 {i+1} ---\n")
        
        # 3.1. 构建Prompt
        full_prompt = "\n".join(prompt_history)
        
        # 3.2. 调用LLM进行思考
        llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
        print(f"模型输出:\n{llm_output}\n")
        prompt_history.append(llm_output)
        
        # 3.3. 解析并执行行动
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            print("解析错误：模型输出中未找到 Action。")
            break
        action_str = action_match.group(1).strip()

        if action_str.startswith("finish"):
            final_answer = re.search(r'finish\(answer="(.*)"\)', action_str).group(1)
            print(f"任务完成，最终答案: {final_answer}")
            break
        
        tool_name = re.search(r"(\w+)\(", action_str).group(1)
        args_str = re.search(r"\((.*)\)", action_str).group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误：未定义的工具 '{tool_name}'"

        # 3.4. 记录观察结果
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "="*40)
        prompt_history.append(observation_str)
