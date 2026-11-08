import json
d = json.load(open("artifacts/w03/library/dimension_check.json", encoding="utf-8"))
print("顶层", list(d.keys()) if isinstance(d, dict) else type(d))
s = json.dumps(d, ensure_ascii=False, indent=1)
print(s[:1500])
print("......")
i = s.find('"home_store": "home_store"')
print(s[max(0, i - 1500): i + 600])