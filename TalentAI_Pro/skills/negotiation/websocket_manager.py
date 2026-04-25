"""
Negotiation WebSocket Manager - 谈判WebSocket通信层
====================================================
支持Recruiter Agent和Candidate Agent之间通过WebSocket实时传递谈判消息

Usage:
    from skills.negotiation.websocket_manager import NegotiationWebSocketManager

    ws_manager = NegotiationWebSocketManager()
    await ws_manager.send_negotiation_message(
        from_agent="recruiter_001",
        to_agent="candidate_001",
        message_type="counter_offer",
        payload={...}
    )
"""

import asyncio
import json
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """消息类型"""
    NEGOTIATION_START = "negotiation_start"
    COUNTER_OFFER = "counter_offer"
    COUNTER_RESPONSE = "counter_response"
    DEAL_PROPOSED = "deal_proposed"
    DEAL_ACCEPTED = "deal_accepted"
    DEAL_REJECTED = "deal_rejected"
    MESSAGE_SENT = "message_sent"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"
    NEGOTIATION_ENDED = "negotiation_ended"
    HEARTBEAT = "heartbeat"


class ChannelType(str, Enum):
    """渠道类型"""
    WECHAT = "wechat"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


@dataclass
class NegotiationMessage:
    """谈判消息"""
    id: str
    message_type: MessageType
    negotiation_id: str
    offer_id: str
    from_agent: str
    to_agent: str
    perspective: str  # 'recruiter' or 'candidate'
    round_num: int
    channel: ChannelType
    payload: Dict[str, Any]  # 包含offer、proposals等
    status: str = "pending"  # pending/sent/delivered/read/replied
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message_type": self.message_type.value if isinstance(self.message_type, Enum) else self.message_type,
            "negotiation_id": self.negotiation_id,
            "offer_id": self.offer_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "perspective": self.perspective,
            "round_num": self.round_num,
            "channel": self.channel.value if isinstance(self.channel, Enum) else self.channel,
            "payload": self.payload,
            "status": self.status,
            "created_at": self.created_at,
        }


