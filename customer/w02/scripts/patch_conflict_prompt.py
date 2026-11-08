import pathlib, shutil, sys
p = pathlib.Path("platform/fde_product/interview_extraction.py")
s = p.read_text(encoding="utf-8")
rule = "一方建议去找另一角色了解某事、而该角色表示不掌握，属于转介未落实的共同未知，不构成分歧；不同角色各自说明自己掌握或不掌握的范围，也不构成分歧。"
if rule in s:
    sys.exit("规则已经加过了，无需重复执行。")
old = "不同条件下的说法不直接裁定谁对谁错，列明需核实的条件。\n\"\"\""
if s.count(old) != 1:
    sys.exit("没有找到唯一的修改位置，未做任何修改。")
pathlib.Path("backup").mkdir(exist_ok=True)
shutil.copy2(p, "backup/interview_extraction.py.v1")
s = s.replace(old, "不同条件下的说法不直接裁定谁对谁错，列明需核实的条件。\n" + rule + "\n\"\"\"")
p.write_text(s, encoding="utf-8", newline="\n")
print("已修改 CONFLICT_PROMPT，原文件备份在 backup\\interview_extraction.py.v1")
