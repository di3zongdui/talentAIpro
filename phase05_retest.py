"""Phase 0.5 重测：3个合成被试第二次回答"""
import json, openai
from pathlib import Path
from datetime import datetime

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "Qwen/Qwen3-Omni-30B-A3B-Instruct"

results_dir = Path("C:/Users/George Guo/WorkBuddy/20260422151119/phase05_results")

# 三个被试的设定（加了时间偏移暗示：3天后的心态可能有微妙变化）
PERSONAS = [
    {"name":"张明","style":"工程师型",
     "retest_hint":"3天过去了，你刚从一场技术复盘会出来，心态更加务实。"},
    {"name":"李华","style":"创意型",
     "retest_hint":"3天过去了，你刚追完一个热点事件，心态更加兴奋和开放。"},
    {"name":"王芳","style":"管理型",
     "retest_hint":"3天过去了，你刚处理完一次团队冲突，心态更加关注协作。"}
]

QUESTIONS = [
    {"round":1,"dimension":"ai_operation",
     "text":"假设你是一个团队负责人，需要快速收集某行业的竞品信息，并整理成一份简报。请告诉我：你会如何利用AI来完成这个任务？具体会怎么跟AI说？"},
    {"round":2,"dimension":"critical_integration",
     "text":"假设AI已经帮你整理好了一份竞品简报，但你发现其中几个数据来源似乎不可靠。你会怎么处理这种情况？请描述你的具体步骤。"},
    {"round":3,"dimension":"ethical_judgment",
     "text":"继续上面的场景，如果AI建议你在简报中忽略那些不可靠的数据，因为'这样看起来更好'。你怎么看这个问题？有没有什么伦理或风险方面的考虑？"},
    {"round":4,"dimension":"workflow_orchestration",
     "text":"现在需要你设计一个包含AI协作的完整工作流程，用来每周自动生成一份市场动态报告。请描述这个流程的各个环节，以及人和AI分别在哪些环节做什么。"},
    {"round":5,"dimension":"ai_collaborative_creativity",
     "text":"以上这些工作如果全部由AI自动化完成了，你觉得人在这个过程中还能发挥什么独特的价值？同时，如果你需要把这份报告的价值讲给团队听，你会怎么组织你的叙述？"},
    {"round":6,"dimension":"ai_adaptability",
     "text":"回想一下你在过去半年使用AI工具的经历——有没有遇到过某个AI工具更新后你需要调整使用方式的情况？你是怎么应对的？你平时如何保持对AI新进展的了解？"}
]

SCORE_PROMPT = """请基于以下对话记录，评估用户的6个维度分数（0-100）。

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

print("="*60)
print("  Phase 0.5 重测 - 生成3人第二次回答 + 评分")
print("="*60)

for p in PERSONAS:
    name = p["name"]
    hint = p["retest_hint"]
    print(f"\n--- {name}（{p['style']}）---")

    responses = []
    for q in QUESTIONS:
        prompt = f"""你是{name}。{hint}

请重新回答以下问题（这次回答不要和上次一样，语气略不同，但观点可以相似）：
问题：{q['text']}

直接回答，40-100字，口语化。"""

        resp = client.chat.completions.create(
            model=MODEL, messages=[{"role":"user","content":prompt}],
            temperature=0.85, max_tokens=300
        )
        answer = resp.choices[0].message.content.strip()
        responses.append({
            "round":q["round"],"dimension":q["dimension"],
            "question":q["text"],"answer":answer
        })
        print(f"  Q{q['round']}({q['dimension']}): {answer[:50]}...")

    # 评分
    dialogue = "\n".join([f"第{r['round']}轮（{r['dimension']}）: {r['answer']}" for r in responses])
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role":"system","content":"你是一个合能评分员。严格按评分协议打分，只输出JSON。"},
                {"role":"user","content":SCORE_PROMPT.format(dialogue=dialogue)}
            ],
            temperature=0.1, max_tokens=2048
        )
        raw = resp.choices[0].message.content.strip()
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()
        scores = json.loads(raw)
    except Exception as e:
        print(f"  ERROR: {e}")
        scores = {}

    record = {
        "subject": name,
        "style": p["style"],
        "timestamp": datetime.now().isoformat(),
        "session": "retest",
        "responses": responses,
        "scores": scores,
        "status": "scored"
    }
    fname = f"synability_{name}_{datetime.now().strftime('%m%d')}_retest.json"
    with open(results_dir / fname, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 已保存+评分: {fname}")

# 对比分析
print(f"\n{'='*60}")
print(f"  重测信度分析")
print(f"{'='*60}")

dim_keys = ["ai_operation","critical_integration","ethical_judgment","workflow_orchestration","ai_collaborative_creativity","ai_adaptability"]
dim_labels = ["AI操作力","批判整合力","伦理判断力","流程编排力","AI协同创造力","AI适应力"]

for p in PERSONAS:
    name = p["name"]
    first_files = list(results_dir.glob(f"synability_{name}_0507.json"))
    retest_files = list(results_dir.glob(f"synability_{name}_0507_retest.json"))

    if not first_files or not retest_files:
        print(f"\n  {name}: 缺少数据文件，跳过")
        continue

    with open(first_files[0], 'r', encoding='utf-8') as f:
        first_data = json.load(f)
    with open(retest_files[0], 'r', encoding='utf-8') as f:
        retest_data = json.load(f)

    first_scores = first_data.get('scores', {})
    retest_scores = retest_data.get('scores', {})

    print(f"\n  {name}（{p['style']}）:")
    total_diff = 0
    for k, label in zip(dim_keys, dim_labels):
        v1 = first_scores.get(k,{}).get('score',0) if isinstance(first_scores.get(k), dict) else first_scores.get(k,0)
        v2 = retest_scores.get(k,{}).get('score',0) if isinstance(retest_scores.get(k), dict) else retest_scores.get(k,0)
        diff = abs(v1 - v2)
        total_diff += diff
        print(f"    {label}: {v1} -> {v2} (差{diff})")
    avg_diff = total_diff / len(dim_keys)
    print(f"    平均差: {avg_diff:.1f}  |  判断: {'OK 稳定' if avg_diff < 15 else ' 不一致'}")

print(f"\n{'='*60}")
print(f"  重测完成！")
print(f"  结果保存在: {results_dir}")
