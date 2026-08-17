"""Interactive page for the customer-churn project."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.churn import (
    feature_importance,
    make_churn_data,
    score_customer,
    threshold_metrics,
    train_churn_model,
)
from portfolio_app.ui import (
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
from utils.ai_insights import generate_insights

configure_page("Customer Churn", "📉")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 01 · Retention analytics",
    "Customer Churn & Retention",
    "Identify which customer profiles to prioritize and see how the score threshold changes campaign workload, precision, and recall.",
    ["Classification", "Logistic regression", "ROC–AUC 0.886", "Decision thresholds"],
)
render_notice(
    "amber",
    "!",
    "Demonstration dataset",
    "The 5,000 customer records are generated from a fixed seed. The page demonstrates a reproducible workflow; its findings are not estimates for a real company.",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return make_churn_data()


@st.cache_resource
def load_model():
    return train_churn_model(make_churn_data())


data = load_data()
model_result = load_model()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Customer records", f"{len(data):,}")
k2.metric("Observed churn", f"{data['Churn'].mean():.1%}")
k3.metric("Holdout ROC–AUC", f"{model_result.auc:.3f}", delta="Better than RF")
k4.metric("Holdout sample", f"{len(model_result.y_test):,}")

render_section(
    "Interactive analysis",
    "From portfolio-level patterns to one customer scenario",
    "Move between the business view, customer score, model diagnostics, and controlled stakeholder brief.",
)
overview_tab, scoring_tab, diagnostics_tab, brief_tab = st.tabs(
    ["Overview", "Score a scenario", "Model diagnostics", "AI-assisted brief"]
)

with overview_tab:
    left, right = st.columns(2)
    contract = data.groupby("Contract", as_index=False)["Churn"].mean()
    fig_contract = px.bar(
        contract,
        x="Contract",
        y="Churn",
        text_auto=".1%",
        title="Churn rate by contract",
        labels={"Churn": "Churn rate"},
        color="Contract",
        color_discrete_sequence=[TEAL, "#55A6D9", NAVY],
    )
    fig_contract.update_yaxes(tickformat=".0%")
    style_plotly(fig_contract, height=390, show_legend=False)
    left.plotly_chart(fig_contract, width="stretch")

    tenure = (
        data.assign(
            tenure_band=pd.cut(
                data["tenure"],
                bins=[0, 12, 24, 48, 72],
                labels=["1–12", "13–24", "25–48", "49–72"],
            )
        )
        .groupby("tenure_band", observed=True, as_index=False)["Churn"]
        .mean()
    )
    fig_tenure = px.line(
        tenure,
        x="tenure_band",
        y="Churn",
        markers=True,
        title="Churn rate by tenure band",
        labels={"tenure_band": "Tenure (months)", "Churn": "Churn rate"},
    )
    fig_tenure.update_traces(line=dict(color=TEAL, width=4), marker=dict(size=10, color=NAVY))
    fig_tenure.update_yaxes(tickformat=".0%")
    style_plotly(fig_tenure, height=390, show_legend=False)
    right.plotly_chart(fig_tenure, width="stretch")

    render_notice(
        "teal",
        "→",
        "Decision takeaway",
        "In this generated scenario, month-to-month contracts and early tenure help prioritize outreach. A real retention program should validate the pattern on production data and measure incremental retention with a randomized holdout.",
    )

with scoring_tab:
    st.subheader("Build one customer scenario")
    st.caption("Adjust the account profile, then calculate its model score.")
    with st.form("customer_form", border=True):
        c1, c2, c3 = st.columns(3)
        tenure_value = c1.slider("Tenure (months)", 1, 72, 8)
        monthly_value = c1.slider("Monthly charges", 20.0, 120.0, 85.0, 1.0)
        senior_value = c1.checkbox("Senior citizen")

        contract_value = c2.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        internet_value = c2.selectbox("Internet service", ["DSL", "Fiber optic", "No"])
        dependents_value = c2.checkbox("Has dependents")

        tech_value = c3.selectbox("Tech support", ["No", "Yes"])
        security_value = c3.selectbox("Online security", ["No", "Yes"])
        payment_value = c3.selectbox(
            "Payment method",
            ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        )
        submitted = st.form_submit_button("Calculate customer risk", width="stretch")

    if submitted:
        customer = {
            "tenure": tenure_value,
            "MonthlyCharges": monthly_value,
            "SeniorCitizen": int(senior_value),
            "Dependents": int(dependents_value),
            "Contract": contract_value,
            "InternetService": internet_value,
            "TechSupport": tech_value,
            "OnlineSecurity": security_value,
            "PaymentMethod": payment_value,
        }
        probability = score_customer(model_result.model, customer)
        band = "High" if probability >= 0.65 else "Medium" if probability >= 0.35 else "Low"
        result_col, explanation_col = st.columns([1, 2])
        result_col.metric("Estimated churn score", f"{probability:.1%}", delta=f"{band} priority")
        with explanation_col:
            render_notice(
                "navy",
                "i",
                f"{band} outreach priority",
                "This score comes from synthetic training data. It demonstrates prioritization logic and is not a probability calibrated for a real customer population.",
            )

with diagnostics_tab:
    st.subheader("Choose an operating threshold")
    st.caption("A lower threshold captures more churners but creates more unnecessary contacts.")
    threshold = st.slider(
        "Flag customers at or above this score",
        min_value=0.20,
        max_value=0.80,
        value=0.50,
        step=0.05,
    )
    metrics = threshold_metrics(model_result, threshold)
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Precision", f"{metrics['precision']:.1%}")
    d2.metric("Recall", f"{metrics['recall']:.1%}")
    d3.metric("F1 score", f"{metrics['f1']:.3f}")
    d4.metric("Customers flagged", f"{metrics['flagged']:,}")

    left, right = st.columns(2)
    matrix = metrics["confusion_matrix"]
    heatmap = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=["Predicted stay", "Predicted churn"],
            y=["Actual stay", "Actual churn"],
            text=matrix,
            texttemplate="%{text}",
            colorscale=[[0, "#E7F5F2"], [0.5, "#55A6D9"], [1, NAVY]],
            showscale=False,
            hovertemplate="%{y}<br>%{x}<br>Customers: %{z}<extra></extra>",
        )
    )
    heatmap.update_layout(title="Holdout confusion matrix")
    style_plotly(heatmap, height=410, show_legend=False)
    left.plotly_chart(heatmap, width="stretch")

    importance = feature_importance(model_result).head(10).sort_values("importance")
    fig_importance = px.bar(
        importance,
        x="importance",
        y="feature",
        orientation="h",
        title="Logistic coefficient magnitude",
        labels={"importance": "Absolute standardized coefficient", "feature": "Feature"},
        color="importance",
        color_continuous_scale=[[0, "#BDE9E1"], [1, TEAL]],
    )
    fig_importance.update_coloraxes(showscale=False)
    style_plotly(fig_importance, height=410, show_legend=False)
    right.plotly_chart(fig_importance, width="stretch")
    st.caption(
        "Coefficient magnitude describes association in this fitted model, not causation. "
        "Threshold selection should reflect contact capacity and the cost of missed churners."
    )

with brief_tab:
    default_metrics = threshold_metrics(model_result, 0.50)
    brief = generate_insights(
        {
            "headline": (
                f"The holdout ROC–AUC is {model_result.auc:.3f}. At a 0.50 threshold, "
                f"recall is {default_metrics['recall']:.1%} and precision is "
                f"{default_metrics['precision']:.1%}."
            ),
            "drivers": [
                "Contract type and monthly charges",
                "Early customer tenure",
                "Internet, support, security, and payment selections",
            ],
            "recommendation": (
                "Pilot prioritized retention outreach, set the score threshold from campaign "
                "capacity and economics, and measure incremental retention against a holdout."
            ),
        }
    )
    render_notice(
        "navy",
        "AI",
        "Controlled text layer",
        "Only calculated metrics and analyst-selected context reach this layer. The model diagnostics do not depend on the LLM.",
    )
    st.markdown(brief)
    with st.expander("How the fallback works"):
        st.write(
            "Without an HF_TOKEN, the app returns a deterministic analyst-authored template. "
            "If the optional inference request fails, the same fallback keeps the page usable."
        )

render_footer()
