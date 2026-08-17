"""Build reviewed public-finance and synthetic corporate-planning outputs."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
SOURCE = PROJECT_DIR / "data" / "raw" / "austin_budget_vs_actual.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
RANDOM_STATE = 42

REQUIRED_COLUMNS = {
    "budget_fiscal_year",
    "thru_quarter",
    "dept_rollup",
    "dept_rollup_name",
    "department_code",
    "department_name",
    "fund_code",
    "fund_name",
    "program_code",
    "program_name",
    "activity_code",
    "activity_name",
    "unit_code",
    "unit_name",
    "expense_code",
    "expense_name",
    "budget",
    "expenditures",
    "key",
}


def load_source(path: str | Path = SOURCE) -> pd.DataFrame:
    """Load and validate the City of Austin operating-budget snapshot."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(
            f"Missing {source}. Run 06-financial-planning/download_data.py first."
        )
    frame = pd.read_csv(
        source,
        dtype={
            "fund_code": "string",
            "program_code": "string",
            "activity_code": "string",
            "unit_code": "string",
            "key": "string",
        },
    )
    frame.columns = frame.columns.str.strip().str.lower()
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Austin source is missing columns: {sorted(missing)}")

    for column in ["budget_fiscal_year", "thru_quarter", "dept_rollup", "department_code"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")
    for column in ["budget", "expenditures"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    text_columns = [
        "dept_rollup_name",
        "department_name",
        "fund_name",
        "program_name",
        "activity_name",
        "unit_name",
        "expense_name",
    ]
    for column in text_columns:
        frame[column] = frame[column].astype("string").str.strip().fillna("Unknown")

    if frame["budget_fiscal_year"].nunique() != 1 or frame["thru_quarter"].nunique() != 1:
        raise ValueError("Expected a single fiscal-year and through-quarter snapshot")
    if frame[["budget", "expenditures"]].isna().any().any():
        raise ValueError("Budget or expenditure values could not be parsed")
    return frame


def expense_category(name: str) -> str:
    """Map detailed objects to a small, documented management-reporting taxonomy."""
    value = str(name).lower()
    if any(
        keyword in value
        for keyword in [
            "wage",
            "salary",
            "overtime",
            "employee",
            "retir",
            "insurance",
            "medical claim",
            "personnel",
            "vacation pay",
            "sick pay",
            "holiday",
        ]
    ):
        return "Personnel & benefits"
    if any(
        keyword in value
        for keyword in ["trf ", "transfer", "debt", "principal", "interest", "redemption"]
    ):
        return "Transfers & debt service"
    if any(keyword in value for keyword in ["grant", "contribution", "subrecipient"]):
        return "Grants & contributions"
    if any(
        keyword in value
        for keyword in [
            "service",
            "contract",
            "professional",
            "consult",
            "legal",
            "administrative support",
        ]
    ):
        return "Contractual services"
    if any(
        keyword in value
        for keyword in [
            "suppl",
            "material",
            "equipment",
            "computer",
            "software",
            "vehicle",
            "fuel",
            "parts",
        ]
    ):
        return "Supplies, technology & equipment"
    return "Other operating costs"


def add_pacing_metrics(summary: pd.DataFrame, elapsed_fraction: float) -> pd.DataFrame:
    """Add expense pacing measures without presenting them as an accounting forecast."""
    result = summary.copy()
    result["elapsed_pct"] = 100 * elapsed_fraction
    result["expected_spend_to_date"] = result["budget"] * elapsed_fraction
    result["remaining_budget"] = result["budget"] - result["expenditures"]
    result["utilization_pct"] = np.where(
        result["budget"].ne(0),
        100 * result["expenditures"] / result["budget"],
        np.nan,
    )
    result["pace_variance"] = result["expenditures"] - result["expected_spend_to_date"]
    result["pace_gap_pct_points"] = result["utilization_pct"] - 100 * elapsed_fraction
    result["linear_run_rate_proxy"] = result["expenditures"] / elapsed_fraction
    result["projected_variance_proxy"] = result["linear_run_rate_proxy"] - result["budget"]

    conditions = [
        result["budget"].eq(0) & result["expenditures"].gt(0),
        result["budget"].le(0),
        result["utilization_pct"].gt(100 * elapsed_fraction + 5),
        result["utilization_pct"].lt(100 * elapsed_fraction - 5),
    ]
    choices = [
        "Review: spend without budget",
        "Review: non-positive budget",
        "Above pace",
        "Below pace",
    ]
    result["pace_status"] = np.select(conditions, choices, default="Near pace")
    return result


def summarize(
    frame: pd.DataFrame, group_columns: list[str], elapsed_fraction: float
) -> pd.DataFrame:
    summary = (
        frame.groupby(group_columns, as_index=False, dropna=False)
        .agg(
            budget=("budget", "sum"),
            expenditures=("expenditures", "sum"),
            source_lines=("key", "nunique"),
        )
        .reset_index(drop=True)
    )
    return add_pacing_metrics(summary, elapsed_fraction)


def build_corporate_plan() -> pd.DataFrame:
    """Create a clearly labeled, seeded corporate FP&A scenario model."""
    rng = np.random.default_rng(RANDOM_STATE)
    business_units = {
        "Enterprise": 1.65,
        "SMB": 1.00,
        "Customer Solutions": 0.70,
    }
    lines = [
        ("Revenue", "Subscription revenue", 3_200_000, -0.025),
        ("Revenue", "Professional services revenue", 720_000, 0.010),
        ("COGS", "Cloud hosting", 510_000, 0.055),
        ("COGS", "Customer support delivery", 245_000, 0.025),
        ("Operating expense", "Sales & marketing", 780_000, 0.075),
        ("Operating expense", "Product & engineering", 920_000, 0.035),
        ("Operating expense", "General & administrative", 430_000, -0.005),
    ]
    rows: list[dict[str, object]] = []
    for month in range(1, 13):
        date = pd.Timestamp(2026, month, 1)
        revenue_seasonality = 1 + 0.035 * np.sin((month - 1) * np.pi / 6)
        if month >= 10:
            revenue_seasonality += 0.09
        cost_seasonality = 1.02 if month in {1, 7} else 1.0
        for business_unit, unit_scale in business_units.items():
            for statement_group, line_item, base, mean_variance in lines:
                seasonality = revenue_seasonality if statement_group == "Revenue" else cost_seasonality
                budget = base * unit_scale * seasonality
                if statement_group == "Operating expense" and line_item == "Product & engineering":
                    budget *= 1 + 0.015 * month
                shock = rng.normal(mean_variance, 0.025)
                if month in {5, 6} and statement_group == "Revenue" and business_unit == "SMB":
                    shock -= 0.055
                if month == 6 and statement_group != "Revenue":
                    shock += 0.025
                actual = budget * (1 + shock) if month <= 7 else np.nan
                future_trend = budget * (1 + 0.70 * mean_variance)
                base_forecast = actual if month <= 7 else future_trend
                rows.append(
                    {
                        "month": date,
                        "fiscal_year": 2026,
                        "month_number": month,
                        "period_status": "Actual" if month <= 7 else "Forecast",
                        "business_unit": business_unit,
                        "statement_group": statement_group,
                        "line_item": line_item,
                        "budget_amount": round(budget, 2),
                        "actual_amount": round(actual, 2) if month <= 7 else np.nan,
                        "base_forecast_amount": round(base_forecast, 2),
                        "pnl_sign": 1 if statement_group == "Revenue" else -1,
                        "is_synthetic": True,
                    }
                )
    return pd.DataFrame(rows)


def build_corporate_monthly(plan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for month, group in plan.groupby("month", sort=True):
        budget_revenue = group.loc[group["statement_group"].eq("Revenue"), "budget_amount"].sum()
        budget_cost = group.loc[group["statement_group"].ne("Revenue"), "budget_amount"].sum()
        forecast_revenue = group.loc[
            group["statement_group"].eq("Revenue"), "base_forecast_amount"
        ].sum()
        forecast_cost = group.loc[
            group["statement_group"].ne("Revenue"), "base_forecast_amount"
        ].sum()
        rows.append(
            {
                "month": month,
                "period_status": group["period_status"].iloc[0],
                "budget_revenue": budget_revenue,
                "budget_cost": budget_cost,
                "budget_ebitda": budget_revenue - budget_cost,
                "base_forecast_revenue": forecast_revenue,
                "base_forecast_cost": forecast_cost,
                "base_forecast_ebitda": forecast_revenue - forecast_cost,
            }
        )
    return pd.DataFrame(rows)


def build_quality(frame: pd.DataFrame) -> pd.DataFrame:
    zero_budget_spend = frame["budget"].eq(0) & frame["expenditures"].gt(0)
    checks = [
        ("source_rows", len(frame), "INFO"),
        ("duplicate_key_rows", int(frame["key"].duplicated().sum()), "PASS"),
        ("missing_dimension_cells", int(frame[list(REQUIRED_COLUMNS)].isna().sum().sum()), "PASS"),
        ("zero_budget_rows", int(frame["budget"].eq(0).sum()), "REVIEW"),
        ("positive_spend_with_zero_budget_rows", int(zero_budget_spend.sum()), "REVIEW"),
        (
            "positive_spend_with_zero_budget_value",
            float(frame.loc[zero_budget_spend, "expenditures"].sum()),
            "REVIEW",
        ),
        ("negative_budget_rows", int(frame["budget"].lt(0).sum()), "REVIEW"),
        ("negative_expenditure_rows", int(frame["expenditures"].lt(0).sum()), "REVIEW"),
        ("fiscal_year_values", int(frame["budget_fiscal_year"].nunique()), "PASS"),
        ("through_quarter_values", int(frame["thru_quarter"].nunique()), "PASS"),
    ]
    return pd.DataFrame(checks, columns=["check_name", "issue_count", "check_status"])


def build_outputs(
    source: str | Path = SOURCE, output_dir: str | Path = OUTPUT_DIR
) -> dict[str, pd.DataFrame]:
    """Build and write all reviewed Project 06 analytical outputs."""
    frame = load_source(source)
    frame["expense_category"] = frame["expense_name"].map(expense_category)
    fiscal_year = int(frame["budget_fiscal_year"].iloc[0])
    through_quarter = int(frame["thru_quarter"].iloc[0])
    elapsed_fraction = through_quarter / 4

    department = summarize(frame, ["dept_rollup_name"], elapsed_fraction).sort_values(
        "budget", ascending=False
    )
    fund = summarize(
        frame, ["dept_rollup_name", "fund_name"], elapsed_fraction
    ).sort_values("budget", ascending=False)
    expense = summarize(
        frame, ["expense_category", "expense_name"], elapsed_fraction
    ).sort_values("budget", ascending=False)
    planning_mart = summarize(
        frame,
        ["dept_rollup_name", "fund_name", "program_name", "expense_category"],
        elapsed_fraction,
    ).sort_values("budget", ascending=False)
    variance_drivers = planning_mart.copy()
    variance_drivers["absolute_pace_variance"] = variance_drivers["pace_variance"].abs()
    variance_drivers = variance_drivers.sort_values(
        "absolute_pace_variance", ascending=False
    ).reset_index(drop=True)

    total_budget = float(frame["budget"].sum())
    total_expenditures = float(frame["expenditures"].sum())
    expected = total_budget * elapsed_fraction
    zero_budget_spend = frame["budget"].eq(0) & frame["expenditures"].gt(0)
    executive = pd.DataFrame(
        [
            {
                "budget_fiscal_year": fiscal_year,
                "through_quarter": through_quarter,
                "elapsed_pct": 100 * elapsed_fraction,
                "source_rows": len(frame),
                "departments": frame["dept_rollup_name"].nunique(),
                "funds": frame["fund_name"].nunique(),
                "programs": frame["program_name"].nunique(),
                "annual_budget": total_budget,
                "expenditures_to_date": total_expenditures,
                "expected_spend_to_date": expected,
                "remaining_budget": total_budget - total_expenditures,
                "utilization_pct": 100 * total_expenditures / total_budget,
                "pace_variance": total_expenditures - expected,
                "linear_run_rate_proxy": total_expenditures / elapsed_fraction,
                "projected_variance_proxy": total_expenditures / elapsed_fraction - total_budget,
                "above_pace_departments": int(department["pace_status"].eq("Above pace").sum()),
                "zero_budget_spend_rows": int(zero_budget_spend.sum()),
                "zero_budget_spend_value": float(
                    frame.loc[zero_budget_spend, "expenditures"].sum()
                ),
            }
        ]
    )
    quality = build_quality(frame)
    corporate_plan = build_corporate_plan()
    corporate_monthly = build_corporate_monthly(corporate_plan)
    source_metadata = pd.DataFrame(
        [
            {
                "dataset_id": "g5k8-8sud",
                "source_name": "City of Austin Program Budget Operating Budget Vs Expense Raw Data",
                "source_url": "https://data.austintexas.gov/d/g5k8-8sud",
                "api_url": "https://data.austintexas.gov/resource/g5k8-8sud.csv?$limit=100000",
                "snapshot_fiscal_year": fiscal_year,
                "snapshot_through_quarter": through_quarter,
                "source_rows": len(frame),
                "corporate_model_status": "Seeded synthetic demonstration; not City of Austin data",
            }
        ]
    )

    outputs = {
        "executive_kpis": executive,
        "department_summary": department,
        "fund_summary": fund,
        "expense_summary": expense,
        "planning_mart": planning_mart,
        "variance_drivers": variance_drivers,
        "corporate_plan": corporate_plan,
        "corporate_monthly": corporate_monthly,
        "data_quality": quality,
        "source_metadata": source_metadata,
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for name, output in outputs.items():
        output.to_csv(destination / f"{name}.csv", index=False)
        print(f"Wrote {destination / f'{name}.csv'} ({len(output):,} rows)")
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    build_outputs(args.source, args.output_dir)
