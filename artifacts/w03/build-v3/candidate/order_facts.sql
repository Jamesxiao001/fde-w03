WITH valid_orders AS (
  SELECT
    o.order_id,
    o.member_id,
    o.ordered_at,
    ROW_NUMBER() OVER (PARTITION BY o.member_id ORDER BY o.ordered_at, o.order_id) AS valid_order_rank
  FROM {{ ref('orders') }} o
  WHERE o.status = 'paid'
    AND o.paid_cents - o.refund_cents > 0
),
valid_order_months AS (
  SELECT
    member_id,
    CAST(date_trunc('month', ordered_at) AS DATE) AS stat_period_start,
    COUNT(*) AS member_month_valid_order_count
  FROM valid_orders
  GROUP BY member_id, CAST(date_trunc('month', ordered_at) AS DATE)
),
eligible_months AS (
  SELECT DISTINCT
    v.member_id,
    CAST(date_trunc('month', v.ordered_at) AS DATE) AS stat_period_start
  FROM valid_orders v
  WHERE EXISTS (
    SELECT 1
    FROM {{ ref('cards') }} c
    WHERE c.member_id = v.member_id
      AND c.card_type IN ('悦享年卡', '家庭季卡')
      AND c.valid_from <= last_day(CAST(date_trunc('month', v.ordered_at) AS DATE))
      AND last_day(CAST(date_trunc('month', v.ordered_at) AS DATE)) < c.valid_until
      AND (c.ended_at IS NULL OR last_day(CAST(date_trunc('month', v.ordered_at) AS DATE)) < c.ended_at)
  )
)
SELECT
  o.order_id,
  o.member_id,
  o.store_id,
  m.home_store_id,
  o.ordered_at,
  o.status,
  o.gross_cents,
  o.paid_cents,
  o.refund_cents,
  o.quantity,
  o.channel,
  CASE WHEN v.order_id IS NOT NULL THEN v.valid_order_rank END AS valid_order_rank,
  CASE WHEN v.order_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_valid_order,
  vm.member_month_valid_order_count,
  CASE WHEN em.member_id IS NOT NULL THEN TRUE ELSE FALSE END AS paid_eligible
FROM {{ ref('orders') }} o
LEFT JOIN {{ ref('members') }} m
  ON o.member_id = m.member_id
LEFT JOIN valid_orders v
  ON o.order_id = v.order_id
LEFT JOIN valid_order_months vm
  ON v.member_id = vm.member_id
 AND CAST(date_trunc('month', v.ordered_at) AS DATE) = vm.stat_period_start
LEFT JOIN eligible_months em
  ON v.member_id = em.member_id
 AND CAST(date_trunc('month', v.ordered_at) AS DATE) = em.stat_period_start