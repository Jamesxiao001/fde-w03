WITH valid_orders AS (
  SELECT member_id, ordered_at, paid_cents - refund_cents AS net_sales_cents
  FROM {{ ref('orders') }}
  WHERE status = 'paid' AND paid_cents - refund_cents > 0
),
monthly AS (
  SELECT member_id,
         CAST(date_trunc('month', ordered_at) AS DATE) AS activity_month,
         COUNT(*) AS valid_order_count,
         SUM(net_sales_cents) AS net_sales_cents
  FROM valid_orders
  GROUP BY member_id, CAST(date_trunc('month', ordered_at) AS DATE)
)
SELECT member_id || '|' || CAST(activity_month AS VARCHAR) AS monthly_member_activity_id,
       member_id,
       activity_month,
       valid_order_count,
       net_sales_cents
FROM monthly