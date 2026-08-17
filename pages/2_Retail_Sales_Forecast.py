"""Interactive page for the U.S. retail-sales forecasting project."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from portfolio_app.forecast import build_forecast, load_retail_sales, monthly_seasonality
from utils.ai_insights import generate_insights

st.set_page_config(page_title="Retail Forecast | Sarvesh Kommawar", page_icon="📈", layout="wide")
st.title("02 · U.S. Retail Sales Forecast")
st.write(
    "**Business question:** What range of U.S. retail and food-services sales is plausible "
    "over the next planning horizon, and does the model beat a simple year-ago baseline?"
)
st.info(
    "This page uses the not-seasonally-adjusted FRED series RSAFSNA. It is a national "
    "macroeconomic indicator—not store, category, or SKU demand."
)

DATA_PATH = Path(__file__).resolve().parents[1] / "portfolio_app" / "data" / "retail_sales_monthly.csv"


@st.cache_data
def get_series() -> pd.Series:
    return load_retail_sales(DATA_PATH)


@st.cache_resource(show_spinner="Fitting and backtesting forecast…")
def get_forecast(horizon: int):
    return build_forecast(get_series(), horizon=horizon, test_months=24)


series = get_series()
horizon = st.sidebar.slider("Forecast horizon (months)", 3, 24, 12, 3)
result = get_forecast(horizon)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Latest observation", series.index.max().strftime("%b %Y"))
m2.metric("Latest sales", f"${series.iloc[-1] / 1_000:,.1f}B")
m3.metric("Backtest MAE", f"${result.mae / 1_000:,.1f}B")
m4.metric("MAE improvement vs baseline", f"{result.improvement_pct:.1f}%")

forecast_tab, validation_tab, seasonality_tab, brief_tab = st.tabs(
    ["Forecast", "Backtest", "Seasonality", "AI-assisted brief"]
)

with forecast_tab:
    history = series.iloc[-60:]
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=history.index, y=history, name="Observed", line=dict(color="#1f4e79")))
    figure.add_trace(
        go.Scatter(
            x=result.upper_80.index,
            y=result.upper_80,
            name="Approx. 80% upper",
            line=dict(width=0),
            showlegend=False,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=result.lower_80.index,
            y=result.lower_80,
            name="Approx. 80% interval",
            fill="tonexty",
            fillcolor="rgba(41, 128, 185, .18)",
            line=dict(width=0),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=result.future_forecast.index,
            y=result.future_forecast,
            name="Holt–Winters forecast",
            line=dict(color="#c0392b", width=3),
        )
    )
    figure.update_layout(
        title=f"Observed history and {horizon}-month forecast",
        yaxis_title="Millions of U.S. dollars",
        hovermode="x unified",
        height=500,
    )
    st.plotly_chart(figure, width="stretch")
    st.caption(
        "The interval is an empirical approximation based on 24-month backtest residuals. "
        "It is not a formal prediction interval and may understate structural shocks."
    )
    download = result.future_forecast.rename("forecast_millions_usd").to_csv().encode("utf-8")
    st.download_button(
        "Download forecast CSV",
        data=download,
        file_name="us_retail_sales_forecast.csv",
        mime="text/csv",
    )

with validation_tab:
    comparison = pd.DataFrame(
        {
            "Actual": result.actual_test,
            "Holt–Winters": result.backtest_forecast,
            "Year-ago baseline": result.naive_forecast,
        }
    )
    figure = px.line(
        comparison,
        x=comparison.index,
        y=comparison.columns,
        title="24-month holdout: forecast versus actual",
        labels={"value": "Millions of U.S. dollars", "variable": "Series", "x": "Month"},
    )
    st.plotly_chart(figure, width="stretch")
    v1, v2, v3 = st.columns(3)
    v1.metric("Model MAE", f"${result.mae:,.0f}M")
    v2.metric("Model RMSE", f"${result.rmse:,.0f}M")
    v3.metric("Seasonal-naive MAE", f"${result.naive_mae:,.0f}M")
    st.write(
        "The holdout is the latest 24 months. The benchmark predicts each month with the "
        "observed value from 12 months earlier. This prevents claiming value from a complex "
        "model without checking whether a simple baseline is already competitive."
    )

with seasonality_tab:
    seasonal = monthly_seasonality(series)
    fig = px.bar(
        seasonal,
        x="month",
        y="index",
        text_auto=".2f",
        title="Average monthly sales index over the latest 10 years",
        labels={"month": "Month", "index": "Index (year average = 1.00)"},
        color="index",
        color_continuous_scale="Blues",
    )
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, width="stretch")
    st.write(
        "Because RSAFSNA is not seasonally adjusted, recurring calendar patterns remain in "
        "the data. December is typically elevated, while January and February tend to reset."
    )

with brief_tab:
    peak_month = result.future_forecast.idxmax().strftime("%B %Y")
    brief = generate_insights(
        {
            "headline": (
                f"The model's 24-month backtest MAE is ${result.mae / 1_000:,.1f}B, "
                f"{result.improvement_pct:.1f}% better than the year-ago baseline. "
                f"The highest point in the selected forecast is {peak_month}."
            ),
            "drivers": [
                "Long-run nominal sales growth",
                "Recurring monthly seasonality in the not-seasonally-adjusted series",
                "Recent level and trend entering the forecast origin",
            ],
            "recommendation": (
                "Use the national series as a macro planning input, refresh it monthly, and "
                "combine it with company-level category data before making inventory decisions."
            ),
        }
    )
    st.markdown(brief)
    st.caption(
        "Source: U.S. Census Bureau via FRED, series RSAFSNA. Snapshot date: "
        f"{series.index.max():%d %B %Y}."
    )
    st.link_button("Open the source series on FRED", "https://fred.stlouisfed.org/series/RSAFSNA")
