"""
Phase 0.5：简化版测试脚本（快速调试）
========================================
不依赖 TalentAI_Pro Gateway，直接用 OpenAI SDK 调用硅基流动
"""

import json
import time
from datetime import datetime
from pathlib import Path

# 尝试导入 openai
try:
    import openai
    print("✅ openai SDK 已安装")
except ImportError:
    print("❌ 缺少 openai 包，安装命令：pip install openai")
    exit(1)

# 配置 - 需要修改你的API Key
SILICONFLOW_API_KEY = "your_api_key_here"  # 替换为你的API密钥
BASE_URL = "https://api.siliconflow.cn/v1"

# 模型配置
MODELS = {
    "syn-v4-flash": "deepseek-ai/DeepSeek-V4-Flash",
    "syn-v32": "deepseek-ai/DeepSeek-V3.2",
    "syn-glm-z1": "THUDM/GLM-Z1-32B-0414"
}

# 5轮对话问题
QUESTIONS = [
    {
        "round": 1,
        "dimension": "ai_operation",
        "text": "假设你是一个团队负责人，需要快速收集某行业的竞品信息，并整理成一份简报。请告诉我：你会如何利用AI来完成这个任务？具体会怎么跟AI说？"
    },
    {
        "round": 2,
        "dimension": "critical_integration",
        "text": "假设AI已经帮你整理好了一份竞品简报，但你发现其中几个数据来源似乎不可靠。你会怎么处理这种情况？请描述你的具体步骤。"
    },
    {
        "round": 3,
        "dimension": "ethical_judgment",
        "text": "继续上面的场景，如果AI建议你在简报中忽略那些不可靠的数据，因为'这样看起来更好'。你怎么看这个问题？有没有什么伦理或风险方面的考虑？"
    },
    {
        "round": 4,
        "dimension": "workflow_orchestration",
        "text": "现在需要你设计一个包含AI协作的完整工作流程，用来每周自动生成一份市场动态报告。请描述这个流程的各个环节，以及人和AI分别在哪些环节做什么。"
    },
    {
        "round": 5,
        "dimension": "ai_collaborative_creativity",
        "text": "以上这些工作如果全部由AI自动化完成了，你觉得人在这个过程中还能发挥什么独特的价值？同时，如果你需要把这份报告的价值讲给团队听，你会怎么组织你的叙述？"
    },
    {
        "round": 6,
        "dimension": "ai_adaptability",
        "text": "回想一下你在过去半年使用AI工具的经历——有没有遇到过某个AI工具更新后你需要调整使用方式的情况？你是怎么应对的？你平时如何保持对AI新进展的了解？"
    }
]

# 评分Prompt
SCORING_PROMPT = """请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation (AI操作力) - 知道AI能做什么、如何指挥AI
2. critical_integration (批判整合力) - 评估AI输出、整合到工作流
3. ai_collaborative_creativity (AI协同创造力) - 与AI配合创造价值
4. workflow_orchestration (流程编排力) - 设计人机协作流程
5. ethical_judgment (伦理判断力) - 识别AI伦理风险
6. ai_adaptability (AI适应力) - 持续学习、适应AI变化

输出格式（严格JSON）：
{{
  "ai_operation": {{"score": 0-100, "evidence": "简短说明"}},
  "critical_integration": {{"score": 0-100, "evidence": "..."}},
  "ai_collaborative_creativity": {{"score": 0-100, "evidence": "..."}},
  "workflow_orchestration": {{"score": 0-100, "evidence": "..."}},
  "ethical_judgment": {{"score": 0-100, "evidence": "..."}},
  "ai_adaptability": {{"score": 0-100, "evidence": "..."}}
}}

只输出JSON，不要任何额外说明。"""

def run_assessment(subject_id="S01", model_key="syn-v4-flash"):
    """运行一次评估"""
    
    print(f"\n{'='*60}")
    print(f"  合能评估 | 被试: {subject_id} | 模型: {model_key}")
    print(f"{'='*60}\n")
    
    # 创建客户端
    client = openai.OpenAI(
        base_url=BASE_URL,
        api_key=SILICONFLOW_API_KEY
    )
    
    model_id = MODELS.get(model_key, MODELS["syn-v4-flash"])
    print(f"✅ 使用模型: {model_id}\n")
    
    # 收集对话
    conversation = []
    
    for q in QUESTIONS:
        print(f"--- 第{q['round']}轮（{q['dimension']}）---")
        print(f"问题：{q['text']}\n")
        
        answer = input("回答：").strip()
        
        conversation.append({
            "round": q['round'],
            "dimension": q['dimension'],
            "question": q['text'],
            "answer": answer
        })
        print()
    
    # LLM评分
    print("--- 正在评分 ---")
    dialogue_text = "\n".join([f"第{c['round']}轮：{c['answer']}" for c in conversation])
    
    try:
        extra_body = {"thinking_mode": "high"} if model_key == "syn-v4-flash" else None
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "你是一个合能评分员。严格按评分协议打分，只输出JSON。"},
                {"role": "user", "content": SCORING_PROMPT.format(dialogue=dialogue_text)}
            ],
            temperature=0.1,
            max_tokens=2048,
            **({"extra_body": extra_body} if extra_body else {})
        )
        
        raw = response.choices[0].message.content.strip()
        
        # 提取JSON
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        
        scores = json.loads(raw)
        print(f"✅ 评分完成\n")
        
        # 显示评分
        for dim, data in scores.items():
            s = data if isinstance(data, int) else data.get('score', 0)
            e = data.get('evidence', '')[:30] if isinstance(data, dict) else ''
            print(f"  {dim:35s}: {s:3d} {e}")
        
        # 保存结果
        result = {
            "subject_id": subject_id,
            "model_id": model_key,
            "timestamp": datetime.now().isoformat(),
            "conversation": conversation,
            "scores": scores
        }
        
        output_dir = Path(__file__).parent / "phase05_results"
        output_dir.mkdir(exist_ok=True)
        
        filename = f"result_{subject_id}_{model_key}_{datetime.now().strftime('%m%d_%H%M')}.json"
        filepath = output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 结果已保存: {filepath}")
        
    except Exception as e:
        print(f"❌ 评分失败: {e}")
        print(f"原始输出: {raw if 'raw' in locals() else 'N/A'}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Phase 0.5：合能评估引擎 - 简化版测试")
    print("="*60)
    
    # 输入被试ID
    subject = input("\n被试ID (默认S01): ").strip() or "S01"
    
    # 选择模型
    print("\n可用模型:")
    for k, v in MODELS.items():
        print(f"  {k}: {v}")
    model = input("选择模型 (默认syn-v4-flash): ").strip() or "syn-v4-flash"
    
    # 检查API Key
    if SILICONFLOW_API_KEY == "your_api_key_here":
        print("\n⚠️ 警告：请先编辑脚本，填入你的硅基流动API Key")
        print("在脚本第15行修改: SILICONFLOW_API_KEY = '你的密钥'")
        exit(1)
    
    # 运行
    run_assessment(subject, model)
