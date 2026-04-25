"""
LLM API Routes - LLM配置和控制API
===================================

提供LLM配置、测试、管理的REST API
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 导入LLM模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import (
    LLMGateway,
    SiliconFlowProvider,
    ProviderType,
)
from llm.provider import Message
from llm.models import ModelRegistry, ProviderConfig, ModelConfig
from llm.semantic_matching import LLMSemanticMatching


router = APIRouter(prefix="/api/llm", tags=["LLM"])

# 全局Gateway实例
_gateway: Optional[LLMGateway] = None
_registry: Optional[ModelRegistry] = None

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"
CONFIG_FILE = CONFIG_DIR / "llm_providers.json"


def get_gateway() -> LLMGateway:
    """获取Gateway实例"""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
        # 从registry加载已配置的providers
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                _gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)
    return _gateway


def get_registry() -> ModelRegistry:
    """获取Model Registry"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
        # 尝试从文件加载
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 重建providers
                _registry.providers = {}
                for p_data in data.get("providers", []):
                    models = [ModelConfig.from_dict(m) for m in p_data.get("models", [])]
                    provider = ProviderConfig(
                        id=p_data["id"],
                        name=p_data["name"],
                        provider_type=p_data["provider_type"],
                        base_url=p_data["base_url"],
                        api_key=p_data.get("api_key", ""),
                        models=models,
                    )
                    _registry.providers[p_data["id"]] = provider
            except Exception as e:
                print(f"Failed to load LLM config: {e}")
    return _registry


def save_registry():
    """保存Registry到文件"""
    global _registry
    if _registry is None:
        return
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(_registry.to_dict(), f, ensure_ascii=False, indent=2)


# ========== Request/Response Models ==========

class ProviderConfigRequest(BaseModel):
    provider: str
    api_key: str
    base_url: Optional[str] = None


class ChatRequest(BaseModel):
    prompt: str
    model: Optional[str] = "qwen3-omni"
    system: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class InterviewEvaluateRequest(BaseModel):
    question: str
    answer: str
    context: str = "职位面试"


class NegotiationMessageRequest(BaseModel):
    situation: str
    tone: str = "moderate"  # aggressive/moderate/conciliatory
    candidate_info: str = ""
    company_offer: str = ""


class ModelConfigRequest(BaseModel):
    provider_id: str
    model_id: str
    api_key: str


# ========== API Endpoints ==========

@router.get("/providers")
async def list_providers():
    """获取所有Provider列表"""
    registry = get_registry()
    providers = []
    for p in registry.providers.values():
        providers.append({
            "id": p.id,
            "name": p.name,
            "provider_type": p.provider_type,
            "base_url": p.base_url,
            "models": [m.to_dict() for m in p.models],
            "has_api_key": bool(p.api_key),
        })
    return {"status": "success", "data": providers}


