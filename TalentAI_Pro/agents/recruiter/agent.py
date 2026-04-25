"""
Recruiter Agent
Represents HR/Recruiter in the ecosystem
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base import (
    Agent, AgentProfile, AgentType, AgentCapability,
    AgentMessage, ProxyAuthorization, AgentDecision
)

# Import Negotiation Engine Skill
from skills.negotiation import NegotiationEngine
from skills.negotiation.prompts import ChannelType


class RecruiterAgent(Agent):
    """
    Recruiter Agent - automates recruitment tasks

    Capabilities:
    - Search and discover candidates
    - Screen resumes automatically
    - Schedule interviews
    - Make job offers
    - Negotiate offers (via NegotiationEngine Skill)
    - Manage onboarding
    """

    def __init__(self, owner_id: str, owner_name: str, company_id: str = "", company_name: str = ""):
        profile = AgentProfile(
            name=f"Recruiter_{owner_name}",
            type=AgentType.RECRUITER,
            description="AI Recruitment Agent - automates candidate search, screening, and hiring",
            capabilities=[
                AgentCapability.SEARCH_CANDIDATES,
                AgentCapability.SCREEN_RESUMES,
                AgentCapability.SCHEDULE_INTERVIEWS,
                AgentCapability.MAKE_OFFERS,
                AgentCapability.NEGOTIATE_OFFERS,
                AgentCapability.ONBOARD_CANDIDATES,
                AgentCapability.COMMUNICATE,
                AgentCapability.LEARN_PREFERENCES,
            ],
            owner_id=owner_id,
            owner_name=owner_name,
            metadata={
                "company_id": company_id,
                "company_name": company_name,
            }
        )
        super().__init__(profile)

        # Recruiter-specific state
        self._active_requisitions: Dict[str, Dict[str, Any]] = {}
        self._candidate_pool: Dict[str, Dict[str, Any]] = {}
        self._interview_schedules: Dict[str, Dict[str, Any]] = {}
        self._offers_made: Dict[str, Dict[str, Any]] = {}

        # Negotiation state - one engine per active negotiation
        self._negotiation_engines: Dict[str, NegotiationEngine] = {}
        self._negotiation_history: Dict[str, List[Dict[str, Any]]] = {}

    @property
    def company_id(self) -> str:
        return self.profile.metadata.get("company_id", "")

    @property
    def company_name(self) -> str:
        return self.profile.metadata.get("company_name", "")

    # ========== Requisition Management ==========

    def create_requisition(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job requisition

        job_data: {
            "title": "Senior Python Engineer",
            "department": "Engineering",
            "level": "senior",
            "skills": ["Python", "FastAPI"],
            "experience_years": 5,
            "salary_range": {"min": 30000, "max": 50000},
            "description": "..."
        }
        """
        req_id = f"req_{self.id}_{len(self._active_requisitions) + 1}"

        requisition = {
            "id": req_id,
            "job_title": job_data.get("title"),
            "department": job_data.get("department"),
            "level": job_data.get("level"),
            "required_skills": job_data.get("skills", []),
            "experience_years": job_data.get("experience_years"),
            "salary_range": job_data.get("salary_range"),
            "description": job_data.get("description"),
            "status": "open",
            "candidates_applied": [],
            "candidates_screened": [],
            "candidates_interviewed": [],
            "candidates_offered": [],
            "candidates_hired": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self._active_requisitions[req_id] = requisition
        return requisition

    def get_requisition(self, req_id: str) -> Optional[Dict[str, Any]]:
        return self._active_requisitions.get(req_id)

    def list_requisitions(self, status: str = None) -> List[Dict[str, Any]]:
        if status:
            return [r for r in self._active_requisitions.values() if r["status"] == status]
        return list(self._active_requisitions.values())

    def update_requisition_status(self, req_id: str, status: str) -> bool:
        if req_id in self._active_requisitions:
            self._active_requisitions[req_id]["status"] = status
            self._active_requisitions[req_id]["updated_at"] = datetime.now().isoformat()
            return True
        return False

    # ========== Candidate Search & Matching ==========

    def search_candidates(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for candidates matching criteria

        criteria: {
            "skills": ["Python", "React"],
            "experience_years_min": 3,
            "location": "北京",
            "salary_expectation_max": 40000,
        }
        """
        # In production, this would call external job boards, LinkedIn, etc.
        # For now, return mock candidates from pool
        results = []

        for candidate_id, candidate in self._candidate_pool.items():
            score = self._calculate_match_score(candidate, criteria)
            if score > 0.5:
                results.append({
                    "candidate_id": candidate_id,
                    "match_score": score,
                    "candidate_data": candidate,
                })

        # Sort by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

    def _calculate_match_score(self, candidate: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate how well a candidate matches criteria"""
        score = 0.0
        weights = 0.0

        # Skills match (40%)
        required_skills = set(criteria.get("skills", []))
        candidate_skills = set(candidate.get("skills", []))
        if required_skills:
            skill_match = len(required_skills & candidate_skills) / len(required_skills)
            score += skill_match * 0.4
            weights += 0.4

        # Experience match (30%)
        exp_min = criteria.get("experience_years_min", 0)
        candidate_exp = candidate.get("experience_years", 0)
        if exp_min and candidate_exp >= exp_min:
            exp_score = min(1.0, candidate_exp / (exp_min * 1.5))
            score += exp_score * 0.3
            weights += 0.3

        # Salary match (20%)
        salary_max = criteria.get("salary_expectation_max")
        candidate_salary = candidate.get("salary_expectation")
        if salary_max and candidate_salary:
            if candidate_salary <= salary_max:
                score += 0.2
            weights += 0.2

        # Location match (10%)
        preferred_location = criteria.get("location")
        candidate_location = candidate.get("location")
        if preferred_location and candidate_location:
            if preferred_location.lower() in candidate_location.lower():
                score += 0.1
            weights += 0.1

        return score / weights if weights > 0 else 0.0

    def add_candidate_to_pool(self, candidate_data: Dict[str, Any]) -> str:
        """Add a candidate to the pool"""
        candidate_id = f"cand_{len(self._candidate_pool) + 1}"
        candidate_data["id"] = candidate_id
        candidate_data["added_at"] = datetime.now().isoformat()
        self._candidate_pool[candidate_id] = candidate_data
        return candidate_id

    # ========== Resume Screening ==========

    def screen_candidate(self, candidate_id: str, requisition_id: str) -> Dict[str, Any]:
        """
        Screen a candidate for a specific requisition

        Returns screening result with match analysis
        """
        candidate = self._candidate_pool.get(candidate_id)
        requisition = self._active_requisitions.get(requisition_id)

        if not candidate or not requisition:
            return {"error": "Candidate or requisition not found"}

        # Calculate detailed match
        required_skills = set(requisition.get("required_skills", []))
        candidate_skills = set(candidate.get("skills", []))
        matched_skills = required_skills & candidate_skills
        missing_skills = required_skills - candidate_skills

        # Experience assessment
        required_exp = requisition.get("experience_years", 0)
        candidate_exp = candidate.get("experience_years", 0)

        # Generate screening report
        screening = {
            "candidate_id": candidate_id,
            "requisition_id": requisition_id,
            "overall_score": self._calculate_match_score(candidate, {
                "skills": requisition.get("required_skills", []),
                "experience_years_min": required_exp,
                "salary_expectation_max": requisition.get("salary_range", {}).get("max"),
            }),
            "skills_match": {
                "matched": list(matched_skills),
                "missing": list(missing_skills),
                "match_rate": len(matched_skills) / len(required_skills) if required_skills else 1.0,
            },
            "experience_assessment": {
                "required": required_exp,
                "candidate": candidate_exp,
                "meets_requirement": candidate_exp >= required_exp,
            },
            "recommendation": self._generate_screening_recommendation(candidate_exp, required_exp, matched_skills, required_skills),
            "screened_at": datetime.now().isoformat(),
        }

        # Update requisition
        if candidate_id not in requisition["candidates_applied"]:
            requisition["candidates_applied"].append(candidate_id)
        requisition["candidates_screened"].append(candidate_id)

        return screening

    def _generate_screening_recommendation(self, exp: int, req_exp: int, matched: set, required: set) -> str:
        """Generate screening recommendation text"""
        if exp < req_exp:
            return "consider"  # Experience below requirement
        if not matched:
            return "reject"  # No matching skills
        match_rate = len(matched) / len(required) if required else 1.0
        if match_rate >= 0.8:
            return "strong_pass"
        elif match_rate >= 0.5:
            return "pass"
        elif match_rate >= 0.3:
            return "consider"
        return "reject"

    # ========== Interview Scheduling ==========

    def schedule_interview(self, requisition_id: str, candidate_id: str,
                          interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule an interview for a candidate

        interview_data: {
            "interview_type": "technical",
            "duration_minutes": 60,
            "interviewer_ids": ["interviewer_1"],
            "preferred_slots": ["2026-04-26T10:00", "2026-04-26T14:00"],
        }
        """
        schedule_id = f"int_{requisition_id}_{candidate_id}_{len(self._interview_schedules) + 1}"

        schedule = {
            "id": schedule_id,
            "requisition_id": requisition_id,
            "candidate_id": candidate_id,
            "interview_type": interview_data.get("interview_type", "general"),
            "duration_minutes": interview_data.get("duration_minutes", 60),
            "interviewers": interview_data.get("interviewer_ids", []),
            "scheduled_time": None,  # Will be confirmed
            "status": "pending_confirmation",
            "interview_agent_id": None,  # AI Interview Agent
            "created_at": datetime.now().isoformat(),
        }

        self._interview_schedules[schedule_id] = schedule

        # Update requisition
        if requisition_id in self._active_requisitions:
            self._active_requisitions[requisition_id]["candidates_interviewed"].append(candidate_id)

        return schedule

    # ========== Offer Management ==========

    def create_offer(self, requisition_id: str, candidate_id: str,
                     offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a job offer for a candidate

        offer_data: {
            "salary": 40000,
            "bonus": 20000,
            " equity": 0.01,
            "start_date": "2026-05-01",
            "benefits": ["五险一金", "年度旅游"],
        }
        """
        offer_id = f"offer_{requisition_id}_{candidate_id}_{len(self._offers_made) + 1}"

        # Check authorization
        if not self.can_auto_decide("make_offers", 0.9):
            # Need human approval
            decision = AgentDecision(
                agent_id=self.id,
                action="make_offer",
                context={
                    "requisition_id": requisition_id,
                    "candidate_id": candidate_id,
                    "offer_data": offer_data,
                },
                reasoning=f"Creating offer for candidate {candidate_id}",
                confidence=0.9,
                auto_approved=False,
            )
            self.record_decision(decision)
            return {
                "requires_approval": True,
                "decision_id": decision.id,
                "offer_id": offer_id,
            }

        return self._create_offer_internal(offer_id, requisition_id, candidate_id, offer_data)

    def _create_offer_internal(self, offer_id: str, req_id: str, cand_id: str,
                                offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to create offer"""
        offer = {
            "id": offer_id,
            "requisition_id": req_id,
            "candidate_id": cand_id,
            "salary": offer_data.get("salary"),
            "bonus": offer_data.get("bonus"),
            "equity": offer_data.get("equity"),
            "start_date": offer_data.get("start_date"),
            "benefits": offer_data.get("benefits", []),
            "status": "pending_response",
            "created_at": datetime.now().isoformat(),
            "responded_at": None,
            "response": None,
        }

        self._offers_made[offer_id] = offer

        # Update requisition
        if req_id in self._active_requisitions:
            self._active_requisitions[req_id]["candidates_offered"].append(cand_id)

        return offer

    def approve_and_create_offer(self, decision_id: str, approved: bool,
                                  modified_offer: Dict[str, Any] = None) -> Dict[str, Any]:
        """Human approves or rejects an offer decision"""
        # Find the decision
        decision = None
        for d in self.decision_history:
            if d.id == decision_id:
                decision = d
                break

        if not decision:
            return {"error": "Decision not found"}

        if approved:
            decision.approve("human_approver")
            offer_data = modified_offer or decision.context.get("offer_data", {})
            return self._create_offer_internal(
                decision.context.get("offer_id", f"offer_{len(self._offers_made)}"),
                decision.context.get("requisition_id"),
                decision.context.get("candidate_id"),
                offer_data
            )
        else:
            decision.reject("human_approver", "Offer rejected by human")
            return {"status": "rejected", "decision_id": decision_id}

    # ========== Message Processing ==========

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message from another agent"""
        content = message.content
        action = content.get("action")

        response_content = {}

        if action == "candidate_interest":
            # Candidate agent expressing interest in a requisition
            req_id = content.get("requisition_id")
            candidate_id = content.get("candidate_id")
            interest_level = content.get("interest_level", "medium")

            response_content = {
                "status": "received",
                "requisition_id": req_id,
                "candidate_id": candidate_id,
                "next_steps": "resume_screening" if interest_level in ["high", "medium"] else "no_match",
            }

        elif action == "request_candidate_info":
            # Another agent requesting candidate details
            candidate_id = content.get("candidate_id")
            candidate = self._candidate_pool.get(candidate_id, {})
            response_content = {"candidate": candidate}

        elif action == "negotiate_offer":
            # Candidate wants to negotiate
            offer_id = content.get("offer_id")
            negotiation_data = content.get("negotiation")
            response_content = self._process_negotiation(offer_id, negotiation_data)

        else:
            response_content = {"error": f"Unknown action: {action}"}

        return AgentMessage(
            to_agent=message.from_agent,
            from_agent=self.id,
            content=response_content,
            message_type="response",
            in_reply_to=message.id,
        )

    def _process_negotiation(self, offer_id: str, negotiation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process offer negotiation using NegotiationEngine Skill"""
        offer = self._offers_made.get(offer_id)
        if not offer:
            return {"error": "Offer not found"}

        offer = self._offers_made.get(offer_id)
        if not offer:
            return {"error": "Offer not found"}

        candidate_id = offer["candidate_id"]
        requisition_id = offer["requisition_id"]
        req = self._active_requisitions.get(requisition_id, {})
        candidate = self._candidate_pool.get(candidate_id, {})

        # Initialize negotiation engine if not exists
        if offer_id not in self._negotiation_engines:
            # Get job context
            job_context = {
                "candidate_name": candidate.get("name", "候选人"),
                "required_skills": req.get("skills", []),
                "candidate_skills": candidate.get("skills", []),
                "candidate_years": candidate.get("experience_years", 3),
                "required_years": req.get("experience_years", 3),
                "hiring_urgency": req.get("urgency", "normal"),
                "market_competition": req.get("market_competition", "medium"),
                "offer_percentile": 50,
                "candidate_market_percentile": 60,
                "growth_score": 0.80,
                "tech_stack_match": 0.85,
            }

            self._negotiation_engines[offer_id] = NegotiationEngine(
                perspective='recruiter',
                company_offer={
                    "salary": offer.get("salary", 0),
                    "signing_bonus": offer.get("signing_bonus", 0),
                    "rsu": offer.get("rsu", 0),
                    "vesting_years": 4,
                    "vacation_days": 10,
                    "remote_days": 1,
                    "learning_budget": 0,
                },
                candidate_expectation={
                    "salary": negotiation_data.get("counteroffer_salary", offer.get("salary", 0)),
                    "signing_bonus": negotiation_data.get("counteroffer_signing_bonus", 0),
                    "rsu": negotiation_data.get("counteroffer_rsu", 0),
                },
                job_context=job_context,
            )
            self._negotiation_history[offer_id] = []

        engine = self._negotiation_engines[offer_id]
        round_num = len(self._negotiation_history[offer_id]) + 1

        # Analyze sentiment from candidate's response
        sentiment = self._analyze_sentiment(negotiation_data)

        # Run negotiation engine
        result = engine.analyze_and_negotiate(
            round_num=round_num,
            counter_offer=negotiation_data,
            candidate_sentiment=sentiment,
        )

        # Record history
        self._negotiation_history[offer_id].append({
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "counter_offer": negotiation_data,
            "sentiment": sentiment,
            "proposals": result["proposals"],
            "deal_reached": result["deal_reached"],
        })

        # Update offer status
        if result["deal_reached"]:
            # Extract the agreed terms from the best proposal
            best_proposal = result["proposals"][0] if result["proposals"] else None
            if best_proposal:
                components = best_proposal.get("components", {})
                offer["salary"] = components.get("salary", offer["salary"])
                offer["signing_bonus"] = components.get("signing_bonus", offer.get("signing_bonus"))
                offer["rsu"] = components.get("rsu", offer.get("rsu"))
                offer["vacation_days"] = components.get("vacation_days", offer.get("vacation_days", 10))
                offer["remote_days"] = components.get("remote_days", offer.get("remote_days", 1))

            offer["status"] = "accepted"
            self._offers_made[offer_id] = offer

            return {
                "status": "deal_reached",
                "final_offer": offer,
                "message": result["message"]["body"],
                "mutual_fit": result["mutual_fit"],
            }

        # Return negotiation state for next round
        return {
            "status": "negotiation_continued",
            "round": round_num,
            "gap_analysis": result["gap"],
            "proposals": result["proposals"],
            "persuasion_for_company": result["persuasion"],
            "suggested_message": result["message"]["body"],
            "mutual_fit": result["mutual_fit"],
        }

    def _analyze_sentiment(self, negotiation_data: Dict[str, Any]) -> str:
        """Analyze candidate's sentiment from negotiation data"""
        text = str(negotiation_data.get("message", "")).lower()
        counteroffer = negotiation_data.get("counteroffer_salary", 0)

        # Simple sentiment analysis
        positive_keywords = ["可以", "接受", "好的", "满意", "同意", "yes", "acceptable"]
        negative_keywords = ["不行", "太低", "不接受", "太少", "no", "insufficient", "reject"]
        question_keywords = ["怎么", "能否", "是否", "可以", "how", "can", "?"]

        has_positive = any(kw in text for kw in positive_keywords)
        has_negative = any(kw in text for kw in negative_keywords)
        has_question = any(kw in text for kw in question_keywords)

        # High counteroffer indicates negative sentiment
        if counteroffer > 0:
            return "negative" if has_negative else "question"

        if has_positive and not has_negative:
            return "positive"
        elif has_negative:
            return "negative"
        elif has_question:
            return "question"
        else:
            return "neutral"

    def get_negotiation_status(self, offer_id: str) -> Dict[str, Any]:
        """Get current negotiation status"""
        if offer_id not in self._negotiation_engines:
            return {"error": "No active negotiation for this offer"}

        engine = self._negotiation_engines[offer_id]
        history = self._negotiation_history.get(offer_id, [])

        return {
            "offer_id": offer_id,
            "current_round": len(history),
            "history": history,
            "mutual_fit": engine.evaluate_mutual_fit(),
        }

    def _get_max_salary_for_offer(self, requisition_id: str) -> int:
        """Get max salary for a requisition"""
        req = self._active_requisitions.get(requisition_id, {})
        return req.get("salary_range", {}).get("max", 100000)

    # ========== Action Execution ==========

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a recruiter action"""
        if action == "search_candidates":
            return {"candidates": self.search_candidates(params.get("criteria", {}))}
        elif action == "screen_candidate":
            return self.screen_candidate(params.get("candidate_id"), params.get("requisition_id"))
        elif action == "schedule_interview":
            return self.schedule_interview(
                params.get("requisition_id"),
                params.get("candidate_id"),
                params.get("interview_data", {})
            )
        elif action == "create_offer":
            return self.create_offer(
                params.get("requisition_id"),
                params.get("candidate_id"),
                params.get("offer_data", {})
            )
        elif action == "list_requisitions":
            return {"requisitions": self.list_requisitions(params.get("status"))}
        else:
            return {"error": f"Unknown action: {action}"}
