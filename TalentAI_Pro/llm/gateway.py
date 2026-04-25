"""
LLM Gateway - 统一网关
=======================

统一管理所有Provider，提供一致的接口

Usage:
    from TalentAI_Pro.llm import LLMGateway

    gateway = LLMGateway()

    # 配置Provider
    gateway.configure_provider("siliconflow", api_key="sk-xxx")

    # 发送消息
    response = await gateway.chat("你好", model="qwen3-omni")

    # 流式对话
    async def on_chunk(chunk):
        print(chunk, end="", flush=True)

    await gateway.stream(messages, model="qwen3-omni", callback=on_chunk)
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass, field

from .provider import (
    BaseProvider,
    ProviderType,
    LLMResponse,
    StreamCallback,
    Message,
)
from .siliconflow import SiliconFlowProvider
from .models import ModelRegistry, ModelConfig, ProviderConfig


logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM全局配置"""
    config_file: str = "llm_config.json"
    default_provider: str = "siliconflow"
    default_model: str = "qwen3-omni"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: float = 120.0


class LLMGateway:
    """
    LLM统一网关

    Features:
    - 多Provider支持
    - 模型自动路由
    - 降级策略
    - 用量统计
    - 前端配置集成
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.registry = ModelRegistry()
        self._providers: Dict[str, BaseProvider] = {}
        self._usage_stats: Dict[str, int] = {
            "total_tokens": 0,
            "total_requests": 0,
            "cost": 0.0,
        }

    def configure_provider(
        self,
        provider_id: str,
        api_key: str,
        base_url: Optional[str] = None,
    ) -> bool:
        """
        配置Provider

        Args:
            provider_id: Provider ID (如 "siliconflow")
            api_key: API密钥
            base_url: 自定义API地址（可选）

        Returns:
            配置是否成功
        """
        provider_config = self.registry.get_provider(provider_id)
        if not provider_config:
            logger.error(f"Provider {provider_id} not found in registry")
            return False

        # 根据类型创建Provider实例
        if provider_config.provider_type == ProviderType.SILICONFLOW.value:
            provider = SiliconFlowProvider(
                api_key=api_key,
                base_url=base_url or provider_config.base_url,
            )
        else:
            logger.error(f"Unsupported provider type: {provider_config.provider_type}")
            return False

        # 验证配置
        if not provider.validate_config():
            logger.error(f"Provider {provider_id} validation failed")
            return False

        self._providers[provider_id] = provider
        logger.info(f"Provider {provider_id} configured successfully")
        return True

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        """获取Provider实例"""
        return self._providers.get(provider_id)

    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        # 遍历所有provider查找model
        for provider_id, provider in self._providers.items():
            model = self.registry.get_model(provider_id, model_id)
            if model:
                return model
        return None

    def get_model_by_key(self, provider_id: str, model_key: str) -> Optional[ModelConfig]:
        """通过model_key获取模型配置"""
        provider = self.registry.get_provider(provider_id)
        if not provider:
            return None
        for model in provider.models:
            if model.model_key == model_key:
                return model
        return None

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送对话请求（简洁接口）

        Args:
            prompt: 用户输入
            model: 模型ID (如 "qwen3-omni")
            messages: 完整消息列表（可选）
            system: 系统提示（可选）
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            LLMResponse
        """
        # 构建消息列表
        if messages is None:
            messages = []
            if system:
                messages.append(Message(role="system", content=system))
            messages.append(Message(role="user", content=prompt))

        # 解析model
        model_config = self.get_model(model or self.config.default_model)
        if not model_config:
            raise ValueError(f"Model {model} not found or not configured")

        # 获取Provider
        provider = self._providers.get(model_config.provider)
        if not provider:
            raise ValueError(f"Provider {model_config.provider} not configured. Call configure_provider() first.")

        # 发送请求
        response = await provider.chat(
            messages=messages,
            model=model_config.model_key,
            temperature=temperature or model_config.default_temperature,
            max_tokens=max_tokens or model_config.max_tokens,
            **kwargs,
        )

        # 更新统计
        self._update_usage(response)

        return response

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        system: Optional[str] = None,
        callback: Optional[StreamCallback] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        流式对话

        Args:
            prompt: 用户输入
            model: 模型ID
            messages: 完整消息列表
            system: 系统提示
            callback: 流式回调函数
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            LLMResponse
        """
        if messages is None:
            messages = []
            if system:
                messages.append(Message(role="system", content=system))
            messages.append(Message(role="user", content=prompt))

        model_config = self.get_model(model or self.config.default_model)
        if not model_config:
            raise ValueError(f"Model {model} not found")

        provider = self._providers.get(model_config.provider)
        if not provider:
            raise ValueError(f"Provider {model_config.provider} not configured")

        response = await provider.stream(
            messages=messages,
            model=model_config.model_key,
            callback=callback or self._default_stream_callback,
            temperature=temperature or model_config.default_temperature,
            max_tokens=max_tokens or model_config.max_tokens,
            **kwargs,
        )

        self._update_usage(response)
        return response

    async def _default_stream_callback(self, chunk: str):
        """默认流式回调"""
        print(chunk, end="", flush=True)

    def _update_usage(self, response: LLMResponse):
        """更新用量统计"""
        self._usage_stats["total_requests"] += 1
        if response.usage:
            prompt_tokens = response.usage.get("prompt_tokens", 0)
            completion_tokens = response.usage.get("completion_tokens", 0)
            self._usage_stats["total_tokens"] += prompt_tokens + completion_tokens

    def get_usage_stats(self) -> Dict[str, Any]:
        """获取用量统计"""
        return {
            **self._usage_stats,
            "providers_configured": list(self._providers.keys()),
        }

    async def health_check(self) -> Dict[str, Any]:
        """健康检查所有已配置的Provider"""
        results = {}
        for provider_id, provider in self._providers.items():
            if hasattr(provider, "health_check"):
                results[provider_id] = await provider.health_check()
            else:
                results[provider_id] = {"status": "unknown"}
        return results

    # ========== 静态方法：构建Message ==========

    @staticmethod
    def user_message(content: str) -> Message:
        return Message(role="user", content=content)

    @staticmethod
    def assistant_message(content: str) -> Message:
        return Message(role="assistant", content=content)

    @staticmethod
    def system_message(content: str) -> Message:
        return Message(role="system", content=content)

    # ========== 便捷方法 ==========

    async def interview_evaluate(
        self,
        question: str,
        answer: str,
        context: str,
    ) -> Dict[str, Any]:
        """
        面试评估专用接口

        Args:
            question: 面试问题
            answer: 候选人回答
            context: 职位上下文

        Returns:
            评估结果
        """
        model = self.get_model("qwen3-omni") or self.get_model(self.config.default_model)
        if not model:
            raise ValueError("No model configured")

        provider = self._providers.get(model.provider)
        if not provider:
            raise ValueError(f"Provider {model.provider} not configured")

        messages = [
            Message(role="system", content="""你是一个专业的面试评估专家。
