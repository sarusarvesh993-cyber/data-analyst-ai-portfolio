from pathlib import Path

import numpy as np

from portfolio_app.forecast import build_forecast, load_retail_sales, monthly_seasonality

DATA = Path(__file__).parents[1] / "portfolio_app" / "data" / "retail_sales_monthly.csv"


def test_snapshot_and_forecast():
    series = load_retail_sales(DATA)
    assert len(series) > 300
    assert series.index.is_monotonic_increasing
    assert not series.isna().any()

    result = build_forecast(series, horizon=6, test_months=24)
    assert len(result.future_forecast) == 6
    assert np.isfinite(result.mae)
    assert result.mae > 0
    assert result.naive_mae > 0
    assert (result.upper_80 >= result.lower_80).all()


def test_seasonality_has_all_months():
    series = load_retail_sales(DATA)
    seasonal = monthly_seasonality(series)
    assert len(seasonal) == 12
    assert seasonal["index"].between(0.5, 1.5).all()
