"""测试三个合能评估模型的API连通性"""
import openai

API_KEY = "sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr"
BASE_URL = "https://api.siliconflow.cn/v1"

models = [
    ("deepseek-ai/DeepSeek-V4-Flash", "V4 Flash"),
    ("deepseek-ai/DeepSeek-V3.2",     "V3.2"),
    ("THUDM/GLM-Z1-32B-0414",         "GLM-Z1-32B"),
]

client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY)

print("=" * 60)
print("  合能评估模型 API连通性测试")
print("=" * 60)

for model_key, model_name in models:
    try:
        resp = client.chat.completions.create(
            model=model_key,
            messages=[{"role": "user", "content": "请用一句话说明你的身份"}],
            temperature=0.1, max_tokens=100
        )
        msg = resp.choices[0].message.content.strip()
        # 去除可能导致GBK报错的字符
        safe_msg = msg.encode('gbk', errors='replace').decode('gbk')
        print(f"  [OK] {model_name}")
        print(f"       回复: {safe_msg[:60]}...")
    except Exception as e:
        print(f"  [ERR] {model_name}: {str(e)[:80]}")
    print()

print("=" * 60)
print("  测试完成")
