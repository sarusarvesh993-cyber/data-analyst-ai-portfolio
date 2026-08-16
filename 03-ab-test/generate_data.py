"""
Generate a realistic, reproducible A/B experiment dataset.
Seeded -> identical every run, no external download, no cost.

Models a 'new checkout page' vs 'old checkout page' conversion test.
Output: data/ab_data.csv  (user_id, group, converted, revenue)

NOTE: the canonical public A/B dataset (Udacity ab_data) is no longer hosted
anywhere stable. This synthetic-but-realistic data has the SAME structure, so
the full statistical analysis stays reproducible, free, and interview-safe.
"""
import numpy as np
import pandas as pd
import os

SEED = 42
N = 100_000  # users per arm


def gen(p, n, start, group):
    rng = np.random.default_rng(SEED)
    uid = np.arange(start, start + n)
    conv = rng.binomial(1, p, n)
    rev = np.round(np.where(conv == 1, rng.uniform(20, 120, n), 0.0), 2)
    return pd.DataFrame({"user_id": uid, "group": group, "converted": conv, "revenue": rev})


if __name__ == "__main__":
    control = gen(0.115, N, 1, "control")
    treatment = gen(0.128, N, N + 1, "treatment")
    df = pd.concat([control, treatment], ignore_index=True)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/ab_data.csv", index=False)
    print(f"rows={len(df)}  control_conv={control['converted'].mean():.4f}  "
          f"treatment_conv={treatment['converted'].mean():.4f}")
