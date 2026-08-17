"""Interactive page for the U.S. retail-sales forecasting project."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_app.forecast import build_forecast, load_retail_sales, monthly_seasonality
from portfolio_app.ui import (
    GOLD,
    NAVY,
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

configure_page("Retail Sales Forecast", "📈")
inject_global_css()
render_sidebar()
render_page_header(
    "Project 02 · Time-series planning",
    "U.S. Retail Sales Forecast",
    "Estimate a plausible national retail-sales range, validate it against recent holdout data, and compare it with a simple year-ago baseline.",
    ["Holt–Winters", "24-month backtest", "Seasonal baseline", "36.4% MAE improvement"],
)
render_notice(
    "navy",
    "i",
    "Macro planning indicator",
    "The page uses FRED series RSAFSNA: national retail trade and food-services sales, not seasonally adjusted. It is not store, category, or SKU demand.",
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
m4.metric("Gain vs baseline", f"{result.improvement_pct:.1f}%", delta="Lower MAE")

render_section(
    "Planning workspace",
    f"Explore a {horizon}-month forecast and its validation",
    "Use the sidebar to change the horizon. The backtest remains fixed so comparisons stay honest.",
)
forecast_tab, validation_tab, seasonality_tab, brief_tab = st.tabs(
    ["Forecast", "Backtest", "Seasonality", "AI-assisted brief"]
)

with forecast_tab:
    history = series.iloc[-60:]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=history.index,
            y=history,
            name="Observed",
            line=dict(color=NAVY, width=2.5),
            hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}M<extra>Observed</extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=result.upper_80.index,
            y=result.upper_80,
            name="Approx. 80% upper",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=result.lower_80.index,
            y=result.lower_80,
            name="Approx. 80% interval",
            fill="tonexty",
            fillcolor="rgba(15,138,123,.16)",
            line=dict(width=0),
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=result.future_forecast.index,
            y=result.future_forecast,
            name="Holt–Winters forecast",
            line=dict(color=TEAL, width=3.5),
            hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}M<extra>Forecast</extra>",
        )
    )
    figure.update_layout(
        title=f"Observed history and {horizon}-month forecast",
        yaxis_title="Millions of U.S. dollars",
        hovermode="x unified",
    )
    style_plotly(figure, height=510)
    st.plotly_chart(figure, width="stretch")
    render_notice(
        "amber",
        "±",
        "Read the band carefully",
        "The shaded range is an empirical approximation from 24-month backtest residuals. It is not a formal prediction interval and may understate a structural shock.",
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
        title="Latest 24-month holdout: forecast versus actual",
        labels={"value": "Millions of U.S. dollars", "variable": "Series", "x": "Month"},
        color_discrete_map={"Actual": NAVY, "Holt–Winters": TEAL, "Year-ago baseline": GOLD},
    )
    figure.update_traces(line=dict(width=2.7))
    style_plotly(figure, height=470)
    st.plotly_chart(figure, width="stretch")
    v1, v2, v3 = st.columns(3)
    v1.metric("Model MAE", f"${result.mae:,.0f}M")
    v2.metric("Model RMSE", f"${result.rmse:,.0f}M")
    v3.metric("Seasonal-naive MAE", f"${result.naive_mae:,.0f}M")
    render_notice(
        "teal",
        "✓",
        "Why the baseline matters",
        "The benchmark predicts each month with the value observed 12 months earlier. The candidate should earn its complexity by reducing error against this credible shortcut.",
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
        color_continuous_scale=[[0, "#DDF7F1"], [0.65, TEAL], [1, NAVY]],
    )
    fig.update_coloraxes(showscale=False)
    fig.add_hline(y=1.0, line_dash="dash", line_color="#7D9190")
    style_plotly(fig, height=460, show_legend=False)
    st.plotly_chart(fig, width="stretch")
    render_notice(
        "navy",
        "12",
        "Calendar pattern retained",
        "Because RSAFSNA is not seasonally adjusted, December is typically elevated while January and February reset below the yearly average.",
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
    render_notice(
        "navy",
        "AI",
        "Controlled planning brief",
        "The text layer receives the displayed backtest metrics and analyst-approved context. It does not fit or alter the forecast.",
    )
    st.markdown(brief)
    st.caption(
        "Source: U.S. Census Bureau via FRED, series RSAFSNA. Snapshot date: "
        f"{series.index.max():%d %B %Y}."
    )
    st.link_button("Open source series on FRED", "https://fred.stlouisfed.org/series/RSAFSNA")

render_footer()
