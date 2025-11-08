'''
Author: vinjinwang vinjinwang@tencent.com
Date: 2025-11-02
Description: Gradio Web UI for Travel Agent with Thought-Action-Observation Loop
'''
import os
import re
import gradio as gr
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple

from huggingface_hub.inference._mcp.agent import Agent

from agents.react_agent import ReActAgent
from models.hello_agents_llm import HelloAgentsLLM
from tools import (
    get_attraction,
    get_weather,
    google_search,
)
from tools.tool_exector import ToolExecutor

load_dotenv()




def format_thinking_process(thinking_process: List[Dict[str, Any]]) -> str:
    """Format thinking process for display"""
    if not thinking_process:
        return "暂无思考过程"
    
    formatted = []
    for step in thinking_process:
        formatted.append(f"""
**第 {step['iteration']} 轮思考**

🤔 **思考过程：**
{step['thought']}

🔧 **执行动作：**
{step['action']}

👁️ **观察结果：**
{step['observation']}

---
""")
    
    return "\n".join(formatted)

def chat_interface(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]], str]:
    """
    Gradio chat interface function
    
    Returns:
        Tuple of (response, updated_history, thinking_process_display)
    """
    if not message.strip():
        return "", history, "请输入您的查询内容。"
    
    # Process the query
    final_answer, thinking_process = agent.run(message)
    
    # Format thinking process for display
    thinking_display = format_thinking_process(thinking_process)
    
    # Update chat history
    history.append([message, final_answer])
    
    return "", history, thinking_display


def create_interface():
    """Create and configure Gradio interface"""
    
    with gr.Blocks(
        title="智能问答与咨询助手",
        theme=gr.themes.Soft(),
        css="""
        .thinking-process {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🌍 智能问答与咨询助手
        
        欢迎使用智能问答与咨询助手！我可以为您提供信息咨询、天气查询、旅行规划与景点推荐等服务。
        
        **功能特点：**
        - 💬 智能问答与咨询
        - 🌤️ 实时天气查询
        - 🧠 透明的思考过程展示
        - 🔍 知识库检索与信息整合
        
        **使用示例：**
        - "请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
        - "我想去上海旅游，请先查看天气情况再给我推荐景点。"
        - "请帮我分析一下最近的经济形势，并给出相应的投资建议。"
        - "请帮我查询一下最近的新闻热点，并给出相应的解读。"
        - "请帮我查询一下最近的股票市场情况，并给出相应的投资建议。"
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="对话记录",
                    height=400,
                    show_label=True,
                    container=True,
                    type="tuples"
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="请输入您的查询...",
                        label="输入消息",
                        lines=2,
                        max_lines=5,
                        show_label=False,
                        container=False,
                        scale=4
                    )
                    send_btn = gr.Button("发送", variant="primary", scale=1)
                
                # Clear button
                clear_btn = gr.Button("清空对话", variant="secondary")
            
            with gr.Column(scale=1):
                # Thinking process display
                thinking_display = gr.Markdown(
                    label="🧠 智能体思考过程",
                    value="等待您的查询...",
                    elem_classes=["thinking-process"],
                    height=500
                )
        
        # Event handlers
        def submit_message(message, history):
            return chat_interface(message, history)
        
        def clear_chat():
            return [], "等待您的查询..."
        
        # Bind events
        send_btn.click(
            submit_message,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, thinking_display]
        )
        
        msg_input.submit(
            submit_message,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, thinking_display]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, thinking_display]
        )
        
        # Example queries
        gr.Examples(
            examples=[
                ["请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"],
                ["我想去上海旅游，请先查看天气情况再给我推荐景点。"],
                ["请帮我分析一下最近的经济形势，并给出相应的投资建议。"],
                ["请帮我查询一下最近的新闻热点，并给出相应的解读。"],
                ["请帮我查询一下最近的股票市场情况，并给出相应的投资建议。"],
            ],
            inputs=msg_input,
            label="示例查询"
        )
        
        gr.Markdown("""
        ---
        
        **注意事项：**
        - 请确保已正确配置环境变量 `LLM_API_KEY` 和 `LLM_BASE_URL`
        - 景点推荐使用 Tavily Search API，知识库检索使用 SerpApi API
        - 右侧面板会实时显示智能体的思考过程，包括每一轮的思考、行动和观察结果
        """)
    
    return demo


def create_agent():
    # Initialize agent
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
    agent = ReActAgent(llm_client, tool_executor)

    return agent

if __name__ == "__main__":
    # Create and launch the interface
    agent = create_agent()
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )