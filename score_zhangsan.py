"""评分张三 - 调试版"""
import json, openai

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V4-Flash"

with open("C:/Users/George Guo/Downloads/synability_张三_2026-05-10.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dialogue = "\n".join([f"第{r['round']}轮（{r['dimension']}）: {r['answer']}" for r in data['responses']])

prompt = f"""请基于以下对话记录评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation - 知道AI能做什么、如何指挥AI
2. critical_integration - 评估AI输出正确性、整合进工作流
3. ethical_judgment - 识别AI伦理风险、保持底线
4. workflow_orchestration - 设计人机协作流程
5. ai_collaborative_creativity - 与AI配合创造、叙事表达
6. ai_adaptability - 持续学习适应AI变化

输出格式：
ai_operation: score, evidence
critical_integration: score, evidence
ethical_judgment: score, evidence
workflow_orchestration: score, evidence
ai_collaborative_creativity: score, evidence
ai_adaptability: score, evidence"""

client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY)
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role":"system","content":"你是一个合能评分员。严格按0-100评分。"},
        {"role":"user","content":prompt}
    ],
    temperature=0.1, max_tokens=2048,
    extra_body={"thinking_mode":"high"}
)

raw = resp.choices[0].message.content.strip()
print(raw)
