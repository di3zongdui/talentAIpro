"""
Agent Registry
Central registry for all agents
"""

from typing import Dict, Optional, List
from .base import Agent, AgentType


class AgentRegistry:
    """Singleton registry for managing agents"""

    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._agents_by_owner: Dict[str, List[str]] = {}
        self._agents_by_type: Dict[AgentType, List[str]] = {}

    def register(self, agent: Agent) -> None:
        """Register an agent"""
        self._agents[agent.id] = agent

        # Index by owner
        owner_id = agent.profile.owner_id
        if owner_id not in self._agents_by_owner:
            self._agents_by_owner[owner_id] = []
        self._agents_by_owner[owner_id].append(agent.id)

        # Index by type
        agent_type = agent.profile.type
        if agent_type not in self._agents_by_type:
            self._agents_by_type[agent_type] = []
        self._agents_by_type[agent_type].append(agent.id)

    def unregister(self, agent_id: str) -> None:
        """Unregister an agent"""
        if agent_id not in self._agents:
            return

        agent = self._agents[agent_id]

        # Remove from owner index
        owner_id = agent.profile.owner_id
        if owner_id in self._agents_by_owner:
            self._agents_by_owner[owner_id].remove(agent_id)

        # Remove from type index
        agent_type = agent.profile.type
        if agent_type in self._agents_by_type:
            self._agents_by_type[agent_type].remove(agent_id)

        # Remove from agents
        del self._agents[agent_id]

    def get(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self._agents.get(agent_id)

    def get_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of a specific type"""
        agent_ids = self._agents_by_type.get(agent_type, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def get_by_owner(self, owner_id: str) -> List[Agent]:
        """Get all agents owned by a specific human"""
        agent_ids = self._agents_by_owner.get(owner_id, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def list_all(self) -> List[Agent]:
        """List all registered agents"""
        return list(self._agents.values())

    def count(self) -> int:
        """Total number of agents"""
        return len(self._agents)