class NegotiationWebSocketManager:
    """
    谈判WebSocket管理器

    功能：
    1. 管理Agent之间的WebSocket连接
    2. 实时传递谈判消息
    3. 跟踪消息状态（发送/送达/已读/回复）
    4. 支持消息订阅和回调
    """

    def __init__(self):
        # Agent连接映射: agent_id -> WebSocket
        self._connections: Dict[str, Any] = {}

        # 订阅者映射: event_type -> [callback列表]
        self._subscribers: Dict[str, List[Callable]] = {}

        # 消息队列（离线消息缓冲）
        self._message_queues: Dict[str, List[NegotiationMessage]] = {}

        # 回调映射
        self._message_handlers: Dict[MessageType, Callable] = {}

    def register_connection(self, agent_id: str, websocket: Any):
        """注册Agent WebSocket连接"""
        self._connections[agent_id] = websocket

        # 发送缓冲的消息
        if agent_id in self._message_queues:
            queue = self._message_queues.pop(agent_id)
            for msg in queue:
                asyncio.create_task(self._send_message(websocket, msg))

        print(f"[WS-Negotiation] Agent {agent_id} connected. Total: {len(self._connections)}")

    def unregister_connection(self, agent_id: str):
        """注销Agent连接"""
        if agent_id in self._connections:
            del self._connections[agent_id]
            print(f"[WS-Negotiation] Agent {agent_id} disconnected. Total: {len(self._connections)}")

    def is_connected(self, agent_id: str) -> bool:
        """检查Agent是否在线"""
        return agent_id in self._connections

    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def register_handler(self, message_type: MessageType, handler: Callable):
        """注册消息处理器"""
        self._message_handlers[message_type] = handler

    async def send_negotiation_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        negotiation_id: str,
        offer_id: str,
        perspective: str,
        round_num: int,
        channel: ChannelType,
        payload: Dict[str, Any],
    ) -> NegotiationMessage:
        """
        发送谈判消息

        Args:
            from_agent: 发送方Agent ID
            to_agent: 接收方Agent ID
            message_type: 消息类型
            negotiation_id: 谈判ID
            offer_id: Offer ID
            perspective: 视角
            round_num: 轮次
            channel: 渠道
            payload: 消息内容

        Returns:
            发送的消息对象
        """
        import uuid
        msg_id = str(uuid.uuid4())[:8]

        message = NegotiationMessage(
            id=msg_id,
            message_type=message_type,
            negotiation_id=negotiation_id,
            offer_id=offer_id,
            from_agent=from_agent,
            to_agent=to_agent,
            perspective=perspective,
            round_num=round_num,
            channel=channel,
            payload=payload,
            status="pending",
        )

        # 检查接收方是否在线
        if to_agent in self._connections:
            await self._send_message(self._connections[to_agent], message)
            message.status = "sent"
        else:
            # 缓冲离线消息
            if to_agent not in self._message_queues:
                self._message_queues[to_agent] = []
            self._message_queues[to_agent].append(message)
            message.status = "queued"

        # 触发订阅回调
        await self._notify_subscribers(message_type.value, message)

        return message

    async def _send_message(self, websocket: Any, message: NegotiationMessage):
        """通过WebSocket发送消息"""
        try:
            await websocket.send_json({
                "type": "negotiation_message",
                "data": message.to_dict()
            })
            message.status = "sent"
        except Exception as e:
            print(f"[WS-Negotiation] Failed to send message: {e}")
            message.status = "failed"

    async def handle_incoming_message(self, agent_id: str, data: Dict[str, Any]) -> NegotiationMessage:
        """
        处理收到的消息

        Args:
            agent_id: 收到消息的Agent ID
            data: 消息数据

        Returns:
            解析后的消息对象
        """
        message_type = MessageType(data.get("message_type", "counter_offer"))
        payload = data.get("payload", {})

        message = NegotiationMessage(
            id=data.get("id", ""),
            message_type=message_type,
            negotiation_id=data.get("negotiation_id", ""),
            offer_id=data.get("offer_id", ""),
            from_agent=data.get("from_agent", ""),
            to_agent=data.get("to_agent", ""),
            perspective=data.get("perspective", ""),
            round_num=data.get("round_num", 1),
            channel=ChannelType(data.get("channel", "in_app")),
            payload=payload,
            status="received",
        )

        # 调用处理器
        if message_type in self._message_handlers:
            await self._message_handlers[message_type](message)

        # 通知订阅者
        await self._notify_subscribers("message_received", message)

        return message

    async def _notify_subscribers(self, event_type: str, message: NegotiationMessage):
        """通知订阅者"""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    print(f"[WS-Negotiation] Subscriber callback error: {e}")

    async def broadcast_to_negotiation_parties(
        self,
        negotiation_id: str,
        message: Dict[str, Any],
        exclude_agent: Optional[str] = None,
    ):
        """广播消息给谈判双方"""
        for agent_id, ws in self._connections.items():
            if agent_id == exclude_agent:
                continue
            try:
                await ws.send_json({
                    "type": "negotiation_broadcast",
                    "negotiation_id": negotiation_id,
                    "data": message,
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                print(f"[WS-Negotiation] Broadcast error: {e}")

    def get_connection_status(self) -> Dict[str, Any]:
        """获取连接状态"""
        return {
            "total_connections": len(self._connections),
            "connected_agents": list(self._connections.keys()),
            "queued_messages": sum(len(q) for q in self._message_queues.values()),
        }

    # ========== 便捷方法 ==========

    async def start_negotiation(
        self,
        recruiter_agent: str,
        candidate_agent: str,
        negotiation_id: str,
        offer_id: str,
        initial_offer: Dict[str, Any],
    ) -> NegotiationMessage:
        """开始一轮谈判"""
        return await self.send_negotiation_message(
            from_agent=recruiter_agent,
            to_agent=candidate_agent,
            message_type=MessageType.NEGOTIATION_START,
            negotiation_id=negotiation_id,
            offer_id=offer_id,
            perspective="recruiter",
            round_num=1,
            channel=ChannelType.IN_APP,
            payload={
                "initial_offer": initial_offer,
                "action": "Please review and respond",
            },
        )

    async def send_counter_offer(
        self,
        from_agent: str,
        to_agent: str,
        negotiation_id: str,
        offer_id: str,
        perspective: str,
        round_num: int,
        counter_offer: Dict[str, Any],
        message: str,
    ) -> NegotiationMessage:
        """发送还价"""
        return await self.send_negotiation_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.COUNTER_OFFER,
            negotiation_id=negotiation_id,
            offer_id=offer_id,
            perspective=perspective,
            round_num=round_num,
            channel=ChannelType.WECHAT,
            payload={
                "counter_offer": counter_offer,
                "message": message,
            },
        )

    async def send_deal_proposal(
        self,
        from_agent: str,
        to_agent: str,
        negotiation_id: str,
        offer_id: str,
        perspective: str,
        round_num: int,
        final_proposal: Dict[str, Any],
    ) -> NegotiationMessage:
        """发送成交提案"""
        return await self.send_negotiation_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.DEAL_PROPOSED,
            negotiation_id=negotiation_id,
            offer_id=offer_id,
            perspective=perspective,
            round_num=round_num,
            channel=ChannelType.WECHAT,
            payload={
                "final_proposal": final_proposal,
                "action": "Please accept or reject",
            },
        )

    async def notify_deal_accepted(
        self,
        negotiation_id: str,
        recruiter_agent: str,
        candidate_agent: str,
        final_terms: Dict[str, Any],
    ):
        """通知交易达成"""
        message = {
            "negotiation_id": negotiation_id,
            "final_terms": final_terms,
            "status": "accepted",
            "timestamp": datetime.now().isoformat(),
        }

        await self.broadcast_to_negotiation_parties(
            negotiation_id,
            {
                "type": "deal_accepted",
                **message,
            },
        )


# 全局实例
_ws_manager: Optional[NegotiationWebSocketManager] = None


def get_websocket_manager() -> NegotiationWebSocketManager:
    """获取全局WebSocket管理器实例"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = NegotiationWebSocketManager()
    return _ws_manager
