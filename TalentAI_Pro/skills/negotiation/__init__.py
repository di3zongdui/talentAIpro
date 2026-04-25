"""
TalentAI Pro - Negotiation Skill
================================
Shared negotiation engine for Recruiter Agent and Candidate Agent.

Usage:
    from skills.negotiation import NegotiationEngine

    # From Recruiter Agent perspective
    engine = NegotiationEngine(
        perspective='recruiter',
        company_offer={...},
        candidate_expectation={...}
    )
    proposals = engine.generate_proposals()

    # From Candidate Agent perspective
    engine = NegotiationEngine(
        perspective='candidate',
        company_offer={...},
        candidate_expectation={...}
    )
    proposals = engine.generate_proposals()
"""

from .engine import NegotiationEngine
from .strategies import StrategyConfig, NegotiationStrategyLibrary, StrategyType
from .prompts import MessageTemplate, ChannelType

__all__ = [
    'NegotiationEngine',
    'StrategyConfig',
    'NegotiationStrategyLibrary',
    'StrategyType',
    'MessageTemplate',
    'ChannelType',
]

__version__ = '1.0.0'
__author__ = 'TalentAI Pro'
