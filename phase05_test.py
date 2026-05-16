"""
Phase 0.5：合能评估引擎 - 模型重测信度实验
===========================================
使用 TalentAI_Pro 现有 LLM Gateway 执行测试

用法：
  1. 确认服务器已启动 (python api/server.py & python phase05_test.py)
     或使用离线模式 (python phase05_test.py --mode run --offline)
  2. python phase05_test.py --mode run --model syn-v4-flash  # V4 Flash首测
  3. python phase05_test.py --mode retest --model syn-v4-flash  # 3天后重测
  4. python phase05_test.py --mode analyze  # 计算重测信度

模型切换：
  --model syn-v4-flash    # V4 Flash - 首推（极低成本）
  --model syn-v32         # V3.2 - 质量最优备选
  --model syn-glm-z1      # GLM-Z1-32B - 推理备选
"""

import json
import time
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# ========== 导入 TalentAI_Pro Gateway ==========
# 确保能导入 TalentAI_Pro 模块
sys.path.insert(0, str(Path(__file__).parent))
from llm import LLMGateway, Message
from llm.gateway import LLMConfig

# ========== 配置 ==========
# 5轮对话模板
DIALOGUE_TEMPLATES = [
    {
        "round": 1,
        "dimension": "ai_operation",
        "prompt": "假设你是一个团队负责人，需要快速收集某行业的竞品信息，并整理成一份简报。请告诉我：你会如何利用AI来完成这个任务？具体会怎么跟AI说？"
    },
    {
        "round": 2,
        "dimension": "critical_integration",
        "sub_prompts": [
            {"part": "前段", "dim": "critical_integration",
             "text": "假设AI已经帮你整理好了一份竞品简报，但你发现其中几个数据来源似乎不可靠。你会怎么处理这种情况？请描述你的具体步骤。"},
            {"part": "后段", "dim": "ethical_judgment",
             "text": "继续上面的场景，如果AI建议你在简报中忽略那些不可靠的数据，因为'这样看起来更好'。你怎么看这个问题？有没有什么伦理或风险方面的考虑？"}
        ]
    },
    {
        "round": 3,
        "dimension": "workflow_orchestration",
        "prompt": "现在需要你设计一个包含AI协作的完整工作流程，用来每周自动生成一份市场动态报告。请描述这个流程的各个环节，以及人和AI分别在哪些环节做什么。"
    },
    {
        "round": 4,
        "dimension": "ai_collaborative_creativity",
        "prompt": "以上这些工作如果全部由AI自动化完成了，你觉得人在这个过程中还能发挥什么独特的价值？同时，如果你需要把这份报告的价值讲给团队听，你会怎么组织你的叙述？"
    },
    {
        "round": 5,
        "dimension": "ai_adaptability",
        "prompt": "回想一下你在过去半年使用AI工具的经历——有没有遇到过某个AI工具更新后你需要调整使用方式的情况？你是怎么应对的？你平时如何保持对AI新进展的了解？"
    }
]

# V4 Flash 的评分模式参数
THINKING_MODES = {
    "syn-v4-flash": {"thinking_mode": "high"},  # Think High评分
    "syn-v32": None,
    "syn-glm-z1": None
}

