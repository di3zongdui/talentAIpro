"""测试搜索描述生成"""
import sys
sys.path.insert(0, 'TalentAI_Pro')
from agents.orchestrator import AgentOrchestrator

o = AgentOrchestrator()

# 测试1: 简化JD
jd1 = "车险高级精算专家 60-90万 北京 本科+ 3年以上 精算经验 GLM Python SAS"
desc1 = o.generate_search_description(o.parse_jd(jd1))
print("测试1 - 简化JD:")
print(f"  搜索描述: {desc1}")

# 测试2: 完整JD
jd2 = """车险高级精算专家
薪资范围60-90万
工作地点北京
职责描述
搭建并维护车险核心精算模型：出险频率模型、严重度模型、纯风险保费模型。
负责车险产品费率厘定、参数设定、产品测算、目标利润测算。
负责车险准备金测算：IBNR、IBNER、链梯法等方法。
任职要求
数学、统计、精算相关专业本科及以上学历。
3年以上保险精算、车险定价经验。
熟练使用Python、SAS、SQL进行数据建模。
熟悉GLM、GBDT或其他常用定价模型框架。"""
desc2 = o.generate_search_description(o.parse_jd(jd2))
print("\n测试2 - 完整JD:")
print(f"  搜索描述: {desc2}")
