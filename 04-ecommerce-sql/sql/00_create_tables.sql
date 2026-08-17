-- Load the eight source CSVs into typed DuckDB tables.
-- {{RAW_DIR}} is replaced by build_warehouse.py with an absolute local path.

CREATE OR REPLACE TABLE raw_customers AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_customers_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_orders AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_orders_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_order_items AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_order_items_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_order_payments AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_order_payments_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_order_reviews AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_order_reviews_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_products AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_products_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_sellers AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/olist_sellers_dataset.csv',
    header = true,
    sample_size = -1
);

CREATE OR REPLACE TABLE raw_category_translation AS
SELECT * FROM read_csv_auto(
    '{{RAW_DIR}}/product_category_name_translation.csv',
    header = true,
    sample_size = -1
);
