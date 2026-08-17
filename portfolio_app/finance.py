"""Load and interrogate reviewed Project 06 financial-planning outputs."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "06-financial-planning" / "outputs"
FILES = {
    "kpis": "executive_kpis.csv",
    "departments": "department_summary.csv",
    "funds": "fund_summary.csv",
    "expenses": "expense_summary.csv",
    "mart": "planning_mart.csv",
    "drivers": "variance_drivers.csv",
    "corporate_plan": "corporate_plan.csv",
    "corporate_monthly": "corporate_monthly.csv",
    "quality": "data_quality.csv",
    "metadata": "source_metadata.csv",
}
REQUIRED_COLUMNS = {
    "kpis": {"annual_budget", "expenditures_to_date", "utilization_pct", "through_quarter"},
    "departments": {"dept_rollup_name", "budget", "expenditures", "pace_status"},
    "funds": {"dept_rollup_name", "fund_name", "budget", "expenditures"},
    "expenses": {"expense_category", "expense_name", "budget", "expenditures"},
    "mart": {
        "dept_rollup_name",
        "fund_name",
        "program_name",
        "expense_category",
        "budget",
        "expenditures",
    },
    "drivers": {"program_name", "pace_variance", "absolute_pace_variance"},
    "corporate_plan": {
        "month",
        "period_status",
        "business_unit",
        "statement_group",
        "line_item",
        "budget_amount",
        "base_forecast_amount",
    },
    "corporate_monthly": {"month", "budget_ebitda", "base_forecast_ebitda"},
    "quality": {"check_name", "issue_count", "check_status"},
    "metadata": {"dataset_id", "source_url", "corporate_model_status"},
}


def load_outputs(output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> dict[str, pd.DataFrame]:
    """Load reviewed outputs and fail clearly if a committed schema drifts."""
    directory = Path(output_dir)
    outputs: dict[str, pd.DataFrame] = {}
    for key, filename in FILES.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing financial-planning output: {path}")
        frame = pd.read_csv(path)
        missing = REQUIRED_COLUMNS[key] - set(frame.columns)
        if missing:
            raise ValueError(f"{filename} is missing columns: {sorted(missing)}")
        outputs[key] = frame
    outputs["corporate_plan"]["month"] = pd.to_datetime(outputs["corporate_plan"]["month"])
    outputs["corporate_monthly"]["month"] = pd.to_datetime(
        outputs["corporate_monthly"]["month"]
    )
    return outputs


def filter_planning_mart(
    mart: pd.DataFrame,
    departments: list[str] | tuple[str, ...] | None = None,
    funds: list[str] | tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Filter the public-finance mart without changing its reviewed source."""
    filtered = mart.copy()
    if departments:
        filtered = filtered.loc[filtered["dept_rollup_name"].isin(departments)]
    if funds:
        filtered = filtered.loc[filtered["fund_name"].isin(funds)]
    return filtered


def apply_corporate_scenario(
    plan: pd.DataFrame,
    revenue_adjustment_pct: float = 0.0,
    cost_inflation_pct: float = 0.0,
    hiring_delay_savings_pct: float = 0.0,
) -> pd.DataFrame:
    """Apply transparent future-period adjustments to the seeded corporate model."""
    if not -30 <= revenue_adjustment_pct <= 30:
        raise ValueError("revenue_adjustment_pct must be between -30 and 30")
    if not -10 <= cost_inflation_pct <= 20:
        raise ValueError("cost_inflation_pct must be between -10 and 20")
    if not 0 <= hiring_delay_savings_pct <= 20:
        raise ValueError("hiring_delay_savings_pct must be between 0 and 20")

    scenario = plan.copy()
    scenario["scenario_amount"] = scenario["base_forecast_amount"]
    future = scenario["period_status"].eq("Forecast")
    revenue = scenario["statement_group"].eq("Revenue")
    scenario.loc[future & revenue, "scenario_amount"] *= 1 + revenue_adjustment_pct / 100
    scenario.loc[future & ~revenue, "scenario_amount"] *= 1 + cost_inflation_pct / 100
    hiring_lines = scenario["line_item"].isin(
        ["Product & engineering", "General & administrative"]
    )
    scenario.loc[future & hiring_lines, "scenario_amount"] *= (
        1 - hiring_delay_savings_pct / 100
    )
    scenario["scenario_amount"] = scenario["scenario_amount"].round(2)
    return scenario


def corporate_pnl(plan: pd.DataFrame, amount_column: str) -> dict[str, float]:
    """Return revenue, cost, and EBITDA totals for one amount column."""
    if amount_column not in plan.columns:
        raise KeyError(amount_column)
    revenue = float(plan.loc[plan["statement_group"].eq("Revenue"), amount_column].sum())
    cost = float(plan.loc[plan["statement_group"].ne("Revenue"), amount_column].sum())
    return {
        "revenue": revenue,
        "cost": cost,
        "ebitda": revenue - cost,
        "margin_pct": 100 * (revenue - cost) / revenue if revenue else np.nan,
    }


def usd(value: float, decimals: int = 1) -> str:
    """Format U.S. dollar values compactly for app metrics."""
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.{decimals}f}B"
    if absolute >= 1_000_000:
        return f"${value / 1_000_000:,.{decimals}f}M"
    if absolute >= 1_000:
        return f"${value / 1_000:,.{decimals}f}K"
    return f"${value:,.2f}"
