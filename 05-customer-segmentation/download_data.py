"""Download the UCI Online Retail workbook from its public source."""
from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import requests

SOURCE_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
TARGET = RAW_DIR / "Online Retail.xlsx"


def download(force: bool = False) -> Path:
    """Download and extract the source workbook, returning its local path."""
    if TARGET.exists() and not force:
        print(f"Source workbook already exists: {TARGET}")
        return TARGET

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}")
    response = requests.get(SOURCE_URL, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        workbook_names = [
            name for name in archive.namelist() if name.lower().endswith(".xlsx")
        ]
        if len(workbook_names) != 1:
            raise RuntimeError(f"Expected one XLSX workbook, found: {workbook_names}")
        with archive.open(workbook_names[0]) as source, TARGET.open("wb") as destination:
            destination.write(source.read())

    if TARGET.stat().st_size < 20_000_000:
        raise RuntimeError("Downloaded workbook is unexpectedly small")
    print(f"Saved {TARGET} ({TARGET.stat().st_size / 1_000_000:.1f} MB)")
    return TARGET


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Replace any existing workbook")
    args = parser.parse_args()
    download(force=args.force)
