"""
LLM Provider 基类定义
=====================

所有Provider必须继承 BaseProvider 并实现抽象方法
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Callable, Awaitable
import logging

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """支持的Provider类型"""
    SILICONFLOW = "siliconflow"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DASHSCOPE = "dashscope"  # 阿里云
    WENXIN = "wenxin"       # 百度文心
    ZHIPU = "zhipu"         # 智谱
    LOCAL = "local"         # 本地模型
    CUSTOM = "custom"       # 自定义


@dataclass
class LLMResponse:
    """LLM响应数据结构"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)  # tokens统计
    latency_ms: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)  # 额外信息


# 流式回调类型
StreamCallback = Callable[[str], Awaitable[None]]


@dataclass
class Message:
    """对话消息"""
    role: str  # system/user/assistant
    content: str


class BaseProvider(ABC):
    """Provider基类"""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """返回Provider类型"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送对话请求

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
        """
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Message],
        model: str,
        callback: StreamCallback,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        流式对话

        Args:
            messages: 消息列表
            model: 模型名称
            callback: 流式回调，每收到一个chunk调用一次
            temperature: 温度参数
            max_tokens: 最大token数
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """列出可用模型"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置是否正确"""
        pass

    def _log_request(self, model: str, messages: List[Message]):
        """记录请求日志"""
        self._logger.debug(f"LLM Request to {model}: {len(messages)} messages")

    def _log_response(self, response: LLMResponse):
        """记录响应日志"""
        self._logger.debug(
            f"LLM Response from {response.model}: "
            f"{len(response.content)} chars, "
            f"{response.latency_ms:.0f}ms"
        )
