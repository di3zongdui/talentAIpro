"""
TalentAI Pro - API v2 测试脚本
验证Agent信任与通信协议API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8089"

def test_health():
    """测试健康检查"""
    print("\n[1/8] 测试健康检查...")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["services"]["api_v2"] == "active"
    print(f"   ✓ 健康检查通过: {data}")

def test_agent_registration():
    """测试Agent注册"""
    print("\n[2/8] 测试Agent注册...")
    
    # 注册候选人Agent
    candidate_agent = {
        "agent_id": "candidate_agent_001",
        "agent_type": "candidate",
        "owner_id": "candidate_001",
        "owner_type": "individual",
        "capabilities": ["job_search", "interview_prep", "salary_negotiation"]
    }
    
    resp = requests.post(f"{BASE_URL}/api/v2/agents/register", json=candidate_agent)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    cert = data["certificate"]
    print(f"   ✓ 候选人Agent注册成功: {cert['certificate_id']}")
    
    # 注册招聘Agent
    recruiter_agent = {
        "agent_id": "recruiter_agent_001",
        "agent_type": "recruiter",
        "owner_id": "enterprise_001",
        "owner_type": "enterprise",
        "capabilities": ["job_matching", "candidate_screening", "offer_negotiation"]
    }
    
    resp = requests.post(f"{BASE_URL}/api/v2/agents/register", json=recruiter_agent)
    assert resp.status_code == 200
    data = resp.json()
    print(f"   ✓ 招聘Agent注册成功: {data['certificate']['certificate_id']}")
    
    return "candidate_agent_001", "recruiter_agent_001"

def test_preference_model():
    """测试偏好模型"""
    print("\n[3/8] 测试偏好模型...")
    
    preferences = {
        "model_id": "pref_candidate_001_v1",
        "owner_id": "candidate_001",
        "owner_type": "individual",
        "priorities": [
            {"dimension": "WLB", "weight": 0.9, "description": "工作生活平衡最重要"},
            {"dimension": "salary", "weight": 0.7, "description": "薪资要达到预期"},
            {"dimension": "growth", "weight": 0.6, "description": "成长空间"}
        ],
        "flexibilities": {
            "salary": {"can_flex_to": 0.8, "requires_approval_below": 0.6},
            "WLB": {"can_flex_to": 0.3, "requires_approval_below": 0.2, "never_below": 0.1}
        },
        "dealbreakers": [
            {"type": "company", "value": "competitor_corp", "strictness": 1.0}
        ],
        "counter_offer_authority": 0.6,
        "auto_accept_threshold": 0.85
    }
    
    resp = requests.post(f"{BASE_URL}/api/v2/preferences/model", json=preferences)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    print(f"   ✓ 偏好模型创建成功: {data['data']}")

def test_authorization():
    """测试代理授权"""
    print("\n[4/8] 测试代理授权...")
    
    authorization = {
        "principal_id": "candidate_001",
        "principal_type": "individual",
        "agent_id": "candidate_agent_001",
        "agent_type": "candidate",
        "agent_capabilities": ["job_search", "interview_prep"],
        "authorized_actions": ["search_jobs", "apply_to_jobs"],
        "denied_actions": ["accept_offers", "sign_contracts"],
        "constraints": {
            "salary_min": 500000,
            "salary_max": 800000,
            "denied_companies": ["competitor_corp"]
        },
        "valid_from": "2026-04-25T00:00:00",
        "valid_until": "2026-12-31T23:59:59",
        "revocable": True
    }
    
    resp = requests.post(f"{BASE_URL}/api/v2/agents/candidate_agent_001/authorize", json=authorization)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    print(f"   ✓ 代理授权成功: {data['authorization_chain_id']}")

def test_disclosure():
    """测试用途绑定披露"""
    print("\n[5/8] 测试用途绑定披露...")
    
    atom = {
        "atom_id": "atom_skill_match_001",
        "content_type": "skill_match",
        "raw_value": {"python": 0.95, "fastapi": 0.88},
        "disclosure_level": "matched_only",
        "proof_type": "none",
        "created_at": "2026-04-25T00:00:00",
        "owner_id": "candidate_001"
    }
    
    resp = requests.post(f"{BASE_URL}/api/v2/disclosure/atoms", json=atom)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    print(f"   ✓ 原子披露创建成功: {data['data']['atom_id']}")
    
    # 获取披露（需要授权）
    resp = requests.get(
        f"{BASE_URL}/api/v2/disclosure/atoms/atom_skill_match_001",
        params={"requestor_id": "recruiter_agent_001", "purpose": "match_notification"}
    )
    assert resp.status_code == 200
    data = resp.json()
    print(f"   ✓ 原子披露获取: success={data['success']}")

def test_semantics():
    """测试语义共识"""
    print("\n[6/8] 测试语义共识...")
    
    resp = requests.get(f"{BASE_URL}/api/v2/semantics/taxonomy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    taxonomy = data["data"]
    print(f"   ✓ Taxonomy获取成功: version={taxonomy['version']}, skills={list(taxonomy['skills'].keys())}")

def test_negotiation():
    """测试谈判协议"""
    print("\n[7/8] 测试谈判协议...")
    
    # 开始谈判
    resp = requests.post(
        f"{BASE_URL}/api/v2/negotiations/start",
        params={
            "job_id": "job_001",
            "candidate_agent_id": "candidate_agent_001",
            "recruiter_agent_id": "recruiter_agent_001"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    neg_id = data["negotiation"]["negotiation_id"]
    print(f"   ✓ 谈判开始: {neg_id}")
    
    # 创建提案
    proposal = {
        "proposal_id": "PROP-001",
        "negotiation_id": neg_id,
        "from_agent": "recruiter_agent_001",
        "to_agent": "candidate_agent_001",
        "content": {"salary": 650000, "bonus": 100000, "title": "Senior Engineer"},
        "match_score": 0.82,
        "generated_at": "2026-04-25T00:00:00"
    }
    
    resp = requests.post(f"{BASE_URL}/api/v2/negotiations/{neg_id}/propose", json=proposal)
    assert resp.status_code == 200
    data = resp.json()
    print(f"   ✓ 提案创建: match_score={data['proposal']['match_score']}, requires_approval={data['requires_human_approval']}")

def test_agent_self_description():
    """测试Agent自我描述"""
    print("\n[8/8] 测试Agent自我描述...")
    
    resp = requests.get(f"{BASE_URL}/api/v2/agents/candidate_agent_001/self-description")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    desc = data["data"]
    print(f"   ✓ Agent自我描述: type={desc['agent_type']}, trust_score={desc['trust_score']}")

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("TalentAI Pro - Agent API v2 测试")
    print("=" * 60)
    
    try:
        test_health()
        test_agent_registration()
        test_preference_model()
        test_authorization()
        test_disclosure()
        test_semantics()
        test_negotiation()
        test_agent_self_description()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        print("\nAPI已就绪:")
        print(f"  - Swagger UI: {BASE_URL}/docs")
        print(f"  - WebSocket: ws://localhost:8089/ws/agents")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到 {BASE_URL}")
        print("请确保API服务器正在运行:")
        print("  cd TalentAI_Pro")
        print("  uvicorn api.server:app --reload --port 8089")

if __name__ == "__main__":
    run_all_tests()
