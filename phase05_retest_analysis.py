"""重测信度对比：手动分析"""
import json
from pathlib import Path

results_dir = Path("C:/Users/George Guo/WorkBuddy/20260422151119/phase05_results")

personas = ["张明", "李华", "王芳"]
dim_keys = ["ai_operation","critical_integration","ethical_judgment","workflow_orchestration","ai_collaborative_creativity","ai_adaptability"]
dim_labels = ["AI操作力","批判整合力","伦理判断力","流程编排力","AI协同创造力","AI适应力"]

print("="*70)
print("  Phase 0.5 重测信度分析")
print("="*70)

all_diffs = []
for name in personas:
    first_file = None
    retest_file = None
    for f in results_dir.glob(f"*{name}*.json"):
        if "retest" in f.stem:
            retest_file = f
        elif "scored" not in f.stem:
            first_file = f

    if not first_file or not retest_file:
        print(f"\n  {name}: 缺文件 first={first_file} retest={retest_file}")
        continue

    with open(first_file, 'r', encoding='utf-8') as f:
        first = json.load(f)
    with open(retest_file, 'r', encoding='utf-8') as f:
        retest = json.load(f)

    fs = first.get('scores',{})
    rs = retest.get('scores',{})

    print(f"\n  {name}:")
    print(f"  {'维度':<12s} {'第1次':>6s} {'第2次':>6s} {'差':>6s}")
    print(f"  {'-'*32}")
    total = 0
    for k, label in zip(dim_keys, dim_labels):
        v1 = fs.get(k,{}).get('score',0) if isinstance(fs.get(k), dict) else fs.get(k,0)
        v2 = rs.get(k,{}).get('score',0) if isinstance(rs.get(k), dict) else rs.get(k,0)
        diff = abs(v1 - v2)
        total += diff
        print(f"  {label:<12s} {v1:>6d} {v2:>6d} {diff:>+5d}")
    avg = total / len(dim_keys)
    all_diffs.append(avg)
    verdict = "OK 稳定" if avg < 15 else "不一致"
    print(f"  {'平均差':<12s} {'':>6s} {'':>6s} {avg:>5.1f}")
    print(f"  判断: {verdict}")

print(f"\n{'='*70}")
print(f"  总体结论:")
print(f"  3人平均重测差: {sum(all_diffs)/len(all_diffs):.1f} 分")
print(f"  成功标准: <15分")
print(f"  结果: {'通过' if sum(all_diffs)/len(all_diffs) < 15 else '不通过'}")
print(f"{'='*70}")
