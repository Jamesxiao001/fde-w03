p = "customer/w03/build-metrics/SKILL.md"
s = open(p, encoding="utf-8-sig").read()
a1 = "限制不能只写在 description 里。"
assert s.count(a1) == 1, s.count(a1)
s = s.replace(a1, a1 + "\n\n业务模型写明某个查询维度存在多种角色、提问时须先讲清是哪一种的（例如“按门店”须先讲清成交门店还是会员归属门店），对同时支持这几种角色分组的每项指标，在 constraints 中写一条：用户只用笼统说法、没有指明角色时须先澄清，不默认任何一种；明确指明角色时按所指角色查询。该约束记入 business_model_usage，quote 逐字取业务模型原文。只为确实同时支持这些角色分组的指标添加。")
a2 = "不把两段话拼成一句，不把自己的解释写成引用。"
assert s.count(a2) == 1, s.count(a2)
s = s.replace(a2, a2 + "逐字包括原文中的 Markdown 符号（如加粗的 **）、标点和空格。")
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s.encode("utf-8")))