# 6维度评分锚点（评分Prompt用）
SCORING_ANCHORS = """
评分协议（每维度0-100，5级行为锚点）：

1. AI操作力：
  Level 1 (0-20): 认为AI什么都能做或完全不能做；无法用自然语言向AI描述任务
  Level 2 (21-40): 知道AI有局限性但描述模糊；能用简单指令指挥AI
  Level 3 (41-60): 能列举1-2种AI典型错误类型；能给出较清晰指令
  Level 4 (61-80): 能区分任务是否适合AI并说明原因；能给出多步骤指令
  Level 5 (81-100): 能精确描述AI能力边界并含风险策略；能用系统化Prompt

2. 批判整合力：
  Level 1 (0-20): 完全接受AI输出，不加判断
  Level 2 (21-40): 知道需要验证但缺乏方法
  Level 3 (41-60): 能指出明显错误；知道交叉验证方法
  Level 4 (61-80): 能系统性评估AI输出质量（多源验证、逻辑检查）
  Level 5 (81-100): 能在确保AI输出质量的同时无缝整合到工作流

3. AI协同创造力：
  Level 1 (0-20): 依赖AI完成所有创意任务
  Level 2 (21-40): 能使用AI产生灵感但无法独立优化
  Level 3 (41-60): 能结合AI输出和自己的创意，形成更好方案
  Level 4 (61-80): 能发现AI做不到的事并发挥人的独特价值；能用故事组织复杂信息
  Level 5 (81-100): 能系统性利用AI放大创造力；叙事表达影响他人决策

4. 流程编排力：
  Level 1 (0-20): 所有任务自己完成，不使用工具协作
  Level 2 (21-40): 能用AI完成单一任务，但无法串联多个步骤
  Level 3 (41-60): 能设计简单的人机协作流程（1-2个交接点）
  Level 4 (61-80): 能拆解复杂任务为人机协作链条（3个以上环节）
  Level 5 (81-100): 能管理多个AI Agent并行协作；能设计异常处理机制

5. AI适应力：
  Level 1 (0-20): 拒绝使用新AI工具；容易在信息中迷失
  Level 2 (21-40): 被动使用已被验证的AI工具
  Level 3 (41-60): 会主动尝试新AI工具并评估效果；有基本时间管理
  Level 4 (61-80): 随AI进化持续调整工作方法；专注力管理得当
  Level 5 (81-100): 系统性追踪AI技术演进；深度工作能力强

6. 伦理判断力：
  Level 1 (0-20): 不考虑AI的伦理风险
  Level 2 (21-40): 知道有伦理风险但无法具体描述
  Level 3 (41-60): 能列举1-2个具体AI伦理问题
  Level 4 (61-80): 能在工作中主动识别并规避AI伦理风险
  Level 5 (81-100): 能系统性维护伦理底线，影响团队规范
"""

# 被试列表（4人快速验证）
SUBJECTS = ["S01", "S02", "S03", "S04"]


class SynAbilityTester:
    """合能评估引擎 - Phase 0.5 测试器"""

    def __init__(self, offline=False):
        self.offline = offline
        if not offline:
            # 使用 TalentAI_Pro Gateway
            config = LLMConfig()
            config.default_provider = "siliconflow"
            config.default_model = "syn-v4-flash"
            config.temperature = 0.1
            self.gateway = LLMGateway(config)

            # Gateway会从 llm_providers.json 读取配置
            registry_path = Path(__file__).parent.parent / "configs" / "llm_providers.json"
            if registry_path.exists():
                from llm.models import ModelRegistry
                registry = ModelRegistry.load_from_file(str(registry_path))
                self.gateway.registry = registry
                print(f"✅ 已加载模型配置: {registry_path}")
            else:
                print("⚠️ 未找到外部配置文件，使用内置默认配置")
        else:
            self.gateway = None
            print("🔇 离线模式：跳过Gateway初始化")

        self.results_dir = Path(__file__).parent / "phase05_results"
        self.results_dir.mkdir(exist_ok=True)

    async def run_assessment(self, subject_id, model_id, session="first"):
        """对单个被试进行一次评估（交互式）"""
        model_name = model_id
        print(f"\n{'='*60}")
        print(f"  {subject_id} | {model_id} | {session.upper()}")
        print(f"{'='*60}")

        conversation = []

        # 5轮对话
        round_num = 1
        for tpl in DIALOGUE_TEMPLATES:
            if "prompt" in tpl:
                # 单问题轮次
                print(f"\n--- 第{round_num}轮（{tpl['dimension']}）---")
                print(f"问题：{tpl['prompt']}")
                answer = input("你的回答：").strip()
                conversation.append({
                    "round": round_num,
                    "dimension": tpl["dimension"],
                    "question": tpl["prompt"],
                    "answer": answer
                })
                round_num += 1
            elif "sub_prompts" in tpl:
                # 多问题轮次（Round 2：批判整合力+伦理判断力）
                for sp in tpl["sub_prompts"]:
                    print(f"\n--- 第{round_num}轮 {sp['part']}（{sp['dim']}）---")
                    print(f"问题：{sp['text']}")
                    answer = input("你的回答：").strip()
                    conversation.append({
                        "round": round_num,
                        "dimension": sp["dim"],
                        "question": sp["text"],
                        "answer": answer
                    })
                round_num += 1

            # 每轮对话后可以进行一轮LLM辅助评分（可选）
            # 但为了重测信度实验，建议5轮完成后统一评分

        # 5轮完成 → LLM评分
        print(f"\n--- 评分阶段 ---")
        scores = await self._score_conversation(conversation, model_id)

        # 保存结果
        result = {
            "subject_id": subject_id,
            "model_id": model_id,
            "session": session,
            "timestamp": datetime.now().isoformat(),
            "conversation": conversation,
            "scores": scores
        }

        filename = f"result_{subject_id}_{model_id}_{session}.json"
        filepath = self.results_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 已保存: {filepath}")
        if scores:
            print(f"   评分结果: {json.dumps({k: v['score'] for k, v in scores.items()}, ensure_ascii=False)}")
        return result

    async def _score_conversation(self, conversation, model_id):
        """基于对话记录，用LLM评分"""
        if self.offline or self.gateway is None:
            print("⚠️ 离线模式：请输入人工评分")
            scores = {}
            for entry in conversation:
                if entry["dimension"] not in scores:
                    try:
                        s = int(input(f"  {entry['dimension']} 评分 (0-100): "))
                        scores[entry["dimension"]] = {"score": s, "source": "manual"}
                    except:
                        scores[entry["dimension"]] = {"score": 50, "source": "default"}
            return scores

        # 格式化对话记录
        dialogue_text = "\n".join([
            f"第{e['round']}轮（{e['dimension']}）: {e['answer']}"
            for e in conversation
        ])

        # 评分Prompt
        score_prompt = f"""请基于以下对话记录和评分锚点协议，评估用户的6个维度分数。

对话记录：
{dialogue_text}

{SCORING_ANCHORS}

输出格式（严格JSON，不要加markdown标记）：
{{
  "ai_operation": {{"score": 0-100, "evidence": "基于哪条锚点的简短说明"}},
  "critical_integration": {{"score": 0-100, "evidence": "..."}},
  "ai_collaborative_creativity": {{"score": 0-100, "evidence": "..."}},
  "workflow_orchestration": {{"score": 0-100, "evidence": "..."}},
  "ai_adaptability": {{"score": 0-100, "evidence": "..."}},
  "ethical_judgment": {{"score": 0-100, "evidence": "..."}}
}}

评分规则：
- 严格基于行为锚点信号匹配，不要自由发挥
- 每个得分必须有简短的evidence说明匹配了哪条锚点
- 对话中未出现的维度评分为0并注明"无法评估"
- 不要加任何额外说明，只输出JSON"""

        # 通过Gateway调用评分
        extra_kwargs = {}
        if model_id in THINKING_MODES and THINKING_MODES[model_id]:
            extra_kwargs["extra_body"] = THINKING_MODES[model_id]

        try:
            system_msg = "你是一个合能评分员。严格按评分协议打分，只输出JSON。"
            response = await self.gateway.chat(
                prompt=score_prompt,
                system=system_msg,
                model=model_id,
                temperature=0.1,
                **extra_kwargs
            )

            raw = response.content.strip()
            # 提取JSON
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            scores = json.loads(raw)
            print(f"📊 LLM评分完成: {model_id}")
            return scores

        except Exception as e:
            print(f"⚠️ 评分失败: {e}")
            print(f"原始输出: {response.content if 'response' in dir() else 'N/A'}")
            return None

    def analyze_reliability(self):
        """分析重测信度：读取所有结果文件，配对计算r值"""
        results = {}
        for f in self.results_dir.glob("result_*.json"):
            # 文件名格式: result_S01_syn-v4-flash_first.json
            parts = f.stem.split("_")
            if len(parts) >= 4:
                sid = parts[1]
                mid = "_".join(parts[2:-1])
                session = parts[-1]
                key = f"{sid}_{mid}"
                if key not in results:
                    results[key] = {}
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    results[key][session] = data.get("scores", {})
                except:
                    print(f"⚠️ 文件读取失败: {f}")

        # 配对并计算相关性
        report = []
        print(f"\n{'='*60}")
        print(f"  重测信度分析报告")
        print(f"{'='*60}")

        for key, sessions in sorted(results.items()):
            if "first" in sessions and "second" in sessions:
                s1 = sessions["first"]
                s2 = sessions["second"]
                diffs = []
                for dim in ["ai_operation", "critical_integration", "ai_collaborative_creativity",
                            "workflow_orchestration", "ai_adaptability", "ethical_judgment"]:
                    v1 = s1.get(dim, {}).get("score", 0) if isinstance(s1.get(dim), dict) else s1.get(dim, 0)
                    v2 = s2.get(dim, {}).get("score", 0) if isinstance(s2.get(dim), dict) else s2.get(dim, 0)
                    diff = abs(v1 - v2)
                    diffs.append(diff)
                avg_diff = sum(diffs) / len(diffs)
                max_diff = max(diffs)
                report.append((key, avg_diff, max_diff, diffs))
                print(f"  {key}: 平均差={avg_diff:.1f}, 最大差={max_diff:.1f}")

        if report:
            overall_avg = sum(r[1] for r in report) / len(report)
            overall_max = max(r[2] for r in report)
            print(f"\n  ───────────────────────────────")
            print(f"  总体: 平均差={overall_avg:.1f}, 最大差={overall_max:.1f}")
            print(f"  评价: {'✅ 一致性优秀' if overall_avg < 10 else '⚠️ 一致性中等' if overall_avg < 20 else '❌ 一致性差'}")

        return report


