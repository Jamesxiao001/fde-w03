"""由独立审核程序 audit.py 生成 tests.json 的期望（运行前生成并冻结，不读取任何 Agent 实际结果）。

用法：python make_tests.py 数据目录 数据版本ID 输出文件
"""
import json, sys
from audit import compute

UNITS = {  # 依据 01/02/03/04 材料中写明的单位与分子分母量纲
    **{m: "count" for m in ["order_count", "paid_order_count", "valid_order_count", "cancelled_order_count",
                            "refund_order_count", "partial_refund_order_count", "full_refund_order_count",
                            "buyer_count", "refund_buyer_count", "selling_store_count", "new_member_count",
                            "first_buyer_count", "first_order_count", "repeat_order_count", "monthly_buyer_count",
                            "monthly_repeat_buyer_count", "monthly_paid_buyer_count", "monthly_paid_order_count",
                            "monthly_paid_repeat_buyer_count"]},
    **{m: "cents" for m in ["payment_cents", "refund_cents", "net_sales_cents", "gross_cents", "discount_cents",
                            "first_order_sales_cents", "monthly_paid_sales_cents"]},
    **{m: "ratio" for m in ["refund_amount_rate", "cancel_rate", "refund_order_rate", "discount_rate",
                            "monthly_repeat_rate", "monthly_paid_repeat_rate"]},
    "valid_order_items": "items", "avg_order_value": "cents_per_order", "avg_buyer_value": "cents_per_member",
    "purchase_frequency": "orders_per_member", "items_per_order": "items_per_order",
    "monthly_paid_avg_order_value": "cents_per_order",
}
SRC = {"order": "01_订单日报说明、02_财务邮件（有效订单 = paid 且实付减累计退款 > 0，退款按原订单日期归属）",
       "ratio": "02_财务邮件（分子指标 / 分母指标，零分母为 null）",
       "member": "03_会员运营周报（按注册日期 registered_at）",
       "first": "03_会员运营周报（全覆盖期有效订单按日期、同日按订单号排序，再按窗口筛选）",
       "monthly": "03_会员运营周报（同一自然月账户有效订单 ≥1 / ≥2，按月分别列）",
       "paid": "04_本期统计确认邮件 + business_model 3.1–3.4（月末最后一天有一张悦享年卡或家庭季卡满足 生效日 ≤ D < min(到期日, 提前终止日)，再统计当月全部有效订单）"}

