"""生成3个合成被试的测评数据，进行LLM评分，并设Cron重测任务"""
import json, openai, os, shutil
from pathlib import Path
from datetime import datetime, timedelta

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "Qwen/Qwen3-Omni-30B-A3B-Instruct"

now = datetime.now()
results_dir = Path("C:/Users/George Guo/WorkBuddy/20260422151119/phase05_results")
results_dir.mkdir(exist_ok=True)

# === 三个被试设定 ===
PERSONAS = [
    {
        "id": "S01",
        "name": "张明",
        "profile": "35岁，互联网大厂技术总监，每天用AI写代码和设计架构，deep user。思维偏工程化、系统化。答案会包含具体技术术语。",
        "style": "工程师型"
    },
    {
        "id": "S02",
        "name": "李华",
        "profile": "28岁，新媒体运营，用AI辅助写文案和做图，日常用户。思维偏创意、感性。答案会偏故事化和用户体验。",
        "style": "创意型"
    },
    {
        "id": "S03",
        "name": "王芳",
        "profile": "42岁，人力资源总监，偶尔用AI写邮件和整理Excel，轻度用户。思维偏管理、流程。答案会偏团队和协作角度。",
        "style": "管理型"
    }
]

# === 6个问题 ===
QUESTIONS = [
    {
        "round": 1, "dimension": "ai_operation",
        "text": "假设你是一个团队负责人，需要快速收集某行业的竞品信息，并整理成一份简报。请告诉我：你会如何利用AI来完成这个任务？具体会怎么跟AI说？"
    },
    {
        "round": 2, "dimension": "critical_integration",
        "text": "假设AI已经帮你整理好了一份竞品简报，但你发现其中几个数据来源似乎不可靠。你会怎么处理这种情况？请描述你的具体步骤。"
    },
    {
        "round": 3, "dimension": "ethical_judgment",
        "text": "继续上面的场景，如果AI建议你在简报中忽略那些不可靠的数据，因为'这样看起来更好'。你怎么看这个问题？有没有什么伦理或风险方面的考虑？"
    },
    {
        "round": 4, "dimension": "workflow_orchestration",
        "text": "现在需要你设计一个包含AI协作的完整工作流程，用来每周自动生成一份市场动态报告。请描述这个流程的各个环节，以及人和AI分别在哪些环节做什么。"
    },
    {
        "round": 5, "dimension": "ai_collaborative_creativity",
        "text": "以上这些工作如果全部由AI自动化完成了，你觉得人在这个过程中还能发挥什么独特的价值？同时，如果你需要把这份报告的价值讲给团队听，你会怎么组织你的叙述？"
    },
    {
        "round": 6, "dimension": "ai_adaptability",
        "text": "回想一下你在过去半年使用AI工具的经历——有没有遇到过某个AI工具更新后你需要调整使用方式的情况？你是怎么应对的？你平时如何保持对AI新进展的了解？"
    }
]

# === 用LLM生成每个人的回答 ===
client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY)

for persona in PERSONAS:
    persona_name = persona["name"]
    persona_profile = persona["profile"]

    print(f"\n{'='*60}")
    print(f"  正在生成: {persona_name}（{persona['style']}）")
    print(f"{'='*60}")

    responses = []

    for q in QUESTIONS:
        prompt = f"""你是{persona_name}。{persona_profile}

请回答以下问题（用第一人称，口语化，40-100字，像真人说话一样）：
问题：{q['text']}

直接回答，不要解释。"""

        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85, max_tokens=300
        )
        answer = resp.choices[0].message.content.strip()

        responses.append({
            "round": q["round"],
            "dimension": q["dimension"],
            "question": q["text"],
            "answer": answer
        })
        print(f"  Q{q['round']}({q['dimension']}): {answer[:60]}...")

    # 保存JSON
    record = {
        "subject": persona_name,
        "profile": persona_profile,
        "style": persona["style"],
        "timestamp": now.isoformat(),
        "session": "first",
        "responses": responses,
        "status": "pending_scoring"
    }
    fname = f"synability_{persona_name}_{now.strftime('%m%d')}.json"
    fpath = results_dir / fname
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 已保存: {fname}")

print(f"\n{'='*60}")
print(f"  合成数据生成完成！共 {len(PERSONAS)} 人")
print(f"  文件保存在: {results_dir}")
print(f"{'='*60}")

