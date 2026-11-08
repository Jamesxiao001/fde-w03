import json, glob
d = json.load(open("artifacts/w03/library/dimension_check.json", encoding="utf-8"))
pm = d["per_metric"]
print("home_store 映射为 home_store 的指标：", sorted(m for m, v in pm.items() if v.get("home_store") == "home_store"))
print("home_store 映射为其他名字的：", {m: v.get("home_store") for m, v in pm.items() if v.get("home_store") != "home_store"})
for p in glob.glob("artifacts/w03/library/**/*.yml", recursive=True) + glob.glob("artifacts/w03/library/**/*.yaml", recursive=True):
    txt = open(p, encoding="utf-8").read()
    if "entities" in txt:
        print("=====", p)
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith(("- name:", "name:", "type:", "expr:", "entities:", "dimensions:", "measures:", "model:")) or "semantic_models" in s:
                print("  ", line.rstrip())