WITH valid_orders AS (
  SELECT order_id, member_id, store_id, ordered_at
  FROM {{ ref('orders') }}
  WHERE status = 'paid' AND paid_cents - refund_cents > 0
),
ranked AS (
  SELECT v.*, ROW_NUMBER() OVER (PARTITION BY v.member_id ORDER BY v.ordered_at, v.order_id) AS valid_order_seq
  FROM valid_orders v
)
SELECT r.order_id,
       r.member_id,
       r.store_id,
       m.home_store_id,
       r.ordered_at,
       r.valid_order_seq
FROM ranked r
LEFT JOIN {{ ref('members') }} m ON r.member_id = m.member_id