"""Forecasting utilities for the U.S. retail-sales project."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


@dataclass
class ForecastResult:
    """Backtest and future forecast outputs for the dashboard."""

    actual_test: pd.Series
    backtest_forecast: pd.Series
    naive_forecast: pd.Series
    future_forecast: pd.Series
    lower_80: pd.Series
    upper_80: pd.Series
    mae: float
    rmse: float
    naive_mae: float
    improvement_pct: float


def load_retail_sales(path: str | Path) -> pd.Series:
    """Load the committed FRED snapshot as a monthly time series."""
    frame = pd.read_csv(path)
    if not {"observation_date", "RetailSales"}.issubset(frame.columns):
        raise ValueError("Expected observation_date and RetailSales columns")
    frame["observation_date"] = pd.to_datetime(frame["observation_date"])
    series = (
        frame.dropna(subset=["RetailSales"])
        .sort_values("observation_date")
        .set_index("observation_date")["RetailSales"]
        .astype(float)
        .asfreq("MS")
    )
    if series.isna().any():
        raise ValueError("The monthly FRED series contains gaps")
    return series


def _fit(series: pd.Series) -> ExponentialSmoothing:
    """Fit a model suited to a positive series with growing seasonal amplitude."""
    return ExponentialSmoothing(
        series,
        trend="add",
        damped_trend=True,
        seasonal="mul",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)


def build_forecast(
    series: pd.Series, horizon: int = 12, test_months: int = 24
) -> ForecastResult:
    """Backtest against seasonal naive, then forecast from all observations."""
    if horizon < 1 or horizon > 36:
        raise ValueError("horizon must be between 1 and 36 months")
    if len(series) <= test_months + 24:
        raise ValueError("Not enough history for the requested backtest")

    train = series.iloc[:-test_months]
    test = series.iloc[-test_months:]
    backtest = _fit(train).forecast(test_months)
    backtest.index = test.index
    naive = series.shift(12).loc[test.index]

    residuals = test - backtest
    mae = float(np.mean(np.abs(residuals)))
    rmse = float(np.sqrt(np.mean(np.square(residuals))))
    naive_mae = float(np.mean(np.abs(test - naive)))
    improvement = 100.0 * (1.0 - mae / naive_mae) if naive_mae else 0.0

    future = _fit(series).forecast(horizon)
    steps = np.arange(1, horizon + 1, dtype=float)
    # Empirical approximation, clearly labeled as such in the dashboard.
    margin = 1.282 * float(residuals.std(ddof=1)) * np.sqrt(steps)
    lower = pd.Series(np.maximum(0.0, future.to_numpy() - margin), index=future.index)
    upper = pd.Series(future.to_numpy() + margin, index=future.index)

    return ForecastResult(
        actual_test=test,
        backtest_forecast=backtest,
        naive_forecast=naive,
        future_forecast=future,
        lower_80=lower,
        upper_80=upper,
        mae=mae,
        rmse=rmse,
        naive_mae=naive_mae,
        improvement_pct=improvement,
    )


def monthly_seasonality(series: pd.Series, years: int = 10) -> pd.DataFrame:
    """Return recent monthly values normalized by each year's average."""
    recent = series.loc[series.index >= series.index.max() - pd.DateOffset(years=years)]
    frame = recent.rename("sales").to_frame()
    frame["year"] = frame.index.year
    frame["month"] = frame.index.month_name().str[:3]
    frame["index"] = frame["sales"] / frame.groupby("year")["sales"].transform("mean")
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    result = frame.groupby("month", as_index=False)["index"].mean()
    result["month"] = pd.Categorical(result["month"], categories=order, ordered=True)
    return result.sort_values("month")
