"""Render static README charts from the reviewed SQL output files."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
ASSET_DIR = PROJECT_DIR / "assets"
NAVY = "#173B63"
TEAL = "#0F8A7B"
GOLD = "#F4A340"
RED = "#E26D5A"


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=0.95)

    monthly = pd.read_csv(OUTPUT_DIR / "monthly_performance.csv", parse_dates=["purchase_month"])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(monthly["purchase_month"], monthly["item_gmv_brl"] / 1_000, width=20, color="#BDE9E1")
    ax.plot(monthly["purchase_month"], monthly["item_gmv_brl"] / 1_000, color=TEAL, marker="o", linewidth=2.3)
    ax.set(title="Monthly delivered-order item GMV", xlabel="", ylabel="GMV (thousand BRL)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "monthly_gmv.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    cohorts = pd.read_csv(OUTPUT_DIR / "cohort_retention.csv", parse_dates=["cohort_month"])
    visible = cohorts.loc[cohorts["month_number"].between(1, 12)].copy()
    matrix = visible.pivot(index="cohort_month", columns="month_number", values="retention_rate_pct")
    matrix.index = matrix.index.strftime("%Y-%m")
    fig, ax = plt.subplots(figsize=(12, 6.5))
    sns.heatmap(
        matrix,
        cmap=sns.light_palette(TEAL, as_cmap=True),
        vmin=0,
        vmax=1.2,
        annot=True,
        fmt=".2f",
        linewidths=0.3,
        cbar_kws={"label": "Retention (%)"},
        ax=ax,
    )
    ax.set(title="Customer retention after first delivered purchase", xlabel="Months after first purchase", ylabel="Cohort")
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "cohort_retention.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    delivery = pd.read_csv(OUTPUT_DIR / "delivery_experience.csv")
    chart = delivery.set_index("delivery_status")[["five_star_review_rate_pct", "low_review_rate_pct"]]
    chart.columns = ["Five-star reviews", "One- or two-star reviews"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    chart.plot(kind="bar", color=[TEAL, RED], rot=0, ax=ax)
    ax.set(title="Review outcomes by delivery status", xlabel="", ylabel="Share of reviews (%)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "delivery_reviews.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    categories = pd.read_csv(OUTPUT_DIR / "category_performance.csv").head(10).sort_values("item_gmv_brl")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(categories["category"], categories["item_gmv_brl"] / 1_000, color=TEAL)
    ax.set(title="Top categories by delivered-order item GMV", xlabel="GMV (thousand BRL)", ylabel="")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ASSET_DIR / "category_gmv.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    print(f"Rendered four charts in {ASSET_DIR.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
