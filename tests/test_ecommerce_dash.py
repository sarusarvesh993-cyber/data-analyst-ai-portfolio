"""Smoke and behavior tests for the standalone e-commerce Dash app."""
from pathlib import Path

import pandas as pd

from portfolio_app.ecommerce import load_outputs
from portfolio_app.ecommerce_dash import (
    build_category_figure,
    build_monthly_figure,
    create_dash_app,
    filter_monthly,
)

ROOT = Path(__file__).parents[1]
OUTPUTS = ROOT / "04-ecommerce-sql" / "outputs"


def test_month_filter_is_inclusive_and_bounds_safe():
    monthly = load_outputs(OUTPUTS)["monthly"]
    selected = filter_monthly(monthly, 2, 5)
    assert len(selected) == 4
    assert selected.iloc[0]["purchase_month"] == monthly.iloc[2]["purchase_month"]
    assert selected.iloc[-1]["purchase_month"] == monthly.iloc[5]["purchase_month"]
    clipped = filter_monthly(monthly, -100, 10_000)
    pd.testing.assert_frame_equal(clipped.reset_index(drop=True), monthly.reset_index(drop=True))


def test_dash_figures_use_reviewed_output_without_changing_totals():
    outputs = load_outputs(OUTPUTS)
    monthly_figure = build_monthly_figure(outputs["monthly"])
    category_figure = build_category_figure(outputs["categories"], "health_beauty")
    assert len(monthly_figure.data) == 2
    assert sum(monthly_figure.data[0].y) == outputs["monthly"]["item_gmv_brl"].sum()
    assert len(category_figure.data[0].y) == 12
    assert "health_beauty" in set(category_figure.data[0].y)


def test_dash_server_exposes_layout_and_callbacks():
    app = create_dash_app(OUTPUTS)
    client = app.server.test_client()
    assert client.get("/").status_code == 200
    layout_response = client.get("/_dash-layout")
    dependencies_response = client.get("/_dash-dependencies")
    assert layout_response.status_code == 200
    assert dependencies_response.status_code == 200
    assert b"Commerce Intelligence" in layout_response.data
    assert len(dependencies_response.get_json()) >= 5


def test_dash_app_has_production_server_and_expected_callback_outputs():
    app = create_dash_app(OUTPUTS)
    callback_outputs = " ".join(app.callback_map)
    assert app.server is not None
    assert "monthly-gmv-chart.figure" in callback_outputs
    assert "state-delivery-chart.figure" in callback_outputs
    assert "category-gmv-chart.figure" in callback_outputs
    assert "brief-download.data" in callback_outputs
