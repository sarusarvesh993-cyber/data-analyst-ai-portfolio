"""Interactive customer segmentation and campaign-planning dashboard."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.segmentation import (
    audience_export,
    campaign_record,
    filter_customers,
    gbp,
    load_outputs as load_segmentation_outputs,
)
from portfolio_app.ui import (
    GOLD,
    NAVY,
    NAVY_DARK,
    PALETTE,
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

configure_page("Customer Segmentation", "🎯")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 05 · Segmentation & campaign analytics",
    "Customer Segmentation Command Center",
    "Turn transaction history into transparent RFM audiences, validate a clustering challenger, and design measurable campaigns with financial guardrails.",
    [
        "UCI Online Retail",
        "4,338 customers",
        "RFM baseline",
        "K-means challenger",
        "Power BI companion",
    ],
)
render_notice(
    "navy",
    "RFM",
    "Real, anonymized transaction data",
    "The project uses the UCI Online Retail workbook. Completed-purchase value is historical sales value—not profit—and customer IDs are anonymous source identifiers rather than contactable personal data.",
)

PROJECT_DIR = Path(__file__).resolve().parents[1] / "05-customer-segmentation"
OUTPUT_DIR = PROJECT_DIR / "outputs"
POWER_BI_DIR = PROJECT_DIR / "power-bi"


@st.cache_data
def get_segmentation_outputs() -> dict[str, pd.DataFrame]:
    """Load the reviewed Project 05 tables under a page-specific cache key."""
    return load_segmentation_outputs(OUTPUT_DIR)


outputs = get_segmentation_outputs()
kpis = outputs["kpis"].iloc[0]
customers = outputs["customers"]
segments = outputs["segments"].sort_values("priority")
clusters = outputs["clusters"]
comparison = outputs["comparison"]
validation = outputs["validation"]
monthly = outputs["monthly"]
quality = outputs["quality"]
metadata = outputs["metadata"]

# Portfolio-level metrics: six reviewed measures at the customer and order grains.
top1, top2, top3, top4, top5, top6 = st.columns(6)
top1.metric("Customers", f"{int(kpis['customers']):,}")
top2.metric("Purchase value", gbp(float(kpis["gross_revenue"]), 2))
top3.metric("Completed invoices", f"{int(kpis['orders']):,}")
top4.metric("Returned value", gbp(float(kpis["returned_value"]), 0))
top5.metric("Net-value proxy", gbp(float(kpis["net_revenue_proxy"]), 2))
top6.metric("Repeat customers", f"{kpis['repeat_customer_rate_pct']:.1f}%")

render_section(
    "Segmentation workspace",
    "Move from portfolio value to campaign action",
    "Rules-based RFM is the primary activation layer. K-means is retained as a validated challenger—not presented as evidence of campaign impact.",
)
overview_tab, explorer_tab, model_tab, campaign_tab, methods_tab = st.tabs(
    [
        "Executive overview",
        "Segment explorer",
        "RFM vs clustering",
        "Campaign planner",
        "Methods & Power BI",
    ]
)

with overview_tab:
    left, right = st.columns([1.45, 1])
    with left:
        trend = go.Figure()
        trend.add_trace(
            go.Bar(
                x=monthly["purchase_month"],
                y=monthly["revenue"],
                name="Purchase value",
                marker_color="rgba(15,138,123,.30)",
                hovertemplate="%{x|%b %Y}<br>Value £%{y:,.0f}<extra></extra>",
            )
        )
        trend.add_trace(
            go.Scatter(
                x=monthly["purchase_month"],
                y=monthly["revenue"],
                name="Monthly trend",
                mode="lines+markers",
                line=dict(color=TEAL, width=3),
                marker=dict(color=NAVY, size=7),
                hovertemplate="%{x|%b %Y}<br>Value £%{y:,.0f}<extra></extra>",
            )
        )
        trend.update_layout(
            title="Monthly completed-purchase value",
            xaxis_title="Purchase month",
            yaxis_title="Pounds sterling (£)",
            hovermode="x unified",
        )
        style_plotly(trend, height=455, show_legend=False)
        st.plotly_chart(trend, width="stretch")

    with right:
        segment_bar = px.bar(
            segments.sort_values("revenue"),
            x="revenue",
            y="rfm_segment",
            orientation="h",
            color="rfm_segment",
            color_discrete_sequence=PALETTE + ["#8FB9A8"],
            title="Historical value by activation segment",
            labels={"revenue": "Purchase value (£)", "rfm_segment": ""},
            custom_data=["customers", "revenue_share_pct"],
        )
        segment_bar.update_traces(
            hovertemplate=(
                "%{y}<br>Value £%{x:,.0f}<br>Customers %{customdata[0]:,.0f}"
                "<br>Value share %{customdata[1]:.1f}%<extra></extra>"
            )
        )
        segment_bar.update_layout(showlegend=False)
        style_plotly(segment_bar, height=455, show_legend=False)
        st.plotly_chart(segment_bar, width="stretch")

    champions = campaign_record(segments, "Champions")
    at_risk = campaign_record(segments, "At Risk")
    hibernating = campaign_record(segments, "Hibernating")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Champions value share", f"{champions['revenue_share_pct']:.1f}%")
    e2.metric("Champions customers", f"{int(champions['customers']):,}")
    e3.metric("At-Risk historical value", gbp(float(at_risk["revenue"]), 2))
    e4.metric("Hibernating customer share", f"{hibernating['customer_share_pct']:.1f}%")

    display_segments = segments[
        [
            "priority",
            "rfm_segment",
            "customers",
            "customer_share_pct",
            "revenue",
            "revenue_share_pct",
            "median_recency_days",
            "repeat_customer_rate_pct",
            "objective",
        ]
    ].rename(
        columns={
            "priority": "Priority",
            "rfm_segment": "Segment",
            "customers": "Customers",
            "customer_share_pct": "Customer share %",
            "revenue": "Purchase value (£)",
            "revenue_share_pct": "Value share %",
            "median_recency_days": "Median recency",
            "repeat_customer_rate_pct": "Repeat rate %",
            "objective": "Campaign objective",
        }
    )
    st.dataframe(
        display_segments,
        hide_index=True,
        width="stretch",
        column_config={
            "Purchase value (£)": st.column_config.NumberColumn(format="£%,.0f"),
            "Customer share %": st.column_config.NumberColumn(format="%.1f%%"),
            "Value share %": st.column_config.NumberColumn(format="%.1f%%"),
            "Repeat rate %": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    brief = generate_insights(
        {
            "headline": (
                f"{int(champions['customers']):,} Champions generated "
                f"{champions['revenue_share_pct']:.1f}% of historical completed-purchase value, "
                f"while the At Risk audience represents {gbp(float(at_risk['revenue']), 2)}."
            ),
            "drivers": [
                f"The repeat-customer rate is {kpis['repeat_customer_rate_pct']:.1f}%",
                f"At Risk customers have median recency of {at_risk['median_recency_days']:.1f} days",
                f"Hibernating customers are {hibernating['customer_share_pct']:.1f}% of customers but only {hibernating['revenue_share_pct']:.1f}% of value",
            ],
            "recommendation": (
                "Protect Champions without blanket discounting, run a randomized At Risk win-back test with a no-contact holdout, and suppress persistent low-value non-responders."
            ),
        }
    )
    with st.expander("AI-assisted executive brief"):
        st.markdown(brief)
        st.caption(
            "The generator receives only the reviewed metrics shown above and falls back to authored text when no API token is configured."
        )

with explorer_tab:
    control1, control2, control3 = st.columns([1.25, 1.25, 1])
    segment_options = segments["rfm_segment"].tolist()
    selected_segments = control1.multiselect(
        "RFM segments",
        segment_options,
        default=segment_options,
        key="segment_explorer_segments",
    )
    country_options = sorted(customers["country"].dropna().unique().tolist())
    selected_countries = control2.multiselect(
        "Countries",
        country_options,
        default=[],
        placeholder="All countries",
    )
    minimum_value = control3.number_input(
        "Minimum customer value (£)",
        min_value=0.0,
        value=0.0,
        step=100.0,
    )
    filtered = filter_customers(
        customers,
        segments=selected_segments,
        countries=selected_countries,
        minimum_value=float(minimum_value),
    )

    filtered_value = float(filtered["monetary_value"].sum())
    filtered_orders = int(filtered["frequency"].sum())
    filtered_recency = float(filtered["recency_days"].median()) if len(filtered) else 0.0
    filtered_repeat = (
        100 * float(filtered["is_repeat_customer"].mean()) if len(filtered) else 0.0
    )
    x1, x2, x3, x4, x5 = st.columns(5)
    x1.metric("Selected customers", f"{len(filtered):,}")
    x2.metric("Historical value", gbp(filtered_value, 2))
    x3.metric("Completed invoices", f"{filtered_orders:,}")
    x4.metric("Median recency", f"{filtered_recency:.0f} days")
    x5.metric("Repeat rate", f"{filtered_repeat:.1f}%")

    if filtered.empty:
        render_notice(
            "amber",
            "!",
            "No customers match these controls",
            "Broaden the segment or country selections, or lower the minimum customer value.",
        )
    else:
        chart_frame = filtered.sample(min(2500, len(filtered)), random_state=42)
        landscape = px.scatter(
            chart_frame,
            x="recency_days",
            y="monetary_value",
            color="rfm_segment",
            size="frequency",
            size_max=34,
            log_y=True,
            hover_data={
                "customer_id": True,
                "country": True,
                "frequency": True,
                "average_order_value": ":.2f",
                "cluster_name": True,
            },
            color_discrete_sequence=PALETTE + ["#8FB9A8"],
            title="Customer RFM landscape",
            labels={
                "recency_days": "Days since last purchase",
                "monetary_value": "Historical value (£, log scale)",
                "rfm_segment": "RFM segment",
                "frequency": "Invoices",
            },
        )
        style_plotly(landscape, height=520)
        st.plotly_chart(landscape, width="stretch")

    customer_display = filtered[
        [
            "customer_id",
            "country",
            "rfm_segment",
            "cluster_name",
            "recency_days",
            "frequency",
            "monetary_value",
            "average_order_value",
            "return_rate_pct",
            "rfm_score",
        ]
    ].rename(
        columns={
            "customer_id": "Customer ID",
            "country": "Country",
            "rfm_segment": "RFM segment",
            "cluster_name": "Cluster",
            "recency_days": "Recency days",
            "frequency": "Invoices",
            "monetary_value": "Historical value (£)",
            "average_order_value": "Average invoice value (£)",
            "return_rate_pct": "Return rate %",
            "rfm_score": "RFM score",
        }
    )
    st.dataframe(
        customer_display,
        hide_index=True,
        width="stretch",
        height=430,
        column_config={
            "Historical value (£)": st.column_config.NumberColumn(format="£%,.2f"),
            "Average invoice value (£)": st.column_config.NumberColumn(format="£%,.2f"),
            "Return rate %": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )
    st.caption(
        "Customer IDs are anonymized source identifiers. The table contains no names, email addresses, telephone numbers, or postal addresses."
    )

with model_tab:
    selected_model = validation.loc[validation["selected_model"]].iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Selected clusters", f"{int(selected_model['n_clusters'])}")
    m2.metric("Silhouette score", f"{selected_model['silhouette_score']:.3f}")
    m3.metric("Seed stability ARI", f"{selected_model['seed_stability_ari']:.3f}")
    m4.metric(
        "Smallest cluster",
        f"{selected_model['minimum_cluster_share_pct']:.2f}%",
    )

    validation_chart = go.Figure()
    validation_chart.add_trace(
        go.Scatter(
            x=validation["n_clusters"],
            y=validation["silhouette_score"],
            mode="lines+markers",
            name="Silhouette",
            line=dict(color=TEAL, width=3),
            marker=dict(size=9),
            hovertemplate="k=%{x}<br>Silhouette %{y:.3f}<extra></extra>",
        )
    )
    validation_chart.add_trace(
        go.Scatter(
            x=validation["n_clusters"],
            y=validation["seed_stability_ari"],
            mode="lines+markers",
            name="Seed stability (ARI)",
            line=dict(color=PURPLE, width=3),
            marker=dict(size=9, symbol="square"),
            hovertemplate="k=%{x}<br>Mean ARI %{y:.3f}<extra></extra>",
        )
    )
    validation_chart.add_vline(
        x=int(selected_model["n_clusters"]),
        line_dash="dash",
        line_color=GOLD,
        annotation_text="Selected k",
    )
    validation_chart.update_layout(
        title="K-means separation and seed stability",
        xaxis_title="Number of clusters",
        yaxis_title="Score",
        yaxis_range=[0, 1.05],
    )
    style_plotly(validation_chart, height=470)
    st.plotly_chart(validation_chart, width="stretch")

    validation_display = validation[
        [
            "n_clusters",
            "silhouette_score",
            "calinski_harabasz_score",
            "davies_bouldin_score",
            "seed_stability_ari",
            "minimum_cluster_share_pct",
            "selected_model",
        ]
    ].rename(
        columns={
            "n_clusters": "Clusters",
            "silhouette_score": "Silhouette",
            "calinski_harabasz_score": "Calinski–Harabasz",
            "davies_bouldin_score": "Davies–Bouldin",
            "seed_stability_ari": "Seed stability ARI",
            "minimum_cluster_share_pct": "Smallest cluster %",
            "selected_model": "Selected",
        }
    )
    st.dataframe(
        validation_display,
        hide_index=True,
        width="stretch",
        column_config={
            "Silhouette": st.column_config.NumberColumn(format="%.3f"),
            "Calinski–Harabasz": st.column_config.NumberColumn(format="%.1f"),
            "Davies–Bouldin": st.column_config.NumberColumn(format="%.3f"),
            "Seed stability ARI": st.column_config.NumberColumn(format="%.3f"),
            "Smallest cluster %": st.column_config.NumberColumn(format="%.2f%%"),
            "Selected": st.column_config.CheckboxColumn(),
        },
    )

    heatmap_frame = comparison.set_index("rfm_segment")
    heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_frame.to_numpy(),
            x=heatmap_frame.columns,
            y=heatmap_frame.index,
            text=np.round(heatmap_frame.to_numpy(), 1),
            texttemplate="%{text:.1f}%",
            colorscale=[[0, "#F2FAF8"], [0.4, "#BDE9E1"], [1, NAVY]],
            colorbar=dict(title="Row share %"),
            hovertemplate=(
                "RFM %{y}<br>Cluster %{x}<br>Customers in row %{z:.1f}%<extra></extra>"
            ),
        )
    )
    heatmap.update_layout(
        title="How rules-based segments map to behavioral clusters",
        xaxis_title="Named K-means cluster",
        yaxis_title="RFM activation segment",
    )
    style_plotly(heatmap, height=500, show_legend=False)
    st.plotly_chart(heatmap, width="stretch")

    cluster_display = clusters[
        [
            "cluster_name",
            "customers",
            "customer_share_pct",
            "revenue",
            "revenue_share_pct",
            "median_recency_days",
            "median_frequency",
            "median_monetary_value",
        ]
    ].rename(
        columns={
            "cluster_name": "Cluster",
            "customers": "Customers",
            "customer_share_pct": "Customer share %",
            "revenue": "Historical value (£)",
            "revenue_share_pct": "Value share %",
            "median_recency_days": "Median recency",
            "median_frequency": "Median invoices",
            "median_monetary_value": "Median value (£)",
        }
    )
    st.dataframe(
        cluster_display,
        hide_index=True,
        width="stretch",
        column_config={
            "Customer share %": st.column_config.NumberColumn(format="%.1f%%"),
            "Historical value (£)": st.column_config.NumberColumn(format="£%,.0f"),
            "Value share %": st.column_config.NumberColumn(format="%.1f%%"),
            "Median value (£)": st.column_config.NumberColumn(format="£%,.0f"),
        },
    )
    render_notice(
        "teal",
        "5",
        "Why the five-cluster challenger was selected",
        "The two-cluster option has stronger silhouette separation but is too broad for campaign activation. Selection was restricted to 3–6 clusters with at least 80% seed stability and 5% minimum size, then balanced separation, stability, cluster size, and compactness. RFM remains primary because its rules are easier to explain and operationalize.",
    )

with campaign_tab:
    campaign_order = segments["rfm_segment"].tolist()
    chosen_segment = st.selectbox(
        "Choose an activation audience",
        campaign_order,
        index=campaign_order.index("At Risk"),
    )
    strategy = campaign_record(segments, chosen_segment)
    audience = audience_export(customers, chosen_segment)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Audience size", f"{len(audience):,}")
    c2.metric("Historical value", gbp(float(strategy["revenue"]), 2))
    c3.metric("Median recency", f"{strategy['median_recency_days']:.1f} days")
    c4.metric("Average return rate", f"{strategy['average_return_rate_pct']:.2f}%")

    st.markdown(
        f"""
        <div class="strategy-grid">
            <div class="strategy-card"><div class="strategy-label">Objective</div><div class="strategy-value">{strategy['objective']}</div></div>
            <div class="strategy-card"><div class="strategy-label">Treatment</div><div class="strategy-value">{strategy['treatment']}</div></div>
            <div class="strategy-card"><div class="strategy-label">Channel</div><div class="strategy-value">{strategy['channel']}</div></div>
            <div class="strategy-card"><div class="strategy-label">Primary KPI</div><div class="strategy-value">{strategy['primary_kpi']}</div></div>
            <div class="strategy-card"><div class="strategy-label">Financial guardrail</div><div class="strategy-value">{strategy['guardrail']}</div></div>
            <div class="strategy-card"><div class="strategy-label">Experiment design</div><div class="strategy-value">{strategy['experiment']}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_notice(
        "amber",
        "A/B",
        "Descriptive segments do not establish treatment effects",
        "Randomize eligible customers before contact, preserve the planned holdout, define the measurement window in advance, and evaluate incremental value after incentive and return costs—not open rate alone.",
    )
    st.download_button(
        "Download anonymized campaign audience",
        data=audience.to_csv(index=False).encode("utf-8"),
        file_name=f"{chosen_segment.lower().replace(' ', '_')}_audience.csv",
        mime="text/csv",
        width="stretch",
    )
    st.caption(
        "The export intentionally excludes product descriptions and contains only anonymized customer IDs plus approved behavioral fields."
    )

