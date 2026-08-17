"""Render reproducible Project 06 documentation and BI companion previews."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
ASSET_DIR = PROJECT_DIR / "assets"

NAVY = "#102A43"
TEAL = "#0F8A7B"
GOLD = "#F4A340"
PURPLE = "#7C6CE7"
RED = "#E26D5A"
BLUE = "#2B6F92"
SLATE = "#63788B"


def _save(fig: plt.Figure, filename: str) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSET_DIR / filename, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {ASSET_DIR / filename}")


def render() -> None:
    sns.set_theme(style="whitegrid", font_scale=0.9)
    kpis = pd.read_csv(OUTPUT_DIR / "executive_kpis.csv").iloc[0]
    departments = pd.read_csv(OUTPUT_DIR / "department_summary.csv")
    expenses = pd.read_csv(OUTPUT_DIR / "expense_summary.csv")
    monthly = pd.read_csv(OUTPUT_DIR / "corporate_monthly.csv")
    monthly["month"] = pd.to_datetime(monthly["month"])

    top = departments.head(15).sort_values("budget")
    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(top))
    ax.barh(y, top["budget"] / 1e6, color="#DCE8E5", label="Annual budget")
    ax.barh(y, top["expenditures"] / 1e6, color=TEAL, label="Q3 expenditures")
    ax.set_yticks(y, top["dept_rollup_name"])
    ax.axvline(0, color=NAVY, lw=0.8)
    ax.set_title("Largest departments: annual budget and Q3 expenditures", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_xlabel("US dollars (millions)")
    ax.set_ylabel("")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    ax.grid(axis="y", visible=False)
    _save(fig, "department_pacing.png")

    category = expenses.groupby("expense_category", as_index=False)[["budget", "expenditures"]].sum()
    category = category.sort_values("budget")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    y = np.arange(len(category))
    height = 0.35
    ax.barh(y + height / 2, category["budget"] / 1e9, height=height, color=NAVY, label="Annual budget")
    ax.barh(y - height / 2, category["expenditures"] / 1e9, height=height, color=GOLD, label="Q3 expenditures")
    ax.set_yticks(y, category["expense_category"])
    ax.set_title("Management expense categories", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_xlabel("US dollars (billions)")
    ax.set_ylabel("")
    ax.legend(frameon=False)
    ax.grid(axis="x", alpha=0.2)
    ax.grid(axis="y", visible=False)
    _save(fig, "expense_mix.png")

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(monthly["month"], monthly["budget_ebitda"] / 1e6, color=NAVY, lw=2.5, marker="o", label="Budget EBITDA")
    ax.plot(monthly["month"], monthly["base_forecast_ebitda"] / 1e6, color=PURPLE, lw=2.5, marker="s", label="Base forecast EBITDA")
    ax.axvspan(monthly.loc[monthly["period_status"].eq("Forecast"), "month"].min(), monthly["month"].max(), color=GOLD, alpha=0.10, label="Forecast period")
    ax.set_title("Synthetic corporate planning model", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_ylabel("EBITDA ($ millions)")
    ax.set_xlabel("")
    ax.legend(frameon=False, ncol=3, loc="lower center")
    ax.grid(alpha=0.2)
    _save(fig, "corporate_plan.png")

    # Power BI companion target.
    fig = plt.figure(figsize=(13.5, 7.6), facecolor="#F3F5F7")
    canvas = fig.add_axes([0, 0, 1, 1])
    canvas.set_axis_off()
    canvas.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, color="#1C1B1F"))
    canvas.text(0.025, 0.965, "FINANCIAL PLANNING & VARIANCE", color="white", weight="bold", va="center", fontsize=13)
    canvas.text(0.825, 0.965, "POWER BI COMPANION", color="#D8D5DC", va="center", fontsize=8)
    canvas.add_patch(plt.Rectangle((0.025, 0.84), 0.95, 0.065, facecolor="white", edgecolor="#DDDEE2"))
    filters = [(0.045, "DEPARTMENT", "All"), (0.31, "FUND", "All"), (0.56, "QUARTER", "Q3"), (0.77, "FISCAL YEAR", "2026")]
    for x, title, value in filters:
        canvas.text(x, 0.882, title, color="#727079", fontsize=7)
        canvas.text(x, 0.852, value, color="#242229", fontsize=10, weight="bold")
    cards = [
        ("ANNUAL BUDGET", f"${kpis['annual_budget'] / 1e9:.2f}B"),
        ("Q3 EXPENDITURES", f"${kpis['expenditures_to_date'] / 1e9:.2f}B"),
        ("UTILIZATION", f"{kpis['utilization_pct']:.1f}%"),
        ("PACE VARIANCE", f"${kpis['pace_variance'] / 1e6:.1f}M"),
        ("REMAINING", f"${kpis['remaining_budget'] / 1e9:.2f}B"),
    ]
    for index, (title, value) in enumerate(cards):
        x = 0.025 + index * 0.192
        canvas.add_patch(plt.Rectangle((x, 0.70), 0.175, 0.105, facecolor="white", edgecolor="#DDDEE2"))
        canvas.add_patch(plt.Rectangle((x, 0.70), 0.175, 0.008, color="#F2C811"))
        canvas.text(x + 0.014, 0.775, title, color="#727079", fontsize=7)
        canvas.text(x + 0.014, 0.728, value, color="#242229", fontsize=16, weight="bold")
    chart1 = fig.add_axes([0.055, 0.12, 0.42, 0.50], facecolor="white")
    plot = departments.head(10).sort_values("budget")
    chart1.barh(plot["dept_rollup_name"], plot["budget"] / 1e9, color="#D9D9D9", label="Budget")
    chart1.barh(plot["dept_rollup_name"], plot["expenditures"] / 1e9, color="#F2C811", label="Expenditures")
    chart1.set_title("Budget pacing by department", loc="left", fontsize=10, weight="bold")
    chart1.set_xlabel("$ billions", fontsize=8)
    chart1.tick_params(labelsize=7)
    chart1.legend(frameon=False, fontsize=7)
    chart1.grid(axis="x", alpha=0.2)
    chart1.grid(axis="y", visible=False)
    chart2 = fig.add_axes([0.56, 0.12, 0.39, 0.50], facecolor="white")
    scatter_data = departments.loc[departments["budget"].ge(1_000_000)].copy()
    sizes = 80 + 800 * scatter_data["budget"] / scatter_data["budget"].max()
    colors = np.where(scatter_data["pace_gap_pct_points"].gt(5), "#E26D5A", np.where(scatter_data["pace_gap_pct_points"].lt(-5), "#5B9BD5", "#70AD47"))
    chart2.scatter(scatter_data["budget"] / 1e6, scatter_data["utilization_pct"], s=sizes, c=colors, alpha=0.75, edgecolor="white")
    chart2.axhline(75, color="#F2C811", linestyle="--", lw=2)
    for row in scatter_data.nlargest(7, "budget").itertuples():
        chart2.annotate(row.dept_rollup_name, (row.budget / 1e6, row.utilization_pct), fontsize=6, xytext=(3, 3), textcoords="offset points")
    chart2.set_title("Budget size versus utilization", loc="left", fontsize=10, weight="bold")
    chart2.set_xlabel("Annual budget ($M)", fontsize=8)
    chart2.set_ylabel("Utilization (%)", fontsize=8)
    chart2.tick_params(labelsize=7)
    chart2.grid(alpha=0.2)
    _save(fig, "power_bi_companion.png")


if __name__ == "__main__":
    render()
