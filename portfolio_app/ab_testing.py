"""Statistical calculations for the A/B test project."""
from __future__ import annotations

from dataclasses import dataclass
import math

from scipy.stats import norm
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


@dataclass(frozen=True)
class ABTestResult:
    control_rate: float
    treatment_rate: float
    absolute_lift: float
    relative_lift: float
    z_score: float
    p_value: float
    ci_low: float
    ci_high: float
    incremental_conversions: float


def analyze_ab_test(
    control_visitors: int,
    control_conversions: int,
    treatment_visitors: int,
    treatment_conversions: int,
    alpha: float = 0.05,
) -> ABTestResult:
    """Run a two-sided pooled z-test and an unpooled CI for rate difference."""
    values = [
        control_visitors,
        control_conversions,
        treatment_visitors,
        treatment_conversions,
    ]
    if any(int(value) != value or value < 0 for value in values):
        raise ValueError("Visitors and conversions must be non-negative integers")
    if control_visitors == 0 or treatment_visitors == 0:
        raise ValueError("Each variant must have at least one visitor")
    if control_conversions > control_visitors:
        raise ValueError("Control conversions cannot exceed control visitors")
    if treatment_conversions > treatment_visitors:
        raise ValueError("Treatment conversions cannot exceed treatment visitors")

    p_control = control_conversions / control_visitors
    p_treatment = treatment_conversions / treatment_visitors
    difference = p_treatment - p_control

    pooled = (control_conversions + treatment_conversions) / (
        control_visitors + treatment_visitors
    )
    pooled_se = math.sqrt(
        pooled * (1.0 - pooled) * (1.0 / control_visitors + 1.0 / treatment_visitors)
    )
    if pooled_se == 0:
        z_score = 0.0
        p_value = 1.0
    else:
        z_score = difference / pooled_se
        p_value = float(2.0 * norm.sf(abs(z_score)))

    ci_se = math.sqrt(
        p_control * (1.0 - p_control) / control_visitors
        + p_treatment * (1.0 - p_treatment) / treatment_visitors
    )
    critical = float(norm.ppf(1.0 - alpha / 2.0))
    relative = difference / p_control if p_control else math.inf

    return ABTestResult(
        control_rate=p_control,
        treatment_rate=p_treatment,
        absolute_lift=difference,
        relative_lift=relative,
        z_score=float(z_score),
        p_value=p_value,
        ci_low=float(difference - critical * ci_se),
        ci_high=float(difference + critical * ci_se),
        incremental_conversions=float(difference * treatment_visitors),
    )


def decision(result: ABTestResult, practical_lift: float = 0.0, alpha: float = 0.05) -> tuple[str, str]:
    """Combine statistical evidence with a minimum useful absolute lift."""
    if result.p_value < alpha and result.ci_low >= practical_lift:
        return (
            "Ship treatment",
            "The result is statistically significant and the confidence interval clears the minimum useful lift.",
        )
    if result.p_value < alpha and result.absolute_lift > practical_lift:
        return (
            "Promising, but assess value",
            "The average lift is useful, but the confidence interval does not fully clear the practical threshold.",
        )
    if result.ci_high < practical_lift:
        return (
            "Do not ship for this goal",
            "The confidence interval is below the minimum useful lift set for the experiment.",
        )
    return (
        "Continue or redesign test",
        "The current evidence is inconclusive; a non-significant result is not proof that the variants are equal.",
    )


def required_sample_per_arm(
    baseline_rate: float,
    relative_mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Estimate equal-sized samples needed for a two-sided proportion test."""
    if not 0 < baseline_rate < 1:
        raise ValueError("baseline_rate must be between 0 and 1")
    if not 0 < relative_mde < 1:
        raise ValueError("relative_mde must be between 0 and 1")
    treatment_rate = baseline_rate * (1.0 + relative_mde)
    if treatment_rate >= 1:
        raise ValueError("baseline plus minimum effect must remain below 100%")
    effect = abs(proportion_effectsize(treatment_rate, baseline_rate))
    estimate = NormalIndPower().solve_power(
        effect_size=effect,
        alpha=alpha,
        power=power,
        ratio=1.0,
        alternative="two-sided",
    )
    return int(math.ceil(estimate))
