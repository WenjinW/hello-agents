'''
Author: vinjinwang vinjinwang@tencent.com
Date: 2025-11-08 21:56:15
LastEditors: vinjinwang vinjinwang@tencent.com
LastEditTime: 2025-11-08 22:26:41
FilePath: /hello-agents/agents/react_agent.py
Description: ReAct Agent

Copyright (c) 2025 by Tencent, All Rights Reserved. 
'''
import re

from models.hello_agents_llm import HelloAgentsLLM
from tools.tool_exector import ToolExecutor
from prompts.react_prompt import REACT_PROMPT_TEMPLATE


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        运行ReAct智能体来回答一个问题。
        """
        self.history = [] # 每次运行时重置历史记录
        current_step = 0

        thinking_process = []
        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            # 2. 调用LLM进行思考
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            
            if not response_text:
                print("错误:LLM未能返回有效响应。")
                break

            # 3. 解析LLM的输出
            thought, action = self._parse_output(response_text)
            
            if thought:
                print(f"思考: {thought}")

            if not action:
                print("警告:未能解析出有效的Action，流程终止。")
                break

            # 4. 执行Action
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = re.match(r"Finish\((.*)\)", action).group(1)
                print(f"🎉 最终答案: {final_answer}")
                return final_answer, thinking_process
            
            tool_name, tool_input_dict = self._parse_action(action)
            if not tool_name or not tool_input_dict:
                # ... 处理无效Action格式 ...
                continue

            print(f"🎬 行动: {tool_name}[{tool_input_dict}]")
            
            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(**tool_input_dict) # 调用真实工具
            print(f"👀 观察: {observation}")

            # 将本轮的Action和Observation添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

            thinking_process.append({
                "iteration": current_step,
                "thought": thought,
                "action": action,
                "observation": observation
            })

        # 循环结束
        print("已达到最大步数，流程终止。")
        return "达到最大迭代次数，任务未完成。", thinking_process

    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。"""
        thought_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入字典。"""
        tool_name = re.search(r"(\w+)\[", action_text).group(1)
        tool_input = re.search(r"\[(.*)\]", action_text).group(1)
        tool_input_dict = dict(re.findall(r'(\w+)="([^"]*)"', tool_input))
        return tool_name, tool_input_dict
        # match = re.match(r"(\w+)\[(.*)\]", action_text)
        # if match:
        #     return match.group(1), match.group(2)
        # return None, None
