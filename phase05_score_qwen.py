"""评分对比：Qwen3-Omni-30B"""
import json, openai

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "Qwen/Qwen3-Omni-30B-A3B-Instruct"

DATA_FILE = "C:/Users/George Guo/Downloads/synability_乔治_2026-05-07.json"

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

dialogue = "\n".join([f"第{r['round']}轮（{r['dimension']}）: {r['answer']}" for r in data['responses']])

prompt = f"""请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation (AI操作力) - 知道AI能做什么、如何指挥AI
2. critical_integration (批判整合力) - 评估AI输出、整合到工作流
3. ethical_judgment (伦理判断力) - 识别AI伦理风险
4. workflow_orchestration (流程编排力) - 设计人机协作流程
5. ai_collaborative_creativity (AI协同创造力) - 与AI配合创造价值
6. ai_adaptability (AI适应力) - 持续学习、适应AI变化

输出格式（严格JSON）：
{{"ai_operation":{{"score":0-100,"evidence":"简短说明"}},"critical_integration":{{"score":0-100,"evidence":"..."}},"ethical_judgment":{{"score":0-100,"evidence":"..."}},"workflow_orchestration":{{"score":0-100,"evidence":"..."}},"ai_collaborative_creativity":{{"score":0-100,"evidence":"..."}},"ai_adaptability":{{"score":0-100,"evidence":"..."}}}}

只输出JSON，不要额外说明。"""

client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY)
resp = client.chat.completions.create(
    model=MODEL, messages=[
        {"role": "system", "content": "你是一个合能评分员。严格按评分协议打分，只输出JSON。"},
        {"role": "user", "content": prompt}
    ], temperature=0.1, max_tokens=2048
)

raw = resp.choices[0].message.content.strip()
if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()

scores = json.loads(raw)

print("=" * 56)
print("  合能评分对比 Qwen3-Omni vs V4 Flash vs 小策")
print("=" * 56)

# V4 Flash 结果（上次跑的）
v4_scores = {"ai_operation":85,"critical_integration":90,"ethical_judgment":95,"workflow_orchestration":92,"ai_collaborative_creativity":80,"ai_adaptability":88}
ce_scores = {"ai_operation":82,"critical_integration":88,"ethical_judgment":92,"workflow_orchestration":90,"ai_collaborative_creativity":78,"ai_adaptability":86}

labels = {"ai_operation":"AI操作力","critical_integration":"批判整合力","ethical_judgment":"伦理判断力","workflow_orchestration":"流程编排力","ai_collaborative_creativity":"AI协同创造力","ai_adaptability":"AI适应力"}

print(f"\n{'维度':<12s} {'Qwen3-Omni':>8s} {'V4 Flash':>8s} {'小策':>6s} {'差异':>6s}")
print("-" * 44)

qwen_total = 0; v4_total = 0; ce_total = 0
for dim, label in labels.items():
    q = scores.get(dim, {}).get('score', 0)
    if isinstance(scores.get(dim), (int, float)):
        q = scores[dim]
    v = v4_scores[dim]
    c = ce_scores[dim]
    d = abs(q - v)
    qwen_total += q; v4_total += v; ce_total += c
    print(f"{label:<12s} {q:>8d} {v:>8d} {c:>6d} {'+' if q>v else ''}{q-v:>+4d}")

print("-" * 44)
print(f"{'平均分':<12s} {qwen_total/6:>8.1f} {v4_total/6:>8.1f} {ce_total/6:>6.1f} {abs(qwen_total-v4_total)/6:>5.1f}")

print(f"\nQwen3-Omni 完整输出:")
print(json.dumps(scores, ensure_ascii=False, indent=2))
