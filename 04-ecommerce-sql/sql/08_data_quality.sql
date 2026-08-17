-- Compact data-quality report for keys, joins, and business-critical fields.
WITH checks AS (
    SELECT 'duplicate_order_ids' AS check_name,
           count(*) - count(DISTINCT order_id) AS issue_count
    FROM raw_orders

    UNION ALL
    SELECT 'duplicate_customer_ids', count(*) - count(DISTINCT customer_id)
    FROM raw_customers

    UNION ALL
    SELECT 'duplicate_order_item_keys', count(*) - count(DISTINCT (order_id, order_item_id))
    FROM raw_order_items

    UNION ALL
    SELECT 'orphan_order_items', count(*)
    FROM raw_order_items AS i
    LEFT JOIN raw_orders AS o USING (order_id)
    WHERE o.order_id IS NULL

    UNION ALL
    SELECT 'orphan_payments', count(*)
    FROM raw_order_payments AS p
    LEFT JOIN raw_orders AS o USING (order_id)
    WHERE o.order_id IS NULL

    UNION ALL
    SELECT 'orphan_customer_orders', count(*)
    FROM raw_orders AS o
    LEFT JOIN raw_customers AS c USING (customer_id)
    WHERE c.customer_id IS NULL

    UNION ALL
    SELECT 'delivered_missing_delivery_date', count(*)
    FROM raw_orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NULL

    UNION ALL
    SELECT 'nonpositive_item_price', count(*)
    FROM raw_order_items
    WHERE price <= 0
)
SELECT
    check_name,
    issue_count,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'REVIEW' END AS check_status
FROM checks
ORDER BY check_status DESC, check_name;
