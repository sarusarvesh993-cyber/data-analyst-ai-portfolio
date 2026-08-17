"""Download the City of Austin FY2026 budget-versus-expenditure snapshot."""
from __future__ import annotations

import argparse
from pathlib import Path

import requests

DATASET_ID = "g5k8-8sud"
SOURCE_URL = f"https://data.austintexas.gov/resource/{DATASET_ID}.csv?$limit=100000"
PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
TARGET = RAW_DIR / "austin_budget_vs_actual.csv"


def download(force: bool = False) -> Path:
    """Download the public Socrata CSV and return the local path."""
    if TARGET.exists() and not force:
        print(f"Source snapshot already exists: {TARGET}")
        return TARGET

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}")
    response = requests.get(SOURCE_URL, timeout=120)
    response.raise_for_status()
    TARGET.write_bytes(response.content)

    if TARGET.stat().st_size < 5_000_000:
        raise RuntimeError("Downloaded budget snapshot is unexpectedly small")
    header = TARGET.open(encoding="utf-8").readline().lower()
    required = {"budget_fiscal_year", "thru_quarter", "budget", "expenditures"}
    if not all(column in header for column in required):
        raise RuntimeError("Downloaded file does not match the expected Austin schema")

    print(f"Saved {TARGET} ({TARGET.stat().st_size / 1_000_000:.1f} MB)")
    return TARGET


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Replace the local snapshot")
    args = parser.parse_args()
    download(force=args.force)
