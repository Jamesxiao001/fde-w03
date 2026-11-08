p = "docs/w03/metric_decisions.md"
s = open(p, encoding="utf-8-sig").read()
old = "artifacts/w03/library 保留为 v1 库，v2 使用 library-v2。"
assert s.count(old) == 1
s = s.replace(old, "之后为与任务书路径一致，把 v1 库改名为 artifacts/w03/library-v1 保留，把定稿 v2 库（原 artifacts/w03/library-v2）改名为 artifacts/w03/library；改名不改内容，已加载的 .runtime 项目不受影响。")
s = s.replace("artifacts/w03/library-v2", "artifacts/w03/library（原 library-v2）")
open(p, "w", encoding="utf-8").write(s)
print("ok", s.count("library-v2"))