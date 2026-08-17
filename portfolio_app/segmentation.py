"""Load and interrogate reviewed customer-segmentation outputs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "05-customer-segmentation" / "outputs"
FILES = {
    "kpis": "executive_kpis.csv",
    "customers": "customer_segments.csv",
    "segments": "segment_summary.csv",
    "clusters": "cluster_summary.csv",
    "comparison": "segment_cluster_comparison.csv",
    "validation": "model_validation.csv",
    "monthly": "monthly_performance.csv",
    "countries": "country_summary.csv",
    "quality": "data_quality.csv",
    "metadata": "feature_metadata.csv",
}
REQUIRED_COLUMNS = {
    "kpis": {"customers", "gross_revenue", "selected_cluster_count"},
    "customers": {
        "customer_id",
        "rfm_segment",
        "cluster_name",
        "recency_days",
        "frequency",
        "monetary_value",
    },
    "segments": {"rfm_segment", "customers", "revenue", "objective", "primary_kpi"},
    "clusters": {"cluster_name", "customers", "revenue"},
    "comparison": {"rfm_segment"},
    "validation": {
        "n_clusters",
        "silhouette_score",
        "seed_stability_ari",
        "selected_model",
    },
    "monthly": {"purchase_month", "revenue", "orders", "active_customers"},
    "countries": {"country", "revenue", "customers"},
    "quality": {"check_name", "issue_count", "check_status"},
    "metadata": {"feature", "winsor_cap_99pct"},
}


def load_outputs(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, pd.DataFrame]:
    """Load committed aggregates and fail if a reviewed schema drifts."""
    directory = Path(output_dir)
    outputs: dict[str, pd.DataFrame] = {}
    for key, filename in FILES.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing segmentation output: {path}")
        frame = pd.read_csv(path)
        missing = REQUIRED_COLUMNS[key] - set(frame.columns)
        if missing:
            raise ValueError(f"{filename} is missing columns: {sorted(missing)}")
        outputs[key] = frame

    outputs["monthly"]["purchase_month"] = pd.to_datetime(
        outputs["monthly"]["purchase_month"]
    )
    for column in ["first_purchase_date", "last_purchase_date"]:
        outputs["customers"][column] = pd.to_datetime(outputs["customers"][column])
    outputs["validation"]["selected_model"] = (
        outputs["validation"]["selected_model"].astype(str).str.lower().eq("true")
    )
    outputs["customers"]["is_repeat_customer"] = (
        outputs["customers"]["is_repeat_customer"].astype(str).str.lower().eq("true")
    )
    return outputs


def filter_customers(
    customers: pd.DataFrame,
    segments: list[str] | tuple[str, ...] | None = None,
    countries: list[str] | tuple[str, ...] | None = None,
    minimum_value: float = 0.0,
) -> pd.DataFrame:
    """Filter the anonymized customer table without mutating source outputs."""
    if minimum_value < 0:
        raise ValueError("minimum_value must be non-negative")
    filtered = customers.loc[customers["monetary_value"].ge(minimum_value)].copy()
    if segments:
        filtered = filtered.loc[filtered["rfm_segment"].isin(segments)]
    if countries:
        filtered = filtered.loc[filtered["country"].isin(countries)]
    return filtered


def audience_export(customers: pd.DataFrame, segment: str) -> pd.DataFrame:
    """Create a campaign-safe audience file using anonymized IDs and approved fields."""
    selected = customers.loc[customers["rfm_segment"].eq(segment)].copy()
    columns = [
        "customer_id",
        "country",
        "rfm_segment",
        "recency_days",
        "frequency",
        "monetary_value",
        "average_order_value",
        "return_rate_pct",
    ]
    return selected[columns].sort_values(
        ["monetary_value", "recency_days"], ascending=[False, True]
    )


def campaign_record(segments: pd.DataFrame, segment: str) -> pd.Series:
    """Return the single reviewed campaign strategy for an RFM segment."""
    selected = segments.loc[segments["rfm_segment"].eq(segment)]
    if len(selected) != 1:
        raise KeyError(f"Expected one campaign record for {segment!r}")
    return selected.iloc[0]


def gbp(value: float, decimals: int = 1) -> str:
    """Format sterling values compactly for app metrics."""
    absolute = abs(value)
    if absolute >= 1_000_000:
        return f"£{value / 1_000_000:,.{decimals}f}M"
    if absolute >= 1_000:
        return f"£{value / 1_000:,.{decimals}f}K"
    return f"£{value:,.2f}"
