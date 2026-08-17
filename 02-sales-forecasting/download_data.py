"""Refresh the public FRED retail-sales snapshot.

Series RSAFSNA is U.S. retail trade and food-services sales, monthly, millions
of dollars, not seasonally adjusted. No API key is required.

Outputs:
- 02-sales-forecasting/data/retail_sales_monthly.csv
- portfolio_app/data/retail_sales_monthly.csv
"""
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

SERIES_ID = "RSAFSNA"
URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}"
PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent


def download() -> pd.DataFrame:
    raw = urlopen(URL, timeout=30).read().decode("utf-8")
    frame = pd.read_csv(StringIO(raw)).dropna()
    frame.columns = ["observation_date", "RetailSales"]
    frame["observation_date"] = pd.to_datetime(frame["observation_date"])
    return frame.sort_values("observation_date").reset_index(drop=True)


def main() -> None:
    print(f"Downloading FRED {SERIES_ID}…")
    frame = download()
    destinations = [
        PROJECT_DIR / "data" / "retail_sales_monthly.csv",
        REPO_ROOT / "portfolio_app" / "data" / "retail_sales_monthly.csv",
    ]
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(destination, index=False)
        print(f"Saved {destination.relative_to(REPO_ROOT)}")
    print(
        f"Rows={len(frame)}  range={frame['observation_date'].min():%Y-%m} "
        f"to {frame['observation_date'].max():%Y-%m}"
    )


if __name__ == "__main__":
    main()
