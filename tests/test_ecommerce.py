from pathlib import Path

import duckdb
import pytest

from portfolio_app.ecommerce import cohort_matrix, load_outputs, weighted_retention

ROOT = Path(__file__).parents[1]
OUTPUTS = ROOT / "04-ecommerce-sql" / "outputs"
MART_SQL = ROOT / "04-ecommerce-sql" / "sql" / "01_marts.sql"


def test_committed_outputs_are_complete_and_plausible():
    outputs = load_outputs(OUTPUTS)
    kpis = outputs["kpis"].iloc[0]
    assert set(outputs) == {
        "kpis",
        "monthly",
        "cohorts",
        "states",
        "delivery",
        "categories",
        "quality",
    }
    assert 90_000 < kpis["delivered_orders"] < 100_000
    assert 10_000_000 < kpis["item_gmv_brl"] < 20_000_000
    assert 0 < kpis["repeat_customer_rate_pct"] < 10
    assert outputs["categories"]["category"].is_unique
    assert outputs["monthly"]["purchase_month"].is_monotonic_increasing


def test_cohort_helpers_preserve_month_zero_and_weight_retention():
    cohorts = load_outputs(OUTPUTS)["cohorts"]
    matrix = cohort_matrix(cohorts, max_month=6)
    assert (matrix["M0"] == 100.0).all()
    assert list(matrix.columns) == [f"M{month}" for month in range(7)]
    month_one = weighted_retention(cohorts, 1)
    assert 0 < month_one < 2


def test_order_mart_prevents_item_payment_multiplication():
    connection = duckdb.connect()
    try:
        connection.execute(
            """
            CREATE TABLE raw_customers AS
            SELECT * FROM (VALUES ('c1', 'u1', '10000', 'sao paulo', 'SP'))
            AS t(customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state);

            CREATE TABLE raw_orders AS
            SELECT * FROM (VALUES (
                'o1', 'c1', 'delivered', TIMESTAMP '2018-01-01 10:00:00',
                TIMESTAMP '2018-01-01 11:00:00', TIMESTAMP '2018-01-02 09:00:00',
                TIMESTAMP '2018-01-05 12:00:00', TIMESTAMP '2018-01-07 00:00:00'
            )) AS t(
                order_id, customer_id, order_status, order_purchase_timestamp,
                order_approved_at, order_delivered_carrier_date,
                order_delivered_customer_date, order_estimated_delivery_date
            );

            CREATE TABLE raw_order_items AS
            SELECT * FROM (VALUES
                ('o1', 1, 'p1', 's1', 10.0, 1.0),
                ('o1', 2, 'p2', 's1', 20.0, 2.0)
            ) AS t(order_id, order_item_id, product_id, seller_id, price, freight_value);

            CREATE TABLE raw_order_payments AS
            SELECT * FROM (VALUES
                ('o1', 1, 'credit_card', 1, 15.0),
                ('o1', 2, 'voucher', 1, 18.0)
            ) AS t(order_id, payment_sequential, payment_type, payment_installments, payment_value);

            CREATE TABLE raw_order_reviews AS
            SELECT * FROM (VALUES ('r1', 'o1', 5, 'great'))
            AS t(review_id, order_id, review_score, review_comment_message);

            CREATE TABLE raw_products AS
            SELECT * FROM (VALUES ('p1', 'cat'), ('p2', 'cat'))
            AS t(product_id, product_category_name);

            CREATE TABLE raw_category_translation AS
            SELECT * FROM (VALUES ('cat', 'Category'))
            AS t(product_category_name, product_category_name_english);
            """
        )
        connection.execute(MART_SQL.read_text(encoding="utf-8"))
        row = connection.execute(
            """
            SELECT item_count, item_gmv, freight_value, payment_records,
                   payment_value, review_score
            FROM order_mart
            """
        ).fetchone()
        assert row == pytest.approx((2, 30.0, 3.0, 2, 33.0, 5.0))
        category = connection.execute(
            "SELECT category_item_count, category_gmv FROM order_category_mart"
        ).fetchone()
        assert category == pytest.approx((2, 30.0))
    finally:
        connection.close()
