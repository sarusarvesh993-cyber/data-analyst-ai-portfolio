import pytest

from portfolio_app.ab_testing import (
    analyze_ab_test,
    decision,
    required_sample_per_arm,
)


def test_known_positive_experiment():
    result = analyze_ab_test(100_000, 11_522, 100_000, 12_802)
    assert result.control_rate == pytest.approx(0.11522)
    assert result.treatment_rate == pytest.approx(0.12802)
    assert result.absolute_lift == pytest.approx(0.0128)
    assert result.p_value < 0.001
    assert result.ci_low > 0
    outcome, _ = decision(result, practical_lift=0.005)
    assert outcome == "Ship treatment"


def test_validation_and_sample_size():
    with pytest.raises(ValueError):
        analyze_ab_test(100, 101, 100, 10)
    required = required_sample_per_arm(0.10, 0.10, power=0.80)
    assert 10_000 < required < 20_000
