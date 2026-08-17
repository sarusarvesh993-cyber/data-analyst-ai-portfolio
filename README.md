# Data Analyst Portfolio — Sarvesh Kommawar

End-to-end analytics work covering classification, time-series forecasting, experimentation, SQL, customer segmentation, financial planning, and decision-focused dashboards. Each project starts with a business question, validates its method, states its limitations, and ends with an action a stakeholder can evaluate.

> **Live portfolio:** [Open the multi-page Streamlit app](https://data-analyst-ai-portfolio-pynrfe2h5275msvq22c7uh.streamlit.app/). Direct links: [Project 04 · E-commerce SQL](https://data-analyst-ai-portfolio-pynrfe2h5275msvq22c7uh.streamlit.app/Ecommerce_SQL) · [Project 05 · Customer Segmentation](https://data-analyst-ai-portfolio-pynrfe2h5275msvq22c7uh.streamlit.app/Customer_Segmentation) · [Project 06 · Financial Planning](https://data-analyst-ai-portfolio-pynrfe2h5275msvq22c7uh.streamlit.app/Financial_Planning).

## Projects

| # | Project | Main skills | Status |
|---|---|---|---|
| 01 | [Customer Churn & Retention](01-customer-churn/) | EDA, classification, ROC–AUC, threshold trade-offs | Analysis + app ready |
| 02 | [U.S. Retail Sales Forecast](02-sales-forecasting/) | time-series backtesting, Holt–Winters, baseline comparison | Analysis + app ready |
| 03 | [A/B Test Decision Calculator](03-ab-test/) | hypothesis testing, confidence intervals, power, practical significance | Analysis + app ready |
| 04 | [E-commerce Revenue & Cohort Analysis](04-ecommerce-sql/) | SQL, DuckDB, data modeling, cohorts, delivery KPIs | Analysis + Streamlit dashboard ready |
| 05 | [Customer Segmentation & Marketing Dashboard](05-customer-segmentation/) | RFM, K-means validation, campaign design, Power BI | Analysis + Streamlit + BI companion ready |
| 06 | [Financial Planning & Variance Command Center](06-financial-planning/) | FP&A, budget vs actual, Excel modeling, scenarios, Power BI | Analysis + Streamlit + Excel + BI companion ready |

## Skills demonstrated now

`Python` · `SQL` · `DuckDB` · `pandas` · `scikit-learn` · `statsmodels` · `SciPy` · `Plotly` · `Streamlit` · `Excel` · `openpyxl` · `Power BI Desktop` · `DAX` · `statistics` · `cohort analysis` · `RFM segmentation` · `clustering` · `FP&A` · `variance analysis` · `scenario planning` · `data modeling` · `model validation` · `Git/GitHub`

Projects 05 and 06 include reviewed Power BI-ready tables, DAX measures, themes, and Desktop build guides. Project 06 also includes a formula-driven `.xlsx` planning model. The repository does not claim an unvalidated `.pbix` binary.

## Run the portfolio app

### Windows PowerShell

```powershell
git clone https://github.com/sarusarvesh993-cyber/data-analyst-ai-portfolio.git
cd data-analyst-ai-portfolio
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app.py
```

If PowerShell blocks activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Reproduce the notebooks

```powershell
pip install -r requirements-dev.txt
python .\01-customer-churn\generate_data.py
python .\03-ab-test\generate_data.py

Push-Location .\01-customer-churn
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
Pop-Location

Push-Location .\02-sales-forecasting
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
Pop-Location

Push-Location .\03-ab-test
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
Pop-Location
```

The forecasting notebook reads a committed FRED snapshot used by the app. Run `python .\02-sales-forecasting\download_data.py` when intentionally refreshing the source data.

To reproduce Projects 04–06 from their public sources:

```powershell
python .\04-ecommerce-sql\download_data.py
python .\04-ecommerce-sql\build_warehouse.py
python .\04-ecommerce-sql\run_analysis.py
python .\04-ecommerce-sql\render_assets.py

python .\05-customer-segmentation\download_data.py
python .\05-customer-segmentation\build_segments.py
python .\05-customer-segmentation\render_assets.py

python .\06-financial-planning\download_data.py
python .\06-financial-planning\build_finance.py
python .\06-financial-planning\build_excel.py
python .\06-financial-planning\render_assets.py
```

Raw source files and the local DuckDB database are ignored by Git; only reviewed dashboard outputs and analyst deliverables are committed for reliable deployment.

## AI-assisted insight layer

The analysis and metrics are deterministic. `utils/ai_insights.py` can turn a controlled metrics dictionary into a draft stakeholder brief:

- with `HF_TOKEN`: it attempts a Hugging Face inference call;
- without a token: it returns an authored, deterministic fallback;
- in either case: the LLM does not generate the dataset, train the model, or calculate the statistics.

This feature is explicit so a reviewer can distinguish quantitative work from generated prose.

## Data and limitations

- **Churn:** seeded synthetic demonstration data. It proves the workflow, not a real company's churn drivers.
- **Forecasting:** U.S. Census Bureau data via FRED, series `RSAFSNA`, not seasonally adjusted. It is a macro indicator, not store/SKU demand.
- **A/B testing:** calculator accepts real aggregate counts; the included example data are seeded and synthetic.
- **E-commerce SQL:** real anonymized Olist marketplace data from 2016–2018 under CC BY-NC-SA 4.0. Item GMV is not accounting revenue, and delivery-review relationships are descriptive rather than causal.
- **Customer segmentation:** real anonymized UCI Online Retail transactions under CC BY 4.0. Completed-purchase value is not profit, customer-level coverage excludes unidentified purchases, and segments do not establish campaign treatment effects.
- **Financial planning:** real City of Austin FY2026 budget-versus-expenditure data is used for public-finance pacing. The 75% Q3 benchmark is not an accounting forecast. A separate seeded corporate model demonstrates revenue, COGS, EBITDA, and scenarios and is always labeled synthetic.

Each project README lists assumptions, methodology, source attribution, and appropriate use.

## Quality checks

```powershell
pytest -q
python -m compileall portfolio_app pages streamlit_app.py
```

GitHub Actions runs the automated tests on every push and pull request.

## Repository structure

```text
.
├── streamlit_app.py              # multi-page portfolio entry point
├── pages/                         # one interactive Streamlit page per project
├── portfolio_app/                # reusable calculations and models
├── tests/                        # automated checks
├── 01-customer-churn/            # notebook, data generator, findings
├── 02-sales-forecasting/         # notebook, source refresh, findings
├── 03-ab-test/                   # notebook, data generator, findings
├── 04-ecommerce-sql/             # DuckDB warehouse, SQL, outputs, source notes
├── 05-customer-segmentation/     # RFM, clustering, campaign and Power BI artifacts
├── 06-financial-planning/        # budget pacing, Excel model, scenarios and BI assets
└── utils/ai_insights.py          # optional text-generation layer
```

## Contact

- GitHub: [@sarusarvesh993-cyber](https://github.com/sarusarvesh993-cyber)
- LinkedIn: [Sarvesh Kommawar](https://www.linkedin.com/in/sarvesh-kommawar-3b166b278/)
- Email: kommawar57@gmail.com
