"""Standalone Plotly Dash command center for the Olist SQL project."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from portfolio_app.ecommerce import brl, cohort_matrix, load_outputs, weighted_retention

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "04-ecommerce-sql" / "outputs"
SQL_DIR = REPO_ROOT / "04-ecommerce-sql" / "sql"
ASSETS_DIR = REPO_ROOT / "assets"

NAVY = "#102A43"
NAVY_MID = "#173B63"
TEAL = "#0F8A7B"
TEAL_BRIGHT = "#18B7A4"
GOLD = "#F4A340"
RED = "#E26D5A"
BLUE = "#2B6F92"
MUTED = "#63788B"
LINE = "#DCE8E5"

GRAPH_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "responsive": True,
}

SQL_FILES = {
    "Order-safe marts": "01_marts.sql",
    "Executive KPIs": "02_executive_kpis.sql",
    "Monthly performance": "03_monthly_performance.sql",
    "Cohort retention": "04_cohort_retention.sql",
    "Delivery by state": "05_delivery_by_state.sql",
    "Delivery experience": "06_delivery_experience.sql",
    "Category performance": "07_category_performance.sql",
    "Data-quality checks": "08_data_quality.sql",
}


def _style_figure(
    figure: go.Figure,
    *,
    height: int = 360,
    show_legend: bool = True,
    margin: dict[str, int] | None = None,
) -> go.Figure:
    """Apply the command center's chart system."""
    figure.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font={"family": "Arial, sans-serif", "color": NAVY, "size": 11},
        margin=margin or {"l": 54, "r": 24, "t": 32, "b": 46},
        colorway=[TEAL, NAVY_MID, GOLD, RED, BLUE],
        hoverlabel={"bgcolor": "#FFFFFF", "font_color": NAVY},
        hovermode="closest",
        showlegend=show_legend,
        legend={"orientation": "h", "y": 1.09, "x": 0},
    )
    figure.update_xaxes(showgrid=False, linecolor=LINE, zeroline=False)
    figure.update_yaxes(gridcolor="#E8F0EE", linecolor=LINE, zeroline=False)
    return figure


def filter_monthly(monthly: pd.DataFrame, start_index: int, end_index: int) -> pd.DataFrame:
    """Slice monthly output using inclusive, validated month indexes."""
    if monthly.empty:
        raise ValueError("monthly output cannot be empty")
    start = max(0, min(int(start_index), len(monthly) - 1))
    end = max(start, min(int(end_index), len(monthly) - 1))
    return monthly.iloc[start : end + 1].copy()


def build_monthly_figure(monthly: pd.DataFrame) -> go.Figure:
    """Build the main GMV trend with the peak month called out."""
    peak = monthly.loc[monthly["item_gmv_brl"].idxmax()]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=monthly["purchase_month"],
            y=monthly["item_gmv_brl"],
            mode="lines+markers",
            name="Item GMV",
            line={"color": TEAL, "width": 3},
            marker={"size": 7, "color": NAVY},
            fill="tozeroy",
            fillcolor="rgba(15,138,123,.10)",
            hovertemplate="%{x|%b %Y}<br>GMV R$%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[peak["purchase_month"]],
            y=[peak["item_gmv_brl"]],
            mode="markers",
            name="Peak month",
            marker={"size": 13, "color": GOLD, "line": {"color": "#FFFFFF", "width": 2}},
            hovertemplate=(
                f"{peak['purchase_month']:%b %Y}<br>GMV R${peak['item_gmv_brl']:,.0f}"
                f"<br>{int(peak['delivered_orders']):,} delivered orders<extra></extra>"
            ),
        )
    )
    figure.add_annotation(
        x=peak["purchase_month"],
        y=peak["item_gmv_brl"],
        text=f"Peak · {peak['purchase_month']:%b %Y}",
        showarrow=True,
        arrowcolor=GOLD,
        arrowwidth=1.5,
        ax=48,
        ay=-42,
        bgcolor=NAVY,
        borderpad=6,
        font={"color": "white", "size": 10},
    )
    figure.update_yaxes(tickprefix="R$", tickformat="~s", title="Item GMV")
    figure.update_xaxes(title=None)
    return _style_figure(figure, height=350, margin={"l": 62, "r": 22, "t": 36, "b": 42})


def build_customer_mix_figure(monthly: pd.DataFrame) -> go.Figure:
    """Show monthly new and returning customers without implying retention causality."""
    mix = monthly.melt(
        id_vars="purchase_month",
        value_vars=["new_customers", "returning_customers"],
        var_name="customer_type",
        value_name="customers",
    )
    mix["customer_type"] = mix["customer_type"].map(
        {"new_customers": "New customers", "returning_customers": "Returning customers"}
    )
    figure = px.area(
        mix,
        x="purchase_month",
        y="customers",
        color="customer_type",
        color_discrete_map={"New customers": NAVY_MID, "Returning customers": GOLD},
        labels={"purchase_month": "", "customers": "Active customers", "customer_type": ""},
    )
    figure.update_traces(hovertemplate="%{x|%b %Y}<br>%{fullData.name}: %{y:,.0f}<extra></extra>")
    return _style_figure(figure, height=300, margin={"l": 52, "r": 16, "t": 42, "b": 38})


