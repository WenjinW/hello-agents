from agents.reflection_agent import ReflectionAgent
from models.hello_agents_llm import HelloAgentsLLM


if __name__ == "__main__":
    llm_client = HelloAgentsLLM()
    reflection_agent = ReflectionAgent(llm_client=llm_client, max_iterations=3)
    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    reflection_agent.run(task=task)