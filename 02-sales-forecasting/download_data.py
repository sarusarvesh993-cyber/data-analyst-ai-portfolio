"""
Download a REAL, stable, reproducible sales series for forecasting:
US Monthly Retail Trade Sales (FRED series RSXFS), $ millions, 1992->present.
Public, no auth, no API key. Saved locally so the project never breaks.
Output: data/retail_sales_monthly.csv  (observation_date, RetailSales)
"""
import os
import io
import urllib.request
import pandas as pd

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=RSXFS"


def main():
    os.makedirs("data", exist_ok=True)
    print("downloading FRED RSXFS (US monthly retail trade sales)...")
    raw = urllib.request.urlopen(URL, timeout=30).read().decode()
    df = pd.read_csv(io.StringIO(raw)).dropna()
    df.columns = ["observation_date", "RetailSales"]
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df = df.sort_values("observation_date").reset_index(drop=True)
    df.to_csv("data/retail_sales_monthly.csv", index=False)
    print(f"saved data/retail_sales_monthly.csv  rows={len(df)}")
    print("range:", df["observation_date"].min().date(), "->", df["observation_date"].max().date())
    print("latest retail sales ($, millions):", int(df["RetailSales"].iloc[-1]))


if __name__ == "__main__":
    main()