@router.get("/models")
async def list_models(provider_id: Optional[str] = None):
    """获取模型列表"""
    registry = get_registry()
    if provider_id:
        provider = registry.get_provider(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        models = [m.to_dict() for m in provider.models]
    else:
        models = [m.to_dict() for m in registry.list_all_models()]
    return {"status": "success", "data": models}


@router.post("/configure")
async def configure_provider(config: ProviderConfigRequest):
    """配置Provider"""
    gateway = get_gateway()

    success = gateway.configure_provider(
        provider_id=config.provider,
        api_key=config.api_key,
        base_url=config.base_url,
    )

    if success:
        # 保存配置
        registry = get_registry()
        provider = registry.get_provider(config.provider)
        if provider:
            provider.api_key = config.api_key
            save_registry()

        return {"status": "success", "message": f"{config.provider} configured successfully"}
    else:
        raise HTTPException(status_code=400, detail="Configuration failed")


@router.post("/test")
async def test_provider(config: ProviderConfigRequest):
    """测试Provider连接"""
    try:
        # 创建临时Provider测试
        base_url = config.base_url
        if not base_url:
            registry = get_registry()
            provider = registry.get_provider(config.provider)
            if provider:
                base_url = provider.base_url

        if config.provider == "siliconflow":
            provider = SiliconFlowProvider(
                api_key=config.api_key,
                base_url=base_url or "https://api.siliconflow.cn/v1",
            )

            if not provider.validate_config():
                return {"status": "error", "error": "Invalid configuration"}

            # 健康检查
            result = await provider.health_check()
            await provider.close()

            if result["status"] == "healthy":
                return {
                    "status": "success",
                    "latency_ms": result.get("status_code", 200),
                    "message": "Connection successful"
                }
            else:
                return {"status": "error", "error": result.get("error", "Unknown error")}
        else:
            return {"status": "error", "error": f"Provider {config.provider} not supported for testing"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/chat")
async def chat(request: ChatRequest):
    """发送对话请求"""
    gateway = get_gateway()

    # 确保Provider已配置
    if not gateway._providers:
        # 尝试从配置文件加载
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)

    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured. Please configure a provider first.")

    try:
        response = await gateway.chat(
            prompt=request.prompt,
            model=request.model,
            system=request.system,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return {
            "status": "success",
            "data": {
                "content": response.content,
                "model": response.model,
                "provider": response.provider,
                "latency_ms": response.latency_ms,
                "usage": response.usage,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-evaluate")
async def interview_evaluate(request: InterviewEvaluateRequest):
    """面试评估"""
    gateway = get_gateway()

    # 确保Provider已配置
    if not gateway._providers:
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)

    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured")

    try:
        result = await gateway.interview_evaluate(
            question=request.question,
            answer=request.answer,
            context=request.context,
        )

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/negotiation-message")
async def negotiation_message(request: NegotiationMessageRequest):
    """生成谈判消息"""
    gateway = get_gateway()

    # 确保Provider已配置
    if not gateway._providers:
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)

    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured")

    try:
        message = await gateway.negotiation_message(
            situation=request.situation,
            tone=request.tone,
            candidate_info=request.candidate_info,
            company_offer=request.company_offer,
        )

        return {"status": "success", "data": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """获取用量统计"""
    gateway = get_gateway()
    return {"status": "success", "data": gateway.get_usage_stats()}


@router.get("/health")
async def health_check():
    """健康检查"""
    gateway = get_gateway()
    results = await gateway.health_check()
    return {"status": "success", "data": results}


@router.post("/default-model")
async def set_default_model(provider_id: str, model_id: str):
    """设置默认模型"""
    gateway = get_gateway()
    gateway.config.default_provider = provider_id
    gateway.config.default_model = model_id
    return {"status": "success", "message": f"Default model set to {provider_id}/{model_id}"}


# ========== Semantic Matching Endpoints ==========

class SemanticMatchRequest(BaseModel):
    job_info: Dict[str, Any]
    candidate_info: Dict[str, Any]


class BatchMatchRequest(BaseModel):
    job_info: Dict[str, Any]
    candidates: List[Dict[str, Any]]


@router.post("/semantic-match")
async def semantic_match(request: SemanticMatchRequest):
    """语义匹配评估"""
    gateway = get_gateway()

    # 确保Provider已配置
    if not gateway._providers:
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)

    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured")

    try:
        matcher = LLMSemanticMatching(gateway)
        result = await matcher.overall_match(
            job_info=request.job_info,
            candidate_info=request.candidate_info,
        )

        return {"status": "success", "data": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-match/batch")
async def batch_semantic_match(request: BatchMatchRequest):
    """批量语义匹配"""
    gateway = get_gateway()

    if not gateway._providers:
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)

    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured")

    try:
        matcher = LLMSemanticMatching(gateway)
        results = await matcher.batch_match(
            job_info=request.job_info,
            candidates=request.candidates,
        )

        return {
            "status": "success",
            "data": [r.to_dict() for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-match/interview-focus")
async def get_interview_focus(request: SemanticMatchRequest):
    """获取面试重点考察方向"""
    gateway = get_gateway()

    if not gateway._providers:
        registry = get_registry()
        for p_id, p_config in registry.providers.items():
            if p_config.api_key:
                gateway.configure_provider(p_id, p_config.api_key, p_config.base_url)

    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured")

    try:
        matcher = LLMSemanticMatching(gateway)
        focus_areas = await matcher.suggest_interview_focus(
            job_info=request.job_info,
            candidate_info=request.candidate_info,
        )

        return {"status": "success", "data": focus_areas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
