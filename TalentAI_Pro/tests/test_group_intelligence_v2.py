"""
Group Intelligence Hub v2 测试脚本
===================================

测试内容：
1. Text Parser - 文本解析
2. Image Parser - 图片OCR解析（模拟）
3. PDF Parser - PDF解析（模拟）
4. Voice Parser - 语音转文字（模拟）
5. Batch Parse - 批量解析
6. Skills Integration - Skills协作入口
"""

import sys
sys.path.insert(0, '.')

from TalentAI_Pro.skills.group_intelligence.hub_v2 import (
    GroupIntelligenceHubV2, ParsedCandidate, ParsedJob,
    TextParser, ImageParser, PDFParser, VoiceParser,
    SkillsIntegration, quick_parse_candidate, quick_parse_job
)


def test_1_text_parser():
    """Test 1: Text Parser - 文本解析"""
    print("\n" + "=" * 60)
    print("Test 1: Text Parser")
    print("=" * 60)

    hub = GroupIntelligenceHubV2()

    # 测试候选人文本
    candidate_text = """
    姓名: 张三
    邮箱: zhangsan@techcompany.com
    电话: 13800138000
    职位: 高级算法工程师
    公司: 字节跳动
    技能: Python, TensorFlow, PyTorch, 机器学习, 深度学习, NLP
    经验: 8年
    学历: 硕士
    LinkedIn: linkedin.com/in/zhangsan
    期望薪资: 80K-100K
    """

    candidate = hub.parse_candidate(candidate_text, source_type="text")
    print(f"\n[Candidate Parse Result]")
    print(f"  Name: {candidate.name}")
    print(f"  Email: {candidate.email}")
    print(f"  Phone: {candidate.phone}")
    print(f"  Title: {candidate.current_title}")
    print(f"  Company: {candidate.current_company}")
    print(f"  Skills: {candidate.skills}")
    print(f"  Years: {candidate.years_experience}")
    print(f"  Education: {candidate.education}")
    print(f"  Salary Expectation: {candidate.salary_expectation}")
    print(f"  LinkedIn: {candidate.linkedin_url}")
    print(f"  Confidence: {candidate.confidence}")

    assert candidate.name == "张三"
    assert candidate.email == "zhangsan@techcompany.com"
    assert candidate.current_title == "高级算法工程师"
    assert candidate.current_company == "字节跳动"
    assert len(candidate.skills) >= 3
    assert candidate.years_experience == 8

    # 测试职位文本
    job_text = """
    职位: 高级Python工程师
    公司: 阿里巴巴
    地点: 杭州
    薪资: 40K-60K
    技能要求: Python, Django, PostgreSQL, Redis, Docker, K8s
    经验要求: 5年以上
    学历要求: 本科

    职位描述:
    负责公司核心后端服务开发，参与架构设计。
    任职要求:
    1. 5年以上Python开发经验
    2. 熟悉分布式系统设计
    3. 有大规模高并发系统经验优先
    """

    job = hub.parse_job(job_text, source_type="text")
    print(f"\n[Job Parse Result]")
    print(f"  Title: {job.title}")
    print(f"  Company: {job.company}")
    print(f"  Location: {job.location}")
    print(f"  Salary Range: {job.salary_range}")
    print(f"  Skills Required: {job.skills_required}")
    print(f"  Experience: {job.experience_years}")
    print(f"  Education: {job.education_level}")
    print(f"  Confidence: {job.confidence}")

    assert job.title == "高级Python工程师"
    assert job.company == "阿里巴巴"
    assert job.location == "杭州"
    assert len(job.skills_required) >= 3
    assert job.experience_years == 5

    print("\n[PASS] Test 1: Text Parser")
    return True


def test_2_image_parser():
    """Test 2: Image Parser - 图片OCR解析"""
    print("\n" + "=" * 60)
    print("Test 2: Image Parser (OCR)")
    print("=" * 60)

    hub = GroupIntelligenceHubV2()

    # 模拟Base64图片
    mock_image_base64 = "data:image/png;base64,iVBORw0KG..."

    candidate = hub.parse_candidate(mock_image_base64, source_type="image")
    print(f"\n[Image Parse Result]")
    print(f"  Name: {candidate.name}")
    print(f"  Email: {candidate.email}")
    print(f"  Phone: {candidate.phone}")
    print(f"  Title: {candidate.current_title}")
    print(f"  Source: {candidate.source}")
    print(f"  Confidence: {candidate.confidence}")

    assert candidate.source == "image"
    assert candidate.name is not None
    assert candidate.email is not None

    print("\n[PASS] Test 2: Image Parser")
    return True


def test_3_pdf_parser():
    """Test 3: PDF Parser - PDF解析"""
    print("\n" + "=" * 60)
    print("Test 3: PDF Parser")
    print("=" * 60)

    hub = GroupIntelligenceHubV2()

    # 模拟PDF文件路径
    mock_pdf_path = "/path/to/resume.pdf"

    candidate = hub.parse_candidate(mock_pdf_path, source_type="pdf")
    print(f"\n[PDF Parse Result]")
    print(f"  Name: {candidate.name}")
    print(f"  Email: {candidate.email}")
    print(f"  Phone: {candidate.phone}")
    print(f"  Title: {candidate.current_title}")
    print(f"  Source: {candidate.source}")
    print(f"  Confidence: {candidate.confidence}")

    assert candidate.source == "pdf"
    assert candidate.name is not None
    assert candidate.email is not None

    print("\n[PASS] Test 3: PDF Parser")
    return True


