p = "docs/w03/metric_decisions.md"
s = open(p, encoding="utf-8-sig").read()
for a, b in [
    ("提交报告：artifacts/w03/metric_test_report.json 为 v2 报告的副本。",
     "提交报告：当时 artifacts/w03/metric_test_report.json 为 v2 报告的副本，已被第三轮报告替换（见文末）。"),
    ("- 报告：artifacts/w03/test-large-v2/metric_test_report.json，副本 artifacts/w03/metric_test_report-large.json。",
     "- 报告：artifacts/w03/test-large-v2/metric_test_report.json（当时的副本已被第三轮替换，见文末）。"),
]:
    if s.count(a) == 1:
        s = s.replace(a, b)
    else:
        print("跳过（未找到）：", a[:30])
s = s.rstrip() + "\n\n"
s += """## 构建迭代记录（续：v3）与第三轮回归

起因：c17“按门店看 7 月净销售额”两轮均直接按成交门店作答。查 Agent 输入（platform/fde_product/metrics/agent.py、product/w03_intent_prompt.txt）：意图提示词要求“业务含义不清”时 clarify，且“每项指标的 query_policy 和 constraints 限制必须遵守”；但 v2 目录中订单类指标的 constraints 为空，Agent 得不到“门店有两种角色须先讲清”的信息。平台代码不改，库文件不手改，改构建方法后重新生成。

| 版本 | Skill 变化 | 结果 |
|---|---|---|
| build-v3 | 第四段新增：业务模型写明某维度有多种角色、提问须先讲清的，对同时支持这些角色分组的指标在 constraints 写明“只用笼统说法时先澄清，不默认任何一种；指明角色时按所指查询”，并记入 business_model_usage；第二段补“引用逐字包括 Markdown 符号、标点和空格”（来自 build-v2 失败）。SKILL.md 9543→10150 字节，v2 备份 artifacts/w03/scratch/SKILL-v2.md | 38 已定义 / 0 未决 / 检查通过，422 秒 |

v3 目录核对：订单类 24 项、首购类 4 项新增门店澄清约束；月内与付费类只保留原有“全门店”限制，注册会员数无约束（只支持归属门店）；business_model_usage 逐字引用业务模型第 5 节“说‘按门店看’之前须先讲清是哪一种……（MSG-04495）”。v3 为整体重新生成（模型名也有变化），因此两套测试全部重跑。

定稿库：v2 库改名为 artifacts/w03/library-v2 留档，build-v3 用 merge 生成 artifacts/w03/library；加载为 .runtime/qinghe-small-v3（已激活）与 .runtime/qinghe-large-v3。

| 轮次 | 项目 | 结果 | 说明 |
|---|---|---|---|
| 小样本 v3 | qinghe-small-v3 | 21/21 | c17 返回 clarify；c12、c13 指明角色仍直接作答；单例合计 185.4 秒 |
| 判定自检 v3 | test-small-v3 报告 | 18/18 | artifacts/w03/judge-checks-v3 |
| 大批量 v3 | qinghe-large-v3 | 13/28，不计入 | 第 14 题起模型接口返回 MODEL_HTTP_402（账户余额不足），15 题 status=error、耗时约 0.6 秒、无模型用量；判定程序正确判为不通过，没有当成 0。前 13 题全部通过 |
| 大批量 v3b | qinghe-large-v3（同一项目，充值后重跑） | 28/28 | 单次查询 0.032–0.204 秒，合计 3.127 秒；单例 5.8–22.3 秒，合计 366.6 秒（命令总计 372 秒） |

提交报告：artifacts/w03/metric_test_report.json = test-small-v3；artifacts/w03/metric_test_report-large.json = test-large-v3b。两者均在由当前 artifacts/w03/library 加载的项目上运行。

c17 说明：期望自始至终是 clarify，三轮未改。通过的依据是 Agent 先问清门店角色；运营默认用哪种门店仍未确认（小林 MSG-04495），王经理 MSG-04524 要求继续列为待确认，SOW 照此保留。
"""
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s.encode("utf-8")))