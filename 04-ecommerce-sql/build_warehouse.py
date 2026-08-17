"""Build a local DuckDB warehouse from the downloaded Olist CSV files."""
from __future__ import annotations

from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
DATABASE_PATH = PROJECT_DIR / "data" / "olist.duckdb"
SQL_DIR = PROJECT_DIR / "sql"
REQUIRED_FILES = [
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def execute_file(connection: duckdb.DuckDBPyConnection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8").replace(
        "{{RAW_DIR}}", RAW_DIR.as_posix().replace("'", "''")
    )
    connection.execute(sql)


def main() -> None:
    missing = [name for name in REQUIRED_FILES if not (RAW_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Raw files are missing. Run `python 04-ecommerce-sql/download_data.py` "
            f"first. Missing: {missing}"
        )

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DATABASE_PATH))
    try:
        execute_file(connection, SQL_DIR / "00_create_tables.sql")
        execute_file(connection, SQL_DIR / "01_marts.sql")
        connection.execute("CHECKPOINT")
        counts = connection.execute(
            """
            SELECT 'orders' AS table_name, count(*) AS rows FROM raw_orders
            UNION ALL SELECT 'order_items', count(*) FROM raw_order_items
            UNION ALL SELECT 'customers', count(*) FROM raw_customers
            UNION ALL SELECT 'order_mart', count(*) FROM order_mart
            ORDER BY table_name
            """
        ).fetchall()
    finally:
        connection.close()

    print(f"Built {DATABASE_PATH.relative_to(PROJECT_DIR)}")
    for table_name, row_count in counts:
        print(f"  {table_name:14s} {row_count:>9,} rows")


if __name__ == "__main__":
    main()