def build_cohort_figure(cohorts: pd.DataFrame, max_month: int = 12) -> go.Figure:
    """Create a readable cohort heatmap with month-zero visually separated."""
    matrix = cohort_matrix(cohorts, max_month=max_month)
    display = matrix.copy()
    text = display.map(lambda value: "" if pd.isna(value) else f"{value:.2f}%")
    figure = go.Figure(
        go.Heatmap(
            z=display.to_numpy(),
            x=display.columns,
            y=display.index,
            text=text.to_numpy(),
            texttemplate="%{text}",
            textfont={"size": 9},
            colorscale=[[0, "#F1FAF8"], [0.08, "#BDE9E1"], [0.35, TEAL], [1, NAVY]],
            zmin=0,
            zmax=2,
            colorbar={"title": "Retention", "ticksuffix": "%", "thickness": 10},
            hovertemplate="Cohort %{y}<br>Age %{x}<br>Retention %{z:.2f}%<extra></extra>",
            hoverongaps=False,
        )
    )
    figure.update_xaxes(side="top", title="Months after first delivered purchase")
    figure.update_yaxes(title="First-purchase cohort", autorange="reversed")
    return _style_figure(
        figure,
        height=610,
        show_legend=False,
        margin={"l": 78, "r": 34, "t": 58, "b": 22},
    )


def build_review_figure(delivery: pd.DataFrame) -> go.Figure:
    """Compare positive and low review outcomes by delivery status."""
    melted = delivery.melt(
        id_vars="delivery_status",
        value_vars=["five_star_review_rate_pct", "low_review_rate_pct"],
        var_name="review_outcome",
        value_name="rate",
    )
    melted["review_outcome"] = melted["review_outcome"].map(
        {
            "five_star_review_rate_pct": "Five-star reviews",
            "low_review_rate_pct": "One- or two-star reviews",
        }
    )
    figure = px.bar(
        melted,
        x="delivery_status",
        y="rate",
        color="review_outcome",
        barmode="group",
        color_discrete_map={"Five-star reviews": TEAL, "One- or two-star reviews": RED},
        labels={"delivery_status": "", "rate": "Share of reviews (%)", "review_outcome": ""},
        text_auto=".1f",
    )
    figure.update_traces(textposition="outside", cliponaxis=False)
    return _style_figure(figure, height=340, margin={"l": 52, "r": 12, "t": 46, "b": 42})


def build_state_figure(states: pd.DataFrame, selected_state: str = "ALL") -> go.Figure:
    """Plot state reliability, reviews, volume, and delivery speed."""
    frame = states.copy()
    selected = frame["customer_state"].eq(selected_state)
    if selected_state == "ALL":
        marker_line = [0] * len(frame)
        opacity = [0.86] * len(frame)
        symbols = ["circle"] * len(frame)
    else:
        marker_line = [3 if value else 0 for value in selected]
        opacity = [1.0 if value else 0.34 for value in selected]
        symbols = ["diamond" if value else "circle" for value in selected]
    figure = go.Figure(
        go.Scatter(
            x=frame["on_time_delivery_rate_pct"],
            y=frame["average_review_score"],
            mode="markers+text" if selected_state != "ALL" else "markers",
            text=[state if state == selected_state else "" for state in frame["customer_state"]],
            textposition="top center",
            customdata=frame[
                ["customer_state", "delivered_orders", "average_delivery_days", "item_gmv_brl"]
            ].to_numpy(),
            marker={
                "size": (14 + 34 * frame["delivered_orders"] / frame["delivered_orders"].max()).tolist(),
                "color": frame["average_delivery_days"],
                "colorscale": [[0, TEAL], [0.55, GOLD], [1, RED]],
                "colorbar": {"title": "Delivery days", "thickness": 10},
                "line": {"color": NAVY, "width": marker_line},
                "opacity": opacity,
                "symbol": symbols,
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>On time %{x:.1f}%<br>Review %{y:.2f}"
                "<br>Orders %{customdata[1]:,.0f}<br>Delivery %{customdata[2]:.1f} days"
                "<br>GMV R$%{customdata[3]:,.0f}<extra></extra>"
            ),
        )
    )
    figure.add_vline(x=91.89, line_dash="dot", line_color=NAVY, opacity=0.5)
    figure.add_annotation(
        x=91.89,
        y=frame["average_review_score"].min(),
        text="Portfolio on-time rate",
        showarrow=False,
        yshift=-18,
        font={"size": 9, "color": MUTED},
    )
    figure.update_xaxes(title="On-time delivery rate (%)")
    figure.update_yaxes(title="Average review score")
    return _style_figure(figure, height=390, show_legend=False)


