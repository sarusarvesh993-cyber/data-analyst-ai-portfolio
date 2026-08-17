# Portfolio Roadmap

- Target role: **Data Analyst**
- Strategy: **six distinct, deep projects** rather than repeated templates
- Delivery: **one consistent multi-page Streamlit portfolio plus reviewed Excel and Power BI companion artifacts**

## Quality standard for every project

A project is complete only when it has:

1. a specific business question and named stakeholder;
2. a credible data source or a prominent synthetic-data limitation;
3. reproducible cleaning and analysis;
4. a simple baseline before a more complex method;
5. validation appropriate to the problem;
6. quantified findings and assumptions;
7. a decision or recommendation tied to evidence;
8. a concise README, executed notebook or SQL scripts, and dashboard view;
9. automated checks for the reusable calculation code;
10. three interview answers: design choice, limitation, and next improvement.

## Build order

### Sprint 1 — Stabilize and deploy Projects 01–03

- [x] Audit repository claims and execute all three notebooks.
- [x] Add a single multi-page Streamlit app.
- [x] Add reusable calculation modules and tests.
- [x] Correct the A/B generator so variants use independent random draws.
- [x] Change forecasting to the not-seasonally-adjusted FRED series `RSAFSNA` so the seasonal interpretation is valid.
- [x] Update and re-execute all three notebooks against the corrected methods.
- [x] Pass local tests and a Streamlit smoke test.
- [x] Push the reviewed work to GitHub.
- [x] Deploy `streamlit_app.py` on Streamlit Community Cloud.
- [x] Add the public app URL to the root and project READMEs.

### Project 04 — E-commerce Revenue & Cohort Analysis

**Primary gap filled:** SQL.

Completed deliverables:

- [x] Real relational Olist e-commerce dataset with source and license recorded.
- [x] DuckDB schema plus reproducible download, load, and export scripts.
- [x] SQL for GMV KPIs, repeat purchase, cohorts, retention, delivery, and categories.
- [x] Explicit order-level grains and automated protection against join multiplication.
- [x] Eight data-quality checks with reviewed handling of incomplete delivery timestamps.
- [x] Full interactive Streamlit page with five analytical views.
- [x] Date-window, cohort-maturity, and category controls that respect each output grain.
- [x] Visible SQL, quality-check table, and an AI-assisted stakeholder brief with deterministic fallback.
- [x] Public Project 04 URL documented.

### Project 05 — Customer Segmentation & Marketing Dashboard

**Primary gaps filled:** segmentation, campaign design, Power BI.

Completed deliverables:

- [x] Real transaction-level UCI Online Retail data with source and CC BY 4.0 license recorded.
- [x] Reproducible purchase, return, customer-feature, and quality-check pipeline.
- [x] Transparent RFM baseline with seven campaign activation segments.
- [x] K-means challenger evaluated on separation, compactness, size, and seed stability.
- [x] Deterministic business naming rules and rules-to-cluster comparison.
- [x] Campaign matrix with audience, treatment, channel, KPI, guardrail, and holdout design.
- [x] Full five-tab Streamlit command center with safe anonymized audience exports.
- [x] Power BI-ready outputs, theme, reviewed DAX, Desktop guide, and reproducible layout preview.
- [x] Explicit boundary that a `.pbix` will only be claimed after official Desktop validation.

### Project 06 — Financial Planning & Variance Command Center

**Primary gaps filled:** FP&A, advanced Excel delivery, budget ownership, and scenario planning.

Completed deliverables:

- [x] Current real City of Austin FY2026 budget-versus-expenditure source with terms and accounting caveats recorded.
- [x] Reproducible 57K-row download, validation, management-category mapping, and aggregate output pipeline.
- [x] Department, fund, program, expense, pacing, and run-rate proxy analysis.
- [x] Explicit boundary between a Q3 straight-line monitoring benchmark and an accounting forecast.
- [x] Separate seeded corporate model for revenue, COGS, OPEX, EBITDA, and scenarios, visibly labeled synthetic.
- [x] Nine-sheet formula-driven Excel workbook with editable assumptions, tables, formulas, and charts.
- [x] Five-tab Streamlit command center with public-finance drilldowns and interactive corporate scenarios.
- [x] Power BI-ready outputs, theme, DAX, Desktop guide, validation checklist, and layout preview.
- [x] Automated schema, reconciliation, filtering, scenario-direction, workbook, and Streamlit smoke tests.

## Final portfolio release

- [x] One consistent visual style and navigation.
- [x] No unsupported skill claims.
- [x] Live links and screenshots in every project README.
- [x] Data sources, licenses, assumptions, and limitations clearly stated.
- [x] All local tests green; GitHub Actions validates every push.
- [ ] Personal project retrospectives written in Sarvesh's own words.
- [ ] Prepare a 90-second and a 5-minute explanation for each project.

## AI-use rule

AI is an explicit feature, not hidden authorship. Quantitative results remain deterministic and reviewable. Generated briefs receive only approved metrics and context, are labeled, and have a no-token fallback. The portfolio owner must be able to explain, modify, and defend every analytical choice.
