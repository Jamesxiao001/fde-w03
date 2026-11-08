import json, pathlib, sys
for p in sys.argv[1:]:
    d = pathlib.Path(p).parent
    s = json.loads((d / "settings.json").read_text(encoding="utf-8"))
    req = json.loads((d / "request.json").read_text(encoding="utf-8"))
    user = next(m for m in req["messages"] if m["role"] == "user")
    bm = json.loads(user["content"])["business_model"]
    ans = json.loads((d / "answer.json").read_text(encoding="utf-8"))["answer"]
    print("=" * 60)
    print("提供业务模型:", s["include_knowledge"], "| 运行:", p)
    print("请求中业务模型字数:", len(bm), "| 含“120 万”:", "120 万" in bm, "| 含“03411”:", "03411" in bm)
    print("--- 回答 ---")
    print(ans)