请评估候选人回答的技术深度、完整性和准确性。
返回JSON格式：
{
    "score": 1-5,
    "quality": "excellent/good/average/poor/fail",
    "keywords_found": ["关键词1", "关键词2"],
    "keywords_missing": ["缺失关键词"],
    "feedback": "详细反馈",
    "suggestions": ["改进建议1", "改进建议2"]
}"""),
            Message(role="user", content=f"""职位要求: {context}

问题: {question}

候选人回答: {answer}

请评估"""),
        ]

        response = await provider.chat(
            messages=messages,
            model=model.model_key,
            temperature=0.3,
        )

        import json
        try:
            result = json.loads(response.content)
            return result
        except:
            return {
                "score": 3,
                "quality": "average",
                "feedback": response.content,
                "suggestions": [],
            }

    async def negotiation_message(
        self,
        situation: str,
        tone: str,
        candidate_info: str,
        company_offer: str,
    ) -> str:
        """
        谈判消息生成专用接口

        Args:
            situation: 当前谈判情况
            tone: 期望语气 (aggressive/moderate/conciliatory)
            candidate_info: 候选人信息
            company_offer: 公司Offer

        Returns:
            生成的谈判消息
        """
        model = self.get_model("qwen3-omni") or self.get_model(self.config.default_model)
        if not model:
            raise ValueError("No model configured")

        provider = self._providers.get(model.provider)
        if not provider:
            raise ValueError(f"Provider {model.provider} not configured")

        tone_instruction = {
            "aggressive": "坚定维护公司利益，直接表达底线",
            "moderate": "平衡双方利益，寻找共赢方案",
            "conciliatory": "积极倾听候选人诉求，展现诚意",
        }.get(tone, "专业友善")

        messages = [
            Message(role="system", content=f"""你是一个经验丰富的HR谈判专家，帮助公司在薪资谈判中达成双赢。
语气要求: {tone_instruction}
不要使用AI、Agent、系统等词汇，用"我"代表公司。
消息要自然、人性化，像真实的人类HR对话。"""),
            Message(role="user", content=f"""候选人背景: {candidate_info}
公司Offer: {company_offer}
当前谈判情况: {situation}

请生成一条发送给候选人的微信消息（100字以内）："""),
        ]

        response = await provider.chat(
            messages=messages,
            model=model.model_key,
            temperature=0.8,
        )

        return response.content.strip()


# 全局单例
_gateway: Optional[LLMGateway] = None


def get_gateway() -> LLMGateway:
    """获取全局Gateway实例"""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway


def configure_gateway(provider_id: str, api_key: str, base_url: Optional[str] = None) -> bool:
    """快速配置全局Gateway"""
    gateway = get_gateway()
    return gateway.configure_provider(provider_id, api_key, base_url)
