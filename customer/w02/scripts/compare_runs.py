import json, pathlib, sys
def show(label, run_json):
    c = json.loads((pathlib.Path(run_json).parent / "candidates.json").read_text(encoding="utf-8"))
    claims, conflicts = c["claims"], c["conflicts"]
    by_id = {x["id"]: x for x in claims}
    print(f"===== {label}: {run_json}")
    print(f"候选 {len(claims)} 条，冲突组 {len(conflicts)} 组")
    for g in conflicts:
        print(f"\n[{g['id']}] {g['question'][:200]}")
        for cid in g["claim_ids"]:
            print(f"   - {cid}: {by_id.get(cid, {}).get('statement', '')[:80]}")
    print("\n关键字命中：")
    for k in ["120", "80 万", "80万", "复述", "不掌握", "授权"]:
        hits = [x["id"] for x in claims if k in json.dumps(x, ensure_ascii=False)]
        print(f"   {k}: {len(hits)} 条 {hits[:6]}")
    print()
for i, path in enumerate(sys.argv[1:], 1):
    show(f"运行{i}", path)