def build_category_figure(categories: pd.DataFrame, selected_category: str = "ALL") -> go.Figure:
    """Rank the leading categories and preserve a selected category in view."""
    top = categories.head(12).copy()
    if selected_category != "ALL" and selected_category not in set(top["category"]):
        selected_row = categories.loc[categories["category"].eq(selected_category)]
        top = pd.concat([top.head(11), selected_row], ignore_index=True)
    top = top.sort_values("item_gmv_brl", ascending=True)
    colors = [
        GOLD if category == selected_category else TEAL if index % 2 else BLUE
        for index, category in enumerate(top["category"])
    ]
    figure = go.Figure(
        go.Bar(
            x=top["item_gmv_brl"],
            y=top["category"],
            orientation="h",
            marker={"color": colors},
            customdata=top[["delivered_orders", "on_time_delivery_rate_pct", "average_review_score"]],
            hovertemplate=(
                "<b>%{y}</b><br>GMV R$%{x:,.0f}<br>Orders %{customdata[0]:,.0f}"
                "<br>On time %{customdata[1]:.1f}%<br>Review %{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )
    figure.update_xaxes(title="Delivered item GMV", tickprefix="R$", tickformat="~s")
    figure.update_yaxes(title=None)
    return _style_figure(
        figure,
        height=430,
        show_legend=False,
        margin={"l": 158, "r": 18, "t": 18, "b": 45},
    )


def _kpi(label: str, value: str, foot: str, tone: str = "teal") -> html.Div:
    return html.Div(
        [html.Div(label, className="commerce-kpi__label"), html.Div(value, className="commerce-kpi__value"), html.Div(foot, className=f"commerce-kpi__foot is-{tone}")],
        className=f"commerce-card commerce-kpi tone-{tone}",
    )


def _panel_header(title: str, description: str, pill: str | None = None) -> html.Div:
    children: list[Any] = [
        html.Div([html.H3(title), html.P(description, className="commerce-panel__description")])
    ]
    if pill:
        children.append(html.Span(pill, className="commerce-pill"))
    return html.Div(children, className="commerce-panel__header")


def _signal(kicker: str, title: str, copy: str) -> html.Div:
    return html.Div(
        [html.Small(kicker), html.Strong(title), html.P(copy)],
        className="commerce-signal",
    )


def _page_title(eyebrow: str, title: str, subtitle: str, context: str) -> html.Div:
    return html.Div(
        [
            html.Div([html.Div(eyebrow, className="commerce-eyebrow"), html.H1(title), html.P(subtitle, className="commerce-subtitle")]),
            html.Div(context, className="commerce-updated"),
        ],
        className="commerce-title-row",
    )


def _overview_layout(outputs: dict[str, pd.DataFrame]) -> html.Section:
    kpis = outputs["kpis"].iloc[0]
    monthly = outputs["monthly"]
    top_category = outputs["categories"].iloc[0]
    on_time = outputs["delivery"].set_index("delivery_status").loc["On time"]
    late = outputs["delivery"].set_index("delivery_status").loc["Late"]
    return html.Section(
        [
            _page_title(
                "MARKETPLACE COMMAND CENTER",
                "Executive overview",
                "Revenue, customer behavior, and fulfillment performance at decision-ready grain.",
                "Warehouse snapshot · 2016–2018",
            ),
            html.Div(
                [
                    html.Div("EXECUTIVE READOUT", className="commerce-hero__eyebrow"),
                    html.H2("Growth is visible. Retention and late-delivery experience are the constraints."),
                    html.P(
                        "The marketplace generated R$13.22M in delivered item GMV, but repeat purchasing remains at 3.0%. Late orders show a material customer-experience penalty and should be treated as an operational priority."
                    ),
                    html.Span("96,478 DELIVERED ORDERS · 93,358 UNIQUE CUSTOMERS", className="commerce-hero__tag"),
                ],
                className="commerce-hero",
            ),
            html.Div(
                [
                    _kpi("ITEM GMV", brl(float(kpis["item_gmv_brl"]), 2), f"{int(kpis['items_sold']):,} items sold"),
                    _kpi("DELIVERED ORDERS", f"{int(kpis['delivered_orders']):,}", f"{brl(float(kpis['average_order_gmv_brl']), 0)} avg order"),
                    _kpi("REPEAT CUSTOMERS", f"{kpis['repeat_customer_rate_pct']:.1f}%", "Primary growth gap", "red"),
                    _kpi("ON-TIME DELIVERY", f"{kpis['on_time_delivery_rate_pct']:.2f}%", f"{kpis['average_delivery_days']:.2f} days average"),
                    _kpi("AVERAGE REVIEW", f"{kpis['average_review_score']:.2f} / 5", f"Late orders: {late['average_review_score']:.2f}", "amber"),
                ],
                className="commerce-kpi-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            _panel_header("Monthly delivered-order GMV", "Complete months with order-count context", "Peak · Nov 2017"),
                            dcc.Loading(dcc.Graph(id="monthly-gmv-chart", figure=build_monthly_figure(monthly), config=GRAPH_CONFIG), type="circle"),
                            html.Div(id="monthly-peak-context", className="commerce-chart-context"),
                        ],
                        className="commerce-card commerce-panel",
                    ),
                    html.Div(
                        [
                            html.H3("What should leadership do next?"),
                            _signal("GROWTH LEVER", "Second-order lifecycle", "Test a controlled post-purchase program against the 3.0% repeat-customer baseline."),
                            _signal("EXPERIENCE RISK", "Late orders drive low ratings", f"{late['low_review_rate_pct']:.2f}% of late deliveries receive one- or two-star reviews."),
                            _signal("OPERATING SIGNAL", "Peak-period reliability", "November 2017 GMV peaked while on-time performance fell to 85.69%."),
                            html.Div([html.B("Decision: "), "Pair growth campaigns with state/category delivery guardrails so demand does not amplify service failures."], className="commerce-callout"),
                        ],
                        className="commerce-card commerce-insight-panel",
                    ),
                ],
                className="commerce-grid-main",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            _panel_header("Monthly active-customer mix", "New versus returning customers in the selected analysis window", "Customer grain"),
                            dcc.Graph(id="customer-mix-chart", figure=build_customer_mix_figure(monthly), config=GRAPH_CONFIG),
                        ],
                        className="commerce-card commerce-panel",
                    ),
                    html.Div(
                        [
                            _panel_header("Evidence snapshot", "Three signals carried into the stakeholder recommendation", "Validated"),
                            html.Div(
                                [
                                    html.Div([html.Span("M1"), html.Strong(f"{weighted_retention(outputs['cohorts'], 1):.2f}%"), html.Small("weighted retention")], className="commerce-evidence"),
                                    html.Div([html.Span("CX"), html.Strong(f"{on_time['average_review_score'] - late['average_review_score']:.2f}★"), html.Small("on-time review advantage")], className="commerce-evidence"),
                                    html.Div([html.Span("#1"), html.Strong(brl(float(top_category["item_gmv_brl"]), 2)), html.Small(str(top_category["category"]))], className="commerce-evidence"),
                                ],
                                className="commerce-evidence-grid",
                            ),
                            html.P("Item GMV is marketplace transaction value—not Olist accounting revenue or profit.", className="commerce-note"),
                        ],
                        className="commerce-card commerce-panel",
                    ),
                ],
                className="commerce-grid-half",
            ),
        ],
        id="overview-page",
        className="commerce-page is-active",
    )


