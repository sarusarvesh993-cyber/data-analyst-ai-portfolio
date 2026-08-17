"""Build reproducible RFM, clustering, campaign, and dashboard outputs."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent
SOURCE = PROJECT_DIR / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_DIR = PROJECT_DIR / "outputs"
RANDOM_STATE = 42
FEATURES = ["recency_days", "frequency", "monetary_value"]

CAMPAIGNS = {
    "Champions": {
        "priority": 1,
        "objective": "Protect loyalty and advocacy",
        "treatment": "Early access, recognition, and referral invitation; avoid blanket discounts",
        "channel": "Email + loyalty messaging",
        "primary_kpi": "Incremental 90-day revenue per customer",
        "guardrail": "Contribution margin and unsubscribe rate",
        "experiment": "Randomized value-added perk versus business-as-usual holdout",
    },
    "At Risk": {
        "priority": 2,
        "objective": "Reactivate previously valuable customers",
        "treatment": "Personalized win-back message with a threshold-based shipping test",
        "channel": "Email + paid retargeting",
        "primary_kpi": "Incremental repeat-purchase rate",
        "guardrail": "Contribution after incentive and return rate",
        "experiment": "Randomized offer test with a 10% no-contact holdout",
    },
    "Loyal": {
        "priority": 3,
        "objective": "Deepen category breadth and order value",
        "treatment": "Relevant cross-sell bundles and replenishment reminders",
        "channel": "Email + onsite recommendations",
        "primary_kpi": "Incremental average order value",
        "guardrail": "Gross margin per order",
        "experiment": "Bundle recommendation versus standard recommendation",
    },
    "Potential Loyalists": {
        "priority": 4,
        "objective": "Build a repeat-purchase habit",
        "treatment": "Second- or third-order journey with product education and social proof",
        "channel": "Triggered email",
        "primary_kpi": "90-day repeat-purchase rate",
        "guardrail": "Discount cost per incremental order",
        "experiment": "Lifecycle journey versus normal promotional calendar",
    },
    "New Customers": {
        "priority": 5,
        "objective": "Convert the first purchase into a second",
        "treatment": "Welcome journey, care guidance, and a shipping-threshold reminder",
        "channel": "Triggered email",
        "primary_kpi": "Second purchase within 60 days",
        "guardrail": "Support contacts and early return rate",
        "experiment": "Three-message onboarding sequence versus receipt-only control",
    },
    "Occasional": {
        "priority": 6,
        "objective": "Increase purchase cadence efficiently",
        "treatment": "Seasonal reminders and product recommendations based on prior baskets",
        "channel": "Email",
        "primary_kpi": "Incremental orders per contacted customer",
        "guardrail": "Revenue per thousand messages",
        "experiment": "Personalized recommendations versus category bestsellers",
    },
    "Hibernating": {
        "priority": 7,
        "objective": "Test low-cost reactivation or suppress",
        "treatment": "One re-permission message; suppress persistent non-responders",
        "channel": "Low-frequency email",
        "primary_kpi": "Incremental profit per contact",
        "guardrail": "Unsubscribe rate and contact cost",
        "experiment": "Single re-permission test with a no-contact holdout",
    },
}


def _snake_case(columns: pd.Index) -> list[str]:
    mapping = {
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    }
    return [mapping.get(str(column), str(column).strip().lower()) for column in columns]


def load_source(path: str | Path = SOURCE) -> pd.DataFrame:
    """Load and type the public UCI workbook."""
    workbook = Path(path)
    if not workbook.exists():
        raise FileNotFoundError(
            f"Missing {workbook}. Run 05-customer-segmentation/download_data.py first."
        )
    frame = pd.read_excel(workbook, engine="openpyxl")
    frame.columns = _snake_case(frame.columns)
    required = {
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Source workbook is missing columns: {sorted(missing)}")
    frame["invoice_no"] = frame["invoice_no"].astype("string").str.strip()
    frame["stock_code"] = frame["stock_code"].astype("string").str.strip()
    frame["invoice_date"] = pd.to_datetime(frame["invoice_date"], errors="coerce")
    frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce")
    frame["unit_price"] = pd.to_numeric(frame["unit_price"], errors="coerce")
    frame["country"] = frame["country"].astype("string").str.strip()
    frame["customer_id"] = pd.to_numeric(frame["customer_id"], errors="coerce").astype("Int64")
    frame["is_cancellation"] = frame["invoice_no"].str.upper().str.startswith("C", na=False)
    frame["line_value"] = frame["quantity"] * frame["unit_price"]
    return frame


def split_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return valid identified purchases and identified return/cancellation lines."""
    common = raw["customer_id"].notna() & raw["invoice_date"].notna() & raw["unit_price"].gt(0)
    purchases = raw.loc[
        common & raw["quantity"].gt(0) & ~raw["is_cancellation"]
    ].copy()
    purchases["customer_id"] = purchases["customer_id"].astype("int64").astype(str)
    purchases["line_revenue"] = purchases["quantity"] * purchases["unit_price"]

    returns = raw.loc[
        common & (raw["quantity"].lt(0) | raw["is_cancellation"])
    ].copy()
    returns["customer_id"] = returns["customer_id"].astype("int64").astype(str)
    returns["return_value"] = (returns["quantity"] * returns["unit_price"]).abs()
    return purchases, returns


