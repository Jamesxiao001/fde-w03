import json
cs = {c["id"]: c for c in json.load(open("customer/w03/tests-large.json", encoding="utf-8"))}
for i in ("c01-order-counts", "c05-ratios-a", "c10-paid-a", "c14-zero-and-null", "c12-net-by-selling-store"):
    e = cs[i]["expected"]
    print(i, e.get("data_version", ""), e["columns"], json.dumps(e["rows"][:4], ensure_ascii=False), "共", len(e["rows"]), "行")