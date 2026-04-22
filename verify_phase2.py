#!/usr/bin/env python
"""Quick Phase 2 verification test"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Test 1: JD Intelligence
try:
    from TalentAI_Pro.skills.jd_parser.jd_intelligence_v2 import JDIntelligenceEngineV2
    engine = JDIntelligenceEngineV2()
    jd_text = "招聘：测试HR\n薪资：30-50万\n要求：从0到1搭建招聘体系"
    report = engine.analyze(jd_text)
    assert len(report.hidden_preferences) >= 1, "Hidden prefs should be found"
    print("[PASS] Test 1: JD Intelligence Engine v2.0")
except Exception as e:
    print(f"[FAIL] Test 1: JD Intelligence - {e}")
    import traceback; traceback.print_exc()

# Test 2: Candidate Intelligence
try:
    from TalentAI_Pro.skills.resume_parser.candidate_intelligence_v2 import CandidateIntelligenceEngineV2
    engine = CandidateIntelligenceEngineV2()
    resume = "【Test User】\nHR总监\n12年经验\n清华大学硕士"
    report = engine.analyze(resume)
    assert report.name == "Test User", "Name should be parsed"
    print("[PASS] Test 2: Candidate Intelligence Engine v2.0")
except Exception as e:
    print(f"[FAIL] Test 2: Candidate Intelligence - {e}")
    import traceback; traceback.print_exc()

# Test 3: Discovery Radar
try:
    from TalentAI_Pro.skills.discovery_radar.discovery_radar import DiscoveryRadar
    radar = DiscoveryRadar(search_func=lambda q: [{"snippet": "test", "url": None}])
    report = radar.investigate_company("Test Corp")
    assert report.company_name == "Test Corp", "Company name should be set"
    print("[PASS] Test 3: Discovery Radar")
except Exception as e:
    print(f"[FAIL] Test 3: Discovery Radar - {e}")
    import traceback; traceback.print_exc()

# Test 4: Matching Engine v2
try:
    from TalentAI_Pro.engine.matching_v2 import MatchingEngineV2
    from TalentAI_Pro.models.job import Job
    from TalentAI_Pro.models.candidate import Candidate
    engine = MatchingEngineV2()
    job = Job(id="J1", title="Test", company_name="Co", location="北京", created_by="test",
              salary_min=300000, salary_max=500000, required_skills=["HR"])
    cand = Candidate(id="C1", name="User", location="北京", current_title="HR Director",
                    current_company="Co", years_of_experience=10)
    result = engine.match(job, cand)
    assert result.composite_score > 0, "Score should be positive"
    print("[PASS] Test 4: Matching Engine v2")
except Exception as e:
    print(f"[FAIL] Test 4: Matching Engine - {e}")
    import traceback; traceback.print_exc()

print("\nPhase 2 Verification Complete")