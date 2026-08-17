"""Execute portfolio SQL queries and export small dashboard-ready CSV files."""
from __future__ import annotations

from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIR / "data" / "olist.duckdb"
SQL_DIR = PROJECT_DIR / "sql"
OUTPUT_DIR = PROJECT_DIR / "outputs"
QUERIES = {
    "02_executive_kpis.sql": "executive_kpis.csv",
    "03_monthly_performance.sql": "monthly_performance.csv",
    "04_cohort_retention.sql": "cohort_retention.csv",
    "05_delivery_by_state.sql": "delivery_by_state.csv",
    "06_delivery_experience.sql": "delivery_experience.csv",
    "07_category_performance.sql": "category_performance.csv",
    "08_data_quality.sql": "data_quality.csv",
}


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Warehouse not found. Run `python 04-ecommerce-sql/build_warehouse.py` first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    try:
        for sql_name, csv_name in QUERIES.items():
            sql = (SQL_DIR / sql_name).read_text(encoding="utf-8")
            frame = connection.execute(sql).fetchdf()
            destination = OUTPUT_DIR / csv_name
            frame.to_csv(destination, index=False)
            print(f"Wrote {destination.relative_to(PROJECT_DIR)} ({len(frame):,} rows)")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
