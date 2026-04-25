"""
SiliconFlow Provider 实现
========================

支持 SiliconFlow API (https://api.siliconflow.cn)

Usage:
    from TalentAI_Pro.llm import SiliconFlowProvider

    provider = SiliconFlowProvider(api_key="sk-xxx")
    response = await provider.chat(messages, model="Qwen/Qwen3-Omni-30B-A3B-Instruct")
"""

import httpx
import json
import time
import asyncio
from typing import List, Optional, Dict, Any
import logging

from .provider import (
    BaseProvider,
    ProviderType,
    LLMResponse,
    StreamCallback,
    Message,
)


logger = logging.getLogger(__name__)


class SiliconFlowProvider(BaseProvider):
    """SiliconFlow API Provider"""

    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1"):
        super().__init__(api_key, base_url)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.SILICONFLOW

    async def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=30.0),
            )
        return self._client

    async def close(self):
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def chat(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """发送对话请求"""
        start_time = time.time()

        # 构建请求
        request_messages = self._format_messages(messages)
        payload = {
            "model": model,
            "messages": request_messages,
            "temperature": temperature,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # 发送请求
        client = await self._get_client()

        try:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            latency = (time.time() - start_time) * 1000

            return LLMResponse(
                content=content,
                model=model,
                provider=self.provider_type.value,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                latency_ms=latency,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"SiliconFlow API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"SiliconFlow request failed: {e}")
            raise

    async def stream(
        self,
        messages: List[Message],
        model: str,
        callback: StreamCallback,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """流式对话"""
        start_time = time.time()

        request_messages = self._format_messages(messages)
        payload = {
            "model": model,
            "messages": request_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        client = await self._get_client()

        try:
            async with client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()

                full_content = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            chunk = data["choices"][0].get("delta", {}).get("content", "")
                            if chunk:
                                full_content += chunk
                                await callback(chunk)
                        except json.JSONDecodeError:
                            continue

                latency = (time.time() - start_time) * 1000

                # 获取usage（部分API会返回）
                usage = {}
                try:
                    # 发送一个非流式请求获取usage
                    non_stream_payload = {**payload, "stream": False}
                    non_stream_resp = await client.post("/chat/completions", json=non_stream_payload)
                    if non_stream_resp.status_code == 200:
                        usage = non_stream_resp.json().get("usage", {})
                except:
                    pass

                return LLMResponse(
                    content=full_content,
                    model=model,
                    provider=self.provider_type.value,
                    usage=usage,
                    latency_ms=latency,
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"SiliconFlow stream error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"SiliconFlow stream failed: {e}")
            raise

    def _format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """格式化消息列表"""
        return [{"role": m.role, "content": m.content} for m in messages]

    def list_models(self) -> List[str]:
        """列出可用模型"""
        return [
            "Qwen/Qwen3-Omni-30B-A3B-Instruct",
            "Qwen/QwQ-32B",
            "deepseek-ai/DeepSeek-V3",
            "THUDM/GLM-4-0520",
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/DeepSeek-R1",
        ]

    def validate_config(self) -> bool:
        """验证配置"""
        if not self.api_key:
            return False
        if not self.base_url:
            return False
        return True

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            client = await self._get_client()
            # 发送一个最小请求测试连接
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.list_models()[0],
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5,
                }
            )
            return {
                "status": "healthy" if response.status_code == 200 else "error",
                "status_code": response.status_code,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
