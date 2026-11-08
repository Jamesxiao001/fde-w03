SELECT
  order_id,
  member_id,
  ordered_at,
  CAST(date_trunc('month', ordered_at) AS DATE) AS stat_period_start,
  paid_cents - refund_cents AS net_sales_cents,
  member_month_valid_order_count,
  paid_eligible
FROM {{ ref('order_facts') }}
WHERE is_valid_order