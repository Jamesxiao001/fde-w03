"""青禾 W03 独立审核程序：直接读四张 CSV，按客户材料与业务模型逐记录计算期望。

不导入指标库、不读 metrics.yml 或生成的 SQL、不调用大模型。
口径依据：01_订单日报说明、02_财务邮件、03_会员运营周报、04_本期统计确认邮件、
docs/w03/business_model.md 3.1–3.4（付费资格）。
用法：python audit.py 数据目录 指标1,指标2 开始日 结束日 [分组1,分组2]
"""
import csv, json, sys, calendar
from datetime import date
from collections import defaultdict

PAID_CARD_TYPES = {"悦享年卡", "家庭季卡"}          # 小林 MSG-04489
ORDER_METRICS = ["order_count", "paid_order_count", "valid_order_count", "cancelled_order_count",
                 "refund_order_count", "partial_refund_order_count", "full_refund_order_count",
                 "payment_cents", "refund_cents", "net_sales_cents", "gross_cents", "discount_cents",
                 "buyer_count", "refund_buyer_count", "selling_store_count", "valid_order_items"]
RATIOS = {"avg_order_value": ("net_sales_cents", "valid_order_count"),
          "avg_buyer_value": ("net_sales_cents", "buyer_count"),
          "purchase_frequency": ("valid_order_count", "buyer_count"),
          "refund_amount_rate": ("refund_cents", "payment_cents"),
          "cancel_rate": ("cancelled_order_count", "order_count"),
          "refund_order_rate": ("refund_order_count", "paid_order_count"),
          "discount_rate": ("discount_cents", "gross_cents"),
          "items_per_order": ("valid_order_items", "valid_order_count"),
          "monthly_repeat_rate": ("monthly_repeat_buyer_count", "monthly_buyer_count"),
          "monthly_paid_repeat_rate": ("monthly_paid_repeat_buyer_count", "monthly_paid_buyer_count"),
          "monthly_paid_avg_order_value": ("monthly_paid_sales_cents", "monthly_paid_order_count")}
FIRST_METRICS = ["first_buyer_count", "first_order_sales_cents", "first_order_count", "repeat_order_count"]
MONTHLY = ["monthly_buyer_count", "monthly_repeat_buyer_count"]
PAID = ["monthly_paid_buyer_count", "monthly_paid_order_count", "monthly_paid_sales_cents",
        "monthly_paid_repeat_buyer_count"]


def d(s):
    return date.fromisoformat(s) if s else None


def load(folder):
    rd = lambda n: list(csv.DictReader(open(f"{folder}/{n}.csv", encoding="utf-8")))
    orders = rd("orders")
    for o in orders:
        for k in ("gross_cents", "paid_cents", "refund_cents", "quantity"):
            o[k] = int(o[k])
        o["date"] = d(o["ordered_at"])
        o["valid"] = o["status"] == "paid" and o["paid_cents"] - o["refund_cents"] > 0   # 02 财务邮件
    members = {m["member_id"]: m for m in rd("members")}
    stores = {s["store_id"]: s for s in rd("stores")}
    cards = defaultdict(list)
    for c in rd("cards"):
        cards[c["member_id"]].append(c)
    return orders, members, stores, cards


def card_valid_on(c, day):
    # 陈姐 MSG-04500、04502：生效日当天有效；到期日、提前终止日当天起无效；二者取先到；终止为空不代表无限期
    end = d(c["valid_until"])
    if c["ended_at"]:
        end = min(end, d(c["ended_at"]))
    return d(c["valid_from"]) <= day < end


def paid_qualified(cards, member_id, day):
    # 按账户判定：名下任一张计入卡在判定日有效即有资格（小林 04493、陈姐 04504）
    return any(c["card_type"] in PAID_CARD_TYPES and card_valid_on(c, day) for c in cards.get(member_id, []))


def group_key(o, group_by, members, stores, kind):
    key = []
    for g in group_by:
        if g == "store":
            key.append(o["store_id"])
        elif g == "store__store_name":
            key.append(stores[o["store_id"]]["store_name"])
        elif g == "store__region":
            key.append(stores[o["store_id"]]["region"])
        elif g == "home_store":
            key.append(members[o["member_id"]]["home_store_id"])
        elif g == "home_store__store_name":
            key.append(stores[members[o["member_id"]]["home_store_id"]]["store_name"])
        elif g == "home_store__region":
            key.append(stores[members[o["member_id"]]["home_store_id"]]["region"])
        elif g == "order__channel":
            key.append(o["channel"])
        elif g == "member__tier":
            key.append(members[o["member_id"]]["tier"])
        elif g == "metric_time__month":
            key.append(o["date"].replace(day=1).isoformat())
        elif g == "metric_time__day":
            key.append(o["date"].isoformat())
        else:
            raise ValueError(f"审核程序不支持分组 {g}")
    return tuple(key)


