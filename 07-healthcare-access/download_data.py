"""Download official National Health Mission quarterly MIS PDFs."""
from __future__ import annotations

import argparse
from pathlib import Path

import requests

BASE_URL = "https://nhm.gov.in/MIS-NHM/2025-26/Dec-25"
FILES = ["ES.pdf", "G1.pdf", "G2.pdf", "G3.pdf", "G4.pdf"]
PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"


def download(force: bool = False) -> list[Path]:
    """Download the December 2025 NHM MIS national and state-group reports."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename in FILES:
        target = RAW_DIR / filename
        if target.exists() and not force:
            print(f"Source already exists: {target}")
            paths.append(target)
            continue
        url = f"{BASE_URL}/{filename}"
        print(f"Downloading {url}")
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        if not response.content.startswith(b"%PDF"):
            raise RuntimeError(f"Unexpected response for {url}")
        target.write_bytes(response.content)
        print(f"Saved {target} ({target.stat().st_size / 1_000:.1f} KB)")
        paths.append(target)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    download(force=args.force)
