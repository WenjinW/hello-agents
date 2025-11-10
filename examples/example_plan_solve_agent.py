'''
Author: wenjinwang 314984354@qq.com
Date: 2025-11-10 17:11:03
LastEditors: wenjinwang 314984354@qq.com
LastEditTime: 2025-11-10 17:11:03
FilePath: /hello-agents/examples/example_plan_solve_agent.py
Description: 

'''
from agents.plan_solve_agent import PlanAndSolveAgent
from models.hello_agents_llm import HelloAgentsLLM


if __name__ == "__main__":
    llm_client = HelloAgentsLLM()
    plan_solve_agent = PlanAndSolveAgent(llm_client)
    question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
    plan_solve_agent.run(question=question)