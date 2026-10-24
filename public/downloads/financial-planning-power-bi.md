# Power BI Desktop companion — Project 06

The interactive product is delivered in Streamlit and the formula-driven Excel
workbook is committed as a reviewed analyst deliverable. This companion shows
how to model the same outputs in free Power BI Desktop.

## Import

Load these files from `06-financial-planning/outputs/`:

- `planning_mart.csv` — public-finance fact table at department, fund, program,
  and management-expense-category grain;
- `department_summary.csv` — reviewed department profile table;
- `variance_drivers.csv` — ranked public-finance pacing drivers;
- `corporate_plan.csv` — clearly labeled seeded synthetic planning model;
- `data_quality.csv` — source reconciliation and review items.

Keep the aggregate summary and quality tables disconnected. Use
`planning_mart` for public-finance visuals and `corporate_plan` for the
corporate page. Import `theme.json`, then create the measures in
`measures.dax`.

## Page 1 — Executive budget pacing

- slicers: department and fund from `planning_mart`;
- cards: Annual Budget, Expenditures To Date, Budget Utilization, Pace
  Variance, and Remaining Budget;
- clustered bar: budget and expenditures by department;
- scatter: annual budget on X, utilization on Y, budget as bubble size;
- matrix: department, budget, expenditures, utilization, pace variance, and
  pace status.

The layout target is `../assets/power_bi_companion.png`.

## Page 2 — Variance drivers

- department and fund slicers;
- decomposition tree beginning with Pace Variance and drilling through
  department, fund, program, and expense category;
- ranked table of program-level pace variance;
- explanatory note that a straight-line 75% benchmark is a monitoring proxy,
  not an accounting forecast.

## Page 3 — Synthetic corporate plan

- actual/forecast month and business-unit slicers;
- revenue, cost, EBITDA, margin, and forecast-variance cards;
- monthly budget-versus-base-forecast line chart;
- P&L matrix by statement group and line item;
- visible badge: `SEEDED SYNTHETIC CORPORATE DEMONSTRATION`.

## Validation checklist

Before committing a Desktop-created `.pbix`:

- reconcile unfiltered public totals to `executive_kpis.csv`;
- verify Annual Budget = $8.102B and Expenditures = $6.021B;
- verify Budget Utilization = 74.32%;
- confirm department/fund slicers affect only `planning_mart` visuals;
- confirm corporate visuals use only `corporate_plan`;
- confirm the synthetic label remains visible;
- refresh successfully and export one screenshot per page;
- save as `financial_planning.pbix` in this directory.

A `.pbix` is proprietary and is not claimed until it is opened, refreshed,
and validated in official Power BI Desktop.
