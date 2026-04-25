"""
Candidate Agent
Represents job seeker in the ecosystem
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base import (
    Agent, AgentProfile, AgentType, AgentCapability,
    AgentMessage, ProxyAuthorization, AgentDecision
)

# Import Negotiation Engine Skill
from skills.negotiation import NegotiationEngine


class CandidateAgent(Agent):
    """
    Candidate Agent - automates job search and application

    Capabilities:
    - Search jobs across platforms
    - Apply to matching positions
    - Prepare for interviews
    - Negotiate offers (via NegotiationEngine Skill)
    - Accept offers
    """

    def __init__(self, owner_id: str, owner_name: str):
        profile = AgentProfile(
            name=f"Candidate_{owner_name}",
            type=AgentType.CANDIDATE,
            description="AI Job Search Agent - automates job search, applications, and interview preparation",
            capabilities=[
                AgentCapability.SEARCH_JOBS,
                AgentCapability.APPLY_JOBS,
                AgentCapability.PREPARE_INTERVIEWS,
                AgentCapability.NEGOTIATE_OFFERS,
                AgentCapability.ACCEPT_OFFERS,
                AgentCapability.COMMUNICATE,
                AgentCapability.LEARN_PREFERENCES,
            ],
            owner_id=owner_id,
            owner_name=owner_name,
            metadata={}
        )
        super().__init__(profile)

        # Candidate-specific state
        self._profile: Dict[str, Any] = {}
        self._preferences: Dict[str, Any] = {}
        self._saved_jobs: List[Dict[str, Any]] = []
        self._applications: Dict[str, Dict[str, Any]] = {}
        self._interviews: Dict[str, Dict[str, Any]] = {}
        self._offers_received: Dict[str, Dict[str, Any]] = {}

        # Negotiation state
        self._negotiation_engines: Dict[str, NegotiationEngine] = {}
        self._negotiation_history: Dict[str, List[Dict[str, Any]]] = {}

    # ========== Profile Management ==========

    def set_profile(self, profile_data: Dict[str, Any]):
        """
        Set candidate profile

        profile_data: {
            "name": "张三",
            "email": "zhangsan@email.com",
            "phone": "13800138000",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_years": 5,
            "current_title": "高级工程师",
            "current_company": "某公司",
            "education": "硕士",
            "location": "北京",
            "salary_expectation": 40000,
            "work_preferences": {
                "remote_flexible": true,
                "min_salary": 35000,
                "preferred_locations": ["北京", "上海"],
                "work_life_balance": "high",
            }
        }
        """
        self._profile = profile_data

    def get_profile(self) -> Dict[str, Any]:
        return self._profile

    def update_preferences(self, preferences: Dict[str, Any]):
        """Update job search preferences"""
        self._preferences = preferences

    def get_preferences(self) -> Dict[str, Any]:
        return self._preferences

    # ========== Job Search ==========

    def search_jobs(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for matching jobs

        criteria: {
            "keywords": ["Python", "Senior"],
            "locations": ["北京", "上海"],
            "salary_min": 30000,
            "remote": true,
        }
        """
        # In production, this would call job boards APIs
        # For now, return mock results
        results = []

        # Mock job listings
        mock_jobs = self._get_mock_jobs()

        for job in mock_jobs:
            score = self._calculate_job_match(job, criteria)
            if score > 0.3:
                results.append({
                    "job": job,
                    "match_score": score,
                })

        # Sort by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

    def _calculate_job_match(self, job: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate how well a job matches criteria"""
        score = 0.0
        weights = 0.0

        # Skills match
        keywords = criteria.get("keywords", [])
        job_skills = set(job.get("skills", []))
        if keywords:
            keyword_match = len([k for k in keywords if any(k.lower() in s.lower() for s in job_skills)]) / len(keywords)
            score += keyword_match * 0.4
            weights += 0.4

        # Location match
        locations = criteria.get("locations", [])
        job_location = job.get("location", "")
        if locations:
            location_match = 1.0 if any(loc in job_location for loc in locations) else 0.3
            score += location_match * 0.2
            weights += 0.2

        # Salary match
        salary_min = criteria.get("salary_min", 0)
        job_salary = job.get("salary_max", 0)
        if salary_min and job_salary:
            salary_match = 1.0 if job_salary >= salary_min else 0.0
            score += salary_match * 0.2
            weights += 0.2

        # Remote match
        remote_required = criteria.get("remote", False)
        job_remote = job.get("remote", False)
        if remote_required:
            remote_match = 1.0 if job_remote else 0.0
            score += remote_match * 0.2
            weights += 0.2

        return score / weights if weights > 0 else 0.0

    def _get_mock_jobs(self) -> List[Dict[str, Any]]:
        """Get mock job listings"""
        return [
            {
                "id": "job_001",
                "title": "高级Python工程师",
                "company": "字节跳动",
                "location": "北京",
                "salary_min": 35000,
                "salary_max": 50000,
                "remote": True,
                "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                "description": "负责后端架构设计与开发",
            },
            {
                "id": "job_002",
                "title": "Senior Backend Engineer",
                "company": "某知名外企",
                "location": "上海",
                "salary_min": 40000,
                "salary_max": 60000,
                "remote": False,
                "skills": ["Python", "Go", "Kubernetes", "AWS"],
                "description": "Lead backend architecture",
            },
            {
                "id": "job_003",
                "title": "全栈工程师",
                "company": "创业公司",
                "location": "北京",
                "salary_min": 25000,
                "salary_max": 40000,
                "remote": True,
                "skills": ["Python", "React", "TypeScript", "PostgreSQL"],
                "description": "快速发展的创业团队",
            },
        ]

    def save_job(self, job: Dict[str, Any]):
        """Save a job for later"""
        if not any(j["id"] == job["id"] for j in self._saved_jobs):
            self._saved_jobs.append(job)

    def get_saved_jobs(self) -> List[Dict[str, Any]]:
        return self._saved_jobs

    # ========== Job Application ==========

    def apply_to_job(self, job: Dict[str, Any], cover_letter: str = None) -> Dict[str, Any]:
        """
        Apply to a job

        Returns application status
        """
        job_id = job.get("id")

        # Check authorization
        if not self.can_auto_decide("apply_jobs", 0.9):
            decision = AgentDecision(
                agent_id=self.id,
                action="apply_job",
                context={"job_id": job_id, "job": job},
                reasoning=f"Applying to {job.get('title')} at {job.get('company')}",
                confidence=0.9,
            )
            self.record_decision(decision)
            return {
                "requires_approval": True,
                "decision_id": decision.id,
                "application_id": f"app_{job_id}",
            }

        return self._create_application(job_id, job, cover_letter)

    def _create_application(self, job_id: str, job: Dict[str, Any],
                           cover_letter: str = None) -> Dict[str, Any]:
        """Internal method to create application"""
        application = {
            "id": f"app_{job_id}",
            "job_id": job_id,
            "job_title": job.get("title"),
            "company": job.get("company"),
            "status": "submitted",
            "applied_at": datetime.now().isoformat(),
            "cover_letter": cover_letter,
            "interview_scheduled": False,
            "interview_id": None,
        }

        self._applications[job_id] = application
        return application

    def get_applications(self, status: str = None) -> List[Dict[str, Any]]:
        if status:
            return [a for a in self._applications.values() if a["status"] == status]
        return list(self._applications.values())

    # ========== Interview Preparation ==========

    def prepare_for_interview(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interview preparation materials
        """
        preparation = {
            "company_research": self._research_company(job.get("company")),
            "common_questions": self._get_common_questions(job),
            "technical_topics": self._get_technical_topics(job),
            "questions_to_ask": self._get_questions_to_ask(job),
            "salary_tips": self._get_salary_tips(job),
            "created_at": datetime.now().isoformat(),
        }

        # Store for this job
        job_id = job.get("id")
        if job_id:
            self._interviews[job_id] = preparation

        return preparation

    def _research_company(self, company: str) -> Dict[str, Any]:
        """Research company information"""
        # In production, would call web search
        return {
            "name": company,
            "industry": "Technology",
            "size": "1000-5000 employees",
            "notable_products": ["Product A", "Product B"],
            "culture_notes": "Fast-paced, innovation-focused",
        }

    def _get_common_questions(self, job: Dict[str, Any]) -> List[str]:
        """Get common interview questions for the role"""
        return [
            "请介绍一下你自己",
            "为什么对这个职位感兴趣？",
            "你最大的技术成就是什么？",
            "如何处理技术挑战？",
            "为什么想离开当前公司？",
        ]

    def _get_technical_topics(self, job: Dict[str, Any]) -> List[str]:
        """Get technical topics to review"""
        skills = job.get("skills", [])
        topics = {
            "Python": ["FastAPI/Django", "Async Programming", "Database Optimization"],
            "PostgreSQL": ["Indexing", "Query Optimization", "Transactions"],
            "Redis": ["Caching", "Pub/Sub", "Data Structures"],
            "Kubernetes": ["Deployments", "Services", "Scaling"],
        }

        result = []
        for skill in skills:
            if skill in topics:
                result.extend(topics[skill])
        return list(set(result))

    def _get_questions_to_ask(self, job: Dict[str, Any]) -> List[str]:
        """Get questions to ask the interviewer"""
        return [
            "团队的技术栈是什么？",
            "入职后的前3个月有什么期待？",
            "团队规模和结构是怎样的？",
            "绩效考核的标准是什么？",
            "远程工作政策是什么？",
        ]

    def _get_salary_tips(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Get salary negotiation tips"""
        return {
            "salary_range": [job.get("salary_min"), job.get("salary_max")],
            "market_rate": 45000,  # Would be calculated from market data
            "negotiation_tips": [
                "先等对方提出薪资",
                "提供市场数据支持",
                "考虑总包(薪资+奖金+期权)",
            ],
        }

    # ========== Offer Negotiation ==========

    def receive_offer(self, offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and process a job offer
        """
        offer_id = f"offer_{offer_data.get('job_id')}"

        offer = {
            "id": offer_id,
            "job_id": offer_data.get("job_id"),
            "job_title": offer_data.get("job_title"),
            "company": offer_data.get("company"),
            "salary": offer_data.get("salary"),
            "bonus": offer_data.get("bonus", 0),
            "equity": offer_data.get("equity", 0),
            "start_date": offer_data.get("start_date"),
            "benefits": offer_data.get("benefits", []),
            "received_at": datetime.now().isoformat(),
            "status": "pending_review",
        }

        self._offers_received[offer_id] = offer
        return offer

    def evaluate_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Evaluate an offer against preferences
        """
        offer = self._offers_received.get(offer_id)
        if not offer:
            return {"error": "Offer not found"}

        # Calculate evaluation
        prefs = self._preferences

        salary_evaluation = 0
        if prefs.get("min_salary") and offer.get("salary", 0) >= prefs["min_salary"]:
            salary_evaluation = 1.0
        elif prefs.get("min_salary"):
            salary_evaluation = offer.get("salary", 0) / prefs["min_salary"]

        return {
            "offer_id": offer_id,
            "overall_score": min(1.0, salary_evaluation * 0.6 + 0.4),  # Simplified
            "salary_score": salary_evaluation,
            "meets_minimum": offer.get("salary", 0) >= prefs.get("min_salary", 0),
            "recommendation": "accept" if salary_evaluation >= 0.9 else "negotiate",
        }

    def negotiate_offer(self, offer_id: str,
                        negotiation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a counter-offer or negotiation request using NegotiationEngine Skill
        """
        offer = self._offers_received.get(offer_id)
        if not offer:
            return {"error": "Offer not found"}

        # Initialize negotiation engine if not exists
        if offer_id not in self._negotiation_engines:
            self._negotiation_engines[offer_id] = NegotiationEngine(
                perspective='candidate',
                company_offer={
                    "salary": offer.get("salary", 0),
                    "signing_bonus": offer.get("signing_bonus", 0),
                    "rsu": offer.get("rsu", 0),
                    "vesting_years": 4,
                    "vacation_days": offer.get("vacation_days", 10),
                    "remote_days": offer.get("remote_days", 1),
                },
                candidate_expectation={
                    "salary": self._profile.get("expected_salary", 0),
                    "signing_bonus": negotiation_data.get("counteroffer_signing_bonus", 0),
                    "rsu": negotiation_data.get("counteroffer_rsu", 0),
                },
                job_context={
                    "candidate_name": self._profile.get("name", "候选人"),
                    "required_skills": offer.get("skills", []),
                    "hiring_urgency": "normal",
                    "candidate_years": self._profile.get("experience_years", 3),
                },
            )
            self._negotiation_history[offer_id] = []

        engine = self._negotiation_engines[offer_id]
        round_num = len(self._negotiation_history[offer_id]) + 1

        # Analyze sentiment from recruiter's response
        sentiment = self._analyze_sentiment(negotiation_data.get("message", ""))

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
            "company_offer": offer,
            "counter_offer": negotiation_data,
            "sentiment": sentiment,
            "result": result,
        })

        # Check if deal reached
        if result["deal_reached"]:
            return {
                "status": "deal_reached",
                "accepted": True,
                "final_terms": result["proposals"][0] if result["proposals"] else offer,
                "message": result["message"]["body"],
            }

        # Return negotiation state
        return {
            "status": "negotiation_continued",
            "round": round_num,
            "gap_analysis": result["gap"],
            "company_proposals": result["proposals"],
            "persuasion_for_candidate": result["persuasion"],
            "suggested_message": result["message"]["body"],
            "mutual_fit": result["mutual_fit"],
        }

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze recruiter's sentiment from message"""
        text = text.lower()
        positive_keywords = ["可以", "好的", "同意", "满足", "yes", "acceptable", "great"]
        negative_keywords = ["不行", "无法", "预算", "上限", "no", "cannot", "limit"]
        question_keywords = ["怎么", "是否", "how", "can", "?"]

        if any(kw in text for kw in positive_keywords):
            return "positive"
        elif any(kw in text for kw in negative_keywords):
            return "negative"
        elif any(kw in text for kw in question_keywords):
            return "question"
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

    def accept_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Accept a job offer
        """
        offer = self._offers_received.get(offer_id)
        if not offer:
            return {"error": "Offer not found"}

        # Check authorization
        if not self.can_auto_decide("accept_offers", 0.95):
            decision = AgentDecision(
                agent_id=self.id,
                action="accept_offer",
                context={"offer_id": offer_id, "offer": offer},
                reasoning=f"Accepting offer from {offer['company']}",
                confidence=0.95,
            )
            self.record_decision(decision)
            return {
                "requires_approval": True,
                "decision_id": decision.id,
            }

        return self._accept_offer_internal(offer_id)

    def _accept_offer_internal(self, offer_id: str) -> Dict[str, Any]:
        """Internal method to accept offer"""
        offer = self._offers_received[offer_id]
        offer["status"] = "accepted"
        offer["accepted_at"] = datetime.now().isoformat()

        return {
            "status": "accepted",
            "offer": offer,
            "message": f"Offer from {offer['company']} accepted!",
        }

    # ========== Message Processing ==========

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message from another agent"""
        content = message.content
        action = content.get("action")

        response_content = {}

        if action == "job_offer":
            # Received a job offer
            offer_data = content.get("offer_data", {})
            offer = self.receive_offer(offer_data)
            response_content = {
                "status": "offer_received",
                "offer_id": offer["id"],
                "evaluation": self.evaluate_offer(offer["id"]),
            }

        elif action == "interview_invitation":
            # Interview invitation
            job_id = content.get("job_id")
            response_content = {
                "status": "invitation_received",
                "job_id": job_id,
                "next_steps": "preparing",
            }

        elif action == "negotiation_response":
            # Response to counter-offer
            response_content = {
                "status": "response_received",
                "message": "Processing negotiation response",
            }

        else:
            response_content = {"error": f"Unknown action: {action}"}

        return AgentMessage(
            to_agent=message.from_agent,
            from_agent=self.id,
            content=response_content,
            message_type="response",
            in_reply_to=message.id,
        )

    # ========== Action Execution ==========

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a candidate action"""
        if action == "search_jobs":
            return {"jobs": self.search_jobs(params.get("criteria", {}))}
        elif action == "apply":
            job = params.get("job", {})
            return self.apply_to_job(job, params.get("cover_letter"))
        elif action == "prepare_interview":
            return self.prepare_for_interview(params.get("job", {}))
        elif action == "evaluate_offer":
            return self.evaluate_offer(params.get("offer_id"))
        elif action == "negotiate":
            return self.negotiate_offer(
                params.get("offer_id"),
                params.get("negotiation_data", {})
            )
        elif action == "accept":
            return self.accept_offer(params.get("offer_id"))
        else:
            return {"error": f"Unknown action: {action}"}
