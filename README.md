# Data Analyst Portfolio — Sarvesh Kommawar

End-to-end analytics work covering classification, time-series forecasting, experimentation, and decision-focused dashboards. Each project starts with a business question, validates its method, states its limitations, and ends with an action a stakeholder can evaluate.

> **Live app:** deployment is the next release step. Until the public URL is added, run the multi-page Streamlit app locally with `streamlit run streamlit_app.py`.

## Projects

| # | Project | Main skills | Status |
|---|---|---|---|
| 01 | [Customer Churn & Retention](01-customer-churn/) | EDA, classification, ROC–AUC, threshold trade-offs | Analysis + app ready |
| 02 | [U.S. Retail Sales Forecast](02-sales-forecasting/) | time-series backtesting, Holt–Winters, baseline comparison | Analysis + app ready |
| 03 | [A/B Test Decision Calculator](03-ab-test/) | hypothesis testing, confidence intervals, power, practical significance | Analysis + app ready |
| 04 | E-commerce Revenue & Cohort Analysis | SQL, DuckDB, data modeling, retention | Next build |
| 05 | Customer Segmentation & Marketing Dashboard | RFM, clustering, Power BI, campaign targeting | Planned |

## Skills demonstrated now

`Python` · `pandas` · `scikit-learn` · `statsmodels` · `SciPy` · `Plotly` · `Streamlit` · `statistics` · `model validation` · `Git/GitHub`

SQL and Power BI will be added through Projects 04 and 05 rather than claimed before the supporting work exists.

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

Each project README lists assumptions, methodology, and appropriate use.

## Quality checks

```powershell
pytest -q
python -m compileall portfolio_app pages streamlit_app.py
```

GitHub Actions runs the automated tests on every push and pull request.

## Repository structure

```text
.
├── streamlit_app.py              # multi-page app entry point
├── pages/                        # one Streamlit page per project
├── portfolio_app/                # reusable calculations and models
├── tests/                        # automated checks
├── 01-customer-churn/            # notebook, data generator, findings
├── 02-sales-forecasting/         # notebook, source refresh, findings
├── 03-ab-test/                   # notebook, data generator, findings
└── utils/ai_insights.py          # optional text-generation layer
```

## Contact

- GitHub: [@sarusarvesh993-cyber](https://github.com/sarusarvesh993-cyber)
- LinkedIn: [Sarvesh Kommawar](https://www.linkedin.com/in/sarvesh-kommawar-3b166b278/)
- Email: kommawar57@gmail.com
