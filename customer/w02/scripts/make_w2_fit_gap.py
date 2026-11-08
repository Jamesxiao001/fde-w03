import json, copy, pathlib, sys
src = pathlib.Path("artifacts/w01/product_fit_gap.json")
dst = pathlib.Path("artifacts/w02/product_fit_gap.json")
patch = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
w1 = json.loads(src.read_text(encoding="utf-8-sig"))
w2 = copy.deepcopy(w1)
items = {x["id"]: x for x in w2["items"]}
for gid, ch in patch.items():
    if gid not in items:
        print("SKIP (not in W1):", gid); continue
    it = items[gid]
    old = (it["category"], it["evidence_status"], len(it["evidence"]))
    if "evidence_status" in ch: it["evidence_status"] = ch["evidence_status"]
    if "request" in ch: it["request"] = ch["request"]
    room = 20 - len(it["evidence"])
    it["evidence"] += ch["add"][:max(room, 0)]
    if len(ch["add"]) > room: print("WARN evidence limit 20:", gid)
    it["next_step"] = ch["next_step"]
    print(gid, "category", old[0], "| status", old[1], "->", it["evidence_status"], "| evidence", old[2], "->", len(it["evidence"]))
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(w2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("written", dst, "| W1 file unchanged")
