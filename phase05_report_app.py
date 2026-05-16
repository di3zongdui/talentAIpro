"""
Phase 0.5：合能评估服务器
=========================
一体式服务：前端页面 + 评分API
用法：python phase05_report_app.py
然后打开 http://localhost:8765
"""

import json, os, sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# 尝试加载openai
try:
    import openai
except ImportError:
    print("❌ 请安装 openai: pip install openai")
    sys.exit(1)

# ===== 配置 =====
# 优先从环境变量读取，其次用默认值（请替换）
import os
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY") or "your_api_key_here"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V4-Flash"
PORT = 8765

# ===== 评分Prompt =====
SCORING_PROMPT = """请基于以下对话记录，评估用户的6个维度分数（0-100）。

对话记录：
{dialogue}

评分维度：
1. ai_operation (AI操作力) - 知道AI能做什么/不能做什么、如何指挥AI
2. critical_integration (批判整合力) - 评估AI输出质量、整合到工作流
3. ethical_judgment (伦理判断力) - 识别AI伦理风险、保持人文底线
4. workflow_orchestration (流程编排力) - 设计人机协作流程
5. ai_collaborative_creativity (AI协同创造力) - 与AI协作创造、叙事表达
6. ai_adaptability (AI适应力) - 持续适应AI变化、保持专注

依据以下级别评分：
- 0-20: 无/极弱  21-40: 弱  41-60: 中等  61-80: 强  81-100: 极强
严格基于实际回答内容，不要自由发挥

输出格式（严格JSON，无任何额外文字）：
{{"ai_operation":{{"score":0-100,"evidence":"..."}},"critical_integration":{{"score":0-100,"evidence":"..."}},"ethical_judgment":{{"score":0-100,"evidence":"..."}},"workflow_orchestration":{{"score":0-100,"evidence":"..."}},"ai_collaborative_creativity":{{"score":0-100,"evidence":"..."}},"ai_adaptability":{{"score":0-100,"evidence":"..."}}}}"""

app = FastAPI(title="合能评估 Phase 0.5")

# 查找HTML文件所在目录
html_dir = Path(__file__).parent

# 读取HTML模板
html_path = html_dir / "phase05-test.html"
if not html_path.exists():
    print(f"❌ 找不到 phase05-test.html (期望路径: {html_path})")
    sys.exit(1)

HTML_TEMPLATE = html_path.read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE


@app.post("/api/score")
async def score(request: Request):
    """接收回答数据，调用LLM评分，返回结果"""
    try:
        data = await request.json()
    except:
        return JSONResponse({"error": "无效的JSON数据"}, status_code=400)

    responses = data.get("responses", [])
    subject = data.get("subject", "匿名")

    if not responses:
        return JSONResponse({"error": "没有回答数据"}, status_code=400)

    # 构建对话文本
    dialogue = "\n".join([
        f"第{r['round']}轮（{r['dimension']}）: {r['answer']}"
        for r in responses if r.get('answer', '').strip()
    ])

    if not dialogue.strip():
        return JSONResponse({"error": "所有回答均为空"}, status_code=400)

    # 调用LLM评分
    try:
        client = openai.OpenAI(base_url=BASE_URL, api_key=SILICONFLOW_API_KEY)

        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个合能评分员，严格按评分协议打分，只输出JSON。"},
                {"role": "user", "content": SCORING_PROMPT.format(dialogue=dialogue)}
            ],
            temperature=0.1,
            max_tokens=2048,
            extra_body={"thinking_mode": "high"}
        )

        raw = resp.choices[0].message.content.strip()
        # 提取JSON
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        scores = json.loads(raw)

    except Exception as e:
        return JSONResponse({"error": f"评分引擎调用失败: {str(e)}", "raw": raw if 'raw' in locals() else ""}, status_code=500)

    # 计算总分和角色
    dim_keys = ["ai_operation", "critical_integration", "ethical_judgment",
                "workflow_orchestration", "ai_collaborative_creativity", "ai_adaptability"]
    dim_labels_map = {
        "ai_operation": "AI操作力",
        "critical_integration": "批判整合力",
        "ethical_judgment": "伦理判断力",
        "workflow_orchestration": "流程编排力",
        "ai_collaborative_creativity": "AI协同创造力",
        "ai_adaptability": "AI适应力"
    }

    dim_values = {}
    for k in dim_keys:
        v = scores.get(k, {})
        dim_values[k] = {
            "score": v.get("score", 0) if isinstance(v, dict) else (v if isinstance(v, (int, float)) else 0),
            "evidence": v.get("evidence", "") if isinstance(v, dict) else "",
            "label": dim_labels_map.get(k, k)
        }

    total = sum(d["score"] for d in dim_values.values())
    avg = total / 6

    # 角色判定（基于最高分维度）
    max_dim = max(dim_keys, key=lambda k: dim_values[k]["score"])
    max_score = dim_values[max_dim]["score"]

    role_map = {
        "ai_operation": {"role": "Prompt Architect", "desc": "你擅长用精准指令让AI产出高质量内容。典型职业：产品经理、营销、内容创作者"},
        "critical_integration": {"role": "Critique Partner", "desc": "你善于识别AI输出中的错误和偏见。典型职业：律师、分析师、编辑"},
        "workflow_orchestration": {"role": "Workflow Weaver", "desc": "你擅长将复杂流程拆解为人机协作链条。典型职业：工程师、项目经理"},
        "ai_collaborative_creativity": {"role": "Creative Integrator", "desc": "你善于在AI基础上发挥独特创造力、用故事影响他人。典型职业：设计师、战略顾问"},
        "ethical_judgment": {"role": "Ethics Guardian", "desc": "你能发现AI系统对组织/社会的潜在风险。典型职业：合规、法务、CSO"},
        "ai_adaptability": {"role": "Learning Pioneer", "desc": "你快速适应AI变化，持续提升人机协作效率。典型职业：技术专家、AI训练师"}
    }
    user_role = role_map.get(max_dim, {"role": "综合型", "desc": "你在多个维度表现均衡"})

    # 如果多个维度接近，考虑混合型
    top_dims = sorted(dim_keys, key=lambda k: dim_values[k]["score"], reverse=True)
    if len(top_dims) >= 2 and dim_values[top_dims[0]]["score"] - dim_values[top_dims[1]]["score"] < 8:
        user_role["note"] = "你的合能类型偏向混合型，兼具多维优势"

    # 保存结果
    result = {
        "subject": subject,
        "timestamp": datetime.now().isoformat(),
        "scores": dim_values,
        "total_score": round(avg, 1),
        "role": user_role["role"],
        "role_description": user_role["desc"],
        "top_dimension": dim_labels_map.get(max_dim, max_dim),
        "top_dimension_score": max_score
    }

    # 保存到文件
    results_dir = html_dir / "phase05_results"
    results_dir.mkdir(exist_ok=True)
    fname = f"synability_{subject}_{datetime.now().strftime('%m%d_%H%M')}.json"
    (results_dir / fname).write_text(
        json.dumps({**data, "result": result}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return JSONResponse(result)


if __name__ == "__main__":
    if SILICONFLOW_API_KEY == "your_api_key_here":
        print("!! 请先修改 phase05_report_app.py 中的 API Key")
        print(f"   编辑第{SILICONFLOW_API_KEY}行，填入你的硅基流动API Key")
        sys.exit(1)

    print(f"\n  ** 合能评估 Phase 0.5 服务已启动 **")
    print(f"  ======================================")
    print(f"  访问地址: http://localhost:{PORT}")
    print(f"  评分模型: {MODEL}")
    print(f"  数据保存: phase05_results/")
    print(f"\n  按 Ctrl+C 停止服务\n")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
