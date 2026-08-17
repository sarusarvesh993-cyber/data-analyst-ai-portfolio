"""Entry point for the multi-page analytics portfolio."""
import streamlit as st

from portfolio_app.ui import (
    configure_page,
    inject_global_css,
    render_footer,
    render_home_hero,
    render_notice,
    render_section,
    render_sidebar,
)

configure_page("Data Analytics Portfolio", "📊")
inject_global_css()
render_sidebar()
render_home_hero()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Interactive projects", "05", help="Five complete analytical workflows")
kpi2.metric("Automated tests", "19", delta="All passing", delta_color="normal")
kpi3.metric(
    "Methods covered",
    "05",
    help="Classification, forecasting, experimentation, SQL, and segmentation",
)
kpi4.metric("Core app cost", "₹0", help="No paid API is required")

render_section(
    "Featured work",
    "Choose a business problem to explore",
    "Each page connects the analytical method to a decision, exposes its assumptions, and lets you interact with the result.",
)

row1 = st.columns(3)
row2 = st.columns(2)
projects = [
    (
        row1[0],
        "01",
        "Customer Churn & Retention",
        "Prioritize retention outreach with a reproducible classifier, adjustable threshold, and customer-level risk scenario.",
        ["Classification", "ROC–AUC 0.886", "Thresholds"],
        "#0F8A7B",
        "#DDF7F1",
        "pages/1_Customer_Churn.py",
        "Explore customer churn →",
    ),
    (
        row1[1],
        "02",
        "U.S. Retail Sales Forecast",
        "Backtest a seasonal forecast against a year-ago baseline and examine uncertainty over the next planning horizon.",
        ["Time series", "36.4% MAE gain", "Backtesting"],
        "#F4A340",
        "#FFF0D9",
        "pages/2_Retail_Sales_Forecast.py",
        "Explore the forecast →",
    ),
    (
        row1[2],
        "03",
        "A/B Test Decision Calculator",
        "Evaluate conversion lift, confidence intervals, practical significance, expected impact, and required sample size.",
        ["Experimentation", "Confidence intervals", "Power"],
        "#7C6CE7",
        "#ECE9FF",
        "pages/3_AB_Test_Calculator.py",
        "Explore the experiment →",
    ),
    (
        row2[0],
        "04",
        "E-commerce SQL Analytics",
        "Analyze 100K marketplace orders with safe SQL grains, cohort retention, delivery KPIs, and category performance.",
        ["DuckDB SQL", "Cohorts", "Data quality"],
        "#E26D5A",
        "#FDE8E3",
        "pages/4_Ecommerce_SQL.py",
        "Explore SQL analytics →",
    ),
    (
        row2[1],
        "05",
        "Customer Segmentation",
        "Build transparent RFM audiences, validate a clustering challenger, and turn segments into measurable campaign tests.",
        ["RFM", "K-means", "Power BI"],
        "#2B6F92",
        "#E4F1F8",
        "pages/5_Customer_Segmentation.py",
        "Explore customer segmentation →",
    ),
]
for column, number, title, copy, tags, accent, soft, page, label in projects:
    tag_html = "".join(f'<span class="tag">{tag}</span>' for tag in tags)
    with column:
        st.markdown(
            f"""
            <div class="project-card" style="--accent:{accent};--soft:{soft};">
                <div class="project-number">{number}</div>
                <div class="project-title">{title}</div>
                <div class="project-copy">{copy}</div>
                {tag_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label=label, width="stretch")

render_section(
    "Capabilities",
    "What this portfolio demonstrates",
    "A balanced data analyst workflow: prepare evidence, validate the method, explain the result, and deliver it clearly.",
)
cap1, cap2, cap3, cap4 = st.columns(4)
for column, icon, title, copy in [
    (
        cap1,
        "01",
        "Business analysis",
        "KPI design, exploratory analysis, segmentation, and decision-focused recommendations.",
    ),
    (
        cap2,
        "02",
        "Statistical rigor",
        "Confidence intervals, A/B tests, baselines, stability checks, and time-based validation.",
    ),
    (
        cap3,
        "03",
        "SQL & data modeling",
        "Relational joins, safe analytical grains, cohorts, quality checks, and BI-ready tables.",
    ),
    (
        cap4,
        "04",
        "Interactive delivery",
        "One consistent Streamlit app, automated tests, and reproducible Power BI companion assets.",
    ),
]:
    with column:
        st.markdown(
            f"""
            <div class="capability-card">
                <div class="capability-icon">{icon}</div>
                <div class="capability-title">{title}</div>
                <div class="capability-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_section("Workflow", "How I approach an analytics problem")
step1, step2, step3, step4 = st.columns(4)
for column, step, title, copy in [
    (
        step1,
        "STEP 01",
        "Frame",
        "Define the decision, stakeholder, metric, and constraints.",
    ),
    (
        step2,
        "STEP 02",
        "Validate",
        "Check data quality and compare with a credible baseline.",
    ),
    (
        step3,
        "STEP 03",
        "Analyze",
        "Use an appropriate statistical, predictive, or segmentation method.",
    ),
    (
        step4,
        "STEP 04",
        "Recommend",
        "State the action, uncertainty, limitation, and next test.",
    ),
]:
    with column:
        st.markdown(
            f"""
            <div class="process-card">
                <div class="process-step">{step}</div>
                <div class="process-title">{title}</div>
                <div class="process-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_notice(
    "navy",
    "AI",
    "AI use is controlled and explicit",
    "The quantitative analysis is deterministic and reviewable. An optional LLM receives only approved metrics to draft a stakeholder brief; it does not create the data, select the model, or calculate the results.",
)
render_footer()
