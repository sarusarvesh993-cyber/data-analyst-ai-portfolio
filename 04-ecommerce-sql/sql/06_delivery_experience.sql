-- Quantify how late delivery is associated with review outcomes.
SELECT
    CASE WHEN is_on_time = 1 THEN 'On time' ELSE 'Late' END AS delivery_status,
    count(*) AS delivered_orders,
    round(avg(delivery_days), 2) AS average_delivery_days,
    round(avg(late_days), 2) AS average_late_days,
    round(avg(review_score), 2) AS average_review_score,
    round(100.0 * avg(CASE WHEN review_score = 5 THEN 1 ELSE 0 END), 2) AS five_star_review_rate_pct,
    round(100.0 * avg(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END), 2) AS low_review_rate_pct
FROM order_mart
WHERE is_delivered = 1
  AND is_on_time IS NOT NULL
  AND review_score IS NOT NULL
GROUP BY delivery_status
ORDER BY delivery_status DESC;
