# 01 · Customer Churn & Retention

## Business question

Which customer profiles should a retention team prioritize, and how does the score threshold change campaign workload, precision, and recall?

## Data

The project uses 5,000 **synthetic** customer records generated with a fixed seed. The fields represent tenure, charges, contract, service selections, payment, demographics, and churn.

This choice makes the workflow free and reproducible, but it also limits the conclusion: the observed drivers are properties of the simulated scenario, not evidence about a real telecom company.

## Method

1. Validate schema, missingness, and target balance.
2. Explore churn rates by contract, tenure, payment, and service choices.
3. Use a stratified 80/20 split.
4. Compare class-weighted logistic regression with a random forest using holdout ROC–AUC; retain logistic regression because it is both simpler and better on this split.
5. Assess precision, recall, F1, and the confusion matrix while varying the operating threshold to connect model output to retention-team capacity.
6. Review feature importance as model behavior, not causal evidence.
7. Convert approved metrics into an optional AI-assisted stakeholder brief.

## Current result

The logistic baseline reaches a holdout ROC–AUC of 0.886; the random forest reaches 0.871. The exact precision, recall, and number of customers flagged depend on the selected threshold; the Streamlit page makes that trade-off visible.

## Recommended use

Use a score to prioritize a **pilot** rather than contact every customer. Set the threshold from contact cost, available capacity, customer value, and the cost of missed churn. Measure incremental retention with a randomized holdout before claiming business impact.

## Limitations

- Synthetic data and a target generated from known rules.
- No causal estimate of what intervention prevents churn.
- No customer lifetime value or campaign-cost optimization yet.
- Probability scores are not calibrated to a real production population.

## Run

From the repository root:

```powershell
python .\01-customer-churn\generate_data.py
Push-Location .\01-customer-churn
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
Pop-Location
streamlit run streamlit_app.py
```

## Files

- `analysis.ipynb` — reproducible analysis narrative
- `generate_data.py` — fixed-seed data generator
- `insights.md` — metric-controlled stakeholder brief
- `assets/` — charts rendered in the notebook
- `../pages/1_Customer_Churn.py` — interactive app page
- `../portfolio_app/churn.py` — tested reusable model functions