def _cohort_layout(outputs: dict[str, pd.DataFrame]) -> html.Section:
    kpis = outputs["kpis"].iloc[0]
    return html.Section(
        [
            _page_title("CUSTOMER BEHAVIOR", "Cohort retention", "First-purchase cohorts tracked by elapsed calendar month.", "Customer grain · customer_unique_id"),
            html.Div(
                [
                    _kpi("MONTH-1 RETENTION", f"{weighted_retention(outputs['cohorts'], 1):.2f}%", "Weighted across cohorts", "red"),
                    _kpi("MONTH-3 RETENTION", f"{weighted_retention(outputs['cohorts'], 3):.2f}%", "Weighted mature cohorts", "amber"),
                    _kpi("UNIQUE CUSTOMERS", f"{int(kpis['unique_customers']):,}", "Delivered orders only"),
                    _kpi("REPEAT RATE", f"{kpis['repeat_customer_rate_pct']:.1f}%", "Second-order opportunity", "red"),
                    _kpi("COHORT BASIS", "Month", "First delivered purchase"),
                ],
                className="commerce-kpi-grid",
            ),
            html.Div(
                [
                    _panel_header("Customer cohort retention matrix", "Percentage of each acquisition cohort purchasing again after month zero", "M0 clipped at 2% scale"),
                    dcc.Graph(figure=build_cohort_figure(outputs["cohorts"]), config=GRAPH_CONFIG),
                    html.Div(
                        [html.B("Interpretation: "), "The first-month drop is persistent across cohorts. A controlled post-purchase experiment should be measured against repeat conversion and incremental margin—not email engagement alone."],
                        className="commerce-notice commerce-notice--amber",
                    ),
                ],
                className="commerce-card commerce-panel",
            ),
        ],
        id="cohort-page",
        className="commerce-page",
    )


