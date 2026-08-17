"""Tests for customer-grain segmentation logic and committed outputs."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from portfolio_app.segmentation import (
    audience_export,
    campaign_record,
    filter_customers,
    load_outputs,
)

ROOT = Path(__file__).parents[1]
PROJECT = ROOT / "05-customer-segmentation"
OUTPUTS = PROJECT / "outputs"


def _load_builder_module():
    spec = importlib.util.spec_from_file_location(
        "segmentation_builder", PROJECT / "build_segments.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_committed_segmentation_outputs_are_complete_and_plausible():
    outputs = load_outputs(OUTPUTS)
    kpis = outputs["kpis"].iloc[0]
    assert set(outputs) == {
        "kpis",
        "customers",
        "segments",
        "clusters",
        "comparison",
        "validation",
        "monthly",
        "countries",
        "quality",
        "metadata",
    }
    assert 4_000 < kpis["customers"] < 5_000
    assert 8_000_000 < kpis["gross_revenue"] < 10_000_000
    assert 50 < kpis["repeat_customer_rate_pct"] < 80
    assert outputs["customers"]["customer_id"].is_unique
    assert outputs["customers"]["rfm_segment"].notna().all()
    assert outputs["customers"]["cluster_name"].notna().all()
    assert outputs["segments"]["revenue_share_pct"].sum() == pytest.approx(100.0)


def test_selected_cluster_model_is_stable_and_avoids_tiny_groups():
    validation = load_outputs(OUTPUTS)["validation"]
    selected = validation.loc[validation["selected_model"]]
    assert len(selected) == 1
    row = selected.iloc[0]
    assert 3 <= row["n_clusters"] <= 6
    assert row["seed_stability_ari"] >= 0.80
    assert row["minimum_cluster_share_pct"] >= 5.0
    assert 0 < row["silhouette_score"] < 1


def test_customer_filters_and_campaign_export_use_approved_fields():
    outputs = load_outputs(OUTPUTS)
    original_count = len(outputs["customers"])
    filtered = filter_customers(
        outputs["customers"],
        segments=["At Risk"],
        countries=["United Kingdom"],
        minimum_value=500,
    )
    assert len(outputs["customers"]) == original_count
    assert not filtered.empty
    assert filtered["rfm_segment"].eq("At Risk").all()
    assert filtered["country"].eq("United Kingdom").all()
    assert filtered["monetary_value"].ge(500).all()
    with pytest.raises(ValueError):
        filter_customers(outputs["customers"], minimum_value=-1)

    audience = audience_export(outputs["customers"], "At Risk")
    assert set(audience.columns) == {
        "customer_id",
        "country",
        "rfm_segment",
        "recency_days",
        "frequency",
        "monetary_value",
        "average_order_value",
        "return_rate_pct",
    }
    campaign = campaign_record(outputs["segments"], "At Risk")
    assert "holdout" in campaign["experiment"].lower()


def test_transaction_split_keeps_sales_and_returns_separate():
    builder = _load_builder_module()
    raw = pd.DataFrame(
        {
            "invoice_no": pd.Series(["100", "C101", "102", "103"], dtype="string"),
            "stock_code": ["a", "a", "b", "c"],
            "description": ["A", "A", "B", "C"],
            "quantity": [2, -1, 3, 1],
            "invoice_date": pd.to_datetime(["2011-01-01"] * 4),
            "unit_price": [10.0, 10.0, 5.0, 9.0],
            "customer_id": pd.Series([1, 1, 2, pd.NA], dtype="Int64"),
            "country": ["UK"] * 4,
            "is_cancellation": [False, True, False, False],
            "line_value": [20.0, -10.0, 15.0, 9.0],
        }
    )
    purchases, returns = builder.split_transactions(raw)
    assert purchases["invoice_no"].tolist() == ["100", "102"]
    assert purchases["line_revenue"].sum() == pytest.approx(35.0)
    assert returns["invoice_no"].tolist() == ["C101"]
    assert returns["return_value"].sum() == pytest.approx(10.0)
