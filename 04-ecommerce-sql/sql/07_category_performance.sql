-- Category performance at the order-category grain.
-- This avoids weighting an order's review once for every raw item row.
SELECT
    category,
    count(DISTINCT order_id) AS delivered_orders,
    sum(category_item_count)::BIGINT AS items_sold,
    round(sum(category_gmv), 2) AS item_gmv_brl,
    round(sum(category_freight), 2) AS freight_value_brl,
    round(sum(category_gmv) / nullif(sum(category_item_count), 0), 2) AS average_item_price_brl,
    round(100.0 * avg(is_on_time), 2) AS on_time_delivery_rate_pct,
    round(avg(delivery_days), 2) AS average_delivery_days,
    round(avg(review_score), 2) AS average_review_score
FROM order_category_mart
WHERE is_delivered = 1
GROUP BY category
HAVING count(DISTINCT order_id) >= 100
ORDER BY item_gmv_brl DESC;
