# 03 · A/B Test Decision Calculator

## Business question

Is the treatment's observed conversion lift reliable and large enough to matter, or should the product team continue or redesign the experiment?

## Data

The notebook includes a seeded example with 100,000 users per arm and the fields `user_id`, `group`, `converted`, and `revenue`. It is **synthetic demonstration data**. The Streamlit calculator accepts aggregate visitor and conversion counts from another experiment.

## Method

1. Validate that users and groups are consistent.
2. Calculate control and treatment conversion rates.
3. Run a two-sided pooled two-proportion z-test.
4. Construct an unpooled confidence interval for treatment minus control.
5. Compare statistical evidence with a user-defined minimum useful lift.
6. Estimate equal-arm sample size from baseline conversion, minimum detectable effect, alpha, and power.
7. State assumptions and warn against unplanned repeated peeking.
8. Convert approved results into an optional AI-assisted decision brief.

## Why the decision rule matters

A small p-value alone is not a shipping decision. The app checks whether the effect is also useful for the business. A non-significant result is treated as inconclusive unless the confidence interval rules out the minimum useful effect.

## Example result

For the default aggregate counts, treatment is 12.80% versus 11.52% for control. The absolute lift is 1.28 percentage points, and the 95% confidence interval excludes zero. The app recalculates these values for user inputs.

## Limitations

- Assumes independent, concurrent random assignment.
- Normal approximation requires adequate expected successes and failures.
- Does not correct fixed-horizon p-values for repeated monitoring.
- Conversion should be reviewed with guardrails such as revenue, refunds, or latency.

## Run

```powershell
python .\03-ab-test\generate_data.py
Push-Location .\03-ab-test
jupyter nbconvert --execute --to notebook --inplace analysis.ipynb
Pop-Location
streamlit run streamlit_app.py
```

## Files

- `analysis.ipynb` — statistical analysis and example
- `generate_data.py` — independent seeded draws for both variants
- `insights.md` — metric-controlled stakeholder brief
- `assets/` — charts rendered in the notebook
- `../pages/3_AB_Test_Calculator.py` — interactive calculator
- `../portfolio_app/ab_testing.py` — tested statistical functions
