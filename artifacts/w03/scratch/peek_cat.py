import json
c = json.load(open("artifacts/w03/library/catalog.json", encoding="utf-8"))
print("条目数", len(c), "| 第一条的键：", list(c[0].keys()))
for it in c:
    if it.get("id") == "net_sales_cents":
        print(json.dumps(it, ensure_ascii=False, indent=1)[:2500])