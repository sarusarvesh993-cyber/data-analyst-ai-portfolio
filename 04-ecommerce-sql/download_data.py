"""Download the public Olist e-commerce dataset from Kaggle.

No Kaggle token is required for the public version used here. Raw files stay
under 04-ecommerce-sql/data/raw/ and are excluded from Git.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
import zipfile

import requests

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
DATASET_VERSION = 2
URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    f"olistbr/brazilian-ecommerce?datasetVersionNumber={DATASET_VERSION}"
)
REQUIRED_FILES = [
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def download(force: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    existing = [name for name in REQUIRED_FILES if (RAW_DIR / name).exists()]
    if len(existing) == len(REQUIRED_FILES) and not force:
        print("All required raw files already exist. Use --force to refresh them.")
        return

    print("Downloading Olist Brazilian E-Commerce dataset (about 43 MB)…")
    with tempfile.NamedTemporaryFile(suffix=".zip") as temporary:
        with requests.get(URL, stream=True, timeout=120) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    temporary.write(chunk)
        temporary.flush()

        with zipfile.ZipFile(temporary.name) as archive:
            available = set(archive.namelist())
            missing = sorted(set(REQUIRED_FILES) - available)
            if missing:
                raise RuntimeError(f"Dataset archive is missing expected files: {missing}")
            for name in REQUIRED_FILES:
                destination = RAW_DIR / name
                if destination.exists() and not force:
                    continue
                with archive.open(name) as source, destination.open("wb") as target:
                    target.write(source.read())
                print(f"Extracted {destination.relative_to(PROJECT_DIR)}")

    print("Download complete.")
    print("Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
    print("License: CC BY-NC-SA 4.0")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="replace existing raw files")
    arguments = parser.parse_args()
    download(force=arguments.force)


if __name__ == "__main__":
    main()
