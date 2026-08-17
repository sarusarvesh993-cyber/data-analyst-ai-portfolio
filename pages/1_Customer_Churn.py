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
from utils.ai_insights import generate_insights

st.set_page_config(page_title="Customer Churn | Sarvesh Kommawar", page_icon="📉", layout="wide")
st.title("01 · Customer Churn & Retention")
st.write(
    "**Business question:** Which customer profiles should the retention team prioritize, "
    "and how does the decision threshold change workload and recall?"
)
st.warning(
    "Portfolio demonstration: the 5,000-customer dataset is synthetic and generated from a "
    "fixed seed. Findings demonstrate the workflow and must not be treated as estimates for "
    "a real company."
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
k1.metric("Customers", f"{len(data):,}")
k2.metric("Observed churn", f"{data['Churn'].mean():.1%}")
k3.metric("Holdout ROC–AUC", f"{model_result.auc:.3f}")
k4.metric("Holdout records", f"{len(model_result.y_test):,}")

overview_tab, scoring_tab, diagnostics_tab, brief_tab = st.tabs(
    ["Business overview", "Risk scenario", "Model diagnostics", "AI-assisted brief"]
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
        color="Churn",
        color_continuous_scale="Blues",
    )
    fig_contract.update_yaxes(tickformat=".0%")
    fig_contract.update_coloraxes(showscale=False)
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
    fig_tenure.update_yaxes(tickformat=".0%")
    right.plotly_chart(fig_tenure, width="stretch")

    st.markdown("**Decision takeaway**")
    st.write(
        "In this generated scenario, month-to-month contracts and early tenure are useful "
        "signals for prioritization. A real retention program would validate these patterns "
        "on production data and measure incremental retention with a controlled experiment."
    )

with scoring_tab:
    st.subheader("Score one customer scenario")
    with st.form("customer_form"):
        c1, c2, c3 = st.columns(3)
        tenure_value = c1.slider("Tenure (months)", 1, 72, 8)
        monthly_value = c1.slider("Monthly charges", 20.0, 120.0, 85.0, 1.0)
        contract_value = c2.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        internet_value = c2.selectbox("Internet service", ["DSL", "Fiber optic", "No"])
        tech_value = c3.selectbox("Tech support", ["No", "Yes"])
        security_value = c3.selectbox("Online security", ["No", "Yes"])
        payment_value = c3.selectbox(
            "Payment method",
            ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        )
        senior_value = c1.checkbox("Senior citizen")
        dependents_value = c2.checkbox("Has dependents")
        submitted = st.form_submit_button("Calculate risk")

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
        st.metric("Estimated churn probability", f"{probability:.1%}", delta=f"{band} priority")
        st.caption(
            "This is a model score from synthetic training data, not a probability calibrated "
            "for a real customer population."
        )

with diagnostics_tab:
    st.subheader("Choose an operating threshold")
    threshold = st.slider(
        "Flag customers at or above this predicted probability",
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
            colorscale="Blues",
            showscale=False,
        )
    )
    heatmap.update_layout(title="Holdout confusion matrix", height=390)
    left.plotly_chart(heatmap, width="stretch")

    importance = feature_importance(model_result).head(10).sort_values("importance")
    fig_importance = px.bar(
        importance,
        x="importance",
        y="feature",
        orientation="h",
        title="Logistic coefficient magnitude",
        labels={"importance": "Absolute standardized coefficient", "feature": "Feature"},
    )
    right.plotly_chart(fig_importance, width="stretch")
    st.caption(
        "Coefficient magnitude describes association in this fitted model; it is not a causal "
        "estimate. Threshold selection should reflect contact capacity and the "
        "cost of missed churners versus unnecessary outreach."
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
    st.markdown(brief)
    with st.expander("How the AI layer is controlled"):
        st.write(
            "Only calculated metrics and analyst-selected context are passed to the text layer. "
            "Without an HF_TOKEN, the function returns a deterministic authored template. The "
            "underlying model metrics do not depend on the LLM."
        )
