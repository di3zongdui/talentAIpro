"""乔治 第1次 vs 第3天重测 对比"""
import json, openai

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V4-Flash"

dims = ["ai_operation","critical_integration","ethical_judgment","workflow_orchestration","ai_collaborative_creativity","ai_adaptability"]
labels = ["AI操作力","批判整合力","伦理判断力","流程编排力","AI协同创造力","AI适应力"]

DATA_NEW = "C:/Users/George Guo/Downloads/synability_乔治_2026-05-10.json"
DATA_OLD = "C:/Users/George Guo/WorkBuddy/20260422151119/phase05_results/synability_乔治_2026-05-07.json"

def load_and_score(path):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    dialogue = "\n".join([f"第{r['round']}轮（{r['dimension']}）: {r['answer']}" for r in d['responses']])

    prompt = f"""请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation (AI操作力)
2. critical_integration (批判整合力)
3. ethical_judgment (伦理判断力)
4. workflow_orchestration (流程编排力)
5. ai_collaborative_creativity (AI协同创造力)
6. ai_adaptability (AI适应力)

输出格式（严格JSON）：
{{"ai_operation":{{"score":0-100,"evidence":"简短说明"}},"critical_integration":{{"score":0-100,"evidence":"..."}},"ethical_judgment":{{"score":0-100,"evidence":"..."}},"workflow_orchestration":{{"score":0-100,"evidence":"..."}},"ai_collaborative_creativity":{{"score":0-100,"evidence":"..."}},"ai_adaptability":{{"score":0-100,"evidence":"..."}}}}"""

    client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY)
    # V4 Flash 使用 Think High 评分模式
    extra = {}
    if MODEL == "deepseek-ai/DeepSeek-V4-Flash":
        extra["extra_body"] = {"thinking_mode": "high"}
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":"你是一个合能评分员。严格按评分协议打分，只输出JSON。"},{"role":"user","content":prompt}],
        temperature=0.1, max_tokens=2048, **extra
    )
    raw = resp.choices[0].message.content.strip()
    if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw), [r['answer'][:40] for r in d['responses']]

print("="*60)
print("  乔治 · 3天后重测对比")
print("="*60)

s1, a1 = load_and_score(DATA_OLD)
s2, a2 = load_and_score(DATA_NEW)

print(f"\n{'维度':<12s} {'3天前(5/7)':>10s} {'今天(5/10)':>10s} {'变化':>6s}")
print("-" * 42)
total1, total2, total_diff = 0, 0, 0
for k, label in zip(dims, labels):
    v1 = s1[k]['score'] if isinstance(s1.get(k), dict) else s1.get(k, 0)
    v2 = s2[k]['score'] if isinstance(s2.get(k), dict) else s2.get(k, 0)
    diff = v2 - v1
    total1 += v1; total2 += v2; total_diff += abs(diff)
    arrow = '↑' if diff > 0 else ('↓' if diff < 0 else '→')
    print(f"  {label:<12s} {v1:>8d} {v2:>8d} {'+' if diff>0 else ''}{diff:+d}{arrow}")
print("-" * 42)
print(f"  {'平均分':<12s} {total1/6:>8.1f} {total2/6:>8.1f}")
print(f"\n  {'平均绝对差':<12s} {total_diff/6:.1f} 分")
print(f"  {'判断':<12s} {'✅ 稳定' if total_diff/6 < 15 else '⚠️ 需关注'}")

# 回答对比
print(f"\n{'='*60}")
print(f"  回答对比")
print(f"{'='*60}")
for i, (k, label) in enumerate(zip(dims, labels)):
    print(f"\n  {label} (Q{i+1}):")
    print(f"    3天前: {a1[i]}")
    print(f"    今天:  {a2[i]}")
