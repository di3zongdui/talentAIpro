"""
Negotiation E2E Test - 端到端自动化测试
========================================
测试Recruiter Agent和Candidate Agent之间的完整谈判流程

测试内容：
1. 初始化Agent
2. 创建招聘需求和Offer
3. 发起谈判
4. 多轮谈判（通过WebSocket模拟）
5. 谈判历史存储
6. 渠道消息发送（微信/邮件）
7. 达成交易/谈判结束

运行方式：
    python -m pytest tests/test_negotiation_e2e.py -v
    或
    python tests/test_negotiation_e2e.py
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from TalentAI_Pro.agents.recruiter.agent import RecruiterAgent
from TalentAI_Pro.agents.candidate.agent import CandidateAgent
from TalentAI_Pro.skills.negotiation.history_storage import NegotiationHistoryStorage, get_negotiation_storage
from TalentAI_Pro.skills.negotiation.websocket_manager import (
    NegotiationWebSocketManager,
    MessageType,
    ChannelType,
    get_websocket_manager,
)
from TalentAI_Pro.skills.negotiation.channel_integrations import (
    ChannelRouter,
    ChannelType as MsgChannelType,
    get_channel_router,
)


class NegotiationE2ETester:
    """端到端谈判测试器"""

    def __init__(self):
        self.recruiter: RecruiterAgent = None
        self.candidate: CandidateAgent = None
        self.storage: NegotiationHistoryStorage = None
        self.ws_manager: NegotiationWebSocketManager = None
        self.channel_router: ChannelRouter = None

        self.requisition_id: str = ""
        self.candidate_id: str = ""
        self.offer_id: str = ""
        self.negotiation_id: str = ""

        self.test_results = []

    def log(self, message: str, status: str = "INFO"):
        """测试日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {"INFO": "📋", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️", "TEST": "🧪"}.get(status, "📋")
        print(f"[{timestamp}] {emoji} [{status}] {message}")
        self.test_results.append({
            "time": timestamp,
            "status": status,
            "message": message,
        })

    async def setup(self):
        """初始化测试环境"""
        self.log("初始化测试环境...")

        # 创建Agent
        self.recruiter = RecruiterAgent(
            owner_id="test_recruiter",
            owner_name="TestRecruiter",
            company_id="company_001",
            company_name="TalentAI Corp",
        )

        self.candidate = CandidateAgent(
            owner_id="test_candidate",
            owner_name="TestCandidate",
        )

        # 设置候选人资料
        self.candidate.set_profile({
            "name": "李明",
            "email": "liming@example.com",
            "phone": "13800138000",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
            "experience_years": 5,
            "current_title": "高级工程师",
            "current_company": "某互联网公司",
            "expected_salary": 50000,
            "work_preferences": {
                "min_salary": 45000,
                "remote_flexible": True,
            },
        })

        # 初始化存储
        self.storage = get_negotiation_storage()

        # 初始化WebSocket管理器
        self.ws_manager = get_websocket_manager()

        # 初始化渠道路由器
        self.channel_router = get_channel_router()

        self.log("测试环境初始化完成", "SUCCESS")

    async def test_1_create_requisition(self):
        """测试1：创建招聘需求"""
        self.log("测试1：创建招聘需求", "TEST")

        job_data = {
            "title": "高级Python工程师",
            "department": "Engineering",
            "level": "senior",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
            "experience_years": 4,
            "salary_range": {"min": 35000, "max": 50000},
            "description": "负责后端架构设计与开发",
            "urgency": "high",
            "market_competition": "fierce",
        }

        requisition = self.recruiter.create_requisition(job_data)
        self.requisition_id = requisition["id"]

        self.assert_true(requisition["id"].startswith("req_"), "需求ID格式正确")
        self.assert_true(requisition["status"] == "open", "需求状态为open")
        self.log(f"创建招聘需求成功: {self.requisition_id}", "SUCCESS")

    async def test_2_add_candidate(self):
        """测试2：添加候选人到人才池"""
        self.log("测试2：添加候选人", "TEST")

        candidate_data = {
            "name": "李明",
            "email": "liming@example.com",
            "phone": "13800138000",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
            "experience_years": 5,
            "current_title": "高级工程师",
            "current_company": "某互联网公司",
            "salary_expectation": 50000,
        }

        self.candidate_id = self.recruiter.add_candidate_to_pool(candidate_data)

        self.assert_true(self.candidate_id.startswith("cand_"), "候选人ID格式正确")
        self.log(f"添加候选人成功: {self.candidate_id}", "SUCCESS")

    async def test_3_screen_candidate(self):
        """测试3：筛选候选人"""
        self.log("测试3：筛选候选人", "TEST")

        screening = self.recruiter.screen_candidate(self.candidate_id, self.requisition_id)

        self.assert_true(screening["overall_score"] > 0.5, f"匹配分数: {screening['overall_score']:.2f}")
        self.log(f"候选人筛选完成，匹配分数: {screening['overall_score']:.2f}", "SUCCESS")

    async def test_4_create_offer(self):
        """测试4：创建Offer"""
        self.log("测试4：创建Offer", "TEST")

        offer_data = {
            "salary": 42000,
            "bonus": 20000,
            "signing_bonus": 30000,
            "rsu": 8000,
            "start_date": "2026-05-01",
            "benefits": ["五险一金", "年度旅游", "弹性工作"],
        }

        offer = self.recruiter.create_offer(
            self.requisition_id,
            self.candidate_id,
            offer_data,
        )

        self.offer_id = offer["id"]
        self.negotiation_id = f"neg_{self.offer_id}"

        self.assert_true(self.offer_id.startswith("offer_"), "Offer ID格式正确")
        self.log(f"创建Offer成功: {self.offer_id}", "SUCCESS")

    async def test_5_start_negotiation(self):
        """测试5：开始谈判（Recruiter发起）"""
        self.log("测试5：开始谈判", "TEST")

        # 模拟候选人发起还价
        negotiation_data = {
            "counteroffer_salary": 48000,
            "counteroffer_signing_bonus": 50000,
            "message": "我对这个薪资有些想法，希望能够进一步讨论。",
        }

        # Recruiter处理谈判
        result = self.recruiter._process_negotiation(self.offer_id, negotiation_data)

        self.assert_true(result["status"] in ["negotiation_continued", "deal_reached"],
                        f"谈判状态: {result['status']}")
        self.assert_true("proposals" in result, "包含方案列表")
        self.assert_true("mutual_fit" in result, "包含匹配度评估")

        # 保存到数据库
        self.storage.save_negotiation_round(
            negotiation_id=self.negotiation_id,
            offer_id=self.offer_id,
            round_num=1,
            perspective="recruiter",
            agent_id=self.recruiter.id,
            company_offer={"salary": 42000, "signing_bonus": 30000},
            candidate_expectation={"salary": 48000, "signing_bonus": 50000},
            result=result,
            sentiment="question",
        )

        # 发送微信消息（模拟）
        contact_info = {"wechat": "liming_wechat", "email": "liming@example.com"}
        channel_msg = await self.channel_router.send_negotiation_auto(
            contact_info=contact_info,
            negotiation_content={
                "proposals": result["proposals"],
                "message": result.get("suggested_message", ""),
                "mutual_fit": result["mutual_fit"],
            },
            preferred_channel=MsgChannelType.WECHAT,
        )
        self.log(f"微信消息发送: {channel_msg.id}", "SUCCESS")

        self.log(f"第1轮谈判完成，匹配度: {result['mutual_fit']['mutual_fit']:.2f}", "SUCCESS")

    async def test_6_second_negotiation_round(self):
        """测试6：第二轮谈判"""
        self.log("测试6：第二轮谈判", "TEST")

        # 模拟Recruiter回应
        negotiation_data = {
            "counteroffer_salary": 45000,
            "counteroffer_signing_bonus": 40000,
            "message": "我们可以把月薪调整到45000，签字费40000，这是我们最大的诚意了。",
        }

        # Recruiter处理第二轮
        result = self.recruiter._process_negotiation(self.offer_id, negotiation_data)

        self.assert_true(result["status"] in ["negotiation_continued", "deal_reached"],
                        f"谈判状态: {result['status']}")

        # 保存到数据库
        self.storage.save_negotiation_round(
            negotiation_id=self.negotiation_id,
            offer_id=self.offer_id,
            round_num=2,
            perspective="recruiter",
            agent_id=self.recruiter.id,
            company_offer={"salary": 45000, "signing_bonus": 40000},
            candidate_expectation={"salary": 48000, "signing_bonus": 50000},
            result=result,
            sentiment="positive",
        )

        self.log(f"第2轮谈判完成，状态: {result['status']}", "SUCCESS")

    async def test_7_candidate_negotiation(self):
        """测试7：候选人端谈判"""
        self.log("测试7：候选人端谈判", "TEST")

        # 模拟候选人收到offer后的回应
        candidate_offer_data = {
            "job_id": self.requisition_id,
            "job_title": "高级Python工程师",
            "company": "TalentAI Corp",
            "salary": 42000,
            "signing_bonus": 30000,
            "rsu": 8000,
            "vacation_days": 10,
            "remote_days": 1,
        }

        self.candidate.receive_offer(candidate_offer_data)

        # 候选人发起谈判
        negotiation_data = {
            "counteroffer_salary": 48000,
            "message": "我对这个Offer整体满意，但希望薪资能进一步讨论。",
        }

        result = self.candidate.negotiate_offer(
            offer_id=f"offer_{self.requisition_id}",
            negotiation_data=negotiation_data,
        )

        self.assert_true("gap_analysis" in result or "status" in result, "包含谈判结果")
        self.log(f"候选人谈判完成，状态: {result.get('status')}", "SUCCESS")

    async def test_8_deal_reached(self):
        """测试8：达成交易"""
        self.log("测试8：检查是否达成交易", "TEST")

        # 检查谈判历史
        history = self.storage.get_negotiation_history(self.negotiation_id)

        self.assert_true(len(history) >= 2, f"谈判记录数: {len(history)}")

        deal_reached = self.storage.is_deal_reached(self.negotiation_id)
        self.log(f"交易达成: {deal_reached}", "SUCCESS" if not deal_reached else "WARN")

        # 发送邮件通知（模拟）
        channel_msg = await self.channel_router.send_via_channel(
            channel_type=MsgChannelType.EMAIL,
            to="liming@example.com",
            body="恭喜！您的Offer已更新，请查收。",
            subject="TalentAI Pro - Offer 谈判完成",
        )
        self.log(f"邮件通知发送: {channel_msg.id}", "SUCCESS")

    async def test_9_websocket_message(self):
        """测试9：WebSocket消息传递"""
        self.log("测试9：WebSocket消息传递", "TEST")

        # 模拟WebSocket发送谈判消息
        msg = await self.ws_manager.send_counter_offer(
            from_agent=self.recruiter.id,
            to_agent=self.candidate.id,
            negotiation_id=self.negotiation_id,
            offer_id=self.offer_id,
            perspective="recruiter",
            round_num=3,
            counter_offer={"salary": 45000, "signing_bonus": 40000},
            message="这是第3轮谈判提案",
        )

        self.assert_true(msg.id.startswith("ws_"), f"消息ID: {msg.id}")
        self.log(f"WebSocket消息发送: {msg.id}, 状态: {msg.status}", "SUCCESS")

        # 检查连接状态
        status = self.ws_manager.get_connection_status()
        self.log(f"WebSocket连接状态: {status['total_connections']}个连接", "SUCCESS")

    async def test_10_negotiation_history(self):
        """测试10：验证谈判历史存储"""
        self.log("测试10：验证谈判历史", "TEST")

        history = self.storage.get_negotiation_history(self.negotiation_id)

        self.assert_true(len(history) >= 2, f"历史记录数: {len(history)}")

        for record in history:
            self.log(f"  轮次{record['round_num']}: {record['perspective']} - {record['message_status']}")

        self.log(f"谈判历史验证完成，共{len(history)}条记录", "SUCCESS")

    def assert_true(self, condition: bool, message: str):
        """断言"""
        if not condition:
            self.log(f"断言失败: {message}", "ERROR")
            raise AssertionError(message)

    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("🧪 TalentAI Pro - 谈判模块端到端测试")
        print("=" * 60 + "\n")

        try:
            await self.setup()
            await self.test_1_create_requisition()
            await self.test_2_add_candidate()
            await self.test_3_screen_candidate()
            await self.test_4_create_offer()
            await self.test_5_start_negotiation()
            await self.test_6_second_negotiation_round()
            await self.test_7_candidate_negotiation()
            await self.test_8_deal_reached()
            await self.test_9_websocket_message()
            await self.test_10_negotiation_history()

            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)

        except AssertionError as e:
            print(f"\n❌ 测试失败: {e}")
            raise
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            raise

    def print_summary(self):
        """打印测试摘要"""
        passed = sum(1 for r in self.test_results if r["status"] == "SUCCESS")
        failed = sum(1 for r in self.test_results if r["status"] == "ERROR")
        print("\n" + "=" * 60)
        print("📊 测试摘要")
        print("=" * 60)
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"总计: {len(self.test_results)}")
        print("=" * 60)


async def main():
    """主函数"""
    tester = NegotiationE2ETester()
    await tester.run_all_tests()
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
