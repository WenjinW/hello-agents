# hello-agents

## 服务注册
- [SerpApi](https://serpapi.com/dashboard)：通过API提供结构化的Google搜索结果，能直接返回“答案摘要框”或精确的知识图谱信息
- [Tavily](https://www.tavily.com/)：根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。

## 环境变量配置
在项目根目录新建 .env 文件，设置环境变量
```bash
LLM_MODEL_ID="xxx"
LLM_BASE_URL="xxx"
LLM_API_KEY="xxx"
OPENAI_API_KEY="xxx"
SERPAPI_API_KEY="xxx"
TAVILY_API_KEY="xxx"
```

## 环境依赖
```bash
pip install requests tavily-python openai
pip install google-search-results
pip install dotenv
pip install gradio
pip install autogen-agentchat==0.7.5
pip install autogen-ext[openai,azure]==0.7.5
```

## 样例
`python webui/react_agent_webui.py`