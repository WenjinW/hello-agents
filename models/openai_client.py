'''
Author: vinjinwang vinjinwang@tencent.com
Date: 2025-11-01 23:06:06
LastEditors: vinjinwang vinjinwang@tencent.com
LastEditTime: 2025-11-01 23:06:27
FilePath: /hello-agents/models/openai_client.py
Description: 兼容OpenAI接口的LLM服务的客户端

Copyright (c) 2025 by Tencent, All Rights Reserved. 
'''
from openai import OpenAI


class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用LLM API来生成回应。"""
        print("正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("大语言模型响应成功。")
            return answer
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return "错误：调用语言模型服务时出错。"
