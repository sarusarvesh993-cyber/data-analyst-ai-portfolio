# Power BI Desktop companion — Project 07

Import `state_health_access.csv`, `region_summary.csv`, and `data_quality.csv`.
Use `state_health_access` as the primary table. Keep the two reviewed aggregate
tables disconnected. Import `theme.json` and create the measures in
`measures.dax`.

## Page 1 — National access overview

- slicers: focus group and review-priority band;
- cards: states/UTs, PHCs, CHCs, district hospitals, reported 24x7 facilities,
  and median urban mapping rate;
- clustered bar: facility counts by focus group;
- scatter: 24x7 facility density vs infant mortality, with population as size;
- matrix: state, facility density, PHC staffing readiness, mapping, IMR, data
  completeness, and review-priority score.

## Page 2 — State readiness

- state slicer;
- cards for reported facility counts and readiness rates;
- bar chart comparing urban mapping, PHC three-nurse readiness, and UPHC
  minimum service package;
- detailed state table and source caveat text.

## Page 3 — Review priority

- ranked review-priority bar chart;
- decomposition tree through focus group, access density, staffing, mapping,
  and IMR;
- data-quality table with visible missingness.

## Validation

Reconcile to `executive_kpis.csv`: 36 states/UTs, 183,562 sub-centres, 26,309
PHCs, 6,388 CHCs, 784 district hospitals, and 23,187 reported 24x7 facilities.
Confirm Telangana and Ladakh population-dependent rates remain blank, not zero.
The priority score is a screening index, not a funding allocation or causal
model. Save a `.pbix` only after official Power BI Desktop refresh and review.
