p = "docs/w03/metric_decisions.md"
s = open(p, encoding="utf-8-sig").read().rstrip() + "\n\n"
s += """## 构建迭代记录（续：v2）

| 版本 | 输入变化 | 结果 | 处理 |
|---|---|---|---|
| build-v2 | Skill 第六段第 3 步新增“实体查询 ID 只对应一跳实体；多对一关联对象上的实体需在事实模型派生 SQL 中带出外键并直接声明”规则 | SOURCE_QUOTE_NOT_EXACT：business_model_usage 引用“会员卡（card）”一段时丢了原文的 Markdown 加粗符号 `**`，其余检查未执行 | 判为偶发抄写偏差，Skill 不改，保留目录作失败记录 |
| build-v2b | 同 v2 | 38 已定义 / 0 未决 / 四项检查通过 | 合并为 artifacts/w03/library-v2，加载为 .runtime/qinghe-small-v2b（已激活） |

v2b 相对 v1 的结构变化：订单事实模型改为派生模型 orders_enriched（orders LEFT JOIN members 带出 home_store_id，每单只对应一个会员，粒度仍为 order_id），并直接声明 home_store 外键实体；首购模型与有效订单序号模型同样直接带 home_store；排序仍在全历史上进行。月内与付费两个“账户×月”模型仍只有 member 实体。

操作备注：merge 不允许覆盖已有输出目录（OUTPUT_ALREADY_EXISTS），第一次误把 v1 库加载成 .runtime/qinghe-small-v2，该项目内容实为 v1，已弃用；artifacts/w03/library 保留为 v1 库，v2 使用 library-v2。

## 解释人工核查

逐条读 Agent 的中文回答，核对“数字之外”的内容是否准确：

- 8 月订单问题（chat-runs/6a5087de…）：有效订单 27 单、净销售额 100300 分，与独立计算一致；回答说明了有效订单口径与退款按原订单日期归属，表述准确。
- 8 月付费会员问题（chat-runs/6467570b…）：6 个账户、10 单、47550 分，与独立计算一致。不足：回答没有点明“资格按月末最后一天判定，判定为有资格后当月更早的有效订单也计入”，客户可能误以为只统计月末之后的订单。属于解释遗漏，数值无误，记为后续改进点。
- c17“按门店看 7 月净销售额”：Agent 未先澄清，但回答明确写出“按订单成交门店分组”，数值（S01 12500、S02 10000、S03 9000，合计 31500 分）与成交门店口径一致。没有误导性表述，但未按期望先确认门店角色。

## 测试与回归记录

期望来源：独立审核程序 customer/w03/audit.py 直接读四张 CSV 逐记录计算，customer/w03/make_tests.py 在运行 Agent 前生成并冻结 tests.json（21 条：16 条 ok、3 条 clarify/unsupported 边界、2 条付费限制），覆盖全部 38 个指标；c01、c10 锁定 data_version。判定程序 customer/w03/judge.py 只做比较，不调用模型。

| 轮次 | 项目 | 结果 | 未通过 |
|---|---|---|---|
| v1 | .runtime/qinghe-small-v1 | 19/21（185 秒） | c13 NATIVE_QUERY_FAILED；c17 期望 clarify 实际 ok |
| v2 | .runtime/qinghe-small-v2b | 20/21（197 秒） | c17 同上 |

c13 根因：v1 订单模型只有 member、store 两个实体，home_store 只挂在 members 上；从订单出发 MetricFlow 只接受两跳名 member__home_store，而产品层只接受目标 ID home_store（用 member__home_store 查询返回 unsupported）。不经模型直接用 query 命令查询同样失败（artifacts/w03/probe/r-home.json），排除模型偶发。维度检查的 per_metric 把全部 38 个指标的 home_store 都映射为 home_store 并判通过，说明该检查没有逐指标实际执行查询，“检查通过”不等于“可查询”。修复后 v2b 上同一查询返回 S01 4500、S02 18000、S03 9000，与期望一致（artifacts/w03/probe/r2-home.json）。

c17 处理：按“不为通过而改期望”的原则保留期望 clarify，记为未通过差异。依据是小林 MSG-04495 确认“按门店”须先讲清成交门店还是归属门店。后续可在 catalog 的门店维度说明中写明歧义，或在 Agent 澄清规则中加入门店角色，再回归验证。

遗留风险：月内与付费“账户×月”模型没有 home_store 实体，但维度检查仍判可按 home_store 分组；实测两类指标按 home_store 查询均被 query_policy 拦截为 unsupported（依据 03 运营周报“仅整月、全门店口径”、04 统计确认邮件），没有落到报错。若将来放开门店拆分，需要先补实体并实测。

判定程序自检：customer/w03/inject.py 以 v1、v2 报告中已通过的真实结果为底稿各做 18 项合成注入与正向检查（错指标、错日期、多筛选、错分组、漏组、重复组、元分混淆、比率误作百分数、null 改 0、篡改数值、error 伪装、错数据版本、原样通过、行序变化、27 对 27.0、布尔、数字字符串、大整数差 1），两轮均 18/18 符合预期（artifacts/w03/judge-checks、judge-checks-v2）。注入是人为构造，不代表模型实际犯过这些错误。

提交报告：artifacts/w03/metric_test_report.json 为 v2 报告的副本。
"""
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s.encode("utf-8")))