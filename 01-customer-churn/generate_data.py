"""Generate the seeded customer-churn demonstration dataset.

Run from any working directory:
    python 01-customer-churn/generate_data.py

Output: 01-customer-churn/data/churn.csv
"""
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent
sys.path.insert(0, str(REPO_ROOT))

from portfolio_app.churn import make_churn_data  # noqa: E402


def main() -> None:
    output = PROJECT_DIR / "data" / "churn.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    data = make_churn_data().drop(columns="customer_id")
    data.to_csv(output, index=False)
    print(
        f"Wrote {output.relative_to(REPO_ROOT)}  "
        f"shape={data.shape}  churn_rate={data['Churn'].mean():.1%}"
    )


if __name__ == "__main__":
    main()
