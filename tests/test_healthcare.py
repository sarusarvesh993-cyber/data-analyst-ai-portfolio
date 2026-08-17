"""Tests for Project 07 healthcare access and readiness outputs."""
from pathlib import Path

import pytest

from portfolio_app.healthcare import filter_states, load_outputs, priority_export

ROOT = Path(__file__).parents[1]
PROJECT = ROOT / "07-healthcare-access"
OUTPUTS = PROJECT / "outputs"


def test_healthcare_outputs_reconcile_to_official_report_extract():
    outputs = load_outputs(OUTPUTS)
    assert set(outputs) == {"kpis", "states", "regions", "priorities", "quality", "dictionary", "metadata"}
    kpis = outputs["kpis"].iloc[0]
    assert int(kpis["states_and_uts"]) == 36
    assert int(kpis["sub_centres"]) == 183_562
    assert int(kpis["phcs"]) == 26_309
    assert int(kpis["chcs"]) == 6_388
    assert int(kpis["district_hospitals"]) == 784
    assert int(kpis["facilities_24x7"]) == 23_187
    assert outputs["states"]["state"].is_unique


def test_population_source_gaps_remain_missing_in_per_capita_rates():
    states = load_outputs(OUTPUTS)["states"].set_index("state")
    assert states.loc["Telangana", "population_lakh_reported"] == 0
    assert states.loc["Telangana", "population_lakh"] != states.loc["Telangana", "population_lakh"]
    assert states.loc["Telangana", "facilities_24x7_per_100k"] != states.loc["Telangana", "facilities_24x7_per_100k"]
    assert states.loc["Ladakh", "population_lakh"] != states.loc["Ladakh", "population_lakh"]


def test_healthcare_filters_do_not_mutate_source():
    states = load_outputs(OUTPUTS)["states"]
    original = len(states)
    filtered = filter_states(
        states,
        focus_groups=["High Focus - Non-NE"],
        priority_bands=["Higher review priority"],
        minimum_completeness_pct=90,
    )
    assert len(states) == original
    assert not filtered.empty
    assert filtered["focus_group"].eq("High Focus - Non-NE").all()
    assert filtered["review_priority_band"].eq("Higher review priority").all()
    assert filtered["data_completeness_pct"].ge(90).all()
    with pytest.raises(ValueError):
        filter_states(states, minimum_completeness_pct=101)


def test_priority_export_uses_approved_transparent_fields():
    states = load_outputs(OUTPUTS)["states"]
    exported = priority_export(states)
    assert len(exported) == 36
    assert exported.iloc[0]["review_priority_score"] >= exported.iloc[1]["review_priority_score"]
    assert "population_lakh_reported" not in exported.columns
    assert {
        "state", "focus_group", "review_priority_score", "review_priority_band",
        "priority_component_count", "data_completeness_pct", "imr", "u5mr",
    }.issubset(exported.columns)