def _delivery_layout(outputs: dict[str, pd.DataFrame]) -> html.Section:
    experience = outputs["delivery"].set_index("delivery_status")
    on_time = experience.loc["On time"]
    late = experience.loc["Late"]
    return html.Section(
        [
            _page_title("FULFILLMENT & EXPERIENCE", "Delivery performance", "Connect operational reliability to customer review outcomes.", "8 missing delivery timestamps isolated"),
            html.Div(
                [
                    _kpi("ON-TIME RATE", "91.89%", "Delivered with timestamps"),
                    _kpi("AVG DELIVERY", "12.50 days", "Purchase to customer"),
                    _kpi("LATE REVIEW", f"{late['average_review_score']:.2f} / 5", f"vs {on_time['average_review_score']:.2f} on time", "red"),
                    _kpi("LATE LOW-REVIEW", f"{late['low_review_rate_pct']:.2f}%", "One- or two-star share", "red"),
                    _kpi("AVG DAYS LATE", f"{late['average_late_days']:.2f}", "Late orders only", "amber"),
                ],
                className="commerce-kpi-grid",
            ),
            html.Div(
                [
                    html.Div([_panel_header("Review outcomes by delivery status", "The experience penalty is large and operationally meaningful", "Descriptive"), dcc.Graph(figure=build_review_figure(outputs["delivery"]), config=GRAPH_CONFIG)], className="commerce-card commerce-panel"),
                    html.Div([_panel_header("Selected-state diagnostic", "Focus a state without hiding the portfolio benchmark", "Filter-aware"), html.Div(id="state-focus-card", className="commerce-focus-card")], className="commerce-card commerce-panel"),
                ],
                className="commerce-grid-half commerce-grid-half--uneven",
            ),
            html.Div([_panel_header("State delivery reliability and reviews", "Bubble size represents delivered orders; color represents average delivery days", "Portfolio benchmark · 91.89%"), dcc.Loading(dcc.Graph(id="state-delivery-chart", figure=build_state_figure(outputs["states"]), config=GRAPH_CONFIG), type="circle")], className="commerce-card commerce-panel"),
            html.Div([html.B("Analytical caution: "), "The delivery-review relationship is descriptive. Carrier, geography, seller behavior, product mix, and promise-setting may all contribute."], className="commerce-notice"),
        ],
        id="delivery-page",
        className="commerce-page",
    )


def _category_layout(outputs: dict[str, pd.DataFrame]) -> html.Section:
    top = outputs["categories"].iloc[0]
    columns = [
        {"headerName": "Category", "field": "category", "minWidth": 190},
        {"headerName": "Orders", "field": "delivered_orders", "type": "numericColumn", "valueFormatter": {"function": "d3.format(',.0f')(params.value)"}},
        {"headerName": "Items", "field": "items_sold", "type": "numericColumn", "valueFormatter": {"function": "d3.format(',.0f')(params.value)"}},
        {"headerName": "Item GMV (BRL)", "field": "item_gmv_brl", "type": "numericColumn", "minWidth": 145, "valueFormatter": {"function": "'R$' + d3.format(',.0f')(params.value)"}},
        {"headerName": "On-time %", "field": "on_time_delivery_rate_pct", "type": "numericColumn", "valueFormatter": {"function": "d3.format('.1f')(params.value) + '%'"}},
        {"headerName": "Review", "field": "average_review_score", "type": "numericColumn", "valueFormatter": {"function": "d3.format('.2f')(params.value)"}},
    ]
    return html.Section(
        [
            _page_title("MERCHANDISING", "Category performance", "Delivered-order value and customer-experience indicators by translated category.", "Order-category grain · fanout protected"),
            html.Div(
                [
                    html.Div([_panel_header("Leading categories by item GMV", "Selected categories remain visible even outside the default top 12", "Delivered orders"), dcc.Loading(dcc.Graph(id="category-gmv-chart", figure=build_category_figure(outputs["categories"]), config=GRAPH_CONFIG), type="circle")], className="commerce-card commerce-panel"),
                    html.Div([_panel_header("Selected-category readout", "Pair value with reliability and customer experience", "Filter-aware"), html.Div(id="category-focus-card", className="commerce-focus-card")], className="commerce-card commerce-panel"),
                ],
                className="commerce-grid-main",
            ),
            html.Div(
                [
                    _panel_header("Category comparison table", "Sort or filter the reviewed dashboard-ready output", f"Leader · {top['category']}"),
                    dag.AgGrid(
                        id="category-table",
                        columnDefs=columns,
                        rowData=outputs["categories"].to_dict("records"),
                        defaultColDef={"sortable": True, "filter": True, "resizable": True, "flex": 1, "minWidth": 105},
                        dashGridOptions={"pagination": True, "paginationPageSize": 12, "paginationPageSizeSelector": False, "animateRows": False},
                        columnSize="responsiveSizeToFit",
                        className="ag-theme-quartz commerce-grid-table",
                        style={"height": "520px", "width": "100%"},
                    ),
                ],
                className="commerce-card commerce-panel",
            ),
        ],
        id="category-page",
        className="commerce-page",
    )


