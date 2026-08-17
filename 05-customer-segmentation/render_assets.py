"""Render reproducible documentation and Power BI companion previews."""
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
PALETTE = [TEAL, PURPLE, GOLD, RED, BLUE, "#55A6D9", "#8FB9A8"]


def _save(fig: plt.Figure, filename: str) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        ASSET_DIR / filename,
        dpi=170,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)
    print(f"Wrote {ASSET_DIR / filename}")


def render() -> None:
    sns.set_theme(style="whitegrid", font_scale=0.9)
    segments = pd.read_csv(OUTPUT_DIR / "segment_summary.csv").sort_values("revenue")
    customers = pd.read_csv(OUTPUT_DIR / "customer_segments.csv")
    validation = pd.read_csv(OUTPUT_DIR / "model_validation.csv")
    kpis = pd.read_csv(OUTPUT_DIR / "executive_kpis.csv").iloc[0]

    fig, ax = plt.subplots(figsize=(10, 5.6))
    colors = [PALETTE[index % len(PALETTE)] for index in range(len(segments))]
    ax.barh(segments["rfm_segment"], segments["revenue"] / 1_000_000, color=colors)
    ax.set_title(
        "Historical revenue by RFM segment",
        loc="left",
        color=NAVY,
        weight="bold",
        fontsize=15,
    )
    ax.set_xlabel("Completed-purchase value (£ millions)")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.22)
    ax.grid(axis="y", visible=False)
    for index, value in enumerate(segments["revenue"] / 1_000_000):
        ax.text(
            value + 0.03,
            index,
            f"£{value:.2f}M",
            va="center",
            fontsize=8,
            color=NAVY,
        )
    _save(fig, "segment_revenue.png")

    sample = customers.sample(min(2500, len(customers)), random_state=42)
    segment_order = segments.sort_values("priority")["rfm_segment"].tolist()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=sample,
        x="recency_days",
        y="monetary_value",
        hue="rfm_segment",
        hue_order=segment_order,
        palette=PALETTE[: len(segment_order)],
        size="frequency",
        sizes=(18, 180),
        alpha=0.68,
        ax=ax,
    )
    ax.set_yscale("log")
    ax.set_title(
        "Customer RFM landscape",
        loc="left",
        color=NAVY,
        weight="bold",
        fontsize=15,
    )
    ax.set_xlabel("Recency (days since last purchase)")
    ax.set_ylabel("Historical purchase value (£, log scale)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False, fontsize=8)
    _save(fig, "rfm_landscape.png")

    selected = validation.loc[validation["selected_model"]].iloc[0]
    fig, left = plt.subplots(figsize=(10, 5.4))
    right = left.twinx()
    left.plot(
        validation["n_clusters"],
        validation["silhouette_score"],
        color=TEAL,
        marker="o",
        lw=2.5,
        label="Silhouette",
    )
    right.plot(
        validation["n_clusters"],
        validation["seed_stability_ari"],
        color=PURPLE,
        marker="s",
        lw=2.2,
        label="Seed stability (ARI)",
    )
    left.axvline(selected["n_clusters"], color=GOLD, linestyle="--", lw=2)
    left.set_title(
        "K-means validation and selected granularity",
        loc="left",
        color=NAVY,
        weight="bold",
        fontsize=15,
    )
    left.set_xlabel("Number of clusters")
    left.set_ylabel("Silhouette score", color=TEAL)
    right.set_ylabel("Mean adjusted Rand index", color=PURPLE)
    left.grid(alpha=0.2)
    lines = left.lines[:1] + right.lines[:1]
    left.legend(
        lines,
        [line.get_label() for line in lines],
        loc="lower left",
        frameon=False,
    )
    _save(fig, "cluster_validation.png")

    plot = segments.sort_values("priority")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    size = 120 + 900 * plot["revenue_share_pct"] / plot["revenue_share_pct"].max()
    ax.scatter(
        plot["median_recency_days"],
        plot["revenue_share_pct"],
        s=size,
        c=PALETTE[: len(plot)],
        alpha=0.76,
        edgecolor="white",
        linewidth=1.5,
    )
    for row in plot.itertuples():
        ax.annotate(
            row.rfm_segment,
            (row.median_recency_days, row.revenue_share_pct),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_title(
        "Campaign opportunity: value versus recency",
        loc="left",
        color=NAVY,
        weight="bold",
        fontsize=15,
    )
    ax.set_xlabel("Median recency (days)")
    ax.set_ylabel("Share of historical revenue (%)")
    ax.grid(alpha=0.2)
    _save(fig, "campaign_opportunity.png")

    # A reproducible report-layout preview for the Power BI companion build.
    fig = plt.figure(figsize=(13.5, 7.6), facecolor="#F4F5F7")
    canvas = fig.add_axes([0, 0, 1, 1])
    canvas.set_axis_off()
    canvas.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, color="#1C1B1F"))
    canvas.text(
        0.025,
        0.965,
        "CUSTOMER SEGMENTATION REPORT",
        color="white",
        weight="bold",
        va="center",
        fontsize=13,
    )
    canvas.text(
        0.83,
        0.965,
        "POWER BI COMPANION",
        color="#D8D5DC",
        va="center",
        fontsize=8,
    )
    canvas.add_patch(
        plt.Rectangle(
            (0.025, 0.84),
            0.95,
            0.065,
            facecolor="white",
            edgecolor="#DDDEE2",
        )
    )
    filters = [
        (0.045, "SEGMENT", "All"),
        (0.25, "COUNTRY", "All"),
        (0.45, "MODEL", "RFM segments"),
        (0.69, "SNAPSHOT", "10 Dec 2011"),
    ]
    for x, title, value in filters:
        canvas.text(x, 0.882, title, color="#727079", fontsize=7)
        canvas.text(x, 0.852, value, color="#242229", fontsize=10, weight="bold")
    cards = [
        ("CUSTOMERS", f"{int(kpis['customers']):,}"),
        ("GROSS REVENUE", f"£{kpis['gross_revenue'] / 1e6:.2f}M"),
        ("ORDERS", f"{int(kpis['orders']):,}"),
        ("REPEAT RATE", f"{kpis['repeat_customer_rate_pct']:.1f}%"),
        ("AT-RISK VALUE", f"£{kpis['at_risk_historical_value'] / 1e6:.2f}M"),
    ]
    for index, (title, value) in enumerate(cards):
        x = 0.025 + index * 0.192
        canvas.add_patch(
            plt.Rectangle(
                (x, 0.70),
                0.175,
                0.105,
                facecolor="white",
                edgecolor="#DDDEE2",
            )
        )
        canvas.add_patch(plt.Rectangle((x, 0.70), 0.175, 0.008, color="#F2C811"))
        canvas.text(x + 0.014, 0.775, title, color="#727079", fontsize=7)
        canvas.text(
            x + 0.014,
            0.728,
            value,
            color="#242229",
            fontsize=18,
            weight="bold",
        )
    chart1 = fig.add_axes([0.055, 0.12, 0.42, 0.50], facecolor="white")
    top = segments.sort_values("revenue")
    chart1.barh(top["rfm_segment"], top["revenue"] / 1e6, color="#F2C811")
    chart1.set_title("Revenue by segment", loc="left", fontsize=10, weight="bold")
    chart1.set_xlabel("£ millions", fontsize=8)
    chart1.tick_params(labelsize=7)
    chart1.grid(axis="x", alpha=0.2)
    chart1.grid(axis="y", visible=False)
    chart2 = fig.add_axes([0.56, 0.12, 0.39, 0.50], facecolor="white")
    chart2.scatter(
        plot["median_recency_days"],
        plot["revenue_share_pct"],
        s=size * 0.7,
        c="#5B9BD5",
        alpha=0.75,
    )
    for row in plot.itertuples():
        chart2.annotate(
            row.rfm_segment,
            (row.median_recency_days, row.revenue_share_pct),
            fontsize=6,
            xytext=(3, 3),
            textcoords="offset points",
        )
    chart2.set_title(
        "Campaign opportunity matrix", loc="left", fontsize=10, weight="bold"
    )
    chart2.set_xlabel("Median recency", fontsize=8)
    chart2.set_ylabel("Revenue share (%)", fontsize=8)
    chart2.tick_params(labelsize=7)
    chart2.grid(alpha=0.2)
    _save(fig, "power_bi_companion.png")


if __name__ == "__main__":
    render()
