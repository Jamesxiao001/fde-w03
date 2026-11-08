import json
c = json.load(open("artifacts/w03/build-v3/catalog.json", encoding="utf-8"))
has = [x["id"] for x in c if any("门店" in k for k in x.get("constraints", []))]
print("带门店澄清约束的指标数", len(has), has)
for x in c:
    if x["id"] in ("net_sales_cents", "first_buyer_count", "monthly_buyer_count", "new_member_count", "monthly_paid_buyer_count"):
        print(x["id"], json.dumps(x.get("constraints"), ensure_ascii=False))
r = json.load(open("artifacts/w03/build-v3/response.json", encoding="utf-8"))
bm = r.get("business_model_usage") or []
print("business_model_usage 中提到门店的：", [json.dumps(u, ensure_ascii=False)[:300] for u in bm if "门店" in json.dumps(u, ensure_ascii=False)][:2])