def _quality_layout(outputs: dict[str, pd.DataFrame]) -> html.Section:
    quality = outputs["quality"].copy()
    quality["check_name"] = quality["check_name"].str.replace("_", " ").str.title()
    quality["treatment"] = quality["check_status"].map(
        {"PASS": "No action required", "REVIEW": "Excluded only from duration/on-time calculations"}
    )
    return html.Section(
        [
            _page_title("DEFENSIBLE ANALYTICS", "SQL & data quality", "Visible query logic, table grain, and validation evidence.", "DuckDB 1.5.5 · automated tests"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("REVIEW SQL FILE", className="commerce-control-label"),
                            dcc.Dropdown(id="sql-selector", options=list(SQL_FILES), value="Executive KPIs", clearable=False, className="commerce-dropdown commerce-dropdown--light"),
                            html.Div([html.B("Grain rule: "), "Items, payments, and reviews are rolled up to one row per order before joining. Category analysis uses one row per order-category."], className="commerce-notice commerce-notice--navy"),
                        ],
                        className="commerce-sql-menu",
                    ),
                    html.Pre(id="sql-code", children=(SQL_DIR / SQL_FILES["Executive KPIs"]).read_text(encoding="utf-8"), className="commerce-code"),
                ],
                className="commerce-sql-grid",
            ),
            html.Div(
                [
                    _panel_header("Warehouse quality checks", "Seven pass; one documented exception is handled without removing valid value metrics", "No silent failures"),
                    dag.AgGrid(
                        columnDefs=[
                            {"headerName": "Check", "field": "check_name", "minWidth": 245},
                            {"headerName": "Issues", "field": "issue_count", "type": "numericColumn", "maxWidth": 110},
                            {"headerName": "Status", "field": "check_status", "maxWidth": 120, "cellClassRules": {"commerce-status-pass": "params.value === 'PASS'", "commerce-status-review": "params.value === 'REVIEW'"}},
                            {"headerName": "Treatment", "field": "treatment", "minWidth": 280},
                        ],
                        rowData=quality.to_dict("records"),
                        defaultColDef={"sortable": True, "filter": True, "resizable": True, "flex": 1},
                        dashGridOptions={"domLayout": "autoHeight", "animateRows": False},
                        columnSize="responsiveSizeToFit",
                        className="ag-theme-quartz commerce-grid-table",
                    ),
                ],
                className="commerce-card commerce-panel",
            ),
        ],
        id="quality-page",
        className="commerce-page",
    )