def test_4_voice_parser():
    """Test 4: Voice Parser - 语音转文字"""
    print("\n" + "=" * 60)
    print("Test 4: Voice Parser (ASR)")
    print("=" * 60)

    hub = GroupIntelligenceHubV2()

    # 模拟音频文件路径
    mock_audio_path = "/path/to/intro.mp3"

    candidate = hub.parse_candidate(mock_audio_path, source_type="voice")
    print(f"\n[Voice Parse Result]")
    print(f"  Name: {candidate.name}")
    print(f"  Title: {candidate.current_title}")
    print(f"  Company: {candidate.current_company}")
    print(f"  Skills: {candidate.skills}")
    print(f"  Years: {candidate.years_experience}")
    print(f"  Education: {candidate.education}")
    print(f"  Salary: {candidate.salary_expectation}")
    print(f"  Source: {candidate.source}")
    print(f"  Warnings: {candidate.warnings}")
    print(f"  Confidence: {candidate.confidence}")

    assert candidate.source == "voice"
    assert candidate.name is not None
    assert len(candidate.warnings) > 0  # 应该有语音识别警告

    print("\n[PASS] Test 4: Voice Parser")
    return True


def test_5_batch_parse():
    """Test 5: Batch Parse - 批量解析"""
    print("\n" + "=" * 60)
    print("Test 5: Batch Parse")
    print("=" * 60)

    hub = GroupIntelligenceHubV2()

    items = [
        {
            "type": "candidate",
            "content": "姓名: 赵六\n邮箱: zhaoliu@example.com\n职位: 产品经理",
            "source_type": "text"
        },
        {
            "type": "job",
            "content": "职位: 运营总监\n公司: 腾讯\n地点: 深圳",
            "source_type": "text"
        },
        {
            "type": "candidate",
            "content": "姓名: 钱七\n邮箱: qianqi@example.com\n职位: 前端工程师",
            "source_type": "text"
        }
    ]

    results = hub.parse_batch(items)
    print(f"\n[Batch Parse Result]")
    print(f"  Candidates: {len(results['candidates'])}")
    print(f"  Jobs: {len(results['jobs'])}")

    for i, c in enumerate(results['candidates']):
        print(f"  Candidate {i+1}: {c.name} - {c.email}")

    for i, j in enumerate(results['jobs']):
        print(f"  Job {i+1}: {j.title} @ {j.company}")

    assert len(results['candidates']) == 2
    assert len(results['jobs']) == 1

    print("\n[PASS] Test 5: Batch Parse")
    return True


def test_6_skills_integration():
    """Test 6: Skills Integration - Skills协作入口"""
    print("\n" + "=" * 60)
    print("Test 6: Skills Integration")
    print("=" * 60)

    hub = GroupIntelligenceHubV2()
    integration = SkillsIntegration(hub)

    # 检查初始状态
    ready = integration.is_ready()
    print(f"\n[Initial Skills Status]")
    for skill, status in ready.items():
        print(f"  {skill}: {'OK' if status else '--'}")

    # 测试pipeline_candidate（不连接下游Skills）
    candidate_text = """
    姓名: 孙八
    邮箱: sunba@example.com
    职位: 技术总监
    公司: 华为
    技能: Python, C++, 架构设计, AI
    经验: 12年
    """

    results = integration.pipeline_candidate(
        candidate_text,
        source_type="text",
        run_discovery=False,
        run_matching=False,
        run_outreach=False
    )

    print(f"\n[Pipeline Result]")
    print(f"  Parsed: {results['parsed_candidate'].name}")
    print(f"  Intelligence: {results['candidate_intelligence']}")
    print(f"  Discovery: {results['discovery']}")
    print(f"  Matching: {results['matching']}")
    print(f"  Outreach: {results['outreach']}")

    assert results['parsed_candidate'].name == "孙八"
    assert results['candidate_intelligence'] is None  # Skill未连接
    assert results['discovery'] is None

    print("\n[PASS] Test 6: Skills Integration")
    return True


def test_7_quick_parse():
    """Test 7: Quick Parse - 便捷函数"""
    print("\n" + "=" * 60)
    print("Test 7: Quick Parse Functions")
    print("=" * 60)

    # 测试 quick_parse_candidate
    candidate = quick_parse_candidate("姓名: 周九\n邮箱: zhoujiu@example.com\n职位: 数据科学家")
    print(f"\n[Quick Candidate Parse]")
    print(f"  Name: {candidate.name}")
    print(f"  Email: {candidate.email}")
    assert candidate.name == "周九"
    assert candidate.email == "zhoujiu@example.com"

    # 测试 quick_parse_job
    job = quick_parse_job("职位: 算法工程师\n公司: 百度\n地点: 北京")
    print(f"\n[Quick Job Parse]")
    print(f"  Title: {job.title}")
    print(f"  Company: {job.company}")
    print(f"  Location: {job.location}")
    assert job.title == "算法工程师"
    assert job.company == "百度"
    assert job.location == "北京"

    print("\n[PASS] Test 7: Quick Parse")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Group Intelligence Hub v2.0 - Test Suite")
    print("=" * 60)

    tests = [
        ("Text Parser", test_1_text_parser),
        ("Image Parser (OCR)", test_2_image_parser),
        ("PDF Parser", test_3_pdf_parser),
        ("Voice Parser (ASR)", test_4_voice_parser),
        ("Batch Parse", test_5_batch_parse),
        ("Skills Integration", test_6_skills_integration),
        ("Quick Parse", test_7_quick_parse),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "[PASS]", success))
        except Exception as e:
            import traceback
            traceback.print_exc()
            results.append((name, f"[FAIL]: {e}", False))

    # 汇总
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, status, _ in results if status == "[PASS]")
    total = len(results)

    for name, status, _ in results:
        print(f"  {status} - {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Group Intelligence Hub v2.0 verified.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)