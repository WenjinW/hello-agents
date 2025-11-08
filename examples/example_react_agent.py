'''
Author: vinjinwang vinjinwang@tencent.com
Date: 2025-11-08 22:02:23
LastEditors: vinjinwang vinjinwang@tencent.com
LastEditTime: 2025-11-08 22:07:57
FilePath: /hello-agents/examples/example_react_agent.py
Description: 

Copyright (c) 2025 by Tencent, All Rights Reserved. 
'''
from agents.react_agent import ReActAgent
from models.hello_agents_llm import HelloAgentsLLM
from tools import (
    get_attraction,
    get_weather,
    google_search,
)
from tools.tool_exector import ToolExecutor


if __name__ == "__main__":
    llm_client = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    tool_executor.registerTool(
        name="get_weather",
        description="查询指定城市的实时天气。参数说明：\ncity: str，城市名称。",
        func=get_weather
    )
    tool_executor.registerTool(
        name="get_attraction",
        description="根据城市和天气搜索推荐的旅游景点。参数说明：\ncity: str，城市名称。weather: str，天气状况。",
        func=get_attraction
    )
    tool_executor.registerTool(
        name="google_search",
        description="一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。参数说明：\nquery: str，搜索关键词。",
        func=google_search
    )
    react_agent = ReActAgent(llm_client, tool_executor)
    react_agent.run("你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。")