"""
LLM Module Tests - LLM模块测试
===============================

测试LLM Gateway、Provider和集成功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from TalentAI_Pro.llm import (
    LLMGateway,
    Message,
    SiliconFlowProvider,
    ModelRegistry,
)
from TalentAI_Pro.llm.integrations import (
    LLMInterviewIntegration,
    LLMNegotiationIntegration,
)
from TalentAI_Pro.llm.semantic_matching import LLMSemanticMatching


# 测试配置
TEST_API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
TEST_MODEL = "Qwen/Qwen3-Omni-30B-A3B-Instruct"


async def test_provider_config():
    """测试Provider配置"""
    print("\n" + "="*60)
    print("Test 1: Provider Configuration")
    print("="*60)

    provider = SiliconFlowProvider(api_key=TEST_API_KEY)
    print(f"Provider type: {provider.provider_type.value}")
    print(f"Available models: {provider.list_models()}")
    print(f"Config valid: {provider.validate_config()}")

    await provider.close()
    print("✓ Provider configuration test passed")


async def test_gateway_basic():
    """测试Gateway基础功能"""
    print("\n" + "="*60)
    print("Test 2: Gateway Basic Chat")
    print("="*60)

    gateway = LLMGateway()

    # 配置Provider
    success = gateway.configure_provider(
        provider_id="siliconflow",
        api_key=TEST_API_KEY,
    )
    print(f"Provider configured: {success}")

    # 发送测试消息
    response = await gateway.chat(
        prompt="请用一句话介绍你自己",
        model="qwen3-omni",
        temperature=0.7,
    )

    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Latency: {response.latency_ms:.0f}ms")
    print(f"Usage: {response.usage}")

    print("✓ Gateway basic chat test passed")
    return response


async def test_gateway_stream():
    """测试Gateway流式功能"""
    print("\n" + "="*60)
    print("Test 3: Gateway Streaming Chat")
    print("="*60)

    gateway = LLMGateway()
    gateway.configure_provider("siliconflow", TEST_API_KEY)

    chunks = []
    async def on_chunk(chunk):
        chunks.append(chunk)
        print(chunk, end="", flush=True)

    print("Streaming response: ", end="")

    response = await gateway.stream(
        prompt="请列出5个提升Python代码性能的方法，用编号列表",
        model="qwen3-omni",
        callback=on_chunk,
        temperature=0.7,
    )

    print("\n")
    print(f"Total chunks: {len(chunks)}")
    print(f"Final response length: {len(response.content)} chars")

    print("✓ Gateway streaming test passed")


async def test_interview_evaluation():
    """测试面试评估功能"""
    print("\n" + "="*60)
    print("Test 4: Interview LLM Evaluation")
    print("="*60)

    gateway = LLMGateway()
    gateway.configure_provider("siliconflow", TEST_API_KEY)

    integration = LLMInterviewIntegration(gateway)

    # 测试评估
    question = "请解释Python中的装饰器是什么？如何使用？"
    answer = """装饰器是Python的一种高级特性。简单来说，装饰器就是一个函数，它接受一个函数作为参数，并返回一个新的函数。

使用示例：
```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")
```

