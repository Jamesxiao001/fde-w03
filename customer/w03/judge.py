"""青禾 W03 判定程序：纯比较 expected 与 actual，不调用大模型、不另起查询。

比较顺序：状态 → 版本 → 意图 → 单位 → 列 → 行（按分组键对齐）→ 值。
- 意图：指标与分组按名字对齐（顺序无关），筛选按 (field, op, value) 排序后比较；时间严格相等。
- 列：允许列顺序不同，按列名映射；列名不可重复，集合必须一致。
- 行：以 group_by 各列值为键；拒绝缺组、多组、重复组；不分组时两边都只能有一行。
  时间分组键（metric_time__*）只比较日期部分 YYYY-MM-DD，其余分组键精确比较。
- 值：null 只等于 null；期望为整数时精确比较；期望为浮点时 rel_tol=1e-9、abs_tol=1e-7；
  布尔值、字符串、非有限浮点不能当作数值。
"""
import json
import math
import sys

STATUSES = {"ok", "clarify", "unsupported", "error"}
VERSION_KEYS = ("data_version", "data_sha256", "catalog_sha256")
REL_TOL, ABS_TOL = 1e-9, 1e-7


def is_num(x):
    return type(x) in (int, float) and (type(x) is int or math.isfinite(x))


def equal_value(want, got):
    if want is None:
        return got is None
    if not is_num(want) or not is_num(got):
        return False
    if type(want) is int:
        return got == want
    return math.isclose(want, got, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def norm_filters(fs):
    out = []
    for f in fs:
        v = f.get("value")
        v = sorted(v) if isinstance(v, list) else v
        out.append(json.dumps([f.get("field"), f.get("op"), v], ensure_ascii=False, sort_keys=True))
    return sorted(out)


def norm_key(col, v):
    if col.startswith("metric_time__") and isinstance(v, str):
        return v[:10]
    return v


def compare(expected, actual):
    diffs = []
    if not isinstance(actual, dict):
        return {"passed": False, "differences": [{"path": "actual", "rule": "not_object"}]}
    es, as_ = expected.get("status"), actual.get("status")
    if es not in STATUSES:
        diffs.append({"path": "expected.status", "rule": "unsupported_status", "expected": es})
    if as_ != es:
        diffs.append({"path": "status", "expected": es, "actual": as_})
    for k in VERSION_KEYS:
        if k in expected and actual.get(k) != expected[k]:
            diffs.append({"path": k, "expected": expected[k], "actual": actual.get(k)})
    if es != "ok" or diffs:
        return {"passed": not diffs, "differences": diffs}

    # 意图
    ei, ai = expected.get("intent") or {}, actual.get("intent")
    if not isinstance(ai, dict):
        diffs.append({"path": "intent", "rule": "missing"})
    else:
        for f in ("start", "end"):
            if ai.get(f) != ei.get(f):
                diffs.append({"path": f"intent.{f}", "expected": ei.get(f), "actual": ai.get(f)})
        for f in ("metrics", "group_by"):
            a, e = ai.get(f), ei.get(f)
            if not isinstance(a, list) or len(a) != len(set(map(str, a))) or sorted(map(str, a)) != sorted(map(str, e)):
                diffs.append({"path": f"intent.{f}", "expected": e, "actual": a})
        af = ai.get("filters")
        if not isinstance(af, list) or norm_filters(af) != norm_filters(ei.get("filters", [])):
            diffs.append({"path": "intent.filters", "expected": ei.get("filters"), "actual": af})
        extra = set(ai) - {"metrics", "start", "end", "group_by", "filters"}
        if extra:
            diffs.append({"path": "intent", "rule": "unexpected_fields", "actual": sorted(extra)})

    # 单位
    eu, au = expected.get("units") or {}, actual.get("units")
    if not isinstance(au, dict):
        diffs.append({"path": "units", "rule": "missing"})
    else:
        for m in sorted(set(eu) | set(au)):
            if eu.get(m) != au.get(m):
                diffs.append({"path": "units", "metric": m, "expected": eu.get(m), "actual": au.get(m)})

    # 列
    ec, ac = expected.get("columns") or [], actual.get("columns")
    if not isinstance(ac, list) or len(ac) != len(set(map(str, ac))) or set(map(str, ac)) != set(map(str, ec)):
        diffs.append({"path": "columns", "expected": ec, "actual": ac})
        return {"passed": False, "differences": diffs}

    # 行
    groups = list(ei.get("group_by", []))
    metrics = [c for c in ec if c not in groups]

    def index(rows, cols, side):
        if not isinstance(rows, list):
            diffs.append({"path": f"{side}.rows", "rule": "not_list"})
            return None
        out = {}
        for r in rows:
            if not isinstance(r, list) or len(r) != len(cols):
                diffs.append({"path": f"{side}.rows", "rule": "row_shape", "row": r})
                return None
            rec = dict(zip(cols, r))
            key = tuple(norm_key(g, rec[g]) for g in groups)
            if key in out:
                diffs.append({"path": f"{side}.rows", "rule": "duplicate_group", "group": list(key)})
                return None
            out[key] = rec
        return out

    want = index(expected.get("rows"), ec, "expected")
    got = index(actual.get("rows"), ac, "actual")
    if want is None or got is None:
        return {"passed": False, "differences": diffs}
    if not groups and (len(want) != 1 or len(got) != 1):
        diffs.append({"path": "rows", "rule": "ungrouped_must_have_one_row", "expected": len(want), "actual": len(got)})
    for k in sorted(set(want) - set(got), key=str):
        diffs.append({"path": "rows", "rule": "missing_group", "group": list(k)})
    for k in sorted(set(got) - set(want), key=str):
        diffs.append({"path": "rows", "rule": "extra_group", "group": list(k)})
    for k in sorted(set(want) & set(got), key=str):
        for m in metrics:
            w, g = want[k][m], got[k][m]
            if not equal_value(w, g):
                diffs.append({"path": "rows", "group": list(k), "metric": m, "expected": w, "actual": g,
                              "rule": "exact" if type(w) is int else ("null" if w is None else f"rel{REL_TOL}/abs{ABS_TOL}")})
    return {"passed": not diffs, "differences": diffs}


if __name__ == "__main__":
    data = json.load(sys.stdin)
    print(json.dumps(compare(data["expected"], data["actual"]), ensure_ascii=False))