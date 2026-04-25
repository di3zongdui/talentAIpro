"""
Model Configuration - 模型配置
================================

模型配置数据结构和验证
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os


class ModelCapability(Enum):
    """模型能力"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    VISION = "vision"
    FUNCTION_CALL = "function_calling"
    STREAMING = "streaming"


@dataclass
class ModelConfig:
    """单个模型配置"""
    id: str                          # 模型唯一标识，如 "qwen3-omni"
    name: str                        # 显示名称，如 "Qwen3-Omni-30B"
    provider: str                    # Provider ID，如 "siliconflow"
    model_key: str                   # Provider的模型名，如 "Qwen/Qwen3-Omni-30B-A3B-Instruct"
    capabilities: List[ModelCapability] = field(default_factory=list)
    max_tokens: int = 8192          # 最大token数
    default_temperature: float = 0.7
    context_window: int = 32000      # 上下文窗口大小
    input_price: float = 0.0        # 输入价格（元/千token）
    output_price: float = 0.0        # 输出价格（元/千token）
    enabled: bool = True
    description: str = ""            # 模型描述
    extra_params: Dict[str, Any] = field(default_factory=dict)  # 额外参数

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_key": self.model_key,
            "capabilities": [c.value for c in self.capabilities],
            "max_tokens": self.max_tokens,
            "default_temperature": self.default_temperature,
            "context_window": self.context_window,
            "input_price": self.input_price,
            "output_price": self.output_price,
            "enabled": self.enabled,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ModelConfig":
        data = data.copy()
        data["capabilities"] = [
            ModelCapability(c) for c in data.get("capabilities", [])
        ]
        return cls(**data)


@dataclass
class ProviderConfig:
    """Provider配置"""
    id: str                          # Provider唯一标识
    name: str                        # 显示名称
    provider_type: str               # ProviderType.value
    base_url: str                    # API地址
    api_key: str                     # API密钥（加密存储）
    enabled: bool = True
    models: List[ModelConfig] = field(default_factory=list)
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "provider_type": self.provider_type,
            "base_url": self.base_url,
            "api_key": self._mask_api_key(self.api_key) if self.api_key else "",
            "enabled": self.enabled,
            "models": [m.to_dict() for m in self.models],
        }

    @staticmethod
    def _mask_api_key(key: str) -> str:
        """脱敏API Key"""
        if len(key) <= 8:
            return "***"
        return key[:4] + "***" + key[-4:]


class ModelRegistry:
    """模型注册表 - 管理所有可用模型"""

    DEFAULT_MODELS = {
        # SiliconFlow 模型
        "siliconflow": {
            "id": "siliconflow",
            "name": "SiliconFlow",
            "provider_type": "siliconflow",
            "base_url": "https://api.siliconflow.cn/v1",
            "api_key": "",
            "models": [
                {
                    "id": "qwen3-omni",
                    "name": "Qwen3-Omni-30B",
                    "model_key": "Qwen/Qwen3-Omni-30B-A3B-Instruct",
                    "capabilities": ["chat", "function_calling", "streaming"],
                    "context_window": 32000,
                    "description": "通义千问全模态旗舰模型，支持音频理解",
                },
                {
                    "id": "qwq32b",
                    "name": "QwQ-32B",
                    "model_key": "Qwen/QwQ-32B",
                    "capabilities": ["chat", "function_calling", "streaming"],
                    "context_window": 32000,
                    "description": "深度思考模型，数学和代码能力强",
                },
                {
                    "id": "deepseekv3",
                    "name": "DeepSeek-V3",
                    "model_key": "deepseek-ai/DeepSeek-V3",
                    "capabilities": ["chat", "function_calling", "streaming"],
                    "context_window": 64000,
                    "description": "DeepSeek最新模型，性价比高",
                },
                {
                    "id": "glm4",
                    "name": "GLM-4",
                    "model_key": "THUDM/GLM-4-0520",
                    "capabilities": ["chat", "function_calling", "streaming"],
                    "context_window": 128000,
                    "description": "智谱GLM-4旗舰模型",
                },
            ]
        },
        # 阿里云DashScope
        "dashscope": {
            "id": "dashscope",
            "name": "阿里云DashScope",
            "provider_type": "dashscope",
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "api_key": "",
            "models": [
                {
                    "id": "qwen-plus",
                    "name": "Qwen-Plus",
                    "model_key": "qwen-plus",
                    "capabilities": ["chat", "function_calling", "streaming"],
                    "context_window": 131072,
                    "description": "阿里云通义千问Plus模型",
                },
                {
                    "id": "qwen-max",
                    "name": "Qwen-Max",
                    "model_key": "qwen-max",
                    "capabilities": ["chat", "function_calling", "streaming"],
                    "context_window": 8192,
                    "description": "阿里云通义千问最强模型",
                },
            ]
        },
    }

    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self._load_defaults()

    def _load_defaults(self):
        """加载默认Provider配置"""
        for provider_id, provider_data in self.DEFAULT_MODELS.items():
            models = [
                ModelConfig(
                    id=m["id"],
                    name=m["name"],
                    provider=provider_id,
                    model_key=m["model_key"],
                    capabilities=[ModelCapability(c) for c in m.get("capabilities", ["chat"])],
                    context_window=m.get("context_window", 32000),
                    description=m.get("description", ""),
                )
                for m in provider_data.get("models", [])
            ]

            self.providers[provider_id] = ProviderConfig(
                id=provider_id,
                name=provider_data["name"],
                provider_type=provider_data["provider_type"],
                base_url=provider_data["base_url"],
                api_key=provider_data.get("api_key", ""),
                models=models,
            )

    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        return self.providers.get(provider_id)

    def get_model(self, provider_id: str, model_id: str) -> Optional[ModelConfig]:
        provider = self.get_provider(provider_id)
        if not provider:
            return None
        return next((m for m in provider.models if m.id == model_id), None)

    def list_all_models(self) -> List[ModelConfig]:
        """列出所有模型"""
        models = []
        for provider in self.providers.values():
            models.extend(provider.models)
        return models

    def add_provider(self, config: ProviderConfig):
        self.providers[config.id] = config

    def remove_provider(self, provider_id: str):
        if provider_id in self.providers:
            del self.providers[provider_id]

    def update_provider_api_key(self, provider_id: str, api_key: str):
        if provider_id in self.providers:
            self.providers[provider_id].api_key = api_key

    def to_dict(self) -> dict:
        return {
            "providers": [p.to_dict() for p in self.providers.values()]
        }

    def save_to_file(self, path: str):
        """保存配置到文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, path: str) -> "ModelRegistry":
        """从文件加载配置"""
        registry = cls()
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 重建providers
            registry.providers = {}
            for p_data in data.get("providers", []):
                models = [ModelConfig.from_dict(m) for m in p_data.get("models", [])]
                provider = ProviderConfig(
                    id=p_data["id"],
                    name=p_data["name"],
                    provider_type=p_data["provider_type"],
                    base_url=p_data["base_url"],
                    api_key="",  # API key从环境变量或加密存储加载
                    models=models,
                )
                registry.providers[p_data["id"]] = provider
        return registry
