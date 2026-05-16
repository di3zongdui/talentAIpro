"""
Phase 0.5：批量评分脚本
=======================
读取 HTML 界面导出的 JSON 数据，调 LLM 评分并生成报告

用法：
  1. 收集完所有人答题后，导出 JSON 文件放在 phase05_results/ 中
  2. python phase05_score.py
  3. 查看评分结果
"""

import json
import sys
from pathlib import Path
try:
    import openai
except ImportError:
    print("❌ 请先安装 openai: pip install openai")
    sys.exit(1)

# ===== 配置 =====
import os
# 优先取环境变量，否则后续会提示输入
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY") or ""
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V4-Flash"   # 评分用模型

SCORING_PROMPT = """请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度与行为锚点：
1. ai_operation (AI操作力) - 知道AI能做什么/不能做什么、如何指挥AI
2. critical_integration (批判整合力) - 评估AI输出质量、整合到工作流
3. ethical_judgment (伦理判断力) - 识别AI伦理风险、保持人文底线
4. workflow_orchestration (流程编排力) - 设计人机协作流程、管理Agent
5. ai_collaborative_creativity (AI协同创造力) - 与AI配合创造、叙事表达能力
6. ai_adaptability (AI适应力) - 持续学习、适应AI变化、保持专注

评分规则：
- 0-20: 无/极弱, 21-40: 弱, 41-60: 中等, 61-80: 强, 81-100: 极强
- 严格基于回答内容，不要自由发挥
- 如果某维度没有相关回答，给0分并注明"无相关回答"

输出格式（严格JSON）：
{{
  "ai_operation": {{"score": 0-100, "evidence": "简短说明"}},
  "critical_integration": {{"score": 0-100, "evidence": "..."}},
  "ethical_judgment": {{"score": 0-100, "evidence": "..."}},
  "workflow_orchestration": {{"score": 0-100, "evidence": "..."}},
  "ai_collaborative_creativity": {{"score": 0-100, "evidence": "..."}},
  "ai_adaptability": {{"score": 0-100, "evidence": "..."}}
}}

只输出JSON，不要额外说明。"""


def score_one(data):
    """为一份数据评分"""
    dialogue = "\n".join([
        f"第{r['round']}轮（{r['dimension']}）: {r['answer']}"
        for r in data.get('responses', [])
    ])

    if not dialogue.strip():
        return None

    client = openai.OpenAI(base_url=BASE_URL, api_key=SILICONFLOW_API_KEY)

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个合能评分员，严格按评分协议打分，只输出JSON。"},
                {"role": "user", "content": SCORING_PROMPT.format(dialogue=dialogue)}
            ],
            temperature=0.1,
            max_tokens=2048,
            extra_body={"thinking_mode": "high"}
        )

        raw = resp.choices[0].message.content.strip()
        # 提取JSON
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        scores = json.loads(raw)
        return scores

    except Exception as e:
        print(f"  ❌ 评分失败: {e}")
        return None


def main():
    print("=" * 60)
    print("  Phase 0.5 批量评分")
    print("=" * 60)

    if not SILICONFLOW_API_KEY:
        key = input("\n🔑 请输入你的硅基流动 API Key: ").strip()
        if not key:
            print("❌ 需要API Key才能评分")
            print("获取地址: https://cloud.siliconflow.cn/account/apikey")
            sys.exit(1)
        SILICONFLOW_API_KEY = key

    # 查找数据文件
    results_dir = Path(__file__).parent / "phase05_results"
    if not results_dir.exists():
        results_dir.mkdir(exist_ok=True)
        print(f"\n📁 已创建文件夹: {results_dir}")
        print("请将 HTML 界面导出的 JSON 文件放入此文件夹后再运行")
        sys.exit(0)

    json_files = list(results_dir.glob("*.json"))
    if not json_files:
        print(f"\n⚠️ {results_dir} 中没有 JSON 文件")
        print("请先使用 phase05-test.html 收集回答，导出JSON放到此文件夹")
        sys.exit(0)

    print(f"\n📂 找到 {len(json_files)} 个数据文件\n")

    # 逐个评分
    results = []
    for fpath in sorted(json_files):
        print(f"📄 正在评分: {fpath.name}")
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            scores = score_one(data)
            if scores:
                data["scores"] = scores
                data["scored_at"] = __import__('datetime').datetime.now().isoformat()
                fpath.write_text(json.dumps(data, ensure_ascii=False, indent=2))
                score_summary = {k: v['score'] for k, v in scores.items()}
                print(f"  ✅ {score_summary}")
                results.append((fpath.name, scores))
        except Exception as e:
            print(f"  ❌ 读取失败: {e}")

    # 生成汇总报告
    if results:
        print(f"\n{'='*60}")
        print(f"  评分汇总报告")
        print(f"{'='*60}")

        # 表头
        dims = ["ai_operation", "critical_integration", "ethical_judgment",
                "workflow_orchestration", "ai_collaborative_creativity", "ai_adaptability"]
        dim_labels = ["AI操作力", "批判整合力", "伦理判断力",
                      "流程编排力", "AI协同创造力", "AI适应力"]

        header = f"{'被试':<20s}" + " ".join(f"{l:>10s}" for l in dim_labels) + f" {'总分':>5s}"
        print(header)
        print("-" * len(header))

        all_scores = []
        for name, scores in results:
            row = [name[:18]]
            srow = []
            for d in dims:
                s = scores.get(d, {}).get('score', 0)
                srow.append(s)
                row.append(f"{s:>10d}")
            total = sum(srow)
            row.append(f"{total:>5d}")
            print(" ".join(row))
            all_scores.append(srow)

        # 平均分
        if all_scores:
            avgs = [sum(col)/len(col) for col in zip(*all_scores)]
            avg_row = f"{'平均分':<20s}" + " ".join(f"{a:>10.1f}" for a in avgs)
            avg_row += f" {sum(avgs):>5.1f}"
            print("-" * len(header))
            print(avg_row)

        print(f"\n✅ 评分完成！结果已保存到各 JSON 文件中")
    else:
        print("\n⚠️ 没有成功评分的文件")


if __name__ == "__main__":
    main()