def _mode(series: pd.Series) -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return "Unknown"
    modes = values.mode()
    return str(modes.iloc[0]) if not modes.empty else str(values.iloc[0])


def build_customer_features(
    purchases: pd.DataFrame, returns: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Create one row per customer with interpretable behavioral features."""
    snapshot_date = purchases["invoice_date"].max().normalize() + pd.Timedelta(days=1)
    customer = purchases.groupby("customer_id", as_index=False).agg(
        last_purchase_date=("invoice_date", "max"),
        first_purchase_date=("invoice_date", "min"),
        frequency=("invoice_no", "nunique"),
        monetary_value=("line_revenue", "sum"),
        units_purchased=("quantity", "sum"),
        active_months=("invoice_date", lambda values: values.dt.to_period("M").nunique()),
        country=("country", _mode),
    )
    customer["recency_days"] = (
        snapshot_date - customer["last_purchase_date"].dt.normalize()
    ).dt.days
    customer["tenure_days"] = (
        snapshot_date - customer["first_purchase_date"].dt.normalize()
    ).dt.days
    customer["average_order_value"] = customer["monetary_value"] / customer["frequency"]
    customer["is_repeat_customer"] = customer["frequency"].gt(1)

    returned = returns.groupby("customer_id", as_index=False).agg(
        return_value=("return_value", "sum"),
        return_invoices=("invoice_no", "nunique"),
    )
    customer = customer.merge(returned, on="customer_id", how="left")
    customer[["return_value", "return_invoices"]] = customer[
        ["return_value", "return_invoices"]
    ].fillna(0)
    customer["return_rate_pct"] = 100 * customer["return_value"] / (
        customer["monetary_value"] + customer["return_value"]
    )
    return customer, snapshot_date


def score_rfm(customer: pd.DataFrame) -> pd.DataFrame:
    """Add deterministic quintile scores and business-readable RFM segments."""
    scored = customer.copy()
    scored["r_score"] = pd.qcut(
        scored["recency_days"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1],
    ).astype(int)
    for column, target in [("frequency", "f_score"), ("monetary_value", "m_score")]:
        scored[target] = pd.qcut(
            scored[column].rank(method="first"),
            5,
            labels=[1, 2, 3, 4, 5],
        ).astype(int)
    scored["rfm_score"] = scored[["r_score", "f_score", "m_score"]].sum(axis=1)

    conditions = [
        scored["r_score"].ge(4) & scored["f_score"].ge(4) & scored["m_score"].ge(4),
        scored["r_score"].ge(3) & scored["f_score"].ge(4),
        scored["r_score"].eq(5) & scored["frequency"].eq(1),
        scored["r_score"].ge(4) & scored["f_score"].between(2, 3),
        scored["r_score"].le(2) & (scored["f_score"].ge(3) | scored["m_score"].ge(3)),
        scored["r_score"].le(2) & scored["f_score"].le(2),
    ]
    choices = [
        "Champions",
        "Loyal",
        "New Customers",
        "Potential Loyalists",
        "At Risk",
        "Hibernating",
    ]
    scored["rfm_segment"] = np.select(conditions, choices, default="Occasional")
    return scored


def prepare_cluster_matrix(customer: pd.DataFrame) -> tuple[np.ndarray, dict[str, float]]:
    """Winsorize, log-transform, and standardize RFM features for K-means."""
    clipped = customer[FEATURES].copy()
    caps: dict[str, float] = {}
    for column in FEATURES:
        cap = float(clipped[column].quantile(0.99))
        caps[column] = cap
        clipped[column] = clipped[column].clip(upper=cap)
    transformed = np.log1p(clipped)
    matrix = StandardScaler().fit_transform(transformed)
    return matrix, caps


def evaluate_kmeans(matrix: np.ndarray) -> pd.DataFrame:
    """Compare cluster counts using separation, compactness, size, and seed stability."""
    rows: list[dict[str, float | int | bool]] = []
    for clusters in range(2, 9):
        reference = KMeans(
            n_clusters=clusters,
            random_state=RANDOM_STATE,
            n_init=30,
        ).fit_predict(matrix)
        seed_agreement = []
        for seed in range(10):
            labels = KMeans(
                n_clusters=clusters, random_state=seed, n_init=10
            ).fit_predict(matrix)
            seed_agreement.append(adjusted_rand_score(reference, labels))
        counts = pd.Series(reference).value_counts(normalize=True)
        model = KMeans(
            n_clusters=clusters, random_state=RANDOM_STATE, n_init=30
        ).fit(matrix)
        rows.append(
            {
                "n_clusters": clusters,
                "silhouette_score": silhouette_score(matrix, reference),
                "calinski_harabasz_score": calinski_harabasz_score(matrix, reference),
                "davies_bouldin_score": davies_bouldin_score(matrix, reference),
                "inertia": model.inertia_,
                "seed_stability_ari": float(np.mean(seed_agreement)),
                "minimum_cluster_share_pct": float(100 * counts.min()),
            }
        )
    validation = pd.DataFrame(rows)
    eligible = validation.loc[
        validation["seed_stability_ari"].ge(0.80)
        & validation["minimum_cluster_share_pct"].ge(5.0)
        & validation["n_clusters"].between(3, 6)
    ].copy()
    if eligible.empty:
        eligible = validation.loc[validation["n_clusters"].between(3, 6)].copy()
    best_silhouette = eligible["silhouette_score"].max()
    candidates = eligible.loc[
        eligible["silhouette_score"].ge(best_silhouette * 0.90)
    ].copy()
    candidates["selection_score"] = (
        candidates["silhouette_score"].rank(pct=True)
        + candidates["seed_stability_ari"].rank(pct=True)
        + candidates["minimum_cluster_share_pct"].rank(pct=True)
        + candidates["davies_bouldin_score"].rank(pct=True, ascending=False)
    )
    selected_k = int(
        candidates.sort_values(
            ["selection_score", "n_clusters"], ascending=[False, True]
        ).iloc[0]["n_clusters"]
    )
    validation["selected_model"] = validation["n_clusters"].eq(selected_k)
    return validation


def _name_clusters(customer: pd.DataFrame) -> dict[int, str]:
    summary = customer.groupby("cluster_id", as_index=False).agg(
        recency_days=("recency_days", "median"),
        frequency=("frequency", "median"),
        monetary_value=("monetary_value", "median"),
    )
    remaining = set(summary["cluster_id"].astype(int))
    names: dict[int, str] = {}

    value_score = (
        summary["frequency"].rank(pct=True)
        + summary["monetary_value"].rank(pct=True)
        - summary["recency_days"].rank(pct=True)
    )
    best = int(summary.loc[value_score.idxmax(), "cluster_id"])
    names[best] = "High-Value Loyal"
    remaining.discard(best)

    if remaining:
        lapsed_rows = summary.loc[summary["cluster_id"].isin(remaining)]
        lapsed = int(lapsed_rows.loc[lapsed_rows["recency_days"].idxmax(), "cluster_id"])
        names[lapsed] = "Lapsed"
        remaining.discard(lapsed)

    if remaining:
        recent_rows = summary.loc[summary["cluster_id"].isin(remaining)]
        recent_score = recent_rows["recency_days"].rank(pct=True) + recent_rows[
            "frequency"
        ].rank(pct=True)
        recent = int(recent_rows.loc[recent_score.idxmin(), "cluster_id"])
        names[recent] = "Recent Starters"
        remaining.discard(recent)

    fallback_names = [
        "Core Regulars",
        "Growth Potential",
        "Occasional Buyers",
        "Low-Engagement",
    ]
    ordered = summary.loc[summary["cluster_id"].isin(remaining)].sort_values(
        ["frequency", "monetary_value"], ascending=False
    )
    for name, cluster_id in zip(fallback_names, ordered["cluster_id"].astype(int)):
        names[cluster_id] = name
    return names


def add_clusters(
    customer: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    matrix, caps = prepare_cluster_matrix(customer)
    validation = evaluate_kmeans(matrix)
    selected_k = int(
        validation.loc[validation["selected_model"], "n_clusters"].iloc[0]
    )
    labels = KMeans(
        n_clusters=selected_k, random_state=RANDOM_STATE, n_init=30
    ).fit_predict(matrix)
    clustered = customer.copy()
    clustered["cluster_id"] = labels.astype(int)
    names = _name_clusters(clustered)
    clustered["cluster_name"] = clustered["cluster_id"].map(names)
    return clustered, validation, caps


def build_summaries(
    customer: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build rule-segment, cluster, and cross-model comparison summaries."""
    total_customers = len(customer)
    total_revenue = customer["monetary_value"].sum()

    def summarize(group_column: str) -> pd.DataFrame:
        summary = customer.groupby(group_column, as_index=False).agg(
            customers=("customer_id", "nunique"),
            revenue=("monetary_value", "sum"),
            orders=("frequency", "sum"),
            median_recency_days=("recency_days", "median"),
            median_frequency=("frequency", "median"),
            median_monetary_value=("monetary_value", "median"),
            average_order_value=("average_order_value", "mean"),
            repeat_customer_rate_pct=(
                "is_repeat_customer",
                lambda values: 100 * values.mean(),
            ),
            average_return_rate_pct=("return_rate_pct", "mean"),
        )
        summary["customer_share_pct"] = 100 * summary["customers"] / total_customers
        summary["revenue_share_pct"] = 100 * summary["revenue"] / total_revenue
        return summary.sort_values("revenue", ascending=False).reset_index(drop=True)

    segments = summarize("rfm_segment")
    campaigns = pd.DataFrame.from_dict(CAMPAIGNS, orient="index").reset_index(
        names="rfm_segment"
    )
    segments = segments.merge(campaigns, on="rfm_segment", how="left").sort_values(
        "priority"
    )
    clusters = summarize("cluster_name")
    comparison = (
        pd.crosstab(
            customer["rfm_segment"], customer["cluster_name"], normalize="index"
        )
        .mul(100)
        .reset_index()
    )
    return segments, clusters, comparison


def build_monthly(purchases: pd.DataFrame) -> pd.DataFrame:
    frame = purchases.copy()
    frame["purchase_month"] = frame["invoice_date"].dt.to_period("M").dt.to_timestamp()
    first_month = frame.groupby("customer_id")["purchase_month"].min().rename("first_month")
    frame = frame.merge(first_month, on="customer_id", how="left")
    frame["is_new_customer"] = frame["purchase_month"].eq(frame["first_month"])
    customer_month = frame[
        ["purchase_month", "customer_id", "is_new_customer"]
    ].drop_duplicates()
    customer_counts = customer_month.groupby("purchase_month", as_index=False).agg(
        active_customers=("customer_id", "nunique"),
        new_customers=("is_new_customer", "sum"),
    )
    customer_counts["returning_customers"] = (
        customer_counts["active_customers"] - customer_counts["new_customers"]
    )
    monthly = frame.groupby("purchase_month", as_index=False).agg(
        revenue=("line_revenue", "sum"),
        orders=("invoice_no", "nunique"),
        units=("quantity", "sum"),
    )
    monthly = monthly.merge(customer_counts, on="purchase_month", how="left")
    monthly["average_order_value"] = monthly["revenue"] / monthly["orders"]
    return monthly.sort_values("purchase_month")


def build_quality(
    raw: pd.DataFrame,
    purchases: pd.DataFrame,
    returns: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    checks = [
        ("raw_rows", len(raw), "INFO"),
        ("missing_customer_id_rows", int(raw["customer_id"].isna().sum()), "REVIEW"),
        ("cancellation_invoice_rows", int(raw["is_cancellation"].sum()), "INFO"),
        ("non_positive_quantity_rows", int(raw["quantity"].le(0).sum()), "INFO"),
        ("non_positive_price_rows", int(raw["unit_price"].le(0).sum()), "REVIEW"),
        ("exact_duplicate_rows", int(raw.duplicated().sum()), "REVIEW"),
        ("valid_identified_purchase_rows", len(purchases), "PASS"),
        ("identified_return_rows", len(returns), "PASS"),
        (
            "duplicate_customer_feature_rows",
            int(customers["customer_id"].duplicated().sum()),
            "PASS",
        ),
        (
            "unassigned_rfm_segment_rows",
            int(customers["rfm_segment"].isna().sum()),
            "PASS",
        ),
        (
            "unassigned_cluster_rows",
            int(customers["cluster_name"].isna().sum()),
            "PASS",
        ),
    ]
    return pd.DataFrame(checks, columns=["check_name", "issue_count", "check_status"])


def build_outputs(
    source: str | Path = SOURCE, output_dir: str | Path = OUTPUT_DIR
) -> dict[str, pd.DataFrame]:
    """Run the complete deterministic segmentation workflow and write CSV outputs."""
    raw = load_source(source)
    purchases, returns = split_transactions(raw)
    customers, snapshot_date = build_customer_features(purchases, returns)
    customers = score_rfm(customers)
    customers, validation, caps = add_clusters(customers)
    segments, clusters, comparison = build_summaries(customers)
    monthly = build_monthly(purchases)
    countries = (
        purchases.groupby("country", as_index=False)
        .agg(
            revenue=("line_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )
    countries["revenue_share_pct"] = (
        100 * countries["revenue"] / countries["revenue"].sum()
    )
    quality = build_quality(raw, purchases, returns, customers)

    selected = validation.loc[validation["selected_model"]].iloc[0]
    at_risk_value = float(
        customers.loc[
            customers["rfm_segment"].eq("At Risk"), "monetary_value"
        ].sum()
    )
    identified_positive = raw.loc[
        raw["quantity"].gt(0)
        & raw["unit_price"].gt(0)
        & ~raw["is_cancellation"],
        "line_value",
    ].sum()
    executive = pd.DataFrame(
        [
            {
                "snapshot_date": snapshot_date.date().isoformat(),
                "customers": len(customers),
                "orders": purchases["invoice_no"].nunique(),
                "gross_revenue": purchases["line_revenue"].sum(),
                "returned_value": returns["return_value"].sum(),
                "net_revenue_proxy": purchases["line_revenue"].sum()
                - returns["return_value"].sum(),
                "average_order_value": purchases["line_revenue"].sum()
                / purchases["invoice_no"].nunique(),
                "repeat_customer_rate_pct": 100
                * customers["is_repeat_customer"].mean(),
                "at_risk_historical_value": at_risk_value,
                "selected_cluster_count": int(selected["n_clusters"]),
                "selected_silhouette_score": selected["silhouette_score"],
                "selected_seed_stability_ari": selected["seed_stability_ari"],
                "identified_sales_value_coverage_pct": 100
                * purchases["line_revenue"].sum()
                / identified_positive,
                "analysis_start_date": purchases["invoice_date"].min().date().isoformat(),
                "analysis_end_date": purchases["invoice_date"].max().date().isoformat(),
            }
        ]
    )

    customers = customers[
        [
            "customer_id",
            "country",
            "first_purchase_date",
            "last_purchase_date",
            "recency_days",
            "frequency",
            "monetary_value",
            "average_order_value",
            "units_purchased",
            "active_months",
            "tenure_days",
            "return_value",
            "return_invoices",
            "return_rate_pct",
            "is_repeat_customer",
            "r_score",
            "f_score",
            "m_score",
            "rfm_score",
            "rfm_segment",
            "cluster_id",
            "cluster_name",
        ]
    ].sort_values("monetary_value", ascending=False)

    metadata = pd.DataFrame(
        [{"feature": column, "winsor_cap_99pct": value} for column, value in caps.items()]
    )
    outputs = {
        "executive_kpis": executive,
        "customer_segments": customers,
        "segment_summary": segments,
        "cluster_summary": clusters,
        "segment_cluster_comparison": comparison,
        "model_validation": validation,
        "monthly_performance": monthly,
        "country_summary": countries,
        "data_quality": quality,
        "feature_metadata": metadata,
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(destination / f"{name}.csv", index=False)
        print(f"Wrote {destination / f'{name}.csv'} ({len(frame):,} rows)")
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    build_outputs(args.source, args.output_dir)
