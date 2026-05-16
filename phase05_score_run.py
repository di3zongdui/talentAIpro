# 合能评分：一键运行
import json, sys, os
sys.path.insert(0, r'C:\Users\George Guo\WorkBuddy\20260422151119')
import openai

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V4-Flash"

DATA_FILE = r'C:\Users\George Guo\WorkBuddy\20260422151119\phase05_results\synability_乔治_2026-05-07.json'
OUTPUT_FILE = r'C:\Users\George Guo\WorkBuddy\20260422151119\phase05_results\synability_乔治_2026-05-07_scored.json'

PROMPT = """请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation (AI操作力) - 知道AI能做什么/不能做什么、如何指挥AI
2. critical_integration (批判整合力) - 评估AI输出质量、整合到工作流
3. ethical_judgment (伦理判断力) - 识别AI伦理风险、保持人文底线
4. workflow_orchestration (流程编排力) - 设计人机协作流程、管理Agent
5. ai_collaborative_creativity (AI协同创造力) - 与AI配合创造、叙事表达
6. ai_adaptability (AI适应力) - 持续学习、适应AI变化、保持专注

评分规则：0-20极弱 21-40弱 41-60中等 61-80强 81-100极强

输出格式（严格JSON）：
{{
  "ai_operation": {{"score": 0-100, "evidence": "简短说明"}},
  "critical_integration": {{"score": 0-100, "evidence": "..."}},
  "ethical_judgment": {{"score": 0-100, "evidence": "..."}},
  "workflow_orchestration": {{"score": 0-100, "evidence": "..."}},
  "ai_collaborative_creativity": {{"score": 0-100, "evidence": "..."}},
  "ai_adaptability": {{"score": 0-100, "evidence": "..."}}
}}"""

import subprocess
subprocess.run('chcp 65001', shell=True, capture_output=True)

print("=" * 56)
print("  合能 Phase 0.5 - LLM自动评分")
print("=" * 56)

# 读取数据
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

dialogue = "\n".join([f"第{r['round']}轮（{r['dimension']}）: {r['answer']}" for r in data['responses']])
print(f"\n  被试: {data['subject']}")
print(f"  共 {len(data['responses'])} 轮对话\n")

# 调用LLM评分
client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY)
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是一个合能评分员，严格按评分协议打分，只输出JSON。"},
        {"role": "user", "content": PROMPT.format(dialogue=dialogue)}
    ],
    temperature=0.1,
    max_tokens=2048,
    extra_body={"thinking_mode": "high"}
)

raw = resp.choices[0].message.content.strip()
if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()

scores = json.loads(raw)

# 保存结果
data['scores'] = scores
data['scored_at'] = __import__('datetime').datetime.now().isoformat()
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 显示结果
print(f"{'维度':<30s} {'分数':>5s}  {'证据':<30s}")
print("-" * 80)
for dim, info in scores.items():
    s = info.get('score', 0)
    e = info.get('evidence', '')[:40]
    print(f"{dim:<30s} {s:>5d}  {e}")

avg = sum(v.get('score',0) for v in scores.values()) / len(scores)
print("-" * 80)
print(f"{'平均分':<30s} {avg:>5.1f}")
print(f"\n  OK 结果已保存到: {OUTPUT_FILE}")
