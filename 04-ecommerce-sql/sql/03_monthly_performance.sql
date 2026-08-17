-- Complete monthly business view; sparse launch/tail months are excluded.
WITH monthly AS (
    SELECT
        om.purchase_month,
        count(*) AS delivered_orders,
        count(DISTINCT om.customer_unique_id) AS active_customers,
        count(DISTINCT CASE WHEN cf.cohort_month = om.purchase_month THEN om.customer_unique_id END) AS new_customers,
        count(DISTINCT CASE WHEN cf.cohort_month < om.purchase_month THEN om.customer_unique_id END) AS returning_customers,
        round(sum(om.item_gmv), 2) AS item_gmv_brl,
        round(avg(om.item_gmv), 2) AS average_order_gmv_brl,
        round(100.0 * avg(om.is_on_time), 2) AS on_time_delivery_rate_pct,
        round(avg(om.review_score), 2) AS average_review_score
    FROM order_mart AS om
    JOIN customer_first_purchase AS cf USING (customer_unique_id)
    WHERE om.is_delivered = 1
      AND om.purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
    GROUP BY om.purchase_month
)
SELECT
    *,
    round(
        100.0 * (item_gmv_brl / nullif(lag(item_gmv_brl) OVER (ORDER BY purchase_month), 0) - 1),
        2
    ) AS month_over_month_gmv_pct
FROM monthly
ORDER BY purchase_month;
