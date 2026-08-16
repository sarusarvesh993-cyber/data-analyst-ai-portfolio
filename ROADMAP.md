# Build Roadmap

Step-by-step. Each project reuses the same template so it stays consistent and interview-ready.

## Standard project template (every folder)
```
NN-project-name/
├── README.md          # business Q, data, method, insights, recommendation, how-to-run
├── generate_data.py   # creates a seeded, reproducible dataset in data/
├── analysis.ipynb     # the showcase: narrative + code + charts + AI insights
├── insights.md        # the LLM-generated stakeholder brief (auto-written by the notebook)
├── data/              # generated dataset
└── assets/            # charts (png) embedded in README
```

## AI insight layer (shared)
`utils/ai_insights.py` → `generate_insights(metrics)` returns a natural-language brief.
Free by default; optional live LLM via `HF_TOKEN`.

## Order of build
1. ✅ 01 Customer Churn & Retention  (template established here)
2. 02 Sales & Demand Forecasting    (→ Streamlit deploy)
3. 03 A/B Test Significance Analyzer (→ Streamlit deploy)
4. 04 Loan Default Risk
5. 05 Patient No-Show Predictor
6. 06 Employee Attrition & Retention
7. 07 Customer Segmentation & Targeting (→ Streamlit deploy)
8. 08 Sports Performance & Fan Insights

## After all 8
- Polish root README + per-project READMEs.
- Deploy top 3 as Streamlit Community Cloud apps (free, from this GitHub repo).
- Push to GitHub; add the live app links.
