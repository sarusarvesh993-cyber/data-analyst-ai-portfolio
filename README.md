# Data Analyst AI Portfolio

> End-to-end analytics projects that pair a real ML model with an **AI insight layer** (an LLM that turns numbers into plain-English business briefs). Built 100% free — no paid APIs.

I'm a data analyst who builds the full loop: **business question → data → model → dashboard → recommendation**. Every project below combines a classical ML/statistics model with a free LLM layer that explains the result to non-technical stakeholders.

## Skills demonstrated
`Python` · `pandas` · `scikit-learn` · `statsmodels` · `SQL` · `Excel` · `Power BI` · `Statistics / A/B testing` · `LLM insight layer (free HuggingFace)` · `Streamlit` (deployed apps)

## Projects

| # | Project | Domain | Status |
|---|---------|--------|--------|
| 01 | [Customer Churn & Retention](01-customer-churn/) | Subscription/Retail | ✅ built |
| 02 | [Sales & Demand Forecasting](02-sales-forecasting/) | Retail | ✅ built |
| 03 | [A/B Test Significance Analyzer](03-ab-test/) | Marketing/E-com | ⬜ planned |
| 04 | [Loan Default Risk](04-loan-default/) | Finance | ⬜ planned |
| 05 | [Patient No-Show Predictor](05-noshow/) | Healthcare | ⬜ planned |
| 06 | [Employee Attrition & Retention](06-attrition/) | HR | ⬜ planned |
| 07 | [Customer Segmentation & Targeting](07-segmentation/) | Marketing | ⬜ planned |
| 08 | [Sports Performance & Fan Insights](08-sports/) | Sports | ⬜ planned |

## How the "AI" works (free)
Each project's model outputs metrics; `utils/ai_insights.py` turns them into a stakeholder brief.
- **With a free `HF_TOKEN`** (set in `.env`): calls a free HuggingFace model.
- **Without a token**: uses the bundled, authored narrative — fully functional, **zero cost, nothing breaks**.

## Run anything
```bash
pip install -r requirements.txt
cd 01-customer-churn
python generate_data.py      # creates the (seeded, reproducible) dataset
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb   # runs the full project
```
Open `analysis.ipynb` (or the rendered README + `insights.md`) to see the result.

## Deployed apps
Top projects are also shipped as live Streamlit apps (see each folder's deploy notes).

## Contact
- GitHub: [@sarusarvesh993-cyber](https://github.com/sarusarvesh993-cyber)
- Email / LinkedIn: _add yours_
