-- One-row executive scorecard.
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        count(*) AS delivered_orders
    FROM order_mart
    WHERE is_delivered = 1
      AND customer_unique_id IS NOT NULL
    GROUP BY customer_unique_id
),
repeat_summary AS (
    SELECT
        count(*) AS customers,
        count(*) FILTER (WHERE delivered_orders >= 2) AS repeat_customers
    FROM customer_orders
),
delivered AS (
    SELECT * FROM order_mart WHERE is_delivered = 1
),
all_orders AS (
    SELECT
        count(*) AS total_orders,
        sum(is_canceled) AS canceled_orders
    FROM order_mart
)
SELECT
    min(d.order_purchase_timestamp)::DATE AS first_order_date,
    max(d.order_purchase_timestamp)::DATE AS last_order_date,
    count(*) AS delivered_orders,
    count(DISTINCT d.customer_unique_id) AS unique_customers,
    sum(d.item_count)::BIGINT AS items_sold,
    round(sum(d.item_gmv), 2) AS item_gmv_brl,
    round(sum(d.payment_value), 2) AS payment_value_brl,
    round(avg(d.item_gmv), 2) AS average_order_gmv_brl,
    round(100.0 * rs.repeat_customers / nullif(rs.customers, 0), 2) AS repeat_customer_rate_pct,
    round(100.0 * avg(d.is_on_time), 2) AS on_time_delivery_rate_pct,
    round(avg(d.delivery_days), 2) AS average_delivery_days,
    round(avg(d.review_score), 2) AS average_review_score,
    round(100.0 * ao.canceled_orders / nullif(ao.total_orders, 0), 2) AS canceled_unavailable_rate_pct
FROM delivered AS d
CROSS JOIN repeat_summary AS rs
CROSS JOIN all_orders AS ao
GROUP BY rs.repeat_customers, rs.customers, ao.canceled_orders, ao.total_orders;
