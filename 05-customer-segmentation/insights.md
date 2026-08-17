# Stakeholder brief

## Decision

How should the marketing team prioritize customer audiences for protection,
growth, reactivation, and suppression while keeping campaign measurement
financially credible?

## What the data shows

- 4,338 identified customers generated £8.91M of completed-purchase value
  across 18,532 invoices. The repeat-customer rate was 65.58%.
- Value is highly concentrated: 946 Champions represented 21.81% of customers
  but 64.63% of completed-purchase value (£5.76M).
- 908 At Risk customers represented 20.93% of customers and £1.16M of
  historical value. Their median recency was 138.5 days.
- 827 Hibernating customers represented 19.06% of customers but only 2.14% of
  value, making broad discounting difficult to justify.
- Identified returns totalled £611K. Return behavior should remain a campaign
  guardrail rather than being erased during cleaning.
- A five-cluster K-means solution was selected as the challenger model. Its
  silhouette score was 0.317, seed-stability ARI was 0.992, and its smallest
  cluster still represented 9.94% of customers.

## Recommended actions

### 1. Protect Champions without default discounting

Use recognition, early access, and referral benefits. Measure incremental
90-day revenue per customer and contribution margin against a
business-as-usual holdout.

### 2. Run a controlled At Risk win-back test

Prioritize the £1.16M At Risk audience. Test a personalized message and a
threshold-based shipping offer with at least a 10% no-contact holdout. The
primary KPI is incremental repeat purchase; contribution after incentive and
returns is the guardrail.

### 3. Build early lifecycle journeys

New Customers and Potential Loyalists need second- and third-order journeys,
not the same treatment as established high-value customers. Evaluate repeat
purchase inside fixed 60- or 90-day windows.

### 4. Suppress low-return outreach

Use a low-cost re-permission test for Hibernating customers and suppress
persistent non-responders. Optimize incremental profit per contact rather than
open rate.

## Interpretation boundary

The RFM rules are the primary activation layer because they are transparent
and easy to implement. K-means is a challenger that tests whether natural
behavioral groupings reveal useful structure. Neither method proves that a
campaign will work; treatment effects require randomized measurement.
