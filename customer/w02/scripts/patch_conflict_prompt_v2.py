import pathlib, sys
p = pathlib.Path("platform/fde_product/interview_extraction.py")
s = p.read_text(encoding="utf-8")
add = "多个角色说出相同或一致的说法、或都表示需要核实，属于相同说法或共同未知，不构成分歧；一方给出带口径限定的数字、另一方表示没有可确认统计，也不构成分歧。"
if add in s:
    sys.exit("第二句已经加过了。")
anchor = "不同角色各自说明自己掌握或不掌握的范围，也不构成分歧。"
if s.count(anchor) != 1:
    sys.exit("没有找到第一句规则，请先运行 patch_conflict_prompt.py。")
s = s.replace(anchor, anchor + add)
p.write_text(s, encoding="utf-8", newline="\n")
print("已补充第二句规则。")
