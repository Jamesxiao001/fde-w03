"""规模数据期望：复用 make_tests.py 的用例与 audit.py 的计算，只替换小样本逐条备注（对规模数据不适用），
并追加多种问法（x 开头）。期望全部由 audit.py 在该数据版本上逐记录计算。

用法：python make_tests_large.py 数据目录 数据版本ID 输出文件
"""
import sys
import make_tests as mt

NOTE = "规模数据未逐条手核，小样本备注不适用；期望完全由 audit.py 在该数据版本上逐记录计算。"
EXTRA = [
    ("x01-net-colloquial", "青禾 2026 年 8 月一共卖了多少钱？我说的是扣掉退款以后的净额。",
     ["net_sales_cents"], "2026-08-01", "2026-09-01", [], "order", "口语化问法，对应净销售额。", False),
    ("x02-first-buyer-alt", "2026 年 8 月有多少会员是在青禾第一次下有效订单的？",
     ["first_buyer_count"], "2026-08-01", "2026-09-01", [], "first", "换说法问观测期首购会员数。", False),
    ("x03-monthly-repeat-july", "2026 年 7 月青禾当月下了两单及以上有效订单的会员有多少个？",
     ["monthly_repeat_buyer_count"], "2026-07-01", "2026-08-01", [], "monthly", "换说法问月内复购会员数。", False),
    ("x04-paid-rate-alt", "看一下 2026 年 8 月青禾付费会员的复购率。",
     ["monthly_paid_repeat_rate"], "2026-08-01", "2026-09-01", [], "paid", "简短问法问月末付费会员复购率。", False),
    ("x05-valid-by-region", "2026 年 8 月青禾按成交门店所在地区统计的有效订单数是多少？",
     ["valid_order_count"], "2026-08-01", "2026-09-01", ["store__region"], "order", "成交门店属性分组。", False),
    ("x06-buyers-by-home-store", "2026 年 8 月青禾按会员归属门店统计的购买会员数是多少？",
     ["buyer_count"], "2026-08-01", "2026-09-01", ["home_store"], "order", "另一订单类指标按归属门店，检验 c13 修复不只对净销售额有效。", False),
    ("x07-net-by-day", "2026 年 8 月青禾每天的净销售额分别是多少？",
     ["net_sales_cents"], "2026-08-01", "2026-09-01", ["metric_time__day"], "order", "按日分组。", False),
]
mt.OK_CASES = [c[:7] + (NOTE,) + c[8:] for c in mt.OK_CASES] + [c[:7] + (NOTE + c[7],) + c[8:] for c in EXTRA]

if __name__ == "__main__":
    mt.main(*sys.argv[1:4])