装饰器可以在不修改原函数的情况下，增加额外的功能。常见的用途包括日志记录、性能测试、权限校验等。"""

    evaluation = await integration.evaluate_answer(
        question=question,
        answer=answer,
        context={
            "level": "mid",
            "required_skills": ["Python", "装饰器"],
        }
    )

    print(f"Score: {evaluation.score}/5")
    print(f"Quality: {evaluation.quality}")
    print(f"Keywords found: {evaluation.keywords_found}")
    print(f"Keywords missing: {evaluation.keywords_missing}")
    print(f"Feedback: {evaluation.feedback[:200]}...")
    print(f"Suggestions: {evaluation.suggestions}")

    print("✓ Interview evaluation test passed")


async def test_negotiation_message():
    """测试谈判消息生成"""
    print("\n" + "="*60)
    print("Test 5: Negotiation Message Generation")
    print("="*60)

    gateway = LLMGateway()
    gateway.configure_provider("siliconflow", TEST_API_KEY)

    integration = LLMNegotiationIntegration(gateway)

    message = await integration.generate_message(
        situation="候选人收到Offer后表示薪资低于预期，希望月薪从42000提高到48000",
        tone="moderate",
        candidate_info="李明，3年Python开发经验，原薪资28000，技术能力突出",
        company_offer={
            "salary": 42000,
            "signing_bonus": 20000,
            "rsu": 5000,
            "vacation_days": 15,
            "remote_days": 2,
        }
    )

    print(f"Generated message:\n{message}")

    print("✓ Negotiation message test passed")


async def test_model_registry():
    """测试模型注册表"""
    print("\n" + "="*60)
    print("Test 6: Model Registry")
    print("="*60)

    registry = ModelRegistry()

    # 列出所有Provider
    print(f"Providers: {list(registry.providers.keys())}")

    # 列出所有模型
    all_models = registry.list_all_models()
    print(f"Total models: {len(all_models)}")
    for m in all_models[:5]:
        print(f"  - {m.name} ({m.id})")

    # 获取特定模型
    model = registry.get_model("siliconflow", "qwen3-omni")
    if model:
        print(f"\nSelected model: {model.name}")
        print(f"  Key: {model.model_key}")
        print(f"  Context window: {model.context_window}")
        print(f"  Capabilities: {[c.value for c in model.capabilities]}")

    print("✓ Model registry test passed")


async def test_gateway_stats():
    """测试用量统计"""
    print("\n" + "="*60)
    print("Test 7: Gateway Usage Stats")
    print("="*60)

    gateway = LLMGateway()
    gateway.configure_provider("siliconflow", TEST_API_KEY)

    # 发送几个请求
    for i in range(3):
        await gateway.chat(prompt=f"测试{i+1}", model="qwen3-omni")

    stats = gateway.get_usage_stats()
    print(f"Usage stats: {stats}")

    print("✓ Gateway stats test passed")


async def test_semantic_matching():
    """测试语义匹配功能"""
    print("\n" + "="*60)
    print("Test 8: Semantic Matching")
    print("="*60)

    gateway = LLMGateway()
    gateway.configure_provider("siliconflow", TEST_API_KEY)

    matcher = LLMSemanticMatching(gateway)

    job_info = {
        "title": "高级Python工程师",
        "required_skills": ["Python", "Django", "Flask", "PostgreSQL", "Docker"],
        "min_experience_years": 3,
        "level": "senior",
    }

    candidate_info = {
        "name": "李明",
        "current_title": "Python开发工程师",
        "years_of_experience": 4,
        "skills": ["Flask", "Django", "PostgreSQL", "Docker", "Redis"],
        "achievements": "主导过电商平台后端开发，日活10万",
    }

    # 技能匹配
    skill_result = await matcher.match_skills(
        required_skills=job_info["required_skills"],
        candidate_skills=candidate_info["skills"],
    )
    print(f"Skill match score: {skill_result.get('skill_match_score', 0)}")

    # 经验匹配
    exp_result = await matcher.match_experience(
        job_info=job_info,
        candidate_info=candidate_info,
    )
    print(f"Experience match score: {exp_result.get('experience_match_score', 0)}")

    # 整体匹配
    overall_result = await matcher.overall_match(
        job_info=job_info,
        candidate_info=candidate_info,
    )
    print(f"Overall score: {overall_result.overall_score}")
    print(f"Recommendation: {overall_result.recommendation}")
    print(f"Hidden strengths: {overall_result.hidden_strengths}")
    print(f"Gaps: {overall_result.gaps}")

    print("✓ Semantic matching test passed")
    return overall_result


async def test_interview_focus():
    """测试面试重点生成"""
    print("\n" + "="*60)
    print("Test 9: Interview Focus Generation")
    print("="*60)

    gateway = LLMGateway()
    gateway.configure_provider("siliconflow", TEST_API_KEY)

    matcher = LLMSemanticMatching(gateway)

    job_info = {
        "title": "高级Python工程师",
        "required_skills": ["Python", "Django", "系统设计"],
    }

    candidate_info = {
        "name": "李明",
        "skills": ["Flask", "Django"],
        "gaps": ["缺少大规模系统设计经验"],
    }

    focus_areas = await matcher.suggest_interview_focus(
        job_info=job_info,
        candidate_info=candidate_info,
    )

    print(f"Generated {len(focus_areas)} focus areas:")
    for i, area in enumerate(focus_areas[:3], 1):
        print(f"  {i}. {area.get('topic', 'N/A')}")

    print("✓ Interview focus test passed")


async def main():
    """运行所有测试"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║           TalentAI Pro LLM Module Tests                   ║
║                                                           ║
║   Testing: SiliconFlow + Qwen3-Omni-30B                  ║
╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        # 基础测试
        await test_provider_config()
        await test_gateway_basic()
        await test_model_registry()
        await test_gateway_stats()

        # 功能测试
        await test_gateway_stream()
        await test_interview_evaluation()
        await test_negotiation_message()
        await test_semantic_matching()
        await test_interview_focus()

        print("""
╔═══════════════════════════════════════════════════════════╗
║                   All Tests Passed!                       ║
╚═══════════════════════════════════════════════════════════╝
        """)

    except Exception as e:
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║                      Test Failed                          ║
╠═══════════════════════════════════════════════════════════╣
║  Error: {str(e)[:50]}                        ║
╚═══════════════════════════════════════════════════════════╝
        """)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