# (id, 问题, 指标, 开始, 结束, 分组, 依据键, 补充说明, 是否锁版本)
OK_CASES = [
    ("c01-order-counts", "2026 年 8 月青禾的创建订单数、支付订单数、有效订单数和取消订单数分别是多少？",
     ["order_count", "paid_order_count", "valid_order_count", "cancelled_order_count"], "2026-08-01", "2026-09-01", [], "order",
     "8 月 32 单：取消 O0000005、O0000039；全额退款 O0000004、O0000012、O0000040 计支付不计有效。", True),
    ("c02-refund-orders", "2026 年 8 月青禾的退款订单数、部分退款订单数和全额退款订单数各是多少？",
     ["refund_order_count", "partial_refund_order_count", "full_refund_order_count"], "2026-08-01", "2026-09-01", [], "order",
     "部分退款 O0000003（实付 9000 退 2000）；全额退款 O0000004、O0000012、O0000040。", False),
    ("c03-amounts", "2026 年 8 月青禾的实付金额、退款金额、净销售额、支付订单原价金额和优惠金额分别是多少？",
     ["payment_cents", "refund_cents", "net_sales_cents", "gross_cents", "discount_cents"], "2026-08-01", "2026-09-01", [], "order",
     "只计 paid；优惠 = 原价 − 实付，退款不冲减优惠。", False),
    ("c04-distinct", "2026 年 8 月青禾的购买会员数、退款会员数、成交门店数和有效订单商品件数分别是多少？",
     ["buyer_count", "refund_buyer_count", "selling_store_count", "valid_order_items"], "2026-08-01", "2026-09-01", [], "order",
     "购买会员按有效订单的 CRM 账户去重；成交门店按有效订单 store_id 去重（S03 8 月无订单）。", False),
    ("c05-ratios-a", "2026 年 8 月青禾的有效订单均额、购买会员人均消费、购买频次和单均商品件数是多少？",
     ["avg_order_value", "avg_buyer_value", "purchase_frequency", "items_per_order"], "2026-08-01", "2026-09-01", [], "ratio",
     "100300/27、100300/15、27/15、33/27。", False),
    ("c06-ratios-b", "2026 年 8 月青禾的退款金额占比、取消率、退款订单率和优惠率是多少？",
     ["refund_amount_rate", "cancel_rate", "refund_order_rate", "discount_rate"], "2026-08-01", "2026-09-01", [], "ratio",
     "18750/119050、2/32、4/30、5200/124250。", False),
    ("c07-new-members-home", "2026 年 7 月青禾按会员归属门店统计的注册会员数是多少？",
     ["new_member_count"], "2026-07-01", "2026-08-01", ["home_store"], "member",
     "M00009–M00020 于 2026-07-01 注册，归属 S01、S02 各 6 个。", False),
    ("c08-first-repeat", "2026 年 8 月青禾的观测期首购会员数、观测期首单净销售额、观测期首单数和观测期后续购买订单数分别是多少？",
     ["first_buyer_count", "first_order_sales_cents", "first_order_count", "repeat_order_count"], "2026-08-01", "2026-09-01", [], "first",
     "首单在 8 月的为 M00007、M00009、M00015、M00016、M00018；M00001 首单 2024-09-01，8 月两单计后续，用来区分“全历史排序”与“窗口内排序”；M00003、M00017 只有全退订单不算首购。", False),
    ("c09-monthly-by-month", "青禾 2026 年 7 月和 8 月的月内购买会员数、月内复购会员数和月内复购率，按月分别列出。",
     ["monthly_buyer_count", "monthly_repeat_buyer_count", "monthly_repeat_rate"], "2026-07-01", "2026-09-01", ["metric_time__month"], "monthly",
     "按自然月分别计；不跨月加总人数。", False),
    ("c10-paid-a", "2026 年 8 月青禾月末付费会员购买人数、月末付费会员有效订单数和月末付费会员净销售额分别是多少？",
     ["monthly_paid_buyer_count", "monthly_paid_order_count", "monthly_paid_sales_cents"], "2026-08-01", "2026-09-01", [], "paid",
     "8 月末有资格且当月有效购买的为 M00001（两卡只算一人）、M00007、M00013（08-31 生效计入）、M00012（09-01 终止仍有效）、M00014（换卡）、M00016；M00004、M00010（08-31 到期）、M00005、M00011（08-31 终止）、M00002（联名卡）、M00008、M00020（体验卡）、M00015（金卡无卡）均不计。", True),
    ("c11-paid-b", "2026 年 8 月青禾月末付费会员复购人数、月末付费会员复购率和月末付费会员订单均额是多少？",
     ["monthly_paid_repeat_buyer_count", "monthly_paid_repeat_rate", "monthly_paid_avg_order_value"], "2026-08-01", "2026-09-01", [], "paid",
     "复购（当月 ≥2 笔有效）为 M00001、M00012、M00013、M00014；复购率 4/6；订单均额 47550/10。", False),
    ("c12-net-by-selling-store", "2026 年 7 月青禾按订单成交门店统计的净销售额是多少？",
     ["net_sales_cents"], "2026-07-01", "2026-08-01", ["store"], "order",
     "与 c13 同月同指标，只换门店角色：多名会员归属 S02 但 7 月在 S01 下单，两种分组结果不同，可区分关联是否接对。", False),
    ("c13-net-by-home-store", "2026 年 7 月青禾按会员归属门店统计的净销售额是多少？",
     ["net_sales_cents"], "2026-07-01", "2026-08-01", ["home_store"], "order",
     "见 c12，归属门店来自 members.home_store_id。", False),
    ("c14-zero-and-null", "2026 年 5 月青禾的有效订单数和有效订单均额是多少？",
     ["valid_order_count", "avg_order_value"], "2026-05-01", "2026-06-01", [], "ratio",
     "覆盖期内 5 月无订单：订单数为已知的 0，均额零分母为 null，不能写成 0。", False),
    ("c15-paid-july", "2026 年 7 月青禾月末付费会员购买人数是多少？",
     ["monthly_paid_buyer_count"], "2026-07-01", "2026-08-01", [], "paid",
     "7 月末判定日为 2026-07-31：M00005（08-31 终止）、M00010（08-31 到期）、M00011（08-31 终止）、M00019（08-30 到期）7 月末仍有效、8 月末无效，另有 M00012、M00014；用来检查判定日是否随月份变化。", False),
    ("c16-paid-synonym", "8 月份（2026 年）青禾付费会员里在当月下过有效订单的有几个账户？",
     ["monthly_paid_buyer_count"], "2026-08-01", "2026-09-01", [], "paid",
     "c10 的换说法，期望意图与数值相同。", False),
]
NON_OK = [
    ("c17-ambiguous-store", "按门店看青禾 2026 年 7 月的净销售额是多少？", "clarify",
     "“按门店”未讲清成交门店还是会员归属门店；小林 MSG-04495 确认须先讲清，运营默认用法未定，期望先澄清。"),
    ("c18-no-period", "青禾的有效订单数是多少？", "clarify", "未给时间范围，需先确认期间。"),
    ("c19-out-of-coverage", "2026 年 9 月青禾的净销售额是多少？", "unsupported",
     "数据覆盖 2024-09-01 至 2026-09-01（不含），9 月超出覆盖，不能当作 0。"),
    ("c20-paid-half-month", "2026 年 8 月 1 日到 8 月 15 日青禾月末付费会员购买人数是多少？", "unsupported",
     "04 邮件：付费 6 项只支持完整自然月。"),
    ("c21-paid-by-store", "2026 年 8 月青禾按成交门店拆分的月末付费会员购买人数是多少？", "unsupported",
     "04 邮件：暂不按门店或渠道拆付费会员月报。"),
]


def main(folder, data_version, out):
    cases = []
    for cid, q, metrics, s, e, g, src, note, lock in OK_CASES:
        cols, rows = compute(folder, metrics, s, e, g)
        exp = {"status": "ok", "intent": {"metrics": metrics, "start": s, "end": e, "group_by": g, "filters": []},
               "columns": cols, "rows": rows, "units": {m: UNITS[m] for m in metrics}}
        if lock:
            exp["data_version"] = data_version
        cases.append({"id": cid, "question": q, "expected": exp,
                      "expected_source": f"独立审核程序 customer/w03/audit.py 在 {data_version} 的四张 CSV 上逐记录计算，"
                                         f"口径依据 {SRC[src]}；时间 [{s}, {e})。{note}"})
    for cid, q, status, note in NON_OK:
        cases.append({"id": cid, "question": q, "expected": {"status": status}, "expected_source": note})
    covered = {m for c in cases if c["expected"]["status"] == "ok" for m in c["expected"]["intent"]["metrics"]}
    missing = sorted(set(UNITS) - covered)
    assert not missing, f"未覆盖指标：{missing}"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(json.dumps({"cases": len(cases), "metrics_covered": len(covered)}, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])