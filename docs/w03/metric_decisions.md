# 指标核定与未决项

当前候选库：`artifacts/w03/build-v1/`（38 项全部定义，unresolved 为空，三项检查通过）。指标 ID、中文名、单位、来源引文与查询限制见 `artifacts/w03/build-v1/catalog.json`，执行定义见 `metrics.yml` 与三个派生 SQL；定稿后以 `artifacts/w03/library/` 为准。下文按指标族说明采用依据，不重复抄目录。

## 采用依据

| 指标族（目标 ID） | 采用的口径 | 来源 | 确认状态 |
| --- | --- | --- | --- |
| 订单计数（order_count、paid_order_count、valid_order_count、cancelled_order_count） | 创建订单含取消单；支付订单为 paid（含后来全退）；有效订单为 paid 且实付减累计退款大于 0；取消订单为 cancelled；按下单日期 ordered_at 统计 | `01_订单日报说明.md`；`02_财务邮件.md`（有效订单定义） | 客户书面材料 |
| 退款订单（refund_order_count、partial_refund_order_count、full_refund_order_count） | 退款订单为 paid 且退款大于 0；部分退款为退款大于 0 且小于实付；全额退款为实付大于 0 且退款等于实付；退款按原订单下单日期归属 | `01_订单日报说明.md`；`02_财务邮件.md` | 客户书面材料 |
| 金额（payment_cents、refund_cents、net_sales_cents、gross_cents、discount_cents） | 均只计 paid；净销售额 = 实付 − 退款；优惠金额 = 原价 − 实付，退款不冲减优惠；单位分；退款按原订单日期归属 | `01_订单日报说明.md`；`02_财务邮件.md` | 客户书面材料 |
| 去重计数（buyer_count、refund_buyer_count、selling_store_count） | 有有效订单的不同 CRM 会员账户数（不做跨系统自然人去重）；有退款的 paid 订单关联的不同账户数；有有效订单的不同成交门店数 | `01_订单日报说明.md`；`05_数据字典.md`（member_id 为 CRM 账户，store_id 为成交门店） | 客户书面材料 |
| 件数（valid_order_items） | 有效订单原始购买件数合计，不是净商品销量 | `01_订单日报说明.md` | 客户书面材料 |
| 比率（avg_order_value、avg_buyer_value、purchase_frequency、refund_amount_rate、cancel_rate、refund_order_rate、discount_rate、items_per_order） | 均为分子指标与分母指标之比（不对逐单比率求平均）；分母为零时未定义（null） | `02_财务邮件.md` | 客户书面材料 |
| 注册会员（new_member_count） | 按注册日期 registered_at 统计新注册 CRM 账户数，可按归属门店和等级分组，不等于自然人数 | `03_会员运营周报.md` | 客户书面材料 |
| 观测期首购与后续（first_buyer_count、first_order_sales_cents、first_order_count、repeat_order_count） | 在测试覆盖期全部有效订单上为每个账户按下单日期、同日按订单号排序；第一笔落入窗口计首购／首单，按该单日期归属；第二笔及以后按订单日期落入窗口计后续；不代表终身首购 | `03_会员运营周报.md` | 客户书面材料 |
| 月内购买与复购（monthly_buyer_count、monthly_repeat_buyer_count、monthly_repeat_rate） | 同一自然月有至少一笔／两笔有效订单的账户数及其比；仅整月、全门店；多月按月分别展示，不跨月加总；复购率分母为同月有效购买账户（周报已由全部注册会员改为此口径） | `03_会员运营周报.md` | 客户书面材料 |
| 月末付费会员（monthly_paid_buyer_count、monthly_paid_order_count、monthly_paid_sales_cents、monthly_paid_repeat_buyer_count、monthly_paid_repeat_rate、monthly_paid_avg_order_value） | 统计选择：按自然月最后一天判断资格，先选月末有资格的账户，再统计其当月全渠道、全门店有效订单，不要求下单当天已有资格；仅整月、全渠道、全门店，暂不按门店或渠道拆，多月按月列；零分母未定义 | `04_本期统计确认邮件.md`（王经理） | 客户书面材料 |
| ↳ 付费资格规则 | 计入卡产品为悦享年卡、家庭季卡（异业联名卡、体验卡不计入，与购卡金额无关；只约束本期总部运营月报）；等级与金额不用于判定；按 CRM 账户判定，多卡不重复计人、不重复累计订单；卡在判定日 D 有效当且仅当 生效日 ≤ D 且 D 早于计划到期日与提前终止日中较早者，提前终止为空不代表无限期 | `docs/w03/business_model.md` 3.1–3.4；小林 MSG-04489、04493；陈姐 MSG-04500、04502、04504；王经理 MSG-04519 指明卡范围以小林、日期规则以陈姐答复为准 | 访谈口头确认，**不是客户书面确认**：访谈中小林、陈姐均未能指出成文口径文件 |

