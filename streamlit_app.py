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
kpi1.metric("Interactive projects", "04", help="Four complete analytical workflows")
kpi2.metric("Automated tests", "14", delta="All passing", delta_color="normal")
kpi3.metric("Methods covered", "04", help="Classification, forecasting, experimentation, and SQL")
kpi4.metric("Core app cost", "₹0", help="No paid API is required")

render_section(
    "Featured work",
    "Choose a business problem to explore",
    "Each page connects the analytical method to a decision, exposes its assumptions, and lets you interact with the result.",
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        """
        <div class="project-card" style="--accent:#0F8A7B;--soft:#DDF7F1;">
            <div class="project-number">01</div>
            <div class="project-title">Customer Churn &amp; Retention</div>
            <div class="project-copy">
                Prioritize retention outreach with a reproducible classifier,
                adjustable threshold, and customer-level risk scenario.
            </div>
            <span class="tag">Classification</span>
            <span class="tag">ROC–AUC 0.886</span>
            <span class="tag">Thresholds</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Customer_Churn.py", label="Explore customer churn →", width="stretch")

with col2:
    st.markdown(
        """
        <div class="project-card" style="--accent:#F4A340;--soft:#FFF0D9;">
            <div class="project-number">02</div>
            <div class="project-title">U.S. Retail Sales Forecast</div>
            <div class="project-copy">
                Backtest a seasonal forecast against a year-ago baseline and
                examine uncertainty over the next planning horizon.
            </div>
            <span class="tag">Time series</span>
            <span class="tag">36.4% MAE gain</span>
            <span class="tag">Backtesting</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Retail_Sales_Forecast.py", label="Explore the forecast →", width="stretch")

with col3:
    st.markdown(
        """
        <div class="project-card" style="--accent:#7C6CE7;--soft:#ECE9FF;">
            <div class="project-number">03</div>
            <div class="project-title">A/B Test Decision Calculator</div>
            <div class="project-copy">
                Evaluate conversion lift, confidence intervals, practical
                significance, expected impact, and required sample size.
            </div>
            <span class="tag">Experimentation</span>
            <span class="tag">Confidence intervals</span>
            <span class="tag">Power</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_AB_Test_Calculator.py", label="Explore the experiment →", width="stretch")

with col4:
    st.markdown(
        """
        <div class="project-card" style="--accent:#E26D5A;--soft:#FDE8E3;">
            <div class="project-number">04</div>
            <div class="project-title">E-commerce SQL Analytics</div>
            <div class="project-copy">
                Analyze 100K marketplace orders with safe SQL grains,
                cohort retention, delivery KPIs, and category performance.
            </div>
            <span class="tag">DuckDB SQL</span>
            <span class="tag">Cohorts</span>
            <span class="tag">Data quality</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/4_Ecommerce_SQL.py", label="Explore SQL analytics →", width="stretch")

render_section(
    "Capabilities",
    "What this portfolio demonstrates",
    "A balanced data analyst workflow: prepare evidence, validate the method, explain the result, and deliver it clearly.",
)
cap1, cap2, cap3, cap4 = st.columns(4)
for column, icon, title, copy in [
    (cap1, "01", "Business analysis", "KPI design, exploratory analysis, and decision-focused recommendations."),
    (cap2, "02", "Statistical rigor", "Confidence intervals, A/B tests, baselines, and time-based validation."),
    (cap3, "03", "SQL & data modeling", "Relational joins, safe analytical grains, cohorts, and quality checks."),
    (cap4, "04", "Interactive delivery", "One consistent Streamlit app, automated tests, and a GitHub deployment workflow."),
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
    (step1, "STEP 01", "Frame", "Define the decision, stakeholder, metric, and constraints."),
    (step2, "STEP 02", "Validate", "Check data quality and compare with a credible baseline."),
    (step3, "STEP 03", "Analyze", "Use an appropriate statistical or predictive method."),
    (step4, "STEP 04", "Recommend", "State the action, uncertainty, limitation, and next test."),
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
