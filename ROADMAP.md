# Portfolio Roadmap

- Target role: **Data Analyst**
- Strategy: **five distinct, deep projects** rather than eight repeated templates
- Delivery: **one multi-page Streamlit app**

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
- [ ] Push one reviewed commit to GitHub.
- [ ] Deploy `streamlit_app.py` on Streamlit Community Cloud.
- [ ] Add the public app URL to the root and project READMEs.

### Project 04 — E-commerce Revenue & Cohort Analysis

**Primary gap filled:** SQL.

Planned deliverables:

- relational e-commerce dataset with source and license recorded;
- DuckDB schema and reproducible load script;
- SQL for revenue KPIs, repeat purchase, cohorts, retention, and delivery performance;
- data-quality checks that prevent double counting across joins;
- Streamlit page that displays query-backed results;
- business memo with three prioritized actions.

### Project 05 — Customer Segmentation & Marketing Dashboard

**Primary gaps filled:** segmentation, campaign design, Power BI.

Planned deliverables:

- transaction-level customer data with source and license;
- RFM segmentation baseline plus clustering comparison;
- segment stability and business naming rules;
- campaign matrix with audience, offer, channel, and KPI;
- Power BI dashboard screenshots and `.pbix`/project artifact created in Power BI Desktop;
- final Streamlit summary page linking the analytical and BI work.

## Final portfolio release

- [ ] One consistent visual style and navigation.
- [ ] No unsupported skill claims.
- [ ] Live links and screenshots in every README.
- [ ] Data sources, licenses, assumptions, and limitations clearly stated.
- [ ] All tests green on GitHub Actions.
- [ ] Personal project retrospectives written in Sarvesh's own words.
- [ ] Prepare a 90-second and a 5-minute explanation for each project.

## AI-use rule

AI is an explicit feature, not hidden authorship. Quantitative results remain deterministic and reviewable. Generated briefs receive only approved metrics and context, are labeled, and have a no-token fallback. The portfolio owner must be able to explain, modify, and defend every analytical choice.
