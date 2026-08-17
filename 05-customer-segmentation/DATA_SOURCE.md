# Data source and license

## UCI Online Retail

- **Source:** UCI Machine Learning Repository
- **Dataset ID:** 352
- **DOI:** [10.24432/C5BW33](https://doi.org/10.24432/C5BW33)
- **Public page:** https://archive.ics.uci.edu/dataset/352/online+retail
- **Public archive:** https://archive.ics.uci.edu/static/public/352/online+retail.zip
- **Citation:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

The workbook contains 541,909 invoice-line records for a UK-based non-store
retailer between 1 December 2010 and 9 December 2011. Fields include invoice,
product, description, quantity, invoice timestamp, unit price, customer ID,
and country. Invoice numbers beginning with `C` denote cancellations.

## How this project uses the source

The raw workbook is downloaded by `download_data.py` and excluded from Git.
`build_segments.py` creates reviewed customer-grain and aggregate CSV outputs
that are committed for reliable Streamlit deployment.

Completed-purchase RFM features require:

- an identified customer;
- a positive quantity;
- a positive unit price;
- a non-cancellation invoice.

Cancellation and negative-quantity lines are retained separately as return
signals rather than silently treated as purchases.

## Limitations

- The retailer is historical and has a substantial wholesale customer base;
  segment behavior should not be generalized to every consumer retailer.
- 135,080 source rows have no customer ID and cannot support customer-level
  RFM analysis. Identified completed purchases represent 83.54% of positive
  sales value in the source.
- The data have no product cost, margin, acquisition channel, campaign
  exposure, or customer demographics.
- Completed-purchase value is not profit. The net-revenue field is a proxy
  subtracting identified return value, not an accounting measure.
- Customer IDs are source-provided anonymized identifiers, not contactable
  personal information.
- Segments and clusters are descriptive. Campaign impact must be established
  through controlled experiments.
