WITH valid_orders AS (
  SELECT member_id,
         ordered_at,
         paid_cents - refund_cents AS net_sales_cents
  FROM {{ ref('orders') }}
  WHERE status = 'paid' AND paid_cents - refund_cents > 0
),
monthly_orders AS (
  SELECT member_id,
         CAST(date_trunc('month', ordered_at) AS DATE) AS activity_month,
         COUNT(*) AS valid_order_count,
         SUM(net_sales_cents) AS net_sales_cents
  FROM valid_orders
  GROUP BY member_id, CAST(date_trunc('month', ordered_at) AS DATE)
),
eligible_monthly AS (
  SELECT mo.member_id,
         mo.activity_month,
         mo.valid_order_count,
         mo.net_sales_cents
  FROM monthly_orders mo
  WHERE EXISTS (
    SELECT 1
    FROM {{ ref('cards') }} c
    WHERE c.member_id = mo.member_id
      AND c.card_type IN ('悦享年卡', '家庭季卡')
      AND c.valid_from <= CAST(date_trunc('month', mo.activity_month) + INTERVAL 1 MONTH - INTERVAL 1 DAY AS DATE)
      AND CAST(date_trunc('month', mo.activity_month) + INTERVAL 1 MONTH - INTERVAL 1 DAY AS DATE) < LEAST(c.valid_until, COALESCE(c.ended_at, c.valid_until))
  )
)
SELECT member_id || '|' || CAST(activity_month AS VARCHAR) AS monthly_paid_member_activity_id,
       member_id,
       activity_month,
       valid_order_count,
       net_sales_cents
FROM eligible_monthly