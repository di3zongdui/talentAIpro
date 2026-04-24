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


class RecruiterAgent(Agent):
    """
    Recruiter Agent - automates recruitment tasks

    Capabilities:
    - Search and discover candidates
    - Screen resumes automatically
    - Schedule interviews
    - Make job offers
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
        """Process offer negotiation"""
        offer = self._offers_made.get(offer_id)
        if not offer:
            return {"error": "Offer not found"}

        # Simple negotiation logic
        counteroffer_salary = negotiation_data.get("counteroffer_salary")
        if counteroffer_salary:
            current_salary = offer.get("salary", 0)
            max_salary = self._get_max_salary_for_offer(offer["requisition_id"])

            if counteroffer_salary <= max_salary:
                offer["salary"] = counteroffer_salary
                return {
                    "status": "counteroffer_accepted",
                    "new_offer": offer,
                }
            else:
                return {
                    "status": "counteroffer_rejected",
                    "reason": f"Exceeds maximum budget of {max_salary}",
                    "current_offer": offer,
                }

        return {"status": "negotiation_continued"}

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
