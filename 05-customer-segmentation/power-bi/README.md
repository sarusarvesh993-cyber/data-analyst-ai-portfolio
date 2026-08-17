# Power BI Desktop companion build

The complete interactive project is delivered in Streamlit. This companion
report demonstrates that the same reviewed outputs can be modelled and
presented in Power BI Desktop without requiring a paid Power BI Service plan.

## Files to import

From `05-customer-segmentation/outputs/`:

- `customer_segments.csv` — one row per anonymized customer;
- `segment_summary.csv` — one row per rules-based RFM segment;
- `model_validation.csv` — one row per evaluated cluster count;
- `monthly_performance.csv` — one row per purchase month;
- `country_summary.csv` — one row per country.

## Build steps

1. Open Power BI Desktop.
2. Choose **Get data → Text/CSV** and load the five files above.
3. In Power Query, set:
   - customer IDs and segment names to Text;
   - date columns to Date/Time;
   - customer/order counts to Whole Number;
   - revenue, return, and average-order fields to Decimal Number;
   - percentage fields to Decimal Number.
4. Create a one-to-many relationship from
   `segment_summary[rfm_segment]` to
   `customer_segments[rfm_segment]`.
5. Keep monthly and model-validation tables disconnected because they are
   already aggregate outputs at different grains.
6. Import `theme.json` through **View → Themes → Browse for themes**.
7. Create the measures in `measures.dax`.

## Page 1 — Executive segmentation

Use a 16:9 canvas with:

- slicers for RFM segment and country;
- cards for Customers, Completed Purchase Value, Orders, Repeat Customer Rate,
  and At-Risk Historical Value;
- horizontal bar chart of Completed Purchase Value by RFM segment;
- scatter chart with Median Recency on X, revenue share on Y, and customer
  count as bubble size;
- matrix with segment, customers, revenue share, repeat rate, objective, and
  primary KPI.

The reproducible visual target is `../assets/power_bi_companion.png`.

## Page 2 — Campaign strategy

- Segment slicer;
- cards for audience size, value, recency, and return rate;
- campaign matrix fields: objective, treatment, channel, KPI, guardrail, and
  experiment design;
- table of anonymized eligible customer IDs for export.

## Page 3 — Model validation

- line chart of silhouette score by number of clusters;
- line chart of seed stability by number of clusters;
- table showing Davies–Bouldin score, minimum cluster share, and selected model;
- explanatory text noting that the rules-based RFM segments remain the primary
  activation layer and K-means is a challenger model.

## Evidence checklist

Before committing a `.pbix` created in Power BI Desktop:

- refresh all data sources successfully;
- verify totals against `executive_kpis.csv`;
- confirm segment and country slicers affect customer-grain visuals;
- confirm aggregate validation charts are not incorrectly cross-filtered;
- export one screenshot per page;
- save the file as `customer_segmentation.pbix` in this directory.

Power BI Desktop files are proprietary binaries and should only be added after
opening and validating them in the official Windows application. The project
does not claim that a `.pbix` exists until that manual validation is complete.
