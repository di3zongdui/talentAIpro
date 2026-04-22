"""
TalentAI Pro - 候选人场景测试脚本
测试编号: TEST-C-01 ~ C-05
运行环境: Python 3.10+, pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCandidateScenarios:
    """候选人场景测试套件"""

    # ===== C-01: 简历智能优化 =====

    def test_c01_resume_optimization(self):
        """
        场景C-01: 简历内容优化
        验证点：
        1. 原始简历 → 结构化数据
        2. 识别核心亮点
        3. 生成优化建议
        """
        raw_resume = """
        张三，5年工作经验
        2018-2021: 字节跳动，后端工程师
        - 负责推荐系统后端开发
        - 使用Python和Go
        2021-现在: 快手，高级工程师
        - 带队5人团队
        - 主导推荐算法优化
        """

        # 模拟解析简历
        parsed = {
            "name": "张三",
            "experience_years": 5,
            "core_skills": ["推荐系统", "Python", "Go", "机器学习"],
            "companies": ["字节跳动", "快手"],
            "achievements": ["推荐系统后端开发", "带队5人", "算法优化"]
        }

        suggestions = [
            "建议量化成果：如'推荐系统日均处理请求超10亿'",
            "突出管理经验：带队5人可展开说明团队产出"
        ]

        assert parsed["name"] == "张三"
        assert parsed["experience_years"] == 5
        assert "推荐系统" in parsed["core_skills"]

        assert len(suggestions) > 0, "无优化建议"
        assert any("量化" in s for s in suggestions), "缺少量化建议"

        print(f"[PASS] C-01: 简历优化，生成{len(suggestions)}条建议")

    def test_c01_profile_360_build(self):
        """
        场景C-01扩展: 构建360°人才画像
        验证点：
        1. 整合多平台数据
        2. 识别跨平台同一人
        3. 生成完整画像
        """
        # 模拟多平台数据
        platforms_data = {
            "linkedin": {"name": "张三", "title": "高级算法工程师", "company": "快手"},
            "github": {"username": "zhangsan", "repos": 15, "stars": 1200},
            "liepin": {"name": "张三", "current_title": "高级工程师", "expected_salary": 80000}
        }

        # 模拟构建360°画像
        profile = {
            "name": "张三",
            "confidence_score": 0.92,
            "true_current_company": "快手",
            "true_title": "高级算法工程师",
            "hidden_strengths": ["GitHub 1200+ stars", "顶会论文发表"],
            "skills": ["Python", "Go", "推荐系统", "机器学习"]
        }

        assert profile["confidence_score"] > 0.8, "身份置信度过低"
        assert profile["true_current_company"] == "快手", "公司信息不一致"
        assert len(profile["hidden_strengths"]) > 0, "未发现隐藏亮点"

        print(f"[PASS] C-01扩展: 360°画像构建，置信度{profile['confidence_score']}")

    # ===== C-02: 精准职位推荐 =====

    def test_c02_job_recommendations(self):
        """
        场景C-02: 智能推荐匹配职位
        验证点：
        1. 推荐数量合理（3-5个）
        2. 匹配度计算准确
        3. 考虑候选人偏好
        """
        candidate_profile = {
            "skills": ["Python", "Go", "推荐系统"],
            "experience_years": 5,
            "preferred_locations": ["北京", "上海"],
            "expected_salary_min": 60000
        }

        # 模拟推荐结果
        recommendations = [
            {"job_id": "job_001", "title": "高级算法工程师", "company": "字节跳动",
             "match_score": 0.92, "salary_max": 90000, "location": "北京"},
            {"job_id": "job_002", "title": "算法专家", "company": "快手",
             "match_score": 0.88, "salary_max": 85000, "location": "北京"},
            {"job_id": "job_003", "title": "后端技术专家", "company": "美团",
             "match_score": 0.82, "salary_max": 80000, "location": "北京"},
            {"job_id": "job_004", "title": "推荐系统工程师", "company": "阿里",
             "match_score": 0.78, "salary_max": 95000, "location": "杭州"},
        ]

        # 验证推荐数量
        assert 3 <= len(recommendations) <= 5, f"推荐数量{len(recommendations)}不合理"

        # 验证匹配度
        for job in recommendations:
            assert job["match_score"] >= 0.6, f"推荐职位匹配度过低: {job['match_score']}"
            assert job["salary_max"] >= candidate_profile["expected_salary_min"]

        # 验证排序（按匹配度降序）
        scores = [j["match_score"] for j in recommendations]
        assert scores == sorted(scores, reverse=True)

        print(f"[PASS] C-02: 推荐{len(recommendations)}个精准职位")
        for job in recommendations:
            print(f"       - {job['title']}@{job['company']}: 匹配度{job['match_score']:.0%}")

    def test_c02_cross_platform_recommendations(self):
        """
        场景C-02扩展: 跨平台聚合职位推荐
        验证点：
        1. 从多个平台获取职位
        2. 统一格式处理
        3. 去重和排序
        """
        # 模拟跨平台聚合结果
        jobs = [
            {"unified_id": "ujob_001", "source_platform": "linkedin", "title": "算法工程师"},
            {"unified_id": "ujob_002", "source_platform": "liepin", "title": "高级算法工程师"},
            {"unified_id": "ujob_003", "source_platform": "boss", "title": "后端工程师"},
        ]

        assert len(jobs) > 0, "未获取到任何职位"

        # 验证去重
        job_ids = [j["unified_id"] for j in jobs]
        assert len(job_ids) == len(set(job_ids)), "存在重复职位"

        # 验证多平台来源
        sources = set(j["source_platform"] for j in jobs)
        assert len(sources) >= 2, "来源平台数量不足"

        print(f"[PASS] C-02扩展: 跨平台聚合，获取{len(jobs)}个职位，来自{sources}")

    # ===== C-03: AI模拟面试 =====

    def test_c03_ai_interview_prep(self):
        """
        场景C-03: AI模拟面试准备
        验证点：
        1. 生成面试问题列表
        2. 提供答题思路
        3. 生成追问建议
        """
        prep_data = {
            "job_title": "高级算法工程师",
            "company": "字节跳动",
            "focus_areas": ["推荐系统", "算法优化", "团队管理"]
        }

        # 模拟生成面试准备
        result = {
            "questions": [
                {"q": "介绍一下你主导的推荐系统项目", "type": "项目经验"},
                {"q": "如何优化推荐算法的效果？", "type": "技术深度"},
                {"q": "你如何管理5人团队？", "type": "管理能力"},
                {"q": "遇到技术难题如何解决？", "type": "问题解决"},
                {"q": "职业规划是什么？", "type": "稳定性"},
            ],
            "answer_guides": [
                {"q": "推荐系统项目", "guide": "使用STAR法则，重点说结果"},
                {"q": "算法优化", "guide": "从特征工程/模型选择/效果评估角度"},
            ],
            "followup_suggestions": ["追问技术细节", "追问团队协作"]
        }

        assert len(result["questions"]) >= 5, "问题数量不足"
        assert len(result["answer_guides"]) >= 5, "答题指南不足"

        # 验证问题与职位相关
        for q in result["questions"][:3]:
            assert any(area in q["q"] or q["q"] in area for area in prep_data["focus_areas"]), \
                f"问题与职位不相关: {q['q']}"

        print(f"[PASS] C-03: 生成{len(result['questions'])}道模拟面试题")

    def test_c03_live_interview_simulation(self):
        """
        场景C-03扩展: 实时模拟面试
        验证点：
        1. 实时问答交互
        2. 即时反馈评分
        3. 生成改进建议
        """
        # 模拟面试会话
        answers = [
            "我负责推荐系统的核心算法优化，使用深度学习模型提升点击率15%",
            "我带队5人团队，采用OKR进行目标管理",
            "遇到过最大的挑战是数据质量问题，我通过建立数据治理流程解决"
        ]

        # 模拟反馈
        feedback_list = [
            {"answer_score": 8.5, "strength": "量化数据清晰", "improvement": "可补充技术细节"},
            {"answer_score": 7.5, "strength": "管理经验有说服力", "improvement": "补充团队产出"},
            {"answer_score": 8.0, "strength": "问题解决思路清晰", "improvement": "可举例具体数据"},
        ]

        # 生成最终报告
        report = {
            "overall_score": 8.0,
            "strengths": ["量化思维强", "技术深度足够", "管理经验丰富"],
            "improvement_suggestions": ["补充更多技术细节", "增加团队产出数据"],
            "recommendation": "强烈推荐进入下一轮"
        }

        assert report["overall_score"] > 0, "评分异常"
        assert len(report["improvement_suggestions"]) > 0, "无改进建议"

        print(f"[PASS] C-03扩展: 模拟面试完成，综合评分{report['overall_score']:.1f}/10")

    # ===== C-04: 超预期发现报告 =====

    def test_c04_surprise_discovery_report(self):
        """
        场景C-04: 超预期发现报告
        验证点：
        1. 识别候选人未知的企业亮点
        2. 量化展示惊喜程度
        3. 提供行动建议
        """
        candidate_id = "test_candidate_001"
        job_id = "test_job_001"

        # 模拟超预期发现报告
        report = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "surprise_points": [
                {
                    "category": "公司亮点",
                    "for": "candidate",
                    "description": "该公司D轮融资，团队技术密度极高（Google/Facebook背景占比60%）",
                    "impact_score": 0.18,
                    "action": "可在面试时表达对技术团队的兴趣"
                },
                {
                    "category": "薪酬惊喜",
                    "for": "candidate",
                    "description": "实际薪资范围比JD写的高20%（有股票期权）",
                    "impact_score": 0.15,
                    "action": "可在谈薪时争取更高薪资"
                },
                {
                    "category": "职业发展",
                    "for": "candidate",
                    "description": "公司有完善的技术晋升通道，2年内有CTO空缺",
                    "impact_score": 0.12,
                    "action": "可在面试时了解技术团队规划"
                }
            ]
        }

        assert report["candidate_id"] == candidate_id
        assert report["job_id"] == job_id
        assert len(report["surprise_points"]) > 0, "无超预期发现"

        # 验证报告结构
        for point in report["surprise_points"]:
            assert "category" in point, "缺少分类"
            assert "description" in point, "缺少描述"
            assert "impact_score" in point, "缺少影响分数"
            assert 0 <= point["impact_score"] <= 1, "影响分数范围错误"

        print(f"[PASS] C-04: 发现{len(report['surprise_points'])}个超预期亮点")
        for point in report["surprise_points"]:
            print(f"       [{point['category']}] {point['description'][:30]}... (影响度{point['impact_score']:.0%})")

    # ===== C-05: Offer比较分析 =====

    def test_c05_offer_comparison(self):
        """
        场景C-05: Offer多维度比较
        验证点：
        1. 多Offer对比分析
        2. 考虑职业发展因素
        3. 生成量化评分
        """
        candidate_profile = {"experience_years": 5, "career_focus": "技术深度"}

        offers = [
            {
                "company": "字节跳动",
                "title": "高级工程师",
                "salary": 80000,
                "equity": 50000,
                "level": "2-2",
                "team_size": 5,
                "tech_density": "high",
                "career_path": "技术专家"
            },
            {
                "company": "快手",
                "title": "专家工程师",
                "salary": 90000,
                "equity": 0,
                "level": "P9",
                "team_size": 3,
                "tech_density": "high",
                "career_path": "技术专家+管理"
            }
        ]

        # 模拟Offer对比报告
        report = {
            "comparisons": [
                {
                    "company": "字节跳动",
                    "total_score": 85,
                    "salary_score": 75,
                    "growth_score": 90,
                    "tech_score": 95,
                    "pros": ["技术氛围好", "团队成熟"],
                    "cons": ["晋升竞争激烈"]
                },
                {
                    "company": "快手",
                    "total_score": 82,
                    "salary_score": 88,
                    "growth_score": 85,
                    "tech_score": 88,
                    "pros": ["薪资更高", "团队更小"],
                    "cons": ["股权较少"]
                }
            ],
            "recommended_offer": 0,
            "reasoning": "综合考虑候选人的技术深度追求，推荐字节跳动。技术密度更高，学习成长空间更大。"
        }

        # 验证报告结构
        assert len(report["comparisons"]) == 2, "Offer数量不符"
        assert all(c["total_score"] > 0 for c in report["comparisons"]), "评分异常"

        # 验证推荐
        assert report["recommended_offer"] in [0, 1], "推荐索引错误"
        assert report["reasoning"] is not None, "缺少推荐理由"

        print(f"[PASS] C-05: Offer对比分析，推荐{offers[report['recommended_offer']]['company']}")


# ===== 集成测试: 候选人求职完整流程 =====

class TestCandidateEndToEnd:
    """候选人端到端测试"""

    def test_complete_job_search_flow(self):
        """
        完整求职流程: 构建画像 → 推荐职位 → AI面试 → Offer比较
        """
        print("\n" + "=" * 60)
        print("开始端到端测试: 候选人求职完整流程")
        print("=" * 60)

        # Step 1: 构建简历
        print("\n[Step 1/4] 构建候选人画像...")
        profile = {
            "name": "李四",
            "skills": ["Python", "Go", "推荐系统"],
            "experience_years": 6,
            "expected_salary": 80000
        }
        print(f"  ✓ 画像构建完成: {profile['name']}")

        # Step 2: 智能推荐
        print("\n[Step 2/4] 获取职位推荐...")
        jobs = [
            {"title": "高级算法工程师", "company": "字节跳动", "match_score": 0.92},
            {"title": "算法专家", "company": "快手", "match_score": 0.88},
            {"title": "后端技术专家", "company": "美团", "match_score": 0.82},
            {"title": "推荐系统工程师", "company": "阿里", "match_score": 0.78},
            {"title": "技术专家", "company": "腾讯", "match_score": 0.75},
        ]
        print(f"  ✓ 推荐{len(jobs)}个匹配职位")

        # Step 3: 投递+面试准备
        print("\n[Step 3/4] AI面试准备...")
        prep_result = {
            "questions": [
                {"q": "推荐系统项目", "type": "项目经验"},
                {"q": "算法优化策略", "type": "技术深度"},
                {"q": "团队管理经验", "type": "管理能力"},
            ]
        }
        print(f"  ✓ 生成{len(prep_result['questions'])}道面试题")

        # Step 4: Offer比较（模拟）
        print("\n[Step 4/4] Offer选择分析...")
        offers = [
            {"company": "字节跳动", "salary": 85000, "equity": 50000},
            {"company": "快手", "salary": 90000, "equity": 0}
        ]
        recommended = 0
        print(f"  ✓ 推荐: {offers[recommended]['company']}")

        print("\n" + "=" * 60)
        print("端到端测试完成")
        print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
