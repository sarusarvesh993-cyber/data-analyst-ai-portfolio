"""Interactive dashboard for the Olist e-commerce SQL project."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.ecommerce import brl, cohort_matrix, load_outputs, weighted_retention
from portfolio_app.ui import (
    GOLD,
    NAVY,
    PURPLE,
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
from utils.ai_insights import generate_insights

configure_page("E-commerce SQL Analytics", "🛒")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 04 · SQL & marketplace analytics",
    "E-commerce Revenue & Cohort Analysis",
    "Trace marketplace value, customer repeat behavior, delivery reliability, and category performance across a relational order system.",
    ["DuckDB SQL", "100K orders", "8 source tables", "Cohort retention", "Data-quality checks"],
)
render_notice(
    "navy",
    "DB",
    "Real anonymized marketplace data",
    "The analysis uses the Olist Brazilian E-Commerce dataset. Monetary values are BRL; item GMV is marketplace sales volume, not Olist accounting revenue or profit.",
)

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "04-ecommerce-sql" / "outputs"
SQL_DIR = Path(__file__).resolve().parents[1] / "04-ecommerce-sql" / "sql"


@st.cache_data
def get_outputs() -> dict[str, pd.DataFrame]:
    return load_outputs(OUTPUT_DIR)


outputs = get_outputs()
kpis = outputs["kpis"].iloc[0]
monthly = outputs["monthly"]
cohorts = outputs["cohorts"]
states = outputs["states"]
delivery = outputs["delivery"]
categories = outputs["categories"]
quality = outputs["quality"]

first_month = monthly["purchase_month"].min().strftime("%Y-%m")
last_month = monthly["purchase_month"].max().strftime("%Y-%m")
month_options = monthly["purchase_month"].dt.strftime("%Y-%m").tolist()
selected_months = st.sidebar.select_slider(
    "Monthly analysis window",
    options=month_options,
    value=(first_month, last_month),
)
start_month, end_month = pd.to_datetime(selected_months[0]), pd.to_datetime(selected_months[1])
monthly_view = monthly.loc[monthly["purchase_month"].between(start_month, end_month)]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Delivered orders", f"{int(kpis['delivered_orders']):,}")
k2.metric("Item GMV", brl(float(kpis["item_gmv_brl"])))
k3.metric("Average order GMV", brl(float(kpis["average_order_gmv_brl"]), 0))
k4.metric("Repeat customers", f"{kpis['repeat_customer_rate_pct']:.1f}%")
k5.metric("On-time delivery", f"{kpis['on_time_delivery_rate_pct']:.1f}%")

render_section(
    "Marketplace workspace",
    "Follow value, retention, and operational experience",
    "The SQL outputs use explicit order and order-category grains so one-to-many joins do not inflate sales value.",
)
overview_tab, cohort_tab, delivery_tab, category_tab, sql_tab = st.tabs(
    ["Executive trend", "Cohort retention", "Delivery experience", "Categories", "SQL & quality"]
)

with overview_tab:
    peak = monthly_view.loc[monthly_view["item_gmv_brl"].idxmax()]
    trend = go.Figure()
    trend.add_trace(
        go.Bar(
            x=monthly_view["purchase_month"],
            y=monthly_view["item_gmv_brl"],
            name="Item GMV",
            marker_color="rgba(15,138,123,.32)",
            hovertemplate="%{x|%b %Y}<br>GMV R$%{y:,.0f}<extra></extra>",
        )
    )
    trend.add_trace(
        go.Scatter(
            x=monthly_view["purchase_month"],
            y=monthly_view["item_gmv_brl"],
            name="GMV trend",
            mode="lines+markers",
            line=dict(color=TEAL, width=3),
            marker=dict(size=7, color=NAVY),
            hovertemplate="%{x|%b %Y}<br>GMV R$%{y:,.0f}<extra></extra>",
        )
    )
    trend.update_layout(
        title="Monthly delivered-order GMV",
        xaxis_title="Purchase month",
        yaxis_title="Brazilian reais (BRL)",
        hovermode="x unified",
    )
    style_plotly(trend, height=470, show_legend=False)
    st.plotly_chart(trend, width="stretch")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Peak month", peak["purchase_month"].strftime("%b %Y"))
    c2.metric("Peak monthly GMV", brl(float(peak["item_gmv_brl"])))
    c3.metric("Peak delivered orders", f"{int(peak['delivered_orders']):,}")
    c4.metric("Peak on-time rate", f"{peak['on_time_delivery_rate_pct']:.1f}%")

    customer_mix = monthly_view.melt(
        id_vars="purchase_month",
        value_vars=["new_customers", "returning_customers"],
        var_name="customer_type",
        value_name="customers",
    )
    customer_mix["customer_type"] = customer_mix["customer_type"].map(
        {"new_customers": "New customers", "returning_customers": "Returning customers"}
    )
    mix_chart = px.area(
        customer_mix,
        x="purchase_month",
        y="customers",
        color="customer_type",
        title="Monthly active-customer mix",
        color_discrete_map={"New customers": NAVY, "Returning customers": GOLD},
        labels={"purchase_month": "Month", "customers": "Customers", "customer_type": "Type"},
    )
    style_plotly(mix_chart, height=420)
    st.plotly_chart(mix_chart, width="stretch")

    late = delivery.set_index("delivery_status").loc["Late"]
    on_time = delivery.set_index("delivery_status").loc["On time"]
    top_category = categories.iloc[0]
    brief = generate_insights(
        {
            "headline": (
                f"Delivered orders generated {brl(float(kpis['item_gmv_brl']))} in item GMV. "
                f"Only {kpis['repeat_customer_rate_pct']:.1f}% of customers placed at least two delivered orders."
            ),
            "drivers": [
                f"Peak monthly GMV occurred in {peak['purchase_month']:%B %Y}",
                f"Late deliveries averaged {late['average_review_score']:.2f} stars versus {on_time['average_review_score']:.2f} on time",
                f"{top_category['category']} led categories with {brl(float(top_category['item_gmv_brl']))}",
            ],
            "recommendation": (
                "Prioritize repeat-purchase measurement and targeted reactivation, while focusing delivery reliability work on states and categories with lower on-time performance."
            ),
        }
    )
    with st.expander("AI-assisted executive brief"):
        st.markdown(brief)

with cohort_tab:
    maturity = st.slider("Months after first purchase", 3, 18, 12)
    matrix = cohort_matrix(cohorts, max_month=maturity)
    month_one = weighted_retention(cohorts, 1)
    month_three = weighted_retention(cohorts, 3)
    r1, r2, r3 = st.columns(3)
    r1.metric("Repeat-customer rate", f"{kpis['repeat_customer_rate_pct']:.2f}%")
    r2.metric("Weighted month-1 retention", f"{month_one:.2f}%")
    r3.metric("Weighted month-3 retention", f"{month_three:.2f}%")

    heatmap = go.Figure(
        data=go.Heatmap(
            z=matrix.to_numpy(),
            x=matrix.columns,
            y=matrix.index,
            text=np.where(np.isnan(matrix.to_numpy()), "", np.char.add(np.round(matrix.to_numpy(), 2).astype(str), "%")),
            texttemplate="%{text}",
            colorscale=[[0, "#F2FAF8"], [0.15, "#BDE9E1"], [0.5, TEAL], [1, NAVY]],
            zmin=0,
            zmax=2,
            colorbar=dict(title="Retention %"),
            hovertemplate="Cohort %{y}<br>Age %{x}<br>Retention %{z:.2f}%<extra></extra>",
        )
    )
    heatmap.update_layout(title="Monthly retention by first-purchase cohort")
    style_plotly(heatmap, height=590, show_legend=False)
    st.plotly_chart(heatmap, width="stretch")
    render_notice(
        "amber",
        "!",
        "Repeat behavior is very limited in this observation window",
        "Month-zero cells are 100% by definition and are clipped in the color scale so later-month differences remain visible. Low repeat rates may reflect product mix, marketplace behavior, identity limitations, or weak retention—not one proven cause.",
    )

with delivery_tab:
    experience = delivery.set_index("delivery_status")
    on_time = experience.loc["On time"]
    late = experience.loc["Late"]
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("On-time review", f"{on_time['average_review_score']:.2f} / 5")
    d2.metric("Late review", f"{late['average_review_score']:.2f} / 5")
    d3.metric("Late low-review rate", f"{late['low_review_rate_pct']:.1f}%")
    d4.metric("Average late days", f"{late['average_late_days']:.1f}")

    left, right = st.columns(2)
    review_chart = px.bar(
        delivery,
        x="delivery_status",
        y=["five_star_review_rate_pct", "low_review_rate_pct"],
        barmode="group",
        title="Review outcomes by delivery status",
        labels={"value": "Share of reviews (%)", "variable": "Review outcome", "delivery_status": "Delivery"},
        color_discrete_sequence=[TEAL, "#E26D5A"],
    )
    review_chart.for_each_trace(
        lambda trace: trace.update(
            name={
                "five_star_review_rate_pct": "Five-star reviews",
                "low_review_rate_pct": "One- or two-star reviews",
            }.get(trace.name, trace.name)
        )
    )
    style_plotly(review_chart, height=440)
    left.plotly_chart(review_chart, width="stretch")

    state_chart = px.scatter(
        states,
        x="on_time_delivery_rate_pct",
        y="average_review_score",
        size="item_gmv_brl",
        color="average_delivery_days",
        hover_name="customer_state",
        title="State delivery reliability and reviews",
        labels={
            "on_time_delivery_rate_pct": "On-time delivery (%)",
            "average_review_score": "Average review score",
            "average_delivery_days": "Delivery days",
            "item_gmv_brl": "Item GMV",
        },
        color_continuous_scale=[[0, TEAL], [0.55, GOLD], [1, "#E26D5A"]],
        size_max=42,
    )
    style_plotly(state_chart, height=440, show_legend=False)
    right.plotly_chart(state_chart, width="stretch")

    lowest = states.nsmallest(5, "on_time_delivery_rate_pct")
    render_notice(
        "teal",
        "→",
        "Operational priority",
        "Late orders have materially lower review outcomes. Start root-cause work with high-volume states below the portfolio on-time rate, then separate carrier, seller, distance, and promise-setting effects.",
    )
    st.dataframe(
        lowest[
            [
                "customer_state",
                "delivered_orders",
                "on_time_delivery_rate_pct",
                "average_delivery_days",
                "average_review_score",
            ]
        ].rename(
            columns={
                "customer_state": "State",
                "delivered_orders": "Orders",
                "on_time_delivery_rate_pct": "On-time %",
                "average_delivery_days": "Delivery days",
                "average_review_score": "Review score",
            }
        ),
        hide_index=True,
        width="stretch",
    )

with category_tab:
    top_n = st.slider("Number of categories", 8, 25, 15)
    category_view = categories.head(top_n).sort_values("item_gmv_brl")
    cat_bar = px.bar(
        category_view,
        x="item_gmv_brl",
        y="category",
        orientation="h",
        color="item_gmv_brl",
        title=f"Top {top_n} categories by delivered-order GMV",
        labels={"item_gmv_brl": "Item GMV (BRL)", "category": "Category"},
        color_continuous_scale=[[0, "#BDE9E1"], [1, TEAL]],
    )
    cat_bar.update_coloraxes(showscale=False)
    style_plotly(cat_bar, height=max(470, 30 * top_n), show_legend=False)
    st.plotly_chart(cat_bar, width="stretch")

    scatter = px.scatter(
        categories,
        x="item_gmv_brl",
        y="average_review_score",
        size="delivered_orders",
        color="on_time_delivery_rate_pct",
        hover_name="category",
        title="Category value, delivery, and customer experience",
        labels={
            "item_gmv_brl": "Item GMV (BRL)",
            "average_review_score": "Average review score",
            "delivered_orders": "Delivered orders",
            "on_time_delivery_rate_pct": "On-time %",
        },
        color_continuous_scale=[[0, "#E26D5A"], [0.55, GOLD], [1, TEAL]],
        size_max=44,
    )
    style_plotly(scatter, height=480, show_legend=False)
    st.plotly_chart(scatter, width="stretch")
    st.dataframe(
        categories.head(top_n)[
            [
                "category",
                "delivered_orders",
                "items_sold",
                "item_gmv_brl",
                "on_time_delivery_rate_pct",
                "average_review_score",
            ]
        ].rename(
            columns={
                "category": "Category",
                "delivered_orders": "Orders",
                "items_sold": "Items",
                "item_gmv_brl": "Item GMV (BRL)",
                "on_time_delivery_rate_pct": "On-time %",
                "average_review_score": "Review score",
            }
        ),
        hide_index=True,
        width="stretch",
    )

with sql_tab:
    render_notice(
        "navy",
        "1:N",
        "The grain rule that protects every KPI",
        "Items, payments, and reviews are each rolled up to one row per order before joining. Category analysis uses one row per order-category. This prevents many-to-many multiplication of value and reviews.",
    )
    query_labels = {
        "Order-safe marts": "01_marts.sql",
        "Executive KPIs": "02_executive_kpis.sql",
        "Monthly performance": "03_monthly_performance.sql",
        "Cohort retention": "04_cohort_retention.sql",
        "Delivery by state": "05_delivery_by_state.sql",
        "Category performance": "07_category_performance.sql",
        "Data-quality checks": "08_data_quality.sql",
    }
    selected_query = st.selectbox("Review a SQL file", list(query_labels))
    sql_text = (SQL_DIR / query_labels[selected_query]).read_text(encoding="utf-8")
    st.code(sql_text, language="sql", line_numbers=True)

    passed = int(quality["check_status"].eq("PASS").sum())
    review_count = int(quality["check_status"].eq("REVIEW").sum())
    q1, q2, q3 = st.columns(3)
    q1.metric("Quality checks", f"{len(quality)}")
    q2.metric("Passed", f"{passed}")
    q3.metric("Needs review", f"{review_count}")
    st.dataframe(quality, hide_index=True, width="stretch")
    render_notice(
        "amber",
        "8",
        "Eight delivered orders have no customer-delivery timestamp",
        "They remain in delivered-order value metrics but are excluded from on-time and delivery-duration calculations through NULL-aware aggregation.",
    )

render_footer()
