"""
TalentAI Pro - Agent System Test
Tests all agent functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)

    try:
        # Test base module
        from agents.base import (
            Agent, AgentProfile, AgentType, AgentStatus, AgentCapability,
            AgentMessage, ProxyAuthorization, AgentDecision
        )
        print("[OK] agents.base imported successfully")

        # Test registry
        from agents.registry import AgentRegistry
        print("[OK] agents.registry imported successfully")

        # Test recruiter agent
        from agents.recruiter.agent import RecruiterAgent
        print("[OK] RecruiterAgent imported successfully")

        # Test candidate agent
        from agents.candidate.agent import CandidateAgent
        print("[OK] CandidateAgent imported successfully")

        # Test interview components
        from agents.interview import (
            QuestionGenerator, EvaluationEngine, ReportGenerator,
            InterviewSession, InterviewSessionManager
        )
        print("[OK] Interview components imported successfully")

        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_recruiter_agent():
    """Test Recruiter Agent functionality"""
    print("\n" + "=" * 60)
    print("Testing RecruiterAgent")
    print("=" * 60)

    try:
        from agents.recruiter.agent import RecruiterAgent

        # Create agent
        recruiter = RecruiterAgent(owner_id='test_hr', owner_name='Test HR')
        print(f"[OK] Created RecruiterAgent: {recruiter.id}")

        # Create requisition
        req = recruiter.create_requisition({
            "title": "Senior Python Engineer",
            "department": "Engineering",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_years_min": 5,
            "salary_range": {"min": 35000, "max": 50000}
        })
        print(f"[OK] Created requisition: {req['id']}")

        # Search candidates
        candidates = recruiter.search_candidates({
            "skills": ["Python", "FastAPI"],
            "experience_years_min": 3
        })
        print(f"[OK] Found {len(candidates)} candidates")

        return True
    except Exception as e:
        print(f"[FAIL] RecruiterAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_candidate_agent():
    """Test Candidate Agent functionality"""
    print("\n" + "=" * 60)
    print("Testing CandidateAgent")
    print("=" * 60)

    try:
        from agents.candidate.agent import CandidateAgent

        # Create agent
        candidate = CandidateAgent(owner_id='test_user', owner_name='Test User')
        print(f"[OK] Created CandidateAgent: {candidate.id}")

        # Set profile
        candidate.set_profile({
            "name": "Zhang San",
            "email": "zhangsan@example.com",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_years": 5,
            "current_title": "Senior Engineer",
            "salary_expectation": 40000
        })
        print("[OK] Set candidate profile")

        # Update preferences
        candidate.update_preferences({
            "min_salary": 35000,
            "locations": ["Beijing", "Shanghai"],
            "remote_flexible": True
        })
        print("[OK] Updated preferences")

        # Search jobs
        jobs = candidate.search_jobs({
            "keywords": ["Python", "Senior"],
            "locations": ["Beijing"],
            "salary_min": 30000
        })
        print(f"[OK] Found {len(jobs)} matching jobs")

        return True
    except Exception as e:
        print(f"[FAIL] CandidateAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_interview_agent():
    """Test Interview Agent functionality"""
    print("\n" + "=" * 60)
    print("Testing InterviewAgent")
    print("=" * 60)

    try:
        from agents.interview import QuestionGenerator, EvaluationEngine

        # Create question generator
        qgen = QuestionGenerator()
        print(f"[OK] Created QuestionGenerator")

        # Generate questions
        questions = qgen.generate(
            job_description={
                "title": "Senior Python Engineer",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "level": "senior"
            },
            candidate_profile={
                "skills": ["Python", "FastAPI"],
                "experience_years": 5
            }
        )
        print(f"[OK] Generated {questions.total_questions} questions (tech: {len(questions.technical_questions)}, behav: {len(questions.behavioral_questions)})")

        # Create evaluation engine
        engine = EvaluationEngine()
        print(f"[OK] Created EvaluationEngine")

        # Test evaluation
        result = engine.evaluate_answer(
            question={
                "type": "technical",
                "text": "What is Python GIL?",
                "expected_keywords": ["GIL", "thread", "lock"]
            },
            answer="GIL is Global Interpreter Lock..."
        )
        print(f"[OK] Evaluation score: {result.overall_score:.2f}")

        return True
    except Exception as e:
        print(f"[FAIL] InterviewAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_job_searcher():
    """Test JobSearcher functionality"""
    print("\n" + "=" * 60)
    print("Testing JobSearcher")
    print("=" * 60)

    try:
        from agents.candidate.job_searcher import JobSearcher

        searcher = JobSearcher()
        print("[OK] Created JobSearcher")

        # Search jobs
        jobs = searcher.search("Senior Python Engineer", {
            "location": "Beijing",
            "skills": ["Python", "FastAPI"]
        })
        print(f"[OK] Search returned {len(jobs)} jobs")

        # Create alert
        alert = searcher.create_alert(
            name="Python Jobs Alert",
            query="Python Engineer",
            filters={"location": "Beijing"}
        )
        print(f"[OK] Created job alert: {alert['id']}")

        return True
    except Exception as e:
        print(f"[FAIL] JobSearcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_interview_preparer():
    """Test InterviewPreparer functionality"""
    print("\n" + "=" * 60)
    print("Testing InterviewPreparer")
    print("=" * 60)

    try:
        from agents.candidate.interview_prep import InterviewPreparer

        preparer = InterviewPreparer()
        print("[OK] Created InterviewPreparer")

        # Create preparation
        prep = preparer.create_preparation(
            job={
                "title": "Senior Python Engineer",
                "company": "TechCorp",
                "skills": ["Python", "FastAPI"]
            },
            candidate_profile={
                "experience_years": 5,
                "skills": ["Python", "FastAPI"]
            }
        )
        print(f"[OK] Created preparation session: {prep['session_id']}")

        return True
    except Exception as e:
        print(f"[FAIL] InterviewPreparer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_candidate_matcher():
    """Test CandidateMatcher functionality"""
    print("\n" + "=" * 60)
    print("Testing CandidateMatcher")
    print("=" * 60)

    try:
        from agents.recruiter.candidate_matcher import CandidateMatcher

        matcher = CandidateMatcher()
        print("[OK] Created CandidateMatcher")

        # Calculate match
        match_result = matcher.match(
            candidate={
                "skills": ["Python", "FastAPI"],
                "experience_years": 5
            },
            job={
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience_years_min": 3
            }
        )
        print(f"[OK] Match result: overall_score={match_result['overall_score']:.2f}")

        # Rank candidates
        ranked = matcher.batch_match(
            candidates=[
                {"id": "C1", "skills": ["Python"], "experience_years": 3},
                {"id": "C2", "skills": ["Python", "FastAPI"], "experience_years": 5},
            ],
            jobs=[
                {"id": "J1", "title": "Python Engineer", "skills": ["Python", "FastAPI"], "experience_years_min": 3}
            ]
        )
        print(f"[OK] Ranked {len(ranked)} candidates")

        return True
    except Exception as e:
        print(f"[FAIL] CandidateMatcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_registry():
    """Test AgentRegistry functionality"""
    print("\n" + "=" * 60)
    print("Testing AgentRegistry")
    print("=" * 60)

    try:
        from agents.registry import AgentRegistry
        from agents.recruiter.agent import RecruiterAgent
        from agents.candidate.agent import CandidateAgent

        registry = AgentRegistry()
        print("[OK] Created AgentRegistry")

        # Register agents
        recruiter = RecruiterAgent(owner_id='test', owner_name='Test')
        candidate = CandidateAgent(owner_id='test', owner_name='Test')

        registry.register(recruiter)
        registry.register(candidate)

        print(f"[OK] Registered {len(registry.list_all())} agents")

        return True
    except Exception as e:
        print(f"[FAIL] AgentRegistry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TalentAI Pro - Agent System Test Suite")
    print("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("RecruiterAgent", test_recruiter_agent),
        ("CandidateAgent", test_candidate_agent),
        ("InterviewAgent", test_interview_agent),
        ("JobSearcher", test_job_searcher),
        ("InterviewPreparer", test_interview_preparer),
        ("CandidateMatcher", test_candidate_matcher),
        ("AgentRegistry", test_agent_registry),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[CRASH] {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
