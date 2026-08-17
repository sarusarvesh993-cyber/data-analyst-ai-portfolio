"""Generate a seeded A/B experiment demonstration dataset.

The two variants use independent draws from one seeded random-number stream.
Run from any working directory:
    python 03-ab-test/generate_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_PER_ARM = 100_000
PROJECT_DIR = Path(__file__).resolve().parent


def generate_arm(
    rng: np.random.Generator,
    conversion_rate: float,
    size: int,
    first_user_id: int,
    group: str,
) -> pd.DataFrame:
    converted = rng.binomial(1, conversion_rate, size)
    revenue = np.where(converted == 1, rng.uniform(20, 120, size), 0.0)
    return pd.DataFrame(
        {
            "user_id": np.arange(first_user_id, first_user_id + size),
            "group": group,
            "converted": converted,
            "revenue": np.round(revenue, 2),
        }
    )


def main() -> None:
    rng = np.random.default_rng(SEED)
    control = generate_arm(rng, 0.115, N_PER_ARM, 1, "control")
    treatment = generate_arm(
        rng, 0.128, N_PER_ARM, N_PER_ARM + 1, "treatment"
    )
    data = pd.concat([control, treatment], ignore_index=True)
    output = PROJECT_DIR / "data" / "ab_data.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output, index=False)
    print(
        f"Wrote {output}  rows={len(data):,}  "
        f"control={control['converted'].mean():.4f}  "
        f"treatment={treatment['converted'].mean():.4f}"
    )


if __name__ == "__main__":
    main()
