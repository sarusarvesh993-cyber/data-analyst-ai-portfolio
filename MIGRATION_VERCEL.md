# Streamlit → Vercel migration

- **Status:** implemented and validated locally; production Vercel deployment is an owner step.
- **Source base:** `b1421e128204b710202dd559683f417280990464`
- **Production architecture:** static Next.js export served by Vercel; no Streamlit, Python Function, database, or runtime secret.

## Why the original deployment failed

The repository contains a multi-page Streamlit application. Vercel's Python runtime loads ASGI/WSGI entrypoints such as FastAPI, Flask, or Django; it does not convert a Streamlit server into a supported Function. Renaming `streamlit_app.py` would not solve that architectural mismatch.

This migration keeps the original Python analysis reproducible but removes Streamlit from the production runtime.

## Migrated routes

| Project | Vercel route | Preserved interaction |
|---|---|---|
| Overview | `/` | Seven project links and architecture summary |
| 01 · Customer churn | `/customer-churn/` | Customer scoring, threshold diagnostics, contract/tenure patterns |
| 02 · Retail forecast | `/retail-sales-forecast/` | 3–24 month horizons, backtest, seasonality, forecast CSV |
| 03 · A/B testing | `/ab-test-calculator/` | Counts, practical lift, alpha, decision rule, sample planner, result CSV |
| 04 · E-commerce SQL | `/ecommerce-sql/` | Cohort maturity/matrix, category count, delivery views, SQL reviewer |
| 05 · Segmentation | `/customer-segmentation/` | Segment/country/value filters, audience export, campaign selector, model validation |
| 06 · Financial planning | `/financial-planning/` | Department/fund filters, variance direction, corporate scenario, Excel/BI downloads |
| 07 · Healthcare access | `/healthcare-access/` | Focus/band/completeness filters, access scatter, priority screen, quality/dictionary |

All routes are statically prerendered and work on direct load and refresh.

## Architecture

1. **Original analysis remains in the repository.** Notebooks, Python modules, SQL, outputs, tests, and the legacy Streamlit app remain available for review and reproduction.
2. **`scripts/export_web_data.py` exports intentional snapshots.** It trains the seeded churn model, scores a reference customer, calculates holdout thresholds, fits/backtests the forecast, calculates A/B reference values, and serializes reviewed project outputs.
3. **Committed JSON and public downloads live under `public/`.** No source workbook, private credential, or runtime database is required by the frontend.
4. **Next.js client components provide interaction.** Statistical tests, model scoring, filters, scenarios, and CSV generation run in the browser.
5. **`vercel.json` selects Framework = Other (`null`).** Vercel runs `npm run build` and serves `out/` as plain static files. This avoids the Next.js server-builder `out/routes-manifest.json` mismatch as well as the original Python-entrypoint error.

## Verified analytical references

- Churn holdout ROC–AUC: **0.8861168436**; default browser scenario reproduces Python probability **0.9137642401**.
- Forecast 24-month backtest improvement over seasonal naive: **36.3545%**; latest committed observation is **July 2026**.
- A/B default example: pooled two-sided z-test and un-pooled interval; default planner reference **14,745 per arm** at 80% power and **24,411** at 95%.
- Original Python tests: **29/29 passed**.
- Migrated production browser tests: **10/10 passed**.

The browser A/B implementation uses a continued-fraction normal-survival tail so very small p-values are not rounded prematurely to zero.

## Intentional differences from Streamlit

- **No live Hugging Face call.** The Vercel edition uses deterministic decision labels and authored briefs. No `HF_TOKEN` is shipped to the browser or required in Vercel.
- **No long-running app server.** Interaction is client-side against reviewed snapshots. This is not a live retraining or database-query service.
- **Power BI remains a companion.** DAX, themes, build guides, and the formula-driven Excel model are downloadable; no PBIX or hosted Power BI report is claimed.
- **Historical source boundaries remain visible.** Forecast, e-commerce, segmentation, public finance, and healthcare pages retain their source dates and interpretation limitations.
- **Legacy Streamlit files are retained for reference.** They are excluded from Vercel uploads and are not part of the production runtime.

## Local verification

```bash
# Original analysis and Streamlit compatibility checks
pip install -r requirements-dev.txt
pytest -q

# Regenerate reviewed web snapshots intentionally
python scripts/export_web_data.py

# Vercel frontend
npm ci
npm run typecheck
npm run build
npx playwright install chromium
npm test
npm run preview
```

The browser suite covers all routes, JavaScript errors, A/B references, churn scoring/thresholds, forecast horizon/download, cohort controls, segmentation denominators, financial scenarios, healthcare filters, and 390px overflow.

## Deploy the connected GitHub repository

1. Apply and review the supplied migration patch or copy the migrated files into the repository.
2. Commit and push to the branch connected to Vercel (`main` for the current project).
3. Keep `vercel.json` unchanged: framework `null`, build `npm run build`, output `out`.
4. Do not add environment variables for the base deployment.
5. After deployment, run:

```bash
PLAYWRIGHT_BASE_URL="https://YOUR-REAL-DEPLOYMENT.vercel.app" npm test
```

6. Only after the live URL passes, replace the pending Vercel URL in `README.md` and update portfolio links. Keep the old Streamlit URL labeled as legacy until cutover is verified.

If Vercel still shows an old framework/output override in Project Settings, the checked-in `vercel.json` explicitly overrides it for each deployment. Do not re-enable a Python framework preset.
