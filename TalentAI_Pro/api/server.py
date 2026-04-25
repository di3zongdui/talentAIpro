"""
TalentAI Pro - Agent API Server
Agent信任与通信协议 v2 API

运行方式:
    cd TalentAI_Pro
    uvicorn api.server:app --reload --port 8089

或者直接运行:
    python api/server.py
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import os

# 创建FastAPI应用
app = FastAPI(
    title="TalentAI Pro - Agent API",
    description="""
## Agent信任与通信协议 API v2

基于第一性原理设计的Agent信任架构，支持：

### 核心功能
- **Agent注册与认证** - 代理授权链
- **动态偏好模型** - 理解人类真实偏好
- **用途绑定披露** - 原子化信息 + ZKP
- **语义共识层** - 跨平台概念对齐
- **谈判协议** - Agent间自动谈判
- **实时通信** - WebSocket消息推送

### 架构理念
> 让人类信任Agent替自己做出重要招聘决策

所有API都遵循：
- 透明的授权边界
- 可验证的代理声明
- 人类控制权优先
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API v2 端点导入 ==========

try:
    from api.v2 import router as v2_router
except ImportError:
    v2_router = None
    print("[Warning] v2 router not available")

# LLM路由
try:
    from api.llm_routes import router as llm_router
except ImportError:
    llm_router = None
    print("[Warning] llm router not available")

# 注册v2路由
if v2_router:
    app.include_router(v2_router)

# 注册LLM路由
if llm_router:
    app.include_router(llm_router)

# ========== 静态文件服务 ==========
# 提供前端页面访问
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    print(f"[Static] Serving frontend from {frontend_path}")

    # 添加根路径重定向到前端
    @app.get("/")
    async def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/frontend/llm_test_dashboard.html")


# ========== 根路径 ==========

@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "TalentAI Pro - Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "agent_api_v2": "/api/v2",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": "2026-04-25T00:14:00Z",
        "services": {
            "api_v1": "legacy",
            "api_v2": "active",
            "websocket": "active"
        }
    }


# ========== WebSocket端点 ==========

class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        print(f"[WS] Agent {agent_id} connected. Total: {len(self.active_connections)}")

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]
            print(f"[WS] Agent {agent_id} disconnected. Total: {len(self.active_connections)}")

    async def send_to_agent(self, agent_id: str, message: dict):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_json(message)
            return True
        return False

    async def broadcast(self, message: dict, exclude: list[str] = None):
        exclude = exclude or []
        for agent_id, ws in self.active_connections.items():
            if agent_id not in exclude:
                await ws.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    """Agent WebSocket连接端点"""
    agent_id = None
    try:
        # 等待认证消息
        auth_data = await websocket.receive_json()
        if auth_data.get("type") == "auth":
            agent_id = auth_data.get("agent_id")
            await manager.connect(agent_id, websocket)

            await websocket.send_json({
                "type": "auth_success",
                "agent_id": agent_id,
                "message": "Connected to TalentAI Pro Agent Network"
            })

            # 处理消息循环
            while True:
                data = await websocket.receive_json()

                if data.get("type") == "message":
                    # 转发消息给目标Agent
                    to_agent = data.get("to_agent")
                    success = await manager.send_to_agent(to_agent, {
                        "type": "message",
                        "from_agent": agent_id,
                        "content": data.get("content", {}),
                        "timestamp": data.get("timestamp")
                    })

                    if not success:
                        await websocket.send_json({
                            "type": "delivery_failed",
                            "to_agent": to_agent,
                            "reason": "Agent not connected"
                        })

                elif data.get("type") == "subscribe":
                    # 订阅事件
                    event_type = data.get("event_type")
                    await websocket.send_json({
                        "type": "subscribed",
                        "event_type": event_type
                    })

                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        if agent_id:
            manager.disconnect(agent_id)
    except Exception as e:
        print(f"[WS] Error: {e}")
        if agent_id:
            manager.disconnect(agent_id)


# ========== 运行服务器 ==========

def run_server(port: int = 8089, host: str = "0.0.0.0"):
    """运行API服务器"""
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   TalentAI Pro - Agent API Server v2.0                     ║
║                                                           ║
║   API文档: http://localhost:{port}/docs                      ║
║   WebSocket: ws://localhost:{port}/ws/agents                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
