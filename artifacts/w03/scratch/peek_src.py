import json, glob
for p in glob.glob("artifacts/w03/build-v2/**/source_check.json", recursive=True):
    d = json.load(open(p, encoding="utf-8"))
    print("文件", p, "顶层", list(d.keys()) if isinstance(d, dict) else type(d))
    items = d.get("items") or d.get("failures") or d.get("errors") or d
    bad = [x for x in items if isinstance(x, dict) and not x.get("passed", x.get("exact", True))] if isinstance(items, list) else items
    print("未通过条数", len(bad) if isinstance(bad, list) else "?")
    print(json.dumps(bad, ensure_ascii=False, indent=1)[:3000])