核查方式：逐项对照 `metrics.yml` 的 measure 表达式、ratio 引用和三个派生 SQL（`valid_member_orders_ranked`、`member_month_valid_orders`、`paid_member_month_orders`）与上表口径一致；三个派生模型粒度均为 order_id，检查通过，无一对多放大。三项结构检查与来源引文检查只说明结构可用、引文存在，业务数值以第 10 步独立期望核对为准。

## 冲突、未决与不支持

| 事项 | 影响 | 状态 | 下一步 |
| --- | --- | --- | --- |
| 付费资格口径无可指出的成文文件 | 付费 6 项的资格规则来源为访谈说法 | 已按访谈采用，标注“口头确认” | SOW 中约定交付前由客户方书面确认一次；向老周核实是否有系统说明 |
| 月报口径最终确认（签字）人未定 | 付费 6 项及整体验收的确认主体 | 未决（小林 04497；王经理 04519） | 王经理第 2 次访谈提出 |
| “按门店”默认指成交门店还是归属门店 | 用户只说“按门店”时的查询 | 未决（小林 04495） | 指标库同时提供 store 与 home_store 两条路径；Agent 遇到含糊说法应澄清，测试中按 clarify 期望 |
| 卡日期数据边界（生效日与到期日同日、提前终止早于生效日等） | 资格判定的极端记录 | 未决，未推断规则 | 向老周核实测试数据中是否存在 |
| 不支持：月内 3 项与付费 6 项只按完整自然月、全门店（付费另含全渠道）查询，不支持按门店或渠道拆 | 这 9 项的分组与筛选 | 已设 `query_policy.full_month_only = true` | 由查询程序拒绝不完整月份或拆分请求 |
| 不支持：超出数据覆盖（2024-09-01 至 2026-09-01，不含结束日）的时段 | 全部 38 项 | 程序返回不支持，不当作 0 | — |
| 不支持：按条件筛选会员、生成名单 | 本期不在指标库范围 | 属后续能力，按交付时书面范围确认（王经理 04517） | 写入 SOW 后续范围与变更处理 |

## 构建迭代记录

| 轮次 | 输出目录 | 范围 | 结果 | 判断与处理 |
| --- | --- | --- | --- | --- |
| try1 | `artifacts/w03/build-try1` | valid_order_count、net_sales_cents、avg_order_value、buyer_count | 4 项定义，0 未决，三项检查通过 | 核对有效订单、净额、去重会员、比率与单位均正确；验证 Skill 的输出协议、门店两种角色与维度路径可用 |
| try2 | `artifacts/w03/build-try2`（保留失败记录） | 付费 6 项 | `PROJECT_VALIDATION_FAILED`：dbt、粒度、MetricFlow 检查通过，维度覆盖检查失败（store、store__region、store__store_name、order__channel、order__status 不可查询） | 本批 6 项均建在“账户×月”派生模型上，语义图中无法到达订单侧维度；属小批次副作用，且付费 6 项本就不按门店或渠道拆，非 Skill 错误，未改 Skill。同时核对派生 SQL：卡产品范围、月末判定、三个日期端点、EXISTS 防重复均与业务模型一致 |
| v1 | `artifacts/w03/build-v1` | 全部 38 项 | 38 项定义，0 未决，三项检查通过 | 逐项核查见“采用依据”；作为候选定稿库，待第 10 步独立期望核对 |

Skill 版本：`customer/w03/build-metrics/SKILL.md`（三轮相同，各构建目录保存 `skill_used.md`、`input.json`、`trace.json`）。

## 构建迭代记录（续：v2）

