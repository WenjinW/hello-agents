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

from models.openai_client import OpenAICompatibleClient
from prompts.travel_prompt import AGENT_SYSTEM_PROMPT
from tools.available_tools import available_tools

load_dotenv()

class TravelAgent:
    """Travel Agent with Thought-Action-Observation Loop"""
    
    def __init__(self):
        # Configure LLM client
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.BASE_URL = "http://one-api.woa.com/v1"
        self.MODEL_ID = "gpt-4o"
        
        self.llm = OpenAICompatibleClient(
            model=self.MODEL_ID,
            api_key=self.API_KEY,
            base_url=self.BASE_URL
        )
    
    def process_query(self, user_query: str, max_iterations: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process user query through thought-action-observation loop
        
        Returns:
            Tuple of (final_answer, thinking_process)
        """
        if not user_query.strip():
            return "请输入您的查询内容。", []
        
        prompt_history = [f"用户请求: {user_query}"]
        thinking_process = []
        
        for i in range(max_iterations):
            # Build full prompt
            full_prompt = "\n".join(prompt_history)
            
            # Call LLM for thinking
            llm_output = self.llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
            
            # Parse thought and action
            thought_match = re.search(r"Thought: (.*?)(?=Action:|$)", llm_output, re.DOTALL)
            action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
            
            thought = thought_match.group(1).strip() if thought_match else "未找到思考内容"
            
            if not action_match:
                thinking_process.append({
                    "iteration": i + 1,
                    "thought": thought,
                    "action": "解析错误：未找到Action",
                    "observation": "模型输出格式错误"
                })
                return "解析错误：模型输出中未找到 Action。", thinking_process
            
            action_str = action_match.group(1).strip()
            
            # Check if task is finished
            if action_str.startswith("finish"):
                final_answer_match = re.search(r'finish\(answer="(.*)"\)', action_str)
                if final_answer_match:
                    final_answer = final_answer_match.group(1)
                    thinking_process.append({
                        "iteration": i + 1,
                        "thought": thought,
                        "action": action_str,
                        "observation": "任务完成"
                    })
                    return final_answer, thinking_process
                else:
                    return "解析错误：无法提取最终答案。", thinking_process
            
            # Parse and execute tool
            try:
                tool_name = re.search(r"(\w+)\(", action_str).group(1)
                args_str = re.search(r"\((.*)\)", action_str).group(1)
                kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))
                
                if tool_name in available_tools:
                    observation = available_tools[tool_name](**kwargs)
                else:
                    observation = f"错误：未定义的工具 '{tool_name}'"
                
            except Exception as e:
                observation = f"错误：解析或执行工具时出错 - {e}"
            
            # Record thinking process
            thinking_process.append({
                "iteration": i + 1,
                "thought": thought,
                "action": action_str,
                "observation": observation
            })
            
            # Add to prompt history
            prompt_history.append(llm_output)
            observation_str = f"Observation: {observation}"
            prompt_history.append(observation_str)
        
        return "达到最大迭代次数，任务未完成。", thinking_process

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
    
    # Initialize agent
    agent = TravelAgent()
    
    # Process the query
    final_answer, thinking_process = agent.process_query(message)
    
    # Format thinking process for display
    thinking_display = format_thinking_process(thinking_process)
    
    # Update chat history
    history.append([message, final_answer])
    
    return "", history, thinking_display

def create_interface():
    """Create and configure Gradio interface"""
    
    with gr.Blocks(
        title="智能旅行助手",
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
        # 🌍 智能旅行助手
        
        欢迎使用智能旅行助手！我可以帮您查询天气信息并推荐合适的旅游景点。
        
        **功能特点：**
        - 🌤️ 实时天气查询
        - 🏛️ 智能景点推荐
        - 🧠 透明的思考过程展示
        
        **使用示例：**
        - "请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
        - "我想去上海旅游，请先查看天气情况再给我推荐景点。"
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
                        placeholder="请输入您的旅行查询...",
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
                ["查询广州的天气，并推荐适合当前天气的户外活动场所。"],
                ["帮我看看深圳今天的天气如何，推荐一些适合的旅游地点。"]
            ],
            inputs=msg_input,
            label="示例查询"
        )
        
        gr.Markdown("""
        ---
        
        **注意事项：**
        - 请确保已正确配置环境变量 `OPENAI_API_KEY` 和 `TAVILY_API_KEY`
        - 天气查询使用 wttr.in API，景点推荐使用 Tavily Search API
        - 右侧面板会实时显示智能体的思考过程，包括每一轮的思考、行动和观察结果
        """)
    
    return demo

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )