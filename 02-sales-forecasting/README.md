# 02 · Sales & Demand Forecasting

**Business question:** What will retail sales do next year, and how should inventory/staffing plan around the peak?

**Domain:** Retail — and a **Streamlit deploy candidate** (live forecast app).

**Data:** REAL macro sales series — US Monthly Retail Trade Sales (FRED `RSXFS`, $ millions, 1992→present), downloaded by `download_data.py`. Public, no auth, saved locally so it never breaks.

**Approach**
1. Downloaded the real series; profiled long-run trend + monthly seasonality.
2. Forecast: Holt-Winters (additive trend + 12-month seasonality) via `statsmodels`.
3. Honest evaluation: MAE/RMSE vs a **year-ago seasonal-naive baseline** (does the model actually beat "same month last year"?).
4. **AI layer:** LLM writes a planning brief (`insights.md`).

**Key insights** _(see `insights.md`)_
- Strong long-run upward trend + recurring Nov-Dec holiday peak.
- The model beats the year-ago naive baseline clearly (see metrics) — so it's trustworthy for planning.

**Recommendation**
- Pre-position inventory/staffing for the forecasted holiday peak.
- Use the 12-month forecast for budgeting, not just last year + guess.

**Files:** `analysis.ipynb` · `download_data.py` · `insights.md` · `assets/*.png` · `data/retail_sales_monthly.csv`

**How to run**
```bash
python download_data.py
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
```
