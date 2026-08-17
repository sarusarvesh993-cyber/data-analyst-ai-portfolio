"""Interactive page for the A/B test significance project."""
import math

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_app.ab_testing import (
    analyze_ab_test,
    decision,
    required_sample_per_arm,
)
from utils.ai_insights import generate_insights

st.set_page_config(page_title="A/B Test | Sarvesh Kommawar", page_icon="🧪", layout="wide")
st.title("03 · A/B Test Decision Calculator")
st.write(
    "**Business question:** Is the observed conversion lift reliable and large enough to "
    "matter, or should the team continue the experiment?"
)

calculator_tab, planner_tab, method_tab, brief_tab = st.tabs(
    ["Test calculator", "Sample-size planner", "Method", "AI-assisted brief"]
)

with calculator_tab:
    st.subheader("Enter cumulative experiment results")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Control**")
        control_visitors = st.number_input("Control visitors", 1, 10_000_000, 100_000, 100)
        control_conversions = st.number_input("Control conversions", 0, 10_000_000, 11_522, 10)
    with c2:
        st.markdown("**Treatment**")
        treatment_visitors = st.number_input("Treatment visitors", 1, 10_000_000, 100_000, 100)
        treatment_conversions = st.number_input("Treatment conversions", 0, 10_000_000, 12_802, 10)

    practical_lift_pp = st.slider(
        "Minimum useful absolute lift (percentage points)", 0.0, 5.0, 0.5, 0.1
    )
    alpha = st.select_slider("Significance level α", options=[0.01, 0.05, 0.10], value=0.05)

    error = None
    try:
        result = analyze_ab_test(
            int(control_visitors),
            int(control_conversions),
            int(treatment_visitors),
            int(treatment_conversions),
            alpha=float(alpha),
        )
    except ValueError as exc:
        error = str(exc)
        result = None

    if error:
        st.error(error)
    else:
        outcome, explanation = decision(
            result,
            practical_lift=practical_lift_pp / 100.0,
            alpha=float(alpha),
        )
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Control rate", f"{result.control_rate:.2%}")
        r2.metric("Treatment rate", f"{result.treatment_rate:.2%}")
        relative_text = "∞" if math.isinf(result.relative_lift) else f"{result.relative_lift:+.1%}"
        r3.metric("Relative lift", relative_text)
        r4.metric("Two-sided p-value", f"{result.p_value:.3g}")

        st.subheader(outcome)
        st.write(explanation)
        st.write(
            f"**Absolute lift:** {result.absolute_lift:+.2%}  ·  "
            f"**{(1-alpha):.0%} CI:** [{result.ci_low:+.2%}, {result.ci_high:+.2%}]  ·  "
            f"**Estimated incremental conversions in treatment:** {result.incremental_conversions:+,.0f}"
        )

        rates = pd.DataFrame(
            {"Variant": ["Control", "Treatment"], "Conversion rate": [result.control_rate, result.treatment_rate]}
        )
        figure = px.bar(
            rates,
            x="Variant",
            y="Conversion rate",
            text_auto=".2%",
            color="Variant",
            title="Observed conversion rates",
        )
        figure.update_yaxes(tickformat=".1%")
        figure.update_layout(showlegend=False)
        st.plotly_chart(figure, width="stretch")

with planner_tab:
    st.subheader("Plan before launching")
    p1, p2, p3 = st.columns(3)
    baseline = p1.number_input("Expected baseline conversion", 0.1, 99.0, 10.0, 0.1) / 100.0
    relative_mde = p2.number_input("Minimum detectable relative lift", 0.1, 100.0, 10.0, 0.5) / 100.0
    target_power = p3.select_slider("Target power", options=[0.80, 0.85, 0.90, 0.95], value=0.80)
    try:
        required = required_sample_per_arm(
            baseline_rate=baseline,
            relative_mde=relative_mde,
            alpha=0.05,
            power=target_power,
        )
        st.metric("Required sample per arm", f"{required:,}")
        st.caption(
            f"Approximately {required * 2:,} visitors total for two equal groups, a two-sided "
            "test, α = 0.05, and no adjustment for attrition or repeated peeking."
        )
    except ValueError as exc:
        st.error(str(exc))

with method_tab:
    st.markdown(
        """
        ### What is calculated
        1. Conversion rate for each arm.
        2. A two-sided pooled two-proportion z-test for the null hypothesis that rates are equal.
        3. An unpooled normal-approximation confidence interval for treatment minus control.
        4. Statistical significance **and** a user-defined minimum useful effect.

        ### Assumptions
        - Users are independently randomized and appear once.
        - Variants ran concurrently and assignment was not biased.
        - The conversion event and analysis window were specified before looking at results.
        - Sample sizes are large enough for the normal approximation.

        ### Important limitation
        Repeatedly checking and stopping a fixed-horizon test inflates false positives. Use a
        pre-committed sample size or a sequential-testing design if continuous monitoring is required.
        """
    )

with brief_tab:
    if result is None:
        st.info("Enter valid counts in the calculator to create a brief.")
    else:
        outcome, _ = decision(
            result,
            practical_lift=practical_lift_pp / 100.0,
            alpha=float(alpha),
        )
        brief = generate_insights(
            {
                "headline": (
                    f"Treatment converted at {result.treatment_rate:.2%} versus "
                    f"{result.control_rate:.2%} for control. Absolute lift is "
                    f"{result.absolute_lift:+.2%}, p={result.p_value:.3g}, and the "
                    f"confidence interval is [{result.ci_low:+.2%}, {result.ci_high:+.2%}]."
                ),
                "drivers": [
                    "Observed conversion counts and sample sizes",
                    "Sampling uncertainty represented by the confidence interval",
                    f"Business threshold of {practical_lift_pp:.1f} percentage points",
                ],
                "recommendation": (
                    f"Current decision: {outcome}. Confirm guardrail metrics, randomization "
                    "quality, and experiment duration before rollout."
                ),
            }
        )
        st.markdown(brief)
        st.caption(
            "The LLM layer receives only the displayed statistics and decision context. It "
            "does not alter the hypothesis test or sample-size calculation."
        )
