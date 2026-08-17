-- Monthly customer retention by first delivered-purchase cohort.
WITH customer_activity AS (
    SELECT DISTINCT
        customer_unique_id,
        purchase_month AS activity_month
    FROM order_mart
    WHERE is_delivered = 1
      AND customer_unique_id IS NOT NULL
      AND purchase_month <= DATE '2018-08-01'
),
cohort_activity AS (
    SELECT
        cf.cohort_month,
        ca.activity_month,
        date_diff('month', cf.cohort_month, ca.activity_month) AS month_number,
        count(DISTINCT ca.customer_unique_id) AS active_customers
    FROM customer_activity AS ca
    JOIN customer_first_purchase AS cf USING (customer_unique_id)
    WHERE cf.cohort_month BETWEEN DATE '2017-01-01' AND DATE '2018-06-01'
    GROUP BY cf.cohort_month, ca.activity_month, month_number
),
cohort_sizes AS (
    SELECT
        cohort_month,
        active_customers AS cohort_size
    FROM cohort_activity
    WHERE month_number = 0
)
SELECT
    ca.cohort_month,
    ca.activity_month,
    ca.month_number,
    cs.cohort_size,
    ca.active_customers,
    round(100.0 * ca.active_customers / nullif(cs.cohort_size, 0), 2) AS retention_rate_pct
FROM cohort_activity AS ca
JOIN cohort_sizes AS cs USING (cohort_month)
WHERE ca.month_number BETWEEN 0 AND 18
ORDER BY ca.cohort_month, ca.month_number;