def order_bucket(rows):
    paid = [o for o in rows if o["status"] == "paid"]
    valid = [o for o in rows if o["valid"]]
    refunded = [o for o in paid if o["refund_cents"] > 0]
    return {
        "order_count": len(rows),
        "paid_order_count": len(paid),
        "valid_order_count": len(valid),
        "cancelled_order_count": sum(o["status"] == "cancelled" for o in rows),
        "refund_order_count": len(refunded),
        "partial_refund_order_count": sum(0 < o["refund_cents"] < o["paid_cents"] for o in paid),
        "full_refund_order_count": sum(o["paid_cents"] > 0 and o["refund_cents"] == o["paid_cents"] for o in paid),
        "payment_cents": sum(o["paid_cents"] for o in paid),
        "refund_cents": sum(o["refund_cents"] for o in paid),
        "net_sales_cents": sum(o["paid_cents"] - o["refund_cents"] for o in paid),
        "gross_cents": sum(o["gross_cents"] for o in paid),
        "discount_cents": sum(o["gross_cents"] - o["paid_cents"] for o in paid),
        "buyer_count": len({o["member_id"] for o in valid}),
        "refund_buyer_count": len({o["member_id"] for o in refunded}),
        "selling_store_count": len({o["store_id"] for o in valid}),
        "valid_order_items": sum(o["quantity"] for o in valid),
    }


def compute(folder, metrics, start, end, group_by):
    orders, members, stores, cards = load(folder)
    s, e = d(start), d(end)
    win = [o for o in orders if s <= o["date"] < e]
    buckets = defaultdict(dict)

    def put(key, name, value):
        buckets[key][name] = value

    need = set(metrics) | {x for m in metrics if m in RATIOS for x in RATIOS[m]}
    if need & set(ORDER_METRICS):
        groups = defaultdict(list)
        for o in win:
            groups[group_key(o, group_by, members, stores, "order")].append(o)
        for k, rows in groups.items():
            for name, v in order_bucket(rows).items():
                put(k, name, v)
    if need & set(FIRST_METRICS):
        # 03 运营周报：全覆盖期内按日期、同日按订单号排序，再按窗口筛选
        ranked = defaultdict(list)
        for o in sorted([o for o in orders if o["valid"]], key=lambda o: (o["date"], o["order_id"])):
            ranked[o["member_id"]].append(o)
        groups = defaultdict(list)
        for seq in ranked.values():
            for i, o in enumerate(seq, 1):
                if s <= o["date"] < e:
                    groups[group_key(o, group_by, members, stores, "order")].append((i, o))
        for k, rows in groups.items():
            put(k, "first_buyer_count", len({o["member_id"] for i, o in rows if i == 1}))
            put(k, "first_order_sales_cents", sum(o["paid_cents"] - o["refund_cents"] for i, o in rows if i == 1))
            put(k, "first_order_count", sum(1 for i, o in rows if i == 1))
            put(k, "repeat_order_count", sum(1 for i, o in rows if i >= 2))
    if need & (set(MONTHLY) | set(PAID)):
        # 03 运营周报、04 统计确认邮件：自然月 × 账户
        mm = defaultdict(list)
        for o in win:
            if o["valid"]:
                mm[(o["date"].replace(day=1), o["member_id"])].append(o)
        groups = defaultdict(lambda: defaultdict(int))
        for (month, member), rows in mm.items():
            k = tuple(month.isoformat() if g == "metric_time__month" else None for g in group_by)
            g = groups[k]
            g["monthly_buyer_count"] += 1
            g["monthly_repeat_buyer_count"] += len(rows) >= 2
            month_end = month.replace(day=calendar.monthrange(month.year, month.month)[1])
            if paid_qualified(cards, member, month_end):
                g["monthly_paid_buyer_count"] += 1
                g["monthly_paid_order_count"] += len(rows)
                g["monthly_paid_sales_cents"] += sum(o["paid_cents"] - o["refund_cents"] for o in rows)
                g["monthly_paid_repeat_buyer_count"] += len(rows) >= 2
        for k, g in groups.items():
            for name in MONTHLY + PAID:
                put(k, name, g[name])
    if "new_member_count" in need:
        groups = defaultdict(int)
        for m in members.values():
            rd_ = d(m["registered_at"])
            if s <= rd_ < e:
                key = []
                for g in group_by:
                    if g == "home_store":
                        key.append(m["home_store_id"])
                    elif g == "member__tier":
                        key.append(m["tier"])
                    elif g == "metric_time__month":
                        key.append(rd_.replace(day=1).isoformat())
                    else:
                        raise ValueError(f"注册会员数不支持分组 {g}")
                groups[tuple(key)] += 1
        for k, v in groups.items():
            put(k, "new_member_count", v)

    if not group_by and () not in buckets:
        buckets[()] = {}
    rows = []
    for k in sorted(buckets, key=lambda x: tuple(str(i) for i in x)):
        b = buckets[k]
        row = list(k)
        for m in metrics:
            if m in RATIOS:
                num, den = (b.get(x, 0) for x in RATIOS[m])
                row.append(None if den == 0 else num / den)
            else:
                row.append(b.get(m, 0))
        rows.append(row)
    return list(group_by) + list(metrics), rows


if __name__ == "__main__":
    folder, metrics, start, end = sys.argv[1], sys.argv[2].split(","), sys.argv[3], sys.argv[4]
    group_by = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[5] else []
    cols, rows = compute(folder, metrics, start, end, group_by)
    print(json.dumps({"columns": cols, "rows": rows}, ensure_ascii=False))