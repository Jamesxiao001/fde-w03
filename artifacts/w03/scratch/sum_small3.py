import json
d = json.load(open("artifacts/w03/test-small-v3/metric_test_report.json", encoding="utf-8"))
print("passed", d["passed"], "/", d["total"], "complete", d["complete"])
qs = []
for c in d["cases"]:
    a = c["actual"]
    qs.append((c["id"], a.get("status"), a.get("seconds"), a.get("elapsed_seconds")))
    if not c["comparison"]["passed"]:
        print("FAIL", c["id"], json.dumps(c["comparison"]["differences"], ensure_ascii=False)[:500])
print("每例：id / 状态 / 查询秒 / 总秒")
for q in qs:
    print(*q)
sec = [q[2] for q in qs if isinstance(q[2], (int, float))]
el = [q[3] for q in qs if isinstance(q[3], (int, float))]
print("查询秒 最大", max(sec), "合计", round(sum(sec), 3), "| 总秒 最大", max(el), "合计", round(sum(el), 1))