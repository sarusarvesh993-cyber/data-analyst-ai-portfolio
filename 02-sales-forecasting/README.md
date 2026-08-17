# 02 · U.S. Retail Sales Forecast

## Business question

What range of U.S. retail and food-services sales is plausible over the next planning horizon, and does the forecasting method improve on a simple year-ago baseline?

## Data

U.S. Census Bureau **Advance Retail Sales: Retail Trade and Food Services**, retrieved through FRED series [`RSAFSNA`](https://fred.stlouisfed.org/series/RSAFSNA). Values are monthly, millions of U.S. dollars, and **not seasonally adjusted**.

A small snapshot is committed under `portfolio_app/data/` so the dashboard can start without a network call. `download_data.py` intentionally refreshes the snapshot.

## Method

1. Validate monthly frequency, missing periods, and positive values.
2. Reserve the latest 24 months as an honest time-based holdout.
3. Fit damped-trend Holt–Winters with multiplicative 12-month seasonality.
4. Compare holdout MAE and RMSE with a seasonal-naive forecast: the same month one year earlier.
5. Refit on all observations and forecast the user-selected horizon.
6. Show an approximate uncertainty band derived from holdout residuals.
7. Convert approved metrics into an optional AI-assisted planning brief.

## Interpretation

Using an unadjusted series makes recurring calendar seasonality visible, including a typical December peak and early-year reset. The backtest—not visual fit—is the basis for judging whether the method adds value over the baseline.

## Appropriate use

This is a macro planning indicator. A retailer could include it in budgeting or scenario planning, but should combine it with its own store, category, price, promotion, and inventory data before making operational decisions.

## Limitations

- National aggregate rather than company or SKU demand.
- Nominal dollars mix volume and price changes.
- Revisions and structural shocks can reduce forecast accuracy.
- The displayed band is empirical and approximate, not a formal model interval.

## Run and refresh

```powershell
# Optional source refresh
python .\02-sales-forecasting\download_data.py

Push-Location .\02-sales-forecasting
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
Pop-Location

streamlit run streamlit_app.py
```

## Files

- `analysis.ipynb` — time-series analysis and backtest
- `download_data.py` — FRED snapshot refresh
- `insights.md` — metric-controlled stakeholder brief
- `assets/` — charts rendered in the notebook
- `../pages/2_Retail_Sales_Forecast.py` — interactive app page
- `../portfolio_app/forecast.py` — tested reusable forecast functions
