"""
TalentAI Pro - Agents Package
Multi-Agent Recruitment Ecosystem
"""

from .base import (
    Agent,
    AgentProfile,
    AgentType,
    AgentStatus,
    AgentCapability,
    AgentMessage,
    ProxyAuthorization,
    AgentDecision,
)

from .registry import AgentRegistry

# Import specific agents
try:
    from .recruiter.agent import RecruiterAgent
except ImportError:
    RecruiterAgent = None

try:
    from .candidate.agent import CandidateAgent
except ImportError:
    CandidateAgent = None

# Import interview components
try:
    from .interview import (
        QuestionGenerator,
        EvaluationEngine,
        ReportGenerator,
        InterviewSession,
        InterviewSessionManager,
        InterviewType,
        InterviewState,
        EVALUATION_DIMENSIONS,
        RECOMMENDATION_LEVELS,
    )
except ImportError:
    QuestionGenerator = None
    EvaluationEngine = None
    ReportGenerator = None
    InterviewSession = None
    InterviewSessionManager = None
    InterviewType = None
    InterviewState = None
    EVALUATION_DIMENSIONS = None
    RECOMMENDATION_LEVELS = None


__all__ = [
    # Base classes
    'Agent',
    'AgentProfile',
    'AgentType',
    'AgentStatus',
    'AgentCapability',
    'AgentMessage',
    'ProxyAuthorization',
    'AgentDecision',
    # Registry
    'AgentRegistry',
    # Recruiter Agent
    'RecruiterAgent',
    # Candidate Agent
    'CandidateAgent',
    # Interview Agent components
    'QuestionGenerator',
    'EvaluationEngine',
    'ReportGenerator',
    'InterviewSession',
    'InterviewSessionManager',
    'InterviewType',
    'InterviewState',
    'EVALUATION_DIMENSIONS',
    'RECOMMENDATION_LEVELS',
]


def get_agent(agent_type: str):
    """Factory function to get an agent by type"""
    if agent_type == 'recruiter':
        if RecruiterAgent:
            return RecruiterAgent(owner_id='system', owner_name='Recruiter')
    elif agent_type == 'candidate':
        if CandidateAgent:
            return CandidateAgent(owner_id='system', owner_name='Candidate')

    raise ValueError(f"Unknown agent type: {agent_type}")


def list_available_agents():
    """List all available agent types"""
    return {
        'recruiter': RecruiterAgent is not None,
        'candidate': CandidateAgent is not None,
        'interview': QuestionGenerator is not None,
    }