def _sidebar(outputs: dict[str, pd.DataFrame]) -> html.Aside:
    monthly = outputs["monthly"]
    month_marks = {
        index: date.strftime("%b %y")
        for index, date in enumerate(monthly["purchase_month"])
        if index in {0, len(monthly) // 2, len(monthly) - 1}
    }
    state_options = [{"label": "All states", "value": "ALL"}] + [
        {"label": row.customer_state, "value": row.customer_state}
        for row in outputs["states"].itertuples()
    ]
    category_options = [{"label": "All categories", "value": "ALL"}] + [
        {"label": category, "value": category}
        for category in outputs["categories"]["category"]
    ]
    return html.Aside(
        [
            html.Div("WORKSPACE", className="commerce-side-label"),
            dcc.RadioItems(
                id="nav-selector",
                options=[
                    {"label": "▦  Executive overview", "value": "overview"},
                    {"label": "▥  Cohort retention", "value": "cohort"},
                    {"label": "◷  Delivery experience", "value": "delivery"},
                    {"label": "▰  Category performance", "value": "category"},
                    {"label": "⌘  SQL & quality", "value": "quality"},
                ],
                value="overview",
                className="commerce-nav",
            ),
            html.Div(className="commerce-divider"),
            html.Div("ANALYSIS CONTROLS", className="commerce-side-label"),
            html.Div([html.Label("Monthly analysis window"), dcc.RangeSlider(id="month-range", min=0, max=len(monthly) - 1, step=1, value=[0, len(monthly) - 1], marks=month_marks, allowCross=False, tooltip={"placement": "bottom", "always_visible": False})], className="commerce-control commerce-control--range"),
            html.Div([html.Label("State focus"), dcc.Dropdown(id="state-filter", options=state_options, value="ALL", clearable=False, searchable=True, className="commerce-dropdown")], className="commerce-control"),
            html.Div([html.Label("Category focus"), dcc.Dropdown(id="category-filter", options=category_options, value="ALL", clearable=False, searchable=True, className="commerce-dropdown")], className="commerce-control"),
            html.Div([html.Button("Apply filters", id="apply-filters", n_clicks=0, className="commerce-apply"), html.Button("Reset", id="reset-filters", n_clicks=0, className="commerce-reset")], className="commerce-filter-actions"),
            html.Div("Controls update their relevant analytical view; dimensions are not falsely cross-joined.", id="filter-note", className="commerce-filter-note"),
            html.Div([html.Strong("Olist Brazilian E-Commerce"), html.P("8 relational tables · Kaggle v2\nCC BY-NC-SA 4.0")], className="commerce-source"),
        ],
        className="commerce-sidebar",
    )


def _topbar() -> html.Header:
    return html.Header(
        [
            html.Div([html.Div("O", className="commerce-brandmark"), html.Div([html.Strong("Commerce Intelligence"), html.Small("SQL · DUCKDB · DASH")])], className="commerce-brand"),
            html.Div("Portfolio / Project 04 / Executive overview", id="breadcrumb", className="commerce-breadcrumb"),
            html.Div([html.Span("● DATA VALIDATED", className="commerce-status"), html.Button("Export brief", id="export-brief", n_clicks=0, className="commerce-export"), html.Div("SK", className="commerce-avatar")], className="commerce-top-actions"),
            dcc.Download(id="brief-download"),
        ],
        className="commerce-topbar",
    )


def _register_callbacks(app: Dash, outputs: dict[str, pd.DataFrame]) -> None:
    monthly = outputs["monthly"]
    default_filters = {"month_start": 0, "month_end": len(monthly) - 1, "state": "ALL", "category": "ALL"}

    @app.callback(
        Output("overview-page", "className"),
        Output("cohort-page", "className"),
        Output("delivery-page", "className"),
        Output("category-page", "className"),
        Output("quality-page", "className"),
        Output("breadcrumb", "children"),
        Input("nav-selector", "value"),
    )
    def navigate(selected: str) -> tuple[str, str, str, str, str, str]:
        pages = ["overview", "cohort", "delivery", "category", "quality"]
        labels = {
            "overview": "Executive overview",
            "cohort": "Cohort retention",
            "delivery": "Delivery experience",
            "category": "Category performance",
            "quality": "SQL & data quality",
        }
        classes = tuple("commerce-page is-active" if page == selected else "commerce-page" for page in pages)
        return (*classes, f"Portfolio / Project 04 / {labels.get(selected, 'Executive overview')}")

    @app.callback(
        Output("applied-filters", "data"),
        Output("month-range", "value"),
        Output("state-filter", "value"),
        Output("category-filter", "value"),
        Output("filter-note", "children"),
        Input("apply-filters", "n_clicks"),
        Input("reset-filters", "n_clicks"),
        State("month-range", "value"),
        State("state-filter", "value"),
        State("category-filter", "value"),
        prevent_initial_call=True,
    )
    def apply_filters(
        _apply_clicks: int,
        _reset_clicks: int,
        month_range: list[int],
        state: str,
        category: str,
    ) -> tuple[dict[str, Any], Any, Any, Any, str]:
        if ctx.triggered_id == "reset-filters":
            return default_filters, [0, len(monthly) - 1], "ALL", "ALL", "Controls reset to the complete reviewed output."
        selected = {
            "month_start": int(month_range[0]),
            "month_end": int(month_range[1]),
            "state": state or "ALL",
            "category": category or "ALL",
        }
        month_view = filter_monthly(monthly, selected["month_start"], selected["month_end"])
        state_text = "all states" if selected["state"] == "ALL" else selected["state"]
        category_text = "all categories" if selected["category"] == "ALL" else selected["category"]
        note = f"Applied: {month_view.iloc[0]['purchase_month']:%b %Y}–{month_view.iloc[-1]['purchase_month']:%b %Y} · {state_text} · {category_text}."
        return selected, no_update, no_update, no_update, note

    @app.callback(
        Output("monthly-gmv-chart", "figure"),
        Output("customer-mix-chart", "figure"),
        Output("monthly-peak-context", "children"),
        Output("state-delivery-chart", "figure"),
        Output("state-focus-card", "children"),
        Output("category-gmv-chart", "figure"),
        Output("category-focus-card", "children"),
        Output("category-table", "rowData"),
        Input("applied-filters", "data"),
    )
    def update_views(filters: dict[str, Any]) -> tuple[Any, ...]:
        filters = filters or default_filters
        month_view = filter_monthly(monthly, filters["month_start"], filters["month_end"])
        peak = month_view.loc[month_view["item_gmv_brl"].idxmax()]
        peak_context = [
            html.Span(f"{peak['purchase_month']:%B %Y}", className="commerce-chip"),
            html.Span(f"{brl(float(peak['item_gmv_brl']), 2)} GMV"),
            html.Span(f"{int(peak['delivered_orders']):,} orders"),
            html.Span(f"{peak['on_time_delivery_rate_pct']:.2f}% on time"),
        ]

        states = outputs["states"]
        selected_state = filters.get("state", "ALL")
        if selected_state == "ALL":
            state_row = states.iloc[0]
            state_title = "Portfolio view"
            state_copy = "Select a state to compare its reliability with the 91.89% portfolio benchmark."
        else:
            state_row = states.loc[states["customer_state"].eq(selected_state)].iloc[0]
            state_title = f"{selected_state} · {int(state_row['delivered_orders']):,} orders"
            gap = float(state_row["on_time_delivery_rate_pct"] - 91.89)
            state_copy = f"{abs(gap):.2f} percentage points {'above' if gap >= 0 else 'below'} the portfolio on-time rate."
        state_focus = [
            html.Div(state_title, className="commerce-focus-title"),
            html.Div(
                [
                    html.Div([html.Small("ON TIME"), html.Strong(f"{state_row['on_time_delivery_rate_pct']:.2f}%")]),
                    html.Div([html.Small("DELIVERY"), html.Strong(f"{state_row['average_delivery_days']:.2f}d")]),
                    html.Div([html.Small("REVIEW"), html.Strong(f"{state_row['average_review_score']:.2f}")]),
                    html.Div([html.Small("ITEM GMV"), html.Strong(brl(float(state_row["item_gmv_brl"]), 1))]),
                ],
                className="commerce-focus-metrics",
            ),
            html.P(state_copy),
        ]

        categories = outputs["categories"]
        selected_category = filters.get("category", "ALL")
        if selected_category == "ALL":
            category_row = categories.iloc[0]
            category_title = "GMV leader · health_beauty"
            category_copy = "Select a category to compare value, delivery, and customer experience."
        else:
            category_row = categories.loc[categories["category"].eq(selected_category)].iloc[0]
            category_title = selected_category
            rank = int(categories.index[categories["category"].eq(selected_category)][0]) + 1
            category_copy = f"Ranked #{rank} of {len(categories)} categories by delivered item GMV."
        category_focus = [
            html.Div(category_title, className="commerce-focus-title"),
            html.Div(
                [
                    html.Div([html.Small("ITEM GMV"), html.Strong(brl(float(category_row["item_gmv_brl"]), 2))]),
                    html.Div([html.Small("ORDERS"), html.Strong(f"{int(category_row['delivered_orders']):,}")]),
                    html.Div([html.Small("ON TIME"), html.Strong(f"{category_row['on_time_delivery_rate_pct']:.2f}%")]),
                    html.Div([html.Small("REVIEW"), html.Strong(f"{category_row['average_review_score']:.2f}")]),
                ],
                className="commerce-focus-metrics",
            ),
            html.P(category_copy),
        ]
        table_frame = categories.copy()
        if selected_category != "ALL":
            table_frame = pd.concat(
                [table_frame.loc[table_frame["category"].eq(selected_category)], table_frame.loc[~table_frame["category"].eq(selected_category)]],
                ignore_index=True,
            )
        return (
            build_monthly_figure(month_view),
            build_customer_mix_figure(month_view),
            peak_context,
            build_state_figure(states, selected_state),
            state_focus,
            build_category_figure(categories, selected_category),
            category_focus,
            table_frame.to_dict("records"),
        )

    @app.callback(Output("sql-code", "children"), Input("sql-selector", "value"))
    def update_sql(selected_label: str) -> str:
        filename = SQL_FILES.get(selected_label, SQL_FILES["Executive KPIs"])
        return (SQL_DIR / filename).read_text(encoding="utf-8")

    @app.callback(
        Output("brief-download", "data"),
        Input("export-brief", "n_clicks"),
        State("applied-filters", "data"),
        prevent_initial_call=True,
    )
    def export_brief(_clicks: int, filters: dict[str, Any]) -> dict[str, str]:
        month_view = filter_monthly(monthly, filters["month_start"], filters["month_end"])
        peak = month_view.loc[month_view["item_gmv_brl"].idxmax()]
        text = f"""Olist Commerce Command Center — Executive Brief

Analysis window: {month_view.iloc[0]['purchase_month']:%B %Y} to {month_view.iloc[-1]['purchase_month']:%B %Y}
State focus: {filters.get('state', 'ALL')}
Category focus: {filters.get('category', 'ALL')}

Portfolio findings
- 96,478 delivered orders generated R$13,221,498.11 in item GMV.
- 3.0% of customers placed at least two delivered orders.
- Weighted month-one cohort retention was {weighted_retention(outputs['cohorts'], 1):.2f}%.
- On-time orders averaged 4.29 stars versus 2.57 for late orders.
- 53.99% of late orders received one- or two-star reviews.
- The selected window peaked in {peak['purchase_month']:%B %Y} at R${peak['item_gmv_brl']:,.2f}.

Recommended actions
1. Test a controlled second-order lifecycle program.
2. Diagnose delivery reliability by high-volume state and category.
3. Add peak-period capacity and service-risk monitoring.

Definitions
Item GMV is marketplace transaction value, not Olist accounting revenue or profit.
Delivery-review relationships are descriptive rather than causal.
"""
        return dcc.send_string(text, "olist_executive_brief.txt")


def create_dash_app(output_dir: str | Path = OUTPUT_DIR) -> Dash:
    """Create the standalone app so tests and production use the same factory."""
    outputs = load_outputs(output_dir)
    monthly = outputs["monthly"]
    initial_filters = {"month_start": 0, "month_end": len(monthly) - 1, "state": "ALL", "category": "ALL"}
    app = Dash(
        __name__,
        title="Olist Commerce Intelligence | Sarvesh Kommawar",
        assets_folder=str(ASSETS_DIR),
        suppress_callback_exceptions=False,
        update_title="Updating analysis…",
    )
    app.layout = html.Div(
        [
            _topbar(),
            _sidebar(outputs),
            html.Main(
                [
                    dcc.Store(id="applied-filters", data=initial_filters),
                    _overview_layout(outputs),
                    _cohort_layout(outputs),
                    _delivery_layout(outputs),
                    _category_layout(outputs),
                    _quality_layout(outputs),
                ],
                className="commerce-main",
            ),
        ],
        className="commerce-shell",
    )
    _register_callbacks(app, outputs)
    return app
