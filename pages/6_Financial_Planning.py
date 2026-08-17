"""Interactive financial planning, variance, and scenario command center."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.finance import (
    apply_corporate_scenario,
    corporate_pnl,
    filter_planning_mart,
    load_outputs as load_finance_outputs,
    usd,
)
from portfolio_app.ui import (
    GOLD,
    NAVY,
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

configure_page("Financial Planning & Variance", "💼")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 06 · FP&A, Excel & business planning",
    "Financial Planning & Variance Command Center",
    "Reconcile a real FY2026 public operating budget, identify Q3 pacing signals, and test clearly labeled corporate revenue, cost, and hiring scenarios.",
    [
        "City of Austin FY2026",
        "57K source rows",
        "Budget vs actual",
        "Formula-driven Excel",
        "Power BI companion",
    ],
)
render_notice(
    "navy",
    "75%",
    "Pacing is a screening benchmark—not an accounting forecast",
    "The public source is through Q3, so 75% of annual budget is used as a simple timing benchmark. Debt payments, transfers, grants, vacancies, and seasonal operations can make straight-line pacing inappropriate for individual accounts.",
)

PROJECT_DIR = Path(__file__).resolve().parents[1] / "06-financial-planning"
OUTPUT_DIR = PROJECT_DIR / "outputs"
POWER_BI_DIR = PROJECT_DIR / "power-bi"


@st.cache_data
def get_finance_outputs() -> dict[str, pd.DataFrame]:
    """Load Project 06 outputs under a page-specific Streamlit cache key."""
    return load_finance_outputs(OUTPUT_DIR)


outputs = get_finance_outputs()
kpis = outputs["kpis"].iloc[0]
departments = outputs["departments"]
funds = outputs["funds"]
expenses = outputs["expenses"]
mart = outputs["mart"]
drivers = outputs["drivers"]
corporate_plan = outputs["corporate_plan"]
quality = outputs["quality"]
metadata = outputs["metadata"].iloc[0]

p1, p2, p3, p4, p5, p6 = st.columns(6)
p1.metric("FY2026 annual budget", usd(float(kpis["annual_budget"]), 2))
p2.metric("Q3 expenditures", usd(float(kpis["expenditures_to_date"]), 2))
p3.metric("Budget utilization", f"{kpis['utilization_pct']:.2f}%")
p4.metric("Elapsed benchmark", f"{kpis['elapsed_pct']:.0f}%")
p5.metric("Pace variance", usd(float(kpis["pace_variance"]), 1))
p6.metric("Remaining budget", usd(float(kpis["remaining_budget"]), 2))

render_section(
    "Finance workspace",
    "Move from reconciliation to owner action",
    "The first three tabs use real City of Austin public data. The corporate lab is a separate seeded demonstration and never mixes with public-finance totals.",
)
executive_tab, explorer_tab, drivers_tab, corporate_tab, methods_tab = st.tabs(
    [
        "Executive pacing",
        "Department & fund explorer",
        "Variance drivers",
        "Corporate planning lab",
        "Methods & deliverables",
    ]
)

status_colors = {
    "Above pace": "#E26D5A",
    "Near pace": TEAL,
    "Below pace": "#55A6D9",
    "Review: spend without budget": GOLD,
    "Review: non-positive budget": PURPLE,
}

with executive_tab:
    top = departments.head(15).sort_values("budget")
    left, right = st.columns([1.25, 1])
    with left:
        comparison = go.Figure()
        comparison.add_trace(
            go.Bar(
                y=top["dept_rollup_name"],
                x=top["budget"],
                orientation="h",
                name="Annual budget",
                marker_color="rgba(23,59,99,.20)",
                hovertemplate="%{y}<br>Budget $%{x:,.0f}<extra></extra>",
            )
        )
        comparison.add_trace(
            go.Bar(
                y=top["dept_rollup_name"],
                x=top["expenditures"],
                orientation="h",
                name="Q3 expenditures",
                marker_color=TEAL,
                hovertemplate="%{y}<br>Expenditures $%{x:,.0f}<extra></extra>",
            )
        )
        comparison.update_layout(
            title="Largest departments: budget and expenditures",
            xaxis_title="US dollars",
            yaxis_title="",
            barmode="overlay",
        )
        style_plotly(comparison, height=560)
        st.plotly_chart(comparison, width="stretch")

    with right:
        pacing_frame = departments.loc[departments["budget"].ge(1_000_000)].copy()
        pacing = px.scatter(
            pacing_frame,
            x="budget",
            y="utilization_pct",
            size="budget",
            color="pace_status",
            hover_name="dept_rollup_name",
            hover_data={
                "expenditures": ":,.0f",
                "pace_variance": ":,.0f",
                "budget": ":,.0f",
            },
            color_discrete_map=status_colors,
            size_max=46,
            title="Budget size versus Q3 utilization",
            labels={
                "budget": "Annual budget ($)",
                "utilization_pct": "Budget utilization (%)",
                "pace_status": "Pace status",
            },
        )
        pacing.add_hline(
            y=float(kpis["elapsed_pct"]),
            line_dash="dash",
            line_color=GOLD,
            annotation_text="75% elapsed benchmark",
        )
        style_plotly(pacing, height=560)
        st.plotly_chart(pacing, width="stretch")
        st.caption("Scatter excludes departments with net annual budgets below $1M; all departments remain in the reconciliation table.")

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Departments", f"{int(kpis['departments'])}")
    e2.metric("Departments above pace", f"{int(kpis['above_pace_departments'])}")
    e3.metric("Expected spend to date", usd(float(kpis["expected_spend_to_date"]), 2))
    e4.metric("Linear run-rate proxy", usd(float(kpis["linear_run_rate_proxy"]), 2))

    display_departments = departments[
        [
            "dept_rollup_name",
            "budget",
            "expenditures",
            "remaining_budget",
            "utilization_pct",
            "pace_variance",
            "pace_status",
        ]
    ].rename(
        columns={
            "dept_rollup_name": "Department",
            "budget": "Annual budget ($)",
            "expenditures": "Q3 expenditures ($)",
            "remaining_budget": "Remaining budget ($)",
            "utilization_pct": "Utilization %",
            "pace_variance": "Pace variance ($)",
            "pace_status": "Pace status",
        }
    )
    st.dataframe(
        display_departments,
        hide_index=True,
        width="stretch",
        column_config={
            "Annual budget ($)": st.column_config.NumberColumn(format="$%,.0f"),
            "Q3 expenditures ($)": st.column_config.NumberColumn(format="$%,.0f"),
            "Remaining budget ($)": st.column_config.NumberColumn(format="$%,.0f"),
            "Utilization %": st.column_config.NumberColumn(format="%.1f%%"),
            "Pace variance ($)": st.column_config.NumberColumn(format="$%,.0f"),
        },
    )

    top_department = departments.iloc[0]
    brief = generate_insights(
        {
            "headline": (
                f"FY2026 Q3 expenditures are {kpis['utilization_pct']:.2f}% of the "
                f"{usd(float(kpis['annual_budget']), 2)} annual budget, producing a "
                f"{usd(float(kpis['pace_variance']), 1)} variance to the straight-line benchmark."
            ),
            "drivers": [
                f"{int(kpis['above_pace_departments'])} departments are more than five percentage points above pace",
                f"{top_department['dept_rollup_name']} has the largest budget at {usd(float(top_department['budget']), 2)}",
                f"Positive spend on zero-budget source lines totals {usd(float(kpis['zero_budget_spend_value']), 1)} and requires accounting context",
            ],
            "recommendation": (
                "Prioritize owner review for above-pace departments, separate scheduled transfers and debt from recurring operations, and reconcile personnel objects before escalating exceptions."
            ),
        }
    )
    with st.expander("AI-assisted finance brief"):
        st.markdown(brief)
        st.caption("Only reviewed metrics are supplied to the optional generator; calculations remain deterministic.")

with explorer_tab:
    c1, c2 = st.columns(2)
    department_options = departments["dept_rollup_name"].tolist()
    selected_departments = c1.multiselect(
        "Departments",
        department_options,
        default=[],
        placeholder="All departments",
    )
    available_funds = funds.loc[
        funds["dept_rollup_name"].isin(selected_departments)
        if selected_departments
        else pd.Series(True, index=funds.index),
        "fund_name",
    ].drop_duplicates().sort_values().tolist()
    selected_funds = c2.multiselect(
        "Funds",
        available_funds,
        default=[],
        placeholder="All available funds",
    )
    filtered = filter_planning_mart(mart, selected_departments, selected_funds)
    selected_budget = float(filtered["budget"].sum())
    selected_spend = float(filtered["expenditures"].sum())
    selected_expected = float(filtered["expected_spend_to_date"].sum())
    selected_utilization = 100 * selected_spend / selected_budget if selected_budget else 0.0
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("Selected budget", usd(selected_budget, 2))
    f2.metric("Selected expenditures", usd(selected_spend, 2))
    f3.metric("Utilization", f"{selected_utilization:.1f}%")
    f4.metric("Pace variance", usd(selected_spend - selected_expected, 1))
    f5.metric("Programs", f"{filtered['program_name'].nunique():,}")

    category = filtered.groupby("expense_category", as_index=False)[
        ["budget", "expenditures"]
    ].sum()
    category_long = category.melt(
        id_vars="expense_category",
        value_vars=["budget", "expenditures"],
        var_name="measure",
        value_name="amount",
    )
    category_long["measure"] = category_long["measure"].map(
        {"budget": "Annual budget", "expenditures": "Q3 expenditures"}
    )
    category_chart = px.bar(
        category_long,
        x="amount",
        y="expense_category",
        color="measure",
        barmode="group",
        orientation="h",
        color_discrete_map={"Annual budget": NAVY, "Q3 expenditures": GOLD},
        title="Management expense mix",
        labels={"amount": "US dollars", "expense_category": "", "measure": "Measure"},
    )
    style_plotly(category_chart, height=470)
    st.plotly_chart(category_chart, width="stretch")

    explorer_table = filtered[
        [
            "dept_rollup_name",
            "fund_name",
            "program_name",
            "expense_category",
            "budget",
            "expenditures",
            "utilization_pct",
            "pace_variance",
            "pace_status",
        ]
    ].rename(
        columns={
            "dept_rollup_name": "Department",
            "fund_name": "Fund",
            "program_name": "Program",
            "expense_category": "Expense category",
            "budget": "Budget ($)",
            "expenditures": "Expenditures ($)",
            "utilization_pct": "Utilization %",
            "pace_variance": "Pace variance ($)",
            "pace_status": "Pace status",
        }
    )
    st.dataframe(
        explorer_table,
        hide_index=True,
        width="stretch",
        height=470,
        column_config={
            "Budget ($)": st.column_config.NumberColumn(format="$%,.0f"),
            "Expenditures ($)": st.column_config.NumberColumn(format="$%,.0f"),
            "Utilization %": st.column_config.NumberColumn(format="%.1f%%"),
            "Pace variance ($)": st.column_config.NumberColumn(format="$%,.0f"),
        },
    )

with drivers_tab:
    direction = st.radio(
        "Variance direction",
        ["Above pace", "Below pace"],
        horizontal=True,
    )
    driver_view = drivers.loc[
        drivers["pace_variance"].gt(0)
        if direction == "Above pace"
        else drivers["pace_variance"].lt(0)
    ].copy()
    driver_view = driver_view.nlargest(20, "absolute_pace_variance").sort_values(
        "pace_variance"
    )
    driver_view["driver_label"] = (
        driver_view["dept_rollup_name"] + " · " + driver_view["program_name"]
    )
    driver_chart = px.bar(
        driver_view,
        x="pace_variance",
        y="driver_label",
        orientation="h",
        color="pace_variance",
        color_continuous_scale=(
            [[0, "#F7C9C0"], [1, "#E26D5A"]]
            if direction == "Above pace"
            else [[0, "#2B6F92"], [1, "#B9DDF0"]]
        ),
        title=f"Largest program drivers: {direction.lower()}",
        labels={"pace_variance": "Pace variance ($)", "driver_label": ""},
        hover_data={"fund_name": True, "expense_category": True},
    )
    driver_chart.update_coloraxes(showscale=False)
    style_plotly(driver_chart, height=650, show_legend=False)
    st.plotly_chart(driver_chart, width="stretch")

    driver_table = driver_view[
        [
            "dept_rollup_name",
            "fund_name",
            "program_name",
            "expense_category",
            "budget",
            "expenditures",
            "expected_spend_to_date",
            "pace_variance",
        ]
    ].rename(
        columns={
            "dept_rollup_name": "Department",
            "fund_name": "Fund",
            "program_name": "Program",
            "expense_category": "Expense category",
            "budget": "Budget ($)",
            "expenditures": "Expenditures ($)",
            "expected_spend_to_date": "75% benchmark ($)",
            "pace_variance": "Pace variance ($)",
        }
    )
    st.dataframe(
        driver_table,
        hide_index=True,
        width="stretch",
        column_config={
            column: st.column_config.NumberColumn(format="$%,.0f")
            for column in [
                "Budget ($)",
                "Expenditures ($)",
                "75% benchmark ($)",
                "Pace variance ($)",
            ]
        },
    )
    render_notice(
        "amber",
        "!",
        "Review the accounting pattern before calling a variance unfavorable",
        "A program can be above a straight-line benchmark because of scheduled debt, transfers, grant timing, seasonality, or object reclassification. Use these drivers to ask better questions—not to assign blame from the dashboard alone.",
    )

with corporate_tab:
    render_notice(
        "amber",
        "SYN",
        "Seeded synthetic corporate demonstration",
        "This planning lab represents a hypothetical software company. It is not City of Austin data and does not describe a real company. Actual periods run January–July; August–December are forecast periods.",
    )
    s1, s2, s3 = st.columns(3)
    revenue_adjustment = s1.slider("Future revenue adjustment", -10.0, 10.0, 0.0, 0.5, format="%.1f%%")
    cost_inflation = s2.slider("Future cost inflation", -5.0, 10.0, 0.0, 0.5, format="%.1f%%")
    hiring_savings = s3.slider("Hiring-delay savings", 0.0, 15.0, 0.0, 0.5, format="%.1f%%")
    scenario = apply_corporate_scenario(
        corporate_plan,
        revenue_adjustment_pct=revenue_adjustment,
        cost_inflation_pct=cost_inflation,
        hiring_delay_savings_pct=hiring_savings,
    )
    budget_pnl = corporate_pnl(scenario, "budget_amount")
    base_pnl = corporate_pnl(scenario, "base_forecast_amount")
    scenario_pnl = corporate_pnl(scenario, "scenario_amount")

    s1m, s2m, s3m, s4m, s5m = st.columns(5)
    s1m.metric("Scenario revenue", usd(scenario_pnl["revenue"], 2), delta=usd(scenario_pnl["revenue"] - budget_pnl["revenue"], 1))
    s2m.metric("Scenario costs", usd(scenario_pnl["cost"], 2), delta=usd(budget_pnl["cost"] - scenario_pnl["cost"], 1), delta_color="normal")
    s3m.metric("Scenario EBITDA", usd(scenario_pnl["ebitda"], 2), delta=usd(scenario_pnl["ebitda"] - budget_pnl["ebitda"], 1))
    s4m.metric("EBITDA margin", f"{scenario_pnl['margin_pct']:.1f}%", delta=f"{scenario_pnl['margin_pct'] - budget_pnl['margin_pct']:.1f} pp")
    s5m.metric("Change vs base forecast", usd(scenario_pnl["ebitda"] - base_pnl["ebitda"], 1))

    monthly_rows = []
    for month, group in scenario.groupby("month", sort=True):
        budget = corporate_pnl(group, "budget_amount")["ebitda"]
        base = corporate_pnl(group, "base_forecast_amount")["ebitda"]
        scenario_ebitda = corporate_pnl(group, "scenario_amount")["ebitda"]
        monthly_rows.append(
            {
                "month": month,
                "Budget EBITDA": budget,
                "Base forecast EBITDA": base,
                "Scenario EBITDA": scenario_ebitda,
                "period_status": group["period_status"].iloc[0],
            }
        )
    monthly_scenario = pd.DataFrame(monthly_rows)
    scenario_chart = px.line(
        monthly_scenario,
        x="month",
        y=["Budget EBITDA", "Base forecast EBITDA", "Scenario EBITDA"],
        markers=True,
        color_discrete_map={
            "Budget EBITDA": NAVY,
            "Base forecast EBITDA": PURPLE,
            "Scenario EBITDA": TEAL,
        },
        title="Monthly EBITDA plan and scenario",
        labels={"value": "EBITDA ($)", "month": "Month", "variable": "Series"},
    )
    style_plotly(scenario_chart, height=500)
    st.plotly_chart(scenario_chart, width="stretch")

    unit_summary = []
    for business_unit, group in scenario.groupby("business_unit"):
        unit_budget = corporate_pnl(group, "budget_amount")
        unit_scenario = corporate_pnl(group, "scenario_amount")
        unit_summary.append(
            {
                "Business unit": business_unit,
                "Budget revenue ($)": unit_budget["revenue"],
                "Scenario revenue ($)": unit_scenario["revenue"],
                "Budget EBITDA ($)": unit_budget["ebitda"],
                "Scenario EBITDA ($)": unit_scenario["ebitda"],
                "Scenario margin %": unit_scenario["margin_pct"],
            }
        )
    st.dataframe(
        pd.DataFrame(unit_summary),
        hide_index=True,
        width="stretch",
        column_config={
            column: st.column_config.NumberColumn(format="$%,.0f")
            for column in [
                "Budget revenue ($)",
                "Scenario revenue ($)",
                "Budget EBITDA ($)",
                "Scenario EBITDA ($)",
            ]
        }
        | {"Scenario margin %": st.column_config.NumberColumn(format="%.1f%%")},
    )

with methods_tab:
    raw_rows = int(quality.loc[quality["check_name"].eq("source_rows"), "issue_count"].iloc[0])
    duplicate_rows = int(quality.loc[quality["check_name"].eq("duplicate_key_rows"), "issue_count"].iloc[0])
    review_items = int(quality["check_status"].eq("REVIEW").sum())
    q1, q2, q3 = st.columns(3)
    q1.metric("Source rows", f"{raw_rows:,}")
    q2.metric("Duplicate keys", f"{duplicate_rows:,}")
    q3.metric("Checks requiring context", f"{review_items}")
    st.dataframe(quality, hide_index=True, width="stretch")

    render_notice(
        "navy",
        "SRC",
        "Public source and synthetic model are deliberately separated",
        f"Public dataset {metadata['dataset_id']} supplies the Austin analysis. The corporate layer is documented as: {metadata['corporate_model_status']}.",
    )
    st.link_button("Open the City of Austin source", str(metadata["source_url"]), width="stretch")

    render_section(
        "Analyst deliverables",
        "Excel model and Power BI Desktop companion",
        "The Excel workbook is complete and formula-driven. Power BI files include reviewed measures, theme, model instructions, and a reproducible layout target; a .pbix is claimed only after Desktop validation.",
    )
    st.image(
        PROJECT_DIR / "assets" / "power_bi_companion.png",
        caption="Power BI executive-page layout target",
        width="stretch",
    )
    d1, d2, d3, d4 = st.columns(4)
    d1.download_button(
        "Download Excel FP&A model",
        data=(PROJECT_DIR / "assets" / "project_06_fpa_model.xlsx").read_bytes(),
        file_name="project_06_fpa_model.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
    d2.download_button(
        "Download Power BI theme",
        data=(POWER_BI_DIR / "theme.json").read_bytes(),
        file_name="financial_planning_theme.json",
        mime="application/json",
        width="stretch",
    )
    d3.download_button(
        "Download DAX measures",
        data=(POWER_BI_DIR / "measures.dax").read_bytes(),
        file_name="financial_planning_measures.dax",
        mime="text/plain",
        width="stretch",
    )
    d4.download_button(
        "Download Power BI guide",
        data=(POWER_BI_DIR / "README.md").read_bytes(),
        file_name="financial_planning_power_bi_guide.md",
        mime="text/markdown",
        width="stretch",
    )

render_footer()
