"""Entry point for the multi-page analytics portfolio."""
import streamlit as st

st.set_page_config(
    page_title="Sarvesh Kommawar | Data Analytics Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px;}
    [data-testid="stMetric"] {background: #f7f9fc; border: 1px solid #e4e9f2; padding: 1rem; border-radius: .75rem;}
    .project-card {border: 1px solid #e4e9f2; border-radius: .8rem; padding: 1.1rem; min-height: 180px;}
    .eyebrow {color: #1769aa; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: .78rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="eyebrow">Data analyst portfolio</p>', unsafe_allow_html=True)
st.title("From business question to measurable decision")
st.write(
    "I use Python, statistics, machine learning, and interactive dashboards to turn "
    "messy questions into decisions a stakeholder can act on."
)

left, middle, right = st.columns(3)
left.metric("Projects available", "3")
middle.metric("Live analytical workflows", "3")
right.metric("Core app cost", "₹0")

st.subheader("Explore the work")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="project-card">
        <b>01 · Customer churn</b><br><br>
        Prioritize retention outreach using a reproducible classifier, adjustable decision threshold, and customer-level risk scenario.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Customer_Churn.py", label="Open churn project →")
with col2:
    st.markdown(
        """
        <div class="project-card">
        <b>02 · U.S. retail sales forecast</b><br><br>
        Backtest a seasonal forecast against a year-ago baseline and examine the uncertainty around the next planning horizon.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Retail_Sales_Forecast.py", label="Open forecasting project →")
with col3:
    st.markdown(
        """
        <div class="project-card">
        <b>03 · A/B test calculator</b><br><br>
        Evaluate conversion lift, confidence intervals, practical significance, expected impact, and required sample size.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_AB_Test_Calculator.py", label="Open experiment project →")

st.subheader("What this portfolio demonstrates")
skill1, skill2, skill3, skill4 = st.columns(4)
skill1.markdown("**Analysis**\n\npandas · EDA · KPI design")
skill2.markdown("**Statistics**\n\nA/B tests · confidence intervals · backtesting")
skill3.markdown("**Modeling**\n\nclassification · forecasting · threshold selection")
skill4.markdown("**Delivery**\n\nStreamlit · GitHub · reproducible workflows")

st.divider()
st.markdown("### AI use and analytical ownership")
st.write(
    "The numerical analysis in every project is deterministic and reviewable. An optional "
    "LLM layer translates calculated metrics into a draft stakeholder brief; it does not "
    "create data, choose the model, or calculate results. AI-produced text is labeled and "
    "the app remains fully functional without an API token."
)
st.markdown(
    "Portfolio by **Sarvesh Kommawar** · "
    "[GitHub](https://github.com/sarusarvesh993-cyber) · "
    "[LinkedIn](https://www.linkedin.com/in/sarvesh-kommawar-3b166b278/) · "
    "[Email](mailto:kommawar57@gmail.com)"
)