with methods_tab:
    raw_rows = int(
        quality.loc[quality["check_name"].eq("raw_rows"), "issue_count"].iloc[0]
    )
    purchase_rows = int(
        quality.loc[
            quality["check_name"].eq("valid_identified_purchase_rows"), "issue_count"
        ].iloc[0]
    )
    review_checks = int(quality["check_status"].eq("REVIEW").sum())
    q1, q2, q3 = st.columns(3)
    q1.metric("Source invoice lines", f"{raw_rows:,}")
    q2.metric("Valid purchase lines", f"{purchase_rows:,}")
    q3.metric("Checks requiring context", f"{review_checks}")

    st.markdown("#### Reconciliation and quality checks")
    st.dataframe(quality, hide_index=True, width="stretch")
    render_notice(
        "navy",
        "99",
        "Outlier treatment is limited to the clustering model",
        "Recency, frequency, and monetary value are capped at their 99th percentiles, transformed with log1p, and standardized before K-means. Reported RFM values and historical totals remain uncapped, so model preparation does not rewrite business KPIs.",
    )
    st.dataframe(
        metadata.rename(
            columns={
                "feature": "Clustering feature",
                "winsor_cap_99pct": "99th-percentile cap",
            }
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "99th-percentile cap": st.column_config.NumberColumn(format="%,.2f")
        },
    )

    render_section(
        "Power BI companion",
        "Desktop-ready model, measures, theme, and layout target",
        "The live interactive product remains Streamlit. These reviewed artifacts make the same outputs reproducible in free Power BI Desktop without falsely claiming an unvalidated proprietary .pbix binary.",
    )
    st.image(
        PROJECT_DIR / "assets" / "power_bi_companion.png",
        caption="Reproducible Power BI executive-page layout target",
        width="stretch",
    )
    p1, p2, p3 = st.columns(3)
    p1.download_button(
        "Download Power BI theme",
        data=(POWER_BI_DIR / "theme.json").read_bytes(),
        file_name="customer_segmentation_theme.json",
        mime="application/json",
        width="stretch",
    )
    p2.download_button(
        "Download reviewed DAX measures",
        data=(POWER_BI_DIR / "measures.dax").read_bytes(),
        file_name="customer_segmentation_measures.dax",
        mime="text/plain",
        width="stretch",
    )
    p3.download_button(
        "Download Desktop build guide",
        data=(POWER_BI_DIR / "README.md").read_bytes(),
        file_name="power_bi_desktop_build_guide.md",
        mime="text/markdown",
        width="stretch",
    )
    st.caption(
        f"Analysis window: {kpis['analysis_start_date']} to {kpis['analysis_end_date']} · Snapshot: {kpis['snapshot_date']} · Identified sales-value coverage: {kpis['identified_sales_value_coverage_pct']:.2f}%"
    )

render_footer()
