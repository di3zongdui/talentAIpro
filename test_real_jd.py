import sys
sys.path.insert(0, 'TalentAI_Pro')
from agents.orchestrator import AgentOrchestrator

o = AgentOrchestrator()

# 用户提供的真实JD
jd_text = """车险高级精算专家
进行中
职位ID
60-90万
北京
招聘0/1人
发布时间：2026-05-07（运作8天）
预估佣金：
暂无
客户：
CGL（C7093）
维护人：
王舒祥

职位描述
职责描述
1. 车险精算模型开发与维护（核心职责）
搭建并维护车险核心精算模型：出险频率模型、严重度模型、纯风险保费模型。负责模型选型、变量筛选、分布拟合（Poisson/NB/Gamma/LN）、GLM 或 GBDT 等模型训练。定期开展模型校准（Calibration）、模型偏差回溯（NMAE、WAPE、RCCI、Lift、PSI 等）。对重点业务（新能源/黑点车型/地区特殊群体）构建专项精算模型。
2. 费率厘定与产品定价
负责车险产品费率厘定、参数设定、产品测算、目标利润测算。
构建费率结构（基准费率 + 风险因子 + 地区因子 + 车型因子等）。
推动差异化定价（地区/车型/渠道/人群）。
参与新产品定价：新能源 UBI、Telematics、短期车险、场景化保障等。
3. 经营成本与费用精算
测算并校准附加费用率、渠道佣金率、管理费用率、税费等。
负责保费结构拆解：纯风险保费 → 毛保费 → 已赚保费 → 利润贡献。分析费用率偏差并反馈经营部门，提供优化建议。
4. 赔付准备金与 IBNR 测算
负责车险准备金测算：IBNR、IBNER、链梯法、Bornhuetter-Ferguson等方法。监控赔付滞后结构、案件进展、已报未决（RBNS）、事故通道损失率变化。出具准备金分析报告，为财务与再保管理提供依据。
5. 数据体系与精算分析能力
定义精算数据需求，与数据团队建设精算分析底座。
使用 SQL / Python / SAS 建立建模数据集、损失分布、出险分布。建设精算看板（频率、严重度、赔付率、费用率、利润率、准备金等）。

任职要求
必须条件（硬性要求）
数学、统计、精算、金融工程等相关专业本科及以上学历。
精算师资格考试要求：通过国内外所有涉及精算定价相关考试科目（国内外精算师证优先 ）。
3 年以上保险精算、车险定价、准备金、数据分析经验。
熟练使用 Python 或 SAS、SQL 进行数据清洗、建模与分析。
熟悉 GLM、GAM、GBDT 或其他常用定价模型框架。
能独立完成精算模型报告、费率测算、准备金分析。"""

result = o.run_pipeline(jd_text)
print("====== JD解析结果 ======")
for k, v in result.jd_parsed.items():
    if k != 'raw_text':
        print(f"  {k}: {v}")

print("\n====== 搜索描述 ======")
print(f"  {result.search_description}")

print("\n====== 搜索策略 ======")
print(f"  目标经验: {result.search_strategy.get('target_experience_min')}-{result.search_strategy.get('target_experience_max')}年")
print(f"  目标薪资: {result.search_strategy.get('target_salary_min')}-{result.search_strategy.get('target_salary_max')}万")
print(f"  搜索词: {result.search_strategy.get('search_queries')}")
