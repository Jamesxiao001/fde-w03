import json, glob, os
root = "artifacts/w03/build-v2b"
print("文件：", sorted(os.listdir(root)))
for p in sorted(glob.glob(f"{root}/**/*check*.json", recursive=True)):
    d = json.load(open(p, encoding="utf-8"))
    print(os.path.relpath(p, root), "passed =", d.get("passed") if isinstance(d, dict) else "?")
src = None
for p in sorted(glob.glob(f"{root}/**/*.json", recursive=True)):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    if isinstance(d, dict) and "semantic_models" in d and "model_sql" in d:
        src = d; print("来源：", os.path.relpath(p, root)); break
if src:
    for m in src["semantic_models"]:
        print("=====", m["name"], "|", m.get("model"), "| 实体：", [(e["name"], e["type"], e.get("expr")) for e in m.get("entities", [])])
    for k, v in (src.get("model_sql") or {}).items():
        print("----- SQL", k, "\n", v[:700])
    print("grain_keys：", json.dumps(src.get("grain_keys"), ensure_ascii=False))
dc = glob.glob(f"{root}/**/dimension_check.json", recursive=True)
if dc:
    pm = json.load(open(dc[0], encoding="utf-8")).get("per_metric", {})
    for m in ("net_sales_cents", "first_buyer_count", "monthly_buyer_count", "monthly_paid_buyer_count", "new_member_count"):
        print(m, "映射：", json.dumps(pm.get(m), ensure_ascii=False))