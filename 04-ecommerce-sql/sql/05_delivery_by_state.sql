-- Delivery and customer-experience performance by customer state.
SELECT
    customer_state,
    count(*) AS delivered_orders,
    count(DISTINCT customer_unique_id) AS unique_customers,
    round(sum(item_gmv), 2) AS item_gmv_brl,
    round(avg(item_gmv), 2) AS average_order_gmv_brl,
    round(avg(delivery_days), 2) AS average_delivery_days,
    round(100.0 * avg(is_on_time), 2) AS on_time_delivery_rate_pct,
    round(avg(late_days) FILTER (WHERE is_on_time = 0), 2) AS average_late_days,
    round(avg(review_score), 2) AS average_review_score
FROM order_mart
WHERE is_delivered = 1
  AND customer_state IS NOT NULL
GROUP BY customer_state
HAVING count(*) >= 100
ORDER BY item_gmv_brl DESC;
