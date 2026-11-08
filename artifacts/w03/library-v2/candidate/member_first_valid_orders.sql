WITH valid_orders AS (
  SELECT order_id, member_id, store_id, ordered_at, paid_cents, refund_cents
  FROM {{ ref('orders') }}
  WHERE status = 'paid' AND paid_cents - refund_cents > 0
),
ranked AS (
  SELECT v.*, ROW_NUMBER() OVER (PARTITION BY v.member_id ORDER BY v.ordered_at, v.order_id) AS rn
  FROM valid_orders v
)
SELECT r.order_id AS first_order_id,
       r.member_id,
       r.ordered_at AS first_ordered_at,
       r.paid_cents - r.refund_cents AS first_order_net_sales_cents,
       r.store_id,
       m.home_store_id
FROM ranked r
LEFT JOIN {{ ref('members') }} m ON r.member_id = m.member_id
WHERE r.rn = 1