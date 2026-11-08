"""判定程序自检：从一份已核对的测试报告取真实 actual，每份只改一处，检查 judge.py 能否拒绝；
另做正向检查（原样通过、行序变化通过）与数值分支检查。改动均为合成注入，不是模型真实犯错。

用法：python inject.py 报告路径 输出目录
"""
import copy, json, os, sys
from judge import compare


def load_cases(report):
    data = json.load(open(report, encoding="utf-8"))
    return {c["id"]: c for c in data["cases"]}


def main(report, outdir):
    os.makedirs(outdir, exist_ok=True)
    cases = load_cases(report)
    base = cases["c01-order-counts"]
    grp = cases["c12-net-by-selling-store"]
    nul = cases["c14-zero-and-null"]
    rat = cases["c05-ratios-a"]
    for c in (base, grp, nul, rat):
        assert c["comparison"]["passed"], f"{c['id']} 原始结果未通过，不能作为注入底稿"

    checks = []

    def add(name, case, mutate, should_pass, note):
        exp, act = copy.deepcopy(case["expected"]), copy.deepcopy(case["actual"])
        mutate(act)
        res = compare(exp, act)
        ok = res["passed"] == should_pass
        rec = {"name": name, "base_case": case["id"], "note": note, "should_pass": should_pass,
               "comparison": res, "as_expected": ok}
        json.dump({"expected": exp, "actual": act, **rec}, open(os.path.join(outdir, f"{name}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        checks.append(rec)

    def set_(path, value):
        def f(a):
            t = a
            for k in path[:-1]:
                t = t[k]
            t[path[-1]] = value
        return f

    def col(a, name):
        return a["columns"].index(name)

    add("wrong_metric", base, set_(["intent", "metrics"], ["order_count", "paid_order_count", "valid_order_count", "refund_order_count"]), False, "错指标：cancelled_order_count 换成 refund_order_count，数字不变")
    add("wrong_date_same_value", base, set_(["intent", "end"], "2026-08-31"), False, "错日期：结束日改一天，数字不变")
    add("extra_filter", base, set_(["intent", "filters"], [{"field": "order__channel", "op": "eq", "value": "门店"}]), False, "错筛选：多出一条渠道筛选")
    add("wrong_group_by", grp, set_(["intent", "group_by"], ["home_store"]), False, "错分组：成交门店换成归属门店")
    add("missing_group", grp, lambda a: a["rows"].pop(), False, "漏组：删除一个门店分组行")
    add("duplicate_group", grp, lambda a: a["rows"].append(copy.deepcopy(a["rows"][0])), False, "重复组：重复追加同一门店一行")
    add("yuan_cents_confusion", base, set_(["units", "order_count"], "yuan"), False, "单位混淆：count 改成 yuan，数字不变")
    add("ratio_as_percent", rat, lambda a: a["rows"][0].__setitem__(col(a, "purchase_frequency"), a["rows"][0][col(a, "purchase_frequency")] * 100), False, "比例误作百分数：购买频次乘 100")
    add("null_to_zero", nul, lambda a: a["rows"][0].__setitem__(col(a, "avg_order_value"), 0), False, "null 改 0：零分母均额改成 0")
    add("tampered_value", base, lambda a: a["rows"][0].__setitem__(col(a, "valid_order_count"), a["rows"][0][col(a, "valid_order_count")] + 1), False, "篡改数值：有效订单数 +1")
    add("error_as_ok_with_rows", base, set_(["status"], "error"), False, "error 伪装：状态改为 error，保留正确行")
    add("wrong_data_version", base, set_(["data_version"], "qinghe-w03-20260923-large"), False, "错数据版本：锁版本用例换成规模数据版本")
    add("original_passes", base, lambda a: None, True, "原始正确结果")
    add("row_order_changed", grp, lambda a: a["rows"].reverse(), True, "只改变行顺序")
    add("int_vs_float_equal", base, lambda a: a["rows"][0].__setitem__(col(a, "valid_order_count"), float(a["rows"][0][col(a, "valid_order_count")])), True, "整数期望 27 对实际 27.0")
    add("bool_rejected", base, lambda a: a["rows"][0].__setitem__(col(a, "cancelled_order_count"), True), False, "数值位置放布尔值（期望 2）")
    add("string_number_rejected", base, lambda a: a["rows"][0].__setitem__(col(a, "order_count"), str(a["rows"][0][col(a, "order_count")])), False, "数值位置放数字字符串")

    big = compare({"status": "ok", "intent": {"metrics": ["m"], "start": "a", "end": "b", "group_by": [], "filters": []},
                   "columns": ["m"], "rows": [[1000000000]], "units": {"m": "cents"}},
                  {"status": "ok", "intent": {"metrics": ["m"], "start": "a", "end": "b", "group_by": [], "filters": []},
                   "columns": ["m"], "rows": [[1000000001]], "units": {"m": "cents"}})
    checks.append({"name": "big_int_off_by_one", "base_case": "合成输入", "note": "1000000000 对 1000000001 必须拒绝",
                   "should_pass": False, "comparison": big, "as_expected": big["passed"] is False})

    summary = {"report": report, "total": len(checks), "as_expected": sum(c["as_expected"] for c in checks),
               "checks": [{k: c[k] for k in ("name", "base_case", "should_pass", "as_expected")} |
                          {"differences": [d.get("path") if isinstance(d, dict) else d for d in c["comparison"]["differences"]]}
                          for c in checks]}
    json.dump(summary, open(os.path.join(outdir, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"total": summary["total"], "as_expected": summary["as_expected"]}, ensure_ascii=False))
    for c in summary["checks"]:
        print(("OK  " if c["as_expected"] else "FAIL"), c["name"], c["differences"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])