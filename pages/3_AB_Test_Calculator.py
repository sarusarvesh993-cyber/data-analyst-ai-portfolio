"""Interactive page for the A/B test significance project."""
import math

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_app.ab_testing import analyze_ab_test, decision, required_sample_per_arm
from portfolio_app.ui import (
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

configure_page("A/B Test Calculator", "🧪")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 03 · Experimentation",
    "A/B Test Decision Calculator",
    "Decide whether an observed conversion lift is statistically reliable, commercially useful, and supported by an adequately planned sample.",
    ["Two-proportion z-test", "Confidence interval", "Practical significance", "Power planning"],
)
render_notice(
    "teal",
    "✓",
    "Decision rule",
    "A small p-value is not enough. The result should also clear a business-defined minimum useful lift and pass experiment-quality checks before rollout.",
)

render_section(
    "Experiment workspace",
    "Test the result, then plan the next experiment",
    "Use aggregate visitor and conversion counts. The default values reproduce the portfolio example.",
)
calculator_tab, planner_tab, method_tab, brief_tab = st.tabs(
    ["Test calculator", "Sample-size planner", "Method", "AI-assisted brief"]
)

result = None
practical_lift_pp = 0.5
alpha = 0.05

with calculator_tab:
    st.subheader("Enter cumulative experiment results")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### Control · Current experience")
            control_visitors = st.number_input("Control visitors", 1, 10_000_000, 100_000, 100)
            control_conversions = st.number_input("Control conversions", 0, 10_000_000, 11_522, 10)
    with c2:
        with st.container(border=True):
            st.markdown("#### Treatment · New experience")
            treatment_visitors = st.number_input("Treatment visitors", 1, 10_000_000, 100_000, 100)
            treatment_conversions = st.number_input("Treatment conversions", 0, 10_000_000, 12_802, 10)

    control1, control2 = st.columns(2)
    practical_lift_pp = control1.slider(
        "Minimum useful absolute lift (percentage points)", 0.0, 5.0, 0.5, 0.1
    )
    alpha = control2.select_slider("Significance level α", options=[0.01, 0.05, 0.10], value=0.05)

    try:
        result = analyze_ab_test(
            int(control_visitors),
            int(control_conversions),
            int(treatment_visitors),
            int(treatment_conversions),
            alpha=float(alpha),
        )
    except ValueError as exc:
        st.error(str(exc))

    if result is not None:
        outcome, explanation = decision(
            result,
            practical_lift=practical_lift_pp / 100.0,
            alpha=float(alpha),
        )
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Control rate", f"{result.control_rate:.2%}")
        r2.metric("Treatment rate", f"{result.treatment_rate:.2%}")
        relative_text = "∞" if math.isinf(result.relative_lift) else f"{result.relative_lift:+.1%}"
        r3.metric("Relative lift", relative_text, delta="Treatment vs control")
        r4.metric("Two-sided p-value", f"{result.p_value:.3g}")

        notice_kind = "teal" if outcome == "Ship treatment" else "amber"
        render_notice(notice_kind, "→", outcome, explanation)
        st.markdown(
            f"**Absolute lift:** `{result.absolute_lift:+.2%}` &nbsp;·&nbsp; "
            f"**{(1-alpha):.0%} CI:** `[{result.ci_low:+.2%}, {result.ci_high:+.2%}]` &nbsp;·&nbsp; "
            f"**Estimated incremental conversions:** `{result.incremental_conversions:+,.0f}`"
        )

        rates = pd.DataFrame(
            {
                "Variant": ["Control", "Treatment"],
                "Conversion rate": [result.control_rate, result.treatment_rate],
            }
        )
        figure = px.bar(
            rates,
            x="Variant",
            y="Conversion rate",
            text_auto=".2%",
            color="Variant",
            color_discrete_map={"Control": NAVY, "Treatment": TEAL},
            title="Observed conversion rates",
        )
        figure.update_yaxes(tickformat=".1%")
        style_plotly(figure, height=410, show_legend=False)
        st.plotly_chart(figure, width="stretch")

with planner_tab:
    st.subheader("Plan before launching")
    st.caption("Set the assumptions before the result is visible to avoid post-hoc power claims.")
    with st.container(border=True):
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
        s1, s2, s3 = st.columns(3)
        s1.metric("Required per arm", f"{required:,}")
        s2.metric("Total visitors", f"{required * 2:,}")
        s3.metric("Target power", f"{target_power:.0%}")
        render_notice(
            "navy",
            "i",
            "Planning estimate",
            "This assumes two equal groups, a two-sided test, α = 0.05, and no adjustment for attrition, repeated peeking, or multiple metrics.",
        )
    except ValueError as exc:
        st.error(str(exc))

with method_tab:
    left, right = st.columns(2)
    with left:
        st.markdown("### What is calculated")
        st.markdown(
            """
            1. Conversion rate for each arm
            2. Two-sided pooled two-proportion z-test
            3. Unpooled interval for treatment minus control
            4. Statistical and practical significance
            5. Equal-arm sample-size requirement
            """
        )
    with right:
        st.markdown("### Core assumptions")
        st.markdown(
            """
            - Independent randomized users
            - Concurrent experiment variants
            - Pre-specified conversion event and window
            - Adequate expected successes and failures
            - No unplanned repeated stopping
            """
        )
    render_notice(
        "amber",
        "!",
        "Repeated peeking changes the false-positive rate",
        "Use a pre-committed fixed horizon or an appropriate sequential-testing design when continuous monitoring is required.",
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
        render_notice(
            "navy",
            "AI",
            "Controlled decision brief",
            "The text layer receives only the displayed statistics and decision context. It does not alter the hypothesis test or sample-size calculation.",
        )
        st.markdown(brief)

render_footer()