| 版本 | 输入变化 | 结果 | 处理 |
|---|---|---|---|
| build-v2 | Skill 第六段第 3 步新增“实体查询 ID 只对应一跳实体；多对一关联对象上的实体需在事实模型派生 SQL 中带出外键并直接声明”规则 | SOURCE_QUOTE_NOT_EXACT：business_model_usage 引用“会员卡（card）”一段时丢了原文的 Markdown 加粗符号 `**`，其余检查未执行 | 判为偶发抄写偏差，Skill 不改，保留目录作失败记录 |
| build-v2b | 同 v2 | 38 已定义 / 0 未决 / 四项检查通过 | 合并为 artifacts/w03/library（原 library-v2），加载为 .runtime/qinghe-small-v2b（已激活） |

v2b 相对 v1 的结构变化：订单事实模型改为派生模型 orders_enriched（orders LEFT JOIN members 带出 home_store_id，每单只对应一个会员，粒度仍为 order_id），并直接声明 home_store 外键实体；首购模型与有效订单序号模型同样直接带 home_store；排序仍在全历史上进行。月内与付费两个“账户×月”模型仍只有 member 实体。

操作备注：merge 不允许覆盖已有输出目录（OUTPUT_ALREADY_EXISTS），第一次误把 v1 库加载成 .runtime/qinghe-small-v2，该项目内容实为 v1，已弃用；之后为与任务书路径一致，把 v1 库改名为 artifacts/w03/library-v1 保留，把定稿 v2 库（原 artifacts/w03/library（原 library-v2））改名为 artifacts/w03/library；改名不改内容，已加载的 .runtime 项目不受影响。

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

提交报告：当时 artifacts/w03/metric_test_report.json 为 v2 报告的副本，已被第三轮报告替换（见文末）。

## 规模数据回归

- 数据：materials/data/large，manifest id qinghe-w03-20260923-large（合成数据，会员 30000、订单 300000、门店 24、卡 38891；覆盖 2024-09-01 至 2026-09-01，与小样本相同，c19–c21 边界前提不变）。
- 期望：customer/w03/make_tests_large.py 复用 make_tests.py 的 21 条用例与 audit.py 的计算，只把小样本逐条备注换成“规模数据期望完全由审核程序计算”；c01、c10 锁定 qinghe-w03-20260923-large。生成 17 秒，未手写任何期望值。
- 项目：artifacts/w03/library（原 library-v2）（与小样本 v2 同一指标库，未针对规模数据修改）加载为 .runtime/qinghe-large-v1，加载 12 秒，未激活产品端。
- 环境：Microsoft Windows 11 家庭版 中文版 10.0.26300；Intel(R) Core(TM) Ultra 5 225H，14 核 14 线程；内存 31.5 GB；Python 3.11.9；duckdb 1.5.5；dbt-core 1.12.5；metricflow 0.213.0；模型 deepseek-v4-flash（超时 240 秒）。
- 结果：20/21，未通过仅 c17（期望 clarify，实际按成交门店直接作答），与小样本 v2 一致；报告 artifacts/w03/test-large-v1/metric_test_report.json，（第一轮，21 条）。
- 耗时：单次查询 0.031–0.093 秒，21 次查询合计 0.874 秒；含模型解析与回答的单例 6.0–22.0 秒，合计 305.5 秒。瓶颈在模型调用，不在查询引擎。
- 覆盖说明：规模数据 2026-05 有 23289 单有效订单，c14 在规模数据上不再覆盖“零分母为 null”，该分支只由小样本与注入检查 null_to_zero 覆盖。规模数据只验证数值与关联在大量记录下仍一致，不另做逐条人工核对。

### 规模数据补测：多种问法与定稿库路径

- 按任务书“同一问题多写几种问法”，在 customer/w03/make_tests_large.py 追加 7 条（x01 口语化净销售额、x02 换说法首购、x03 换说法月内复购、x04 简短问付费复购率、x05 按成交地区、x06 购买会员数按归属门店、x07 按日分组），期望仍由 audit.py 计算，共 28 条。
- 定稿库改名为 artifacts/w03/library 后，按“定稿库变了要用新项目路径重新加载”重新加载为 .runtime/qinghe-large-v2。
- 结果：27/28，未通过仅 c17；x06 说明 c13 的修复对其他订单类指标同样有效，x07 按日 31 组与审核一致。单次查询 0.031–0.093 秒，21 次以上查询合计 1.184 秒；单例端到端 2.9–20.8 秒，合计 336.7 秒（测试命令总计 342 秒）。环境同上。
- 报告：artifacts/w03/test-large-v2/metric_test_report.json（当时的副本已被第三轮替换，见文末）。

## 构建迭代记录（续：v3）与第三轮回归

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
