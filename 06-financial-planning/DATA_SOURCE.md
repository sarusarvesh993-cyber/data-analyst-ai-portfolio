# Data source, terms, and analytical boundary

## Real public-finance source

**City of Austin — Program Budget Operating Budget Vs Expense Raw Data**

- Dataset ID: `g5k8-8sud`
- Public page: https://data.austintexas.gov/d/g5k8-8sud
- Socrata API: https://data.austintexas.gov/resource/g5k8-8sud.csv?$limit=100000
- Provider: City of Austin, Texas
- Category: Budget and Finance
- Snapshot used: fiscal year 2026 through quarter 3
- Snapshot rows: 57,267
- Access: public City open-data portal; use remains subject to the City of Austin
  Open Data Terms of Use and source disclaimers.

The source includes annual budget and expenditure-to-date values by department,
fund, program, activity, unit, and expense code. The raw CSV is downloaded by
`download_data.py`, excluded from Git, and transformed into reviewed aggregate
outputs by `build_finance.py`.

## Source-specific caveats

The City states that the data are informational. Certain Austin Energy budget
items are excluded as competitive matters under Texas law and City resolution.

The City also warns that personnel budgets and actual expenditures can appear
in different objects. Base wages may be fully budgeted in regular-wage objects,
while actual sick, vacation, holiday, and other leave costs are posted to their
specific timesheet objects. Personnel savings is budgeted separately but
realized through wage categories. Therefore, zero-budget expenditure lines are
retained for review and must not automatically be described as control failures.

## Pacing methodology

The snapshot is through Q3, so the project uses 75% of annual budget as a simple
elapsed-time benchmark:

```text
expected spend to date = annual budget × 75%
pace variance = expenditures to date − expected spend to date
linear run-rate proxy = expenditures to date ÷ 75%
```

Positive pace variance means spending is above the straight-line benchmark.
This is a monitoring proxy, not a year-end accounting forecast. Government
spending is seasonal, debt payments and transfers can be scheduled, and annual
appropriations need not be consumed evenly.

## Synthetic corporate layer

`corporate_plan.csv` is a seeded, hypothetical 2026 software-company planning
model created solely to demonstrate commercial FP&A concepts that are not
present in the City dataset:

- revenue, COGS, operating expense, and EBITDA;
- monthly budget, actual, and forecast periods;
- revenue, cost-inflation, and hiring-delay scenarios.

It is not City of Austin data and does not represent a real company. Every app,
Excel, README, and Power BI view labels this boundary explicitly.
