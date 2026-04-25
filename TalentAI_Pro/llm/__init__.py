"""
LLM Module - 大模型统一接入层
==============================

支持多Provider: SiliconFlow, OpenAI, Anthropic, 阿里云, 百度等
统一接口设计，支持流式输出

Usage:
    from TalentAI_Pro.llm import LLMGateway

    gateway = LLMGateway()
    result = await gateway.chat("你好", model="qwen")

    # Interview评估
    from TalentAI_Pro.llm.integrations import LLMInterviewIntegration
    integration = LLMInterviewIntegration(gateway)
    evaluation = await integration.evaluate_answer(question, answer, context)
"""

from .provider import BaseProvider, ProviderType, LLMResponse, StreamCallback
from .siliconflow import SiliconFlowProvider
from .gateway import LLMGateway
from .models import ModelConfig, ProviderConfig, ModelRegistry
from .integrations import LLMInterviewIntegration, LLMNegotiationIntegration
from .semantic_matching import LLMSemanticMatching, SemanticMatchResult

__all__ = [
    "BaseProvider",
    "ProviderType",
    "LLMResponse",
    "StreamCallback",
    "SiliconFlowProvider",
    "LLMGateway",
    "ModelConfig",
    "ProviderConfig",
    "ModelRegistry",
    "LLMInterviewIntegration",
    "LLMNegotiationIntegration",
    "LLMSemanticMatching",
    "SemanticMatchResult",
]
