"""Portfolio summary and launch page for the standalone Olist Dash app."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.ecommerce import brl, load_outputs, weighted_retention
from portfolio_app.ui import (
    GOLD,
    NAVY,
    TEAL,
    configure_page,
    inject_global_css,
    render_footer,
    render_notice,
    render_page_header,
    render_section,
    render_sidebar,
    style_plotly,
)

configure_page("E-commerce SQL Analytics", "🛒")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 04 · SQL, DuckDB & Plotly Dash",
    "E-commerce Revenue & Cohort Analysis",
    "Analyze marketplace value, repeat behavior, delivery reliability, and category performance across a relational order system.",
    ["100K orders", "8 source tables", "Safe SQL grains", "Cohort retention", "Standalone Dash app"],
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = load_outputs(ROOT / "04-ecommerce-sql" / "outputs")
kpis = OUTPUTS["kpis"].iloc[0]
monthly = OUTPUTS["monthly"]
delivery = OUTPUTS["delivery"]
categories = OUTPUTS["categories"]
quality = OUTPUTS["quality"]


def dash_url() -> str:
    """Read the public Dash URL only when it has been configured."""
    configured = os.getenv("ECOMMERCE_DASH_URL", "").strip()
    if configured:
        return configured
    try:
        return str(st.secrets.get("ECOMMERCE_DASH_URL", "")).strip()
    except (FileNotFoundError, KeyError):
        return ""


public_dash_url = dash_url()
left, right = st.columns([1.45, 1])
with left:
    render_notice(
        "navy",
        "D",
        "A second application framework",
        "The portfolio remains the central Streamlit hub. This project's full command center is built separately in Plotly Dash to demonstrate callback-based dashboard engineering and a production entry point.",
    )
with right:
    if public_dash_url:
        st.link_button("Launch the full Plotly Dash command center →", public_dash_url, width="stretch")
    else:
        st.info("The public Dash URL is added after the first Plotly Cloud deployment. Local entry point: `python ecommerce_dash_app.py`.")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Delivered orders", f"{int(kpis['delivered_orders']):,}")
k2.metric("Item GMV", brl(float(kpis["item_gmv_brl"]), 2))
k3.metric("Average order", brl(float(kpis["average_order_gmv_brl"]), 0))
k4.metric("Repeat customers", f"{kpis['repeat_customer_rate_pct']:.1f}%")
k5.metric("On-time delivery", f"{kpis['on_time_delivery_rate_pct']:.2f}%")

render_section(
    "Executive evidence",
    "Growth is visible; retention and late-delivery experience are the constraints",
    "The public summary shows the headline evidence. The standalone Dash app adds filter controls, state and category diagnostics, SQL selection, and an exportable executive brief.",
)

trend = go.Figure()
trend.add_trace(
    go.Scatter(
        x=monthly["purchase_month"],
        y=monthly["item_gmv_brl"],
        mode="lines+markers",
        line={"color": TEAL, "width": 3},
        marker={"size": 7, "color": NAVY},
        fill="tozeroy",
        fillcolor="rgba(15,138,123,.10)",
        hovertemplate="%{x|%b %Y}<br>GMV R$%{y:,.0f}<extra></extra>",
    )
)
peak = monthly.loc[monthly["item_gmv_brl"].idxmax()]
trend.add_annotation(
    x=peak["purchase_month"],
    y=peak["item_gmv_brl"],
    text=f"Peak · {peak['purchase_month']:%b %Y}",
    showarrow=True,
    bgcolor=NAVY,
    borderpad=6,
    font={"color": "white"},
)
trend.update_layout(title="Monthly delivered-order GMV", yaxis_title="Item GMV (BRL)")
style_plotly(trend, height=430, show_legend=False)
st.plotly_chart(trend, width="stretch")

on_time = delivery.set_index("delivery_status").loc["On time"]
late = delivery.set_index("delivery_status").loc["Late"]
left, right = st.columns(2)
with left:
    review = delivery.melt(
        id_vars="delivery_status",
        value_vars=["five_star_review_rate_pct", "low_review_rate_pct"],
        var_name="outcome",
        value_name="rate",
    )
    review["outcome"] = review["outcome"].map(
        {"five_star_review_rate_pct": "Five-star", "low_review_rate_pct": "One- or two-star"}
    )
    review_chart = px.bar(
        review,
        x="delivery_status",
        y="rate",
        color="outcome",
        barmode="group",
        title="Review outcomes by delivery status",
        color_discrete_map={"Five-star": TEAL, "One- or two-star": "#E26D5A"},
        labels={"delivery_status": "", "rate": "Share of reviews (%)", "outcome": ""},
    )
    style_plotly(review_chart, height=390)
    st.plotly_chart(review_chart, width="stretch")
with right:
    top = categories.head(8).sort_values("item_gmv_brl")
    category_chart = px.bar(
        top,
        x="item_gmv_brl",
        y="category",
        orientation="h",
        title="Leading categories by delivered item GMV",
        color_discrete_sequence=[GOLD],
        labels={"item_gmv_brl": "Item GMV (BRL)", "category": ""},
    )
    style_plotly(category_chart, height=390, show_legend=False)
    st.plotly_chart(category_chart, width="stretch")

render_section("Decision brief", "Three actions supported by the analysis")
rec1, rec2, rec3 = st.columns(3)
with rec1:
    render_notice("teal", "1", "Test second-order lifecycle", f"Measure a controlled intervention against the {kpis['repeat_customer_rate_pct']:.1f}% repeat-customer baseline and {weighted_retention(OUTPUTS['cohorts'], 1):.2f}% month-one retention.")
with rec2:
    render_notice("amber", "2", "Diagnose delivery reliability", f"Late orders averaged {late['average_review_score']:.2f} stars versus {on_time['average_review_score']:.2f} on time; start with high-volume states and categories below benchmark.")
with rec3:
    render_notice("navy", "3", "Monitor peak-period risk", f"November 2017 reached {brl(float(peak['item_gmv_brl']), 2)} GMV while on-time delivery fell to {peak['on_time_delivery_rate_pct']:.2f}%.")

render_section("Credibility", "Grain, quality, and limitations are visible")
q1, q2, q3 = st.columns(3)
q1.metric("Automated quality checks", f"{len(quality)}")
q2.metric("Passed", f"{int(quality['check_status'].eq('PASS').sum())}")
q3.metric("Documented exception", f"{int(quality.loc[quality['check_status'].eq('REVIEW'), 'issue_count'].sum())} rows")
render_notice(
    "navy",
    "1:N",
    "The grain rule protecting every KPI",
    "Order items, payments, and reviews are aggregated independently to one row per order before joining. Category analysis uses one row per order-category. This prevents many-to-many multiplication of GMV and payment value.",
)
render_notice(
    "amber",
    "!",
    "Interpretation boundary",
    "Item GMV is marketplace transaction value, not Olist accounting revenue or profit. Delivery-review relationships and cohort patterns are descriptive rather than causal.",
)

render_footer()
