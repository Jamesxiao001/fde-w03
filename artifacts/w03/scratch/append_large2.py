p = "docs/w03/metric_decisions.md"
s = open(p, encoding="utf-8-sig").read()
s = s.replace("副本 artifacts/w03/metric_test_report-large.json。", "（第一轮，21 条）。")
s = s.rstrip() + "\n\n"
s += """### 规模数据补测：多种问法与定稿库路径

- 按任务书“同一问题多写几种问法”，在 customer/w03/make_tests_large.py 追加 7 条（x01 口语化净销售额、x02 换说法首购、x03 换说法月内复购、x04 简短问付费复购率、x05 按成交地区、x06 购买会员数按归属门店、x07 按日分组），期望仍由 audit.py 计算，共 28 条。
- 定稿库改名为 artifacts/w03/library 后，按“定稿库变了要用新项目路径重新加载”重新加载为 .runtime/qinghe-large-v2。
- 结果：27/28，未通过仅 c17；x06 说明 c13 的修复对其他订单类指标同样有效，x07 按日 31 组与审核一致。单次查询 0.031–0.093 秒，21 次以上查询合计 1.184 秒；单例端到端 2.9–20.8 秒，合计 336.7 秒（测试命令总计 342 秒）。环境同上。
- 报告：artifacts/w03/test-large-v2/metric_test_report.json，副本 artifacts/w03/metric_test_report-large.json。
"""
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s.encode("utf-8")))