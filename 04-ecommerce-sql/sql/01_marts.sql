-- Build analysis marts with explicit grains.
-- The essential rule: aggregate one-to-many tables to order_id BEFORE joining.
-- Joining raw items directly to raw payments would multiply rows and overstate value.

CREATE OR REPLACE VIEW item_rollup AS
SELECT
    order_id,
    count(*) AS item_count,
    count(DISTINCT product_id) AS distinct_products,
    count(DISTINCT seller_id) AS distinct_sellers,
    round(sum(price), 2) AS item_gmv,
    round(sum(freight_value), 2) AS freight_value
FROM raw_order_items
GROUP BY order_id;

CREATE OR REPLACE VIEW payment_rollup AS
SELECT
    order_id,
    count(*) AS payment_records,
    round(sum(payment_value), 2) AS payment_value,
    string_agg(DISTINCT payment_type, ', ' ORDER BY payment_type) AS payment_types,
    max(payment_installments) AS max_installments
FROM raw_order_payments
GROUP BY order_id;

CREATE OR REPLACE VIEW review_rollup AS
SELECT
    order_id,
    count(*) AS review_records,
    round(avg(review_score), 2) AS review_score,
    max(CASE WHEN review_comment_message IS NOT NULL THEN 1 ELSE 0 END) AS has_comment
FROM raw_order_reviews
GROUP BY order_id;

CREATE OR REPLACE VIEW order_mart AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    CAST(date_trunc('month', o.order_purchase_timestamp) AS DATE) AS purchase_month,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    coalesce(i.item_count, 0) AS item_count,
    coalesce(i.distinct_products, 0) AS distinct_products,
    coalesce(i.distinct_sellers, 0) AS distinct_sellers,
    coalesce(i.item_gmv, 0) AS item_gmv,
    coalesce(i.freight_value, 0) AS freight_value,
    coalesce(p.payment_records, 0) AS payment_records,
    coalesce(p.payment_value, 0) AS payment_value,
    p.payment_types,
    p.max_installments,
    r.review_records,
    r.review_score,
    r.has_comment,
    CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END AS is_delivered,
    CASE WHEN o.order_status IN ('canceled', 'unavailable') THEN 1 ELSE 0 END AS is_canceled,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1
        ELSE 0
    END AS is_on_time,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        ELSE date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date)
    END AS delivery_days,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        ELSE greatest(
            date_diff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date),
            0
        )
    END AS late_days
FROM raw_orders AS o
LEFT JOIN raw_customers AS c USING (customer_id)
LEFT JOIN item_rollup AS i USING (order_id)
LEFT JOIN payment_rollup AS p USING (order_id)
LEFT JOIN review_rollup AS r USING (order_id);

CREATE OR REPLACE VIEW customer_first_purchase AS
SELECT
    customer_unique_id,
    min(purchase_month) AS cohort_month
FROM order_mart
WHERE is_delivered = 1
  AND customer_unique_id IS NOT NULL
GROUP BY customer_unique_id;

CREATE OR REPLACE VIEW order_category_mart AS
WITH order_category AS (
    SELECT
        oi.order_id,
        coalesce(t.product_category_name_english, p.product_category_name, 'Unclassified') AS category,
        count(*) AS category_item_count,
        round(sum(oi.price), 2) AS category_gmv,
        round(sum(oi.freight_value), 2) AS category_freight
    FROM raw_order_items AS oi
    LEFT JOIN raw_products AS p USING (product_id)
    LEFT JOIN raw_category_translation AS t USING (product_category_name)
    GROUP BY oi.order_id, category
)
SELECT
    oc.order_id,
    oc.category,
    oc.category_item_count,
    oc.category_gmv,
    oc.category_freight,
    om.customer_unique_id,
    om.customer_state,
    om.purchase_month,
    om.order_status,
    om.is_delivered,
    om.is_on_time,
    om.delivery_days,
    om.late_days,
    om.review_score
FROM order_category AS oc
JOIN order_mart AS om USING (order_id);
