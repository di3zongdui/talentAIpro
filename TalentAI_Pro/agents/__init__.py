"""
TalentAI Pro Agents Package
AI Agents for recruitment ecosystem

Modules:
- interview: Interview Agent (面试Agent)
- recruiter: Recruiter Agent (招聘Agent)
- candidate: Candidate Agent (候选人Agent)
"""

from .base import Agent, AgentCapability, AgentType, AgentStatus
from .registry import AgentRegistry

__all__ = [
    'Agent',
    'AgentCapability',
    'AgentType',
    'AgentStatus',
    'AgentRegistry',
]

# Agent Registry Singleton
_registry = AgentRegistry()

def get_agent(agent_type: str) -> Agent:
    """Get an agent instance by type"""
    return _registry.get(agent_type)

def register_agent(agent: Agent):
    """Register an agent"""
    _registry.register(agent)
