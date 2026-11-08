p = "customer/w03/build-metrics/SKILL.md"
s = open(p, encoding="utf-8-sig").read()
anchor = "dimensions[].name 只写局部名。确实缺少关系依据时列未决，不凭空连接。"
assert s.count(anchor) == 1, s.count(anchor)
add = anchor + "\n   实体查询 ID 只对应事实模型上直接声明的实体（一跳）。经另一实体转接得到的是多跳名（例如订单经会员到归属门店为 member__home_store），不等于目标 ID home_store，查询会失败。某事实模型的指标需要按某个实体目标查询、而该实体只挂在关联对象上时，若主体到关联对象为多对一（每行只对应一个关联对象，不放大行数），在该事实模型的派生 SQL 中关联带出该外键列（例如订单关联会员带出 home_store_id），并在该模型上直接声明同名 foreign 实体；派生模型名不得与接入表重名。材料明确不支持按门店或渠道拆分的指标，不为其补门店实体。"
s = s.replace(anchor, add)
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s.encode("utf-8")))