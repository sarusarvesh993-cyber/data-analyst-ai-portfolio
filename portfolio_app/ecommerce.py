"""Load and validate dashboard-ready outputs for the e-commerce SQL project."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "04-ecommerce-sql" / "outputs"
FILES = {
    "kpis": "executive_kpis.csv",
    "monthly": "monthly_performance.csv",
    "cohorts": "cohort_retention.csv",
    "states": "delivery_by_state.csv",
    "delivery": "delivery_experience.csv",
    "categories": "category_performance.csv",
    "quality": "data_quality.csv",
}
REQUIRED_COLUMNS = {
    "kpis": {"delivered_orders", "item_gmv_brl", "repeat_customer_rate_pct"},
    "monthly": {"purchase_month", "delivered_orders", "item_gmv_brl"},
    "cohorts": {"cohort_month", "month_number", "retention_rate_pct"},
    "states": {"customer_state", "on_time_delivery_rate_pct", "average_review_score"},
    "delivery": {"delivery_status", "average_review_score", "low_review_rate_pct"},
    "categories": {"category", "item_gmv_brl", "delivered_orders"},
    "quality": {"check_name", "issue_count", "check_status"},
}


def load_outputs(output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> dict[str, pd.DataFrame]:
    """Load committed aggregates and fail clearly if a schema drifts."""
    directory = Path(output_dir)
    outputs: dict[str, pd.DataFrame] = {}
    for key, filename in FILES.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing e-commerce output: {path}")
        frame = pd.read_csv(path)
        missing = REQUIRED_COLUMNS[key] - set(frame.columns)
        if missing:
            raise ValueError(f"{filename} is missing columns: {sorted(missing)}")
        outputs[key] = frame

    outputs["monthly"]["purchase_month"] = pd.to_datetime(
        outputs["monthly"]["purchase_month"]
    )
    outputs["cohorts"]["cohort_month"] = pd.to_datetime(
        outputs["cohorts"]["cohort_month"]
    )
    outputs["cohorts"]["activity_month"] = pd.to_datetime(
        outputs["cohorts"]["activity_month"]
    )
    return outputs


def cohort_matrix(cohorts: pd.DataFrame, max_month: int = 12) -> pd.DataFrame:
    """Return a cohort-by-age matrix of retention percentages."""
    if max_month < 0:
        raise ValueError("max_month must be non-negative")
    filtered = cohorts.loc[cohorts["month_number"].between(0, max_month)].copy()
    matrix = filtered.pivot(
        index="cohort_month", columns="month_number", values="retention_rate_pct"
    )
    matrix.index = matrix.index.strftime("%Y-%m")
    matrix.columns = [f"M{int(column)}" for column in matrix.columns]
    return matrix.sort_index()


def weighted_retention(cohorts: pd.DataFrame, month_number: int) -> float:
    """Calculate size-weighted retention for one cohort age."""
    selected = cohorts.loc[cohorts["month_number"].eq(month_number)]
    denominator = selected["cohort_size"].sum()
    if denominator == 0:
        return 0.0
    return float(100.0 * selected["active_customers"].sum() / denominator)


def brl(value: float, decimals: int = 1) -> str:
    """Format a Brazilian-real value compactly for app metrics."""
    absolute = abs(value)
    if absolute >= 1_000_000:
        return f"R${value / 1_000_000:,.{decimals}f}M"
    if absolute >= 1_000:
        return f"R${value / 1_000:,.{decimals}f}K"
    return f"R${value:,.2f}"
