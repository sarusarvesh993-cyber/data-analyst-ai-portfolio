# Data source and interpretation boundary

Project 07 uses the official **National Health Mission Quarterly MIS Report
2025-26**, status as on 31 December 2025.

- Source page: https://nhm.gov.in/index4.php?lang=1&level=0&linkid=457&lid=686
- Publisher: National Health Mission, Ministry of Health & Family Welfare,
  Government of India
- Files parsed: `G1.pdf`, `G2.pdf`, `G3.pdf`, and `G4.pdf`
- Coverage: 36 states and union territories in four NHM focus groups

The reports combine multiple reference periods. Facility and programme status
is reported for 2025-26, while population is Census 2011, most mortality and
fertility indicators are SRS 2023, MMR is SRS 2021-23, and life expectancy is
2019-23. Rates using population are therefore access-screening proxies, not
current population estimates.

The official report shows zero population for Telangana and `NA` for Ladakh;
this project preserves the reported value but leaves population-dependent rates
blank. One mapping ratio exceeds 100% because a reported numerator is larger
than its denominator. It is retained and flagged rather than silently capped.

The review-priority score averages available percentiles for low reported 24x7
facility density, low PHC three-nurse readiness, low urban facility mapping,
and high infant mortality. It requires at least three components. It is not a
causal model, funding formula, ranking of clinical quality, or substitute for
travel-time, beds, workforce, utilization, and local validation.
