import os, sys, platform, importlib.metadata as md
def ver(p):
    try: return md.version(p)
    except Exception: return "?"
env = (f"{os.environ.get('W3_OS')}；{os.environ.get('W3_CPU')}；内存 {os.environ.get('W3_MEM')}；"
       f"Python {platform.python_version()}；duckdb {ver('duckdb')}；dbt-core {ver('dbt-core')}；"
       f"metricflow {ver('metricflow')}；模型 {os.environ.get('FDE_MODEL_NAME')}（超时 {os.environ.get('FDE_MODEL_TIMEOUT')} 秒）")
print(env)
p = "docs/w03/metric_decisions.md"
s = open(p, encoding="utf-8-sig").read().rstrip() + "\n\n"
s += f"""## 规模数据回归

- 数据：materials/data/large，manifest id qinghe-w03-20260923-large（合成数据，会员 30000、订单 300000、门店 24、卡 38891；覆盖 2024-09-01 至 2026-09-01，与小样本相同，c19–c21 边界前提不变）。
- 期望：customer/w03/make_tests_large.py 复用 make_tests.py 的 21 条用例与 audit.py 的计算，只把小样本逐条备注换成“规模数据期望完全由审核程序计算”；c01、c10 锁定 qinghe-w03-20260923-large。生成 17 秒，未手写任何期望值。
- 项目：artifacts/w03/library-v2（与小样本 v2 同一指标库，未针对规模数据修改）加载为 .runtime/qinghe-large-v1，加载 12 秒，未激活产品端。
- 环境：{env}。
- 结果：20/21，未通过仅 c17（期望 clarify，实际按成交门店直接作答），与小样本 v2 一致；报告 artifacts/w03/test-large-v1/metric_test_report.json，副本 artifacts/w03/metric_test_report-large.json。
- 耗时：单次查询 0.031–0.093 秒，21 次查询合计 0.874 秒；含模型解析与回答的单例 6.0–22.0 秒，合计 305.5 秒。瓶颈在模型调用，不在查询引擎。
- 覆盖说明：规模数据 2026-05 有 23289 单有效订单，c14 在规模数据上不再覆盖“零分母为 null”，该分支只由小样本与注入检查 null_to_zero 覆盖。规模数据只验证数值与关联在大量记录下仍一致，不另做逐条人工核对。
"""
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s.encode("utf-8")))