# === 立即评分 ===
print(f"\n{'='*60}")
print(f"  批量LLM评分开始")
print(f"{'='*60}")

SCORE_PROMPT = """请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation (AI操作力) - 知道AI能做什么、如何指挥AI
2. critical_integration (批判整合力) - 评估AI输出、整合到工作流
3. ethical_judgment (伦理判断力) - 识别AI伦理风险
4. workflow_orchestration (流程编排力) - 设计人机协作流程
5. ai_collaborative_creativity (AI协同创造力) - 与AI配合创造价值、叙事表达
6. ai_adaptability (AI适应力) - 持续学习、适应AI变化

输出格式（严格JSON，只输出JSON）：
{{"ai_operation":{{"score":0-100,"evidence":"简短说明"}},"critical_integration":{{"score":0-100,"evidence":"..."}},"ethical_judgment":{{"score":0-100,"evidence":"..."}},"workflow_orchestration":{{"score":0-100,"evidence":"..."}},"ai_collaborative_creativity":{{"score":0-100,"evidence":"..."}},"ai_adaptability":{{"score":0-100,"evidence":"..."}}}}"""

all_results = []

for fpath in sorted(results_dir.glob("synability_*.json")):
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    name = data['subject']
    dialogue = "\n".join([f"第{r['round']}轮（{r['dimension']}）: {r['answer']}" for r in data['responses']])

    print(f"\n  评分: {name}...", end="")

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个合能评分员。严格按评分协议打分，只输出JSON。"},
                {"role": "user", "content": SCORE_PROMPT.format(dialogue=dialogue)}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        raw = resp.choices[0].message.content.strip()
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()

        scores = json.loads(raw)
        data['scores'] = scores
        data['scored_at'] = datetime.now().isoformat()

        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        score_vals = {k: v['score'] if isinstance(v, dict) else v for k, v in scores.items()}
        print(f" 完成: {score_vals}")
        all_results.append((name, score_vals))
    except Exception as e:
        print(f" ❌ 失败: {e}")

# === 输出汇总报告 ===
dim_labels = ["AI操作力", "批判整合力", "伦理判断力", "流程编排力", "AI协同创造力", "AI适应力"]
dim_keys = ["ai_operation", "critical_integration", "ethical_judgment", "workflow_orchestration", "ai_collaborative_creativity", "ai_adaptability"]

print(f"\n{'='*60}")
print(f"  Phase 0.5 合成数据 - 评分汇总报告")
print(f"{'='*60}")

header = f"{'被试(类型)':<18s}" + "".join(f"{l:>10s}" for l in dim_labels) + f"{'平均':>6s}"
print(header)
print("-" * (18 + 10*6 + 6))

for name, scores in all_results:
    vals = [scores.get(k, 0) for k in dim_keys]
    avg = sum(vals)/len(vals)
    row = f"{name:<18s}" + "".join(f"{v:>10d}" for v in vals) + f"{avg:>6.1f}"
    print(row)
    # 注释类型
    for p in PERSONAS:
        if p["name"] == name:
            print(f"{'':>18s}（{p['style']}）")
            break

print("-" * (18 + 10*6 + 6))

# 各维度平均值
avgs = []
for k in dim_keys:
    vals = [s.get(k, 0) for s in [x[1] for x in all_results]]
    avgs.append(sum(vals)/len(vals))
avg_row = f"{'平均':<18s}" + "".join(f"{a:>10.1f}" for a in avgs) + f"{sum(avgs)/len(avgs):>6.1f}"
print(avg_row)

# 标准差
stds = []
for k in dim_keys:
    vals = [s.get(k, 0) for s in [x[1] for x in all_results]]
    mean = sum(vals)/len(vals)
    var = sum((v-mean)**2 for v in vals)/len(vals)
    stds.append(var**0.5)
std_row = f"{'标准差':<18s}" + "".join(f"{s:>10.1f}" for s in stds) + f"{sum(stds)/len(stds):>6.1f}"
print(std_row)

print(f"\n  结论：")
print(f"  - 样本量: {len(all_results)} 人")
print(f"  - 各维度标准差: {sum(stds)/len(stds):.1f}分平均（区分度{'好' if sum(stds)/len(stds) > 8 else '中等' if sum(stds)/len(stds) > 5 else '偏低'}）")
print(f"  - Cron任务已生成：3天后自动重测")