async def main():
    parser = argparse.ArgumentParser(description="合能 Phase 0.5 重测信度实验")
    parser.add_argument("--mode", choices=["run", "retest", "analyze"], required=True,
                        help="run=第一次测试, retest=3天后重测, analyze=计算重测信度")
    parser.add_argument("--model", default="syn-v4-flash",
                        choices=["syn-v4-flash", "syn-v32", "syn-glm-z1"],
                        help="测试模型（默认syn-v4-flash）")
    parser.add_argument("--subjects", nargs="+", default=None,
                        help="被试列表（默认S01-S10）")
    parser.add_argument("--offline", action="store_true",
                        help="离线模式（跳过LLM，手动输入评分）")
    args = parser.parse_args()

    tester = SynAbilityTester(offline=args.offline)
    subjects = args.subjects or SUBJECTS
    session = "first" if args.mode == "run" else "second"

    if args.mode in ("run", "retest"):
        print(f"\n=== Phase 0.5 {session.upper()}测试 | 模型: {args.model} ===")
        print(f"被试: {subjects}")
        print(f"预计耗时: 每人15分钟, 共{len(subjects)*15}分钟\n")

        import asyncio
        for sid in subjects:
            await tester.run_assessment(sid, args.model, session)
            print("\n--- 休息2秒 ---")
            time.sleep(2)

        print(f"\n✅ {session}测试完成！结果已保存到 phase05_results/ 目录")
        print(f"   3天后运行: python phase05_test.py --mode retest --model {args.model}")

    elif args.mode == "analyze":
        tester.analyze_reliability()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
