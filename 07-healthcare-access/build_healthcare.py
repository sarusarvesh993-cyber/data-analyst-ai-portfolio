"""Parse NHM MIS reports and build DuckDB healthcare access/readiness outputs."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pdfplumber

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "outputs"
DATABASE = PROJECT_DIR / "data" / "healthcare.duckdb"
SQL_PATH = PROJECT_DIR / "sql" / "01_healthcare_mart.sql"

GROUPS = {
    "G1.pdf": {
        "focus_group": "High Focus - Non-NE",
        "states": [
            "Bihar", "Chhattisgarh", "Himachal Pradesh", "Jammu & Kashmir",
            "Jharkhand", "Madhya Pradesh", "Odisha", "Rajasthan",
            "Uttar Pradesh", "Uttarakhand",
        ],
    },
    "G2.pdf": {
        "focus_group": "High Focus - NE",
        "states": [
            "Arunachal Pradesh", "Assam", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Sikkim", "Tripura",
        ],
    },
    "G3.pdf": {
        "focus_group": "Non-High Focus - Large",
        "states": [
            "Andhra Pradesh", "Goa", "Gujarat", "Haryana", "Karnataka",
            "Kerala", "Maharashtra", "Punjab", "Tamil Nadu", "Telangana",
            "West Bengal",
        ],
    },
    "G4.pdf": {
        "focus_group": "Non-High Focus - Small & UT",
        "states": [
            "Andaman & Nicobar Islands", "Chandigarh",
            "Dadra & Nagar Haveli and Daman & Diu", "Delhi", "Ladakh",
            "Lakshadweep", "Puducherry",
        ],
    },
}
ROW_MAP = {
    "1": "population_lakh_reported",
    "2": "districts",
    "5": "cities_covered",
    "6": "cities_health_facility_mapped",
    "7": "cities_slum_mapped",
    "8": "cities_vulnerability_mapped",
    "9": "cbr",
    "10": "cdr",
    "11": "imr",
    "12": "mmr",
    "13": "tfr",
    "14": "sex_ratio",
    "15": "life_expectancy",
    "16": "nmr",
    "17": "u5mr",
    "49": "sub_centres",
    "52": "facilities_24x7",
    "54": "uphcs_24x7",
    "55": "phcs",
    "57": "phcs_three_nurses",
    "61": "uphcs_operational",
    "62": "uphcs_minimum_package",
    "63": "chcs",
    "67": "uchcs_24x7",
    "69": "district_hospitals",
}
NUMBER = re.compile(r"(?<![\d.])-?\d+(?:\.\d+)?|\bNA\b")


def _numeric(value: str) -> float:
    return np.nan if value == "NA" else float(value)


def parse_group_report(path: Path, states: list[str], focus_group: str) -> pd.DataFrame:
    """Extract reviewed rows from one state-group PDF table."""
    expected = set(ROW_MAP)
    extracted: dict[str, list[str]] = {}
    with pdfplumber.open(path) as report:
        for page in report.pages:
            for table in page.extract_tables():
                for row in table:
                    if not row:
                        continue
                    code = str(row[0] or "").strip().replace(" ", "")
                    if code not in expected or code in extracted:
                        continue
                    tokens: list[str] = []
                    for cell in row:
                        if cell:
                            tokens.extend(NUMBER.findall(str(cell).replace(",", "")))
                    values = tokens[-len(states):]
                    if len(values) != len(states):
                        raise ValueError(
                            f"{path.name} row {code}: expected {len(states)} state values, found {values}"
                        )
                    extracted[code] = values
    missing = expected - set(extracted)
    if missing:
        raise ValueError(f"{path.name} is missing expected rows: {sorted(missing)}")

    rows = []
    for index, state in enumerate(states):
        row: dict[str, object] = {"state": state, "focus_group": focus_group}
        for code, column in ROW_MAP.items():
            row[column] = _numeric(extracted[code][index])
        rows.append(row)
    return pd.DataFrame(rows)


def parse_reports(raw_dir: str | Path = RAW_DIR) -> pd.DataFrame:
    """Parse all four official state-group reports into one state/UT table."""
    directory = Path(raw_dir)
    frames = []
    for filename, config in GROUPS.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run download_data.py first.")
        frames.append(
            parse_group_report(path, config["states"], config["focus_group"])
        )
    state = pd.concat(frames, ignore_index=True)
    state["population_lakh"] = state["population_lakh_reported"].where(
        state["population_lakh_reported"].gt(0)
    )
    return state


def add_priority_score(mart: pd.DataFrame) -> pd.DataFrame:
    """Build a transparent, completeness-aware review-priority index."""
    scored = mart.copy()
    components = {
        "access_gap_percentile": scored["facilities_24x7_per_100k"].rank(
            pct=True, ascending=False
        ),
        "phc_staffing_gap_percentile": scored["phc_three_nurse_readiness_pct"].rank(
            pct=True, ascending=False
        ),
        "urban_mapping_gap_percentile": scored["urban_facility_mapping_pct"].rank(
            pct=True, ascending=False
        ),
        "infant_mortality_burden_percentile": scored["imr"].rank(
            pct=True, ascending=True
        ),
    }
    for name, values in components.items():
        scored[name] = values
    component_columns = list(components)
    scored["priority_component_count"] = scored[component_columns].notna().sum(axis=1)
    scored["review_priority_score"] = (
        100 * scored[component_columns].mean(axis=1, skipna=True)
    ).where(scored["priority_component_count"].ge(3))
    scored["data_completeness_pct"] = 100 * scored[
        [
            "population_lakh", "urban_facility_mapping_pct",
            "phc_three_nurse_readiness_pct", "facilities_24x7_per_100k",
            "imr", "mmr", "life_expectancy", "u5mr",
        ]
    ].notna().mean(axis=1)
    ranked = scored["review_priority_score"].rank(pct=True)
    scored["review_priority_band"] = np.select(
        [scored["review_priority_score"].isna(), ranked.ge(0.75), ranked.ge(0.40)],
        ["Insufficient data", "Higher review priority", "Moderate review priority"],
        default="Lower review priority",
    )
    return scored.sort_values("review_priority_score", ascending=False, na_position="last")


def build_outputs(
    raw_dir: str | Path = RAW_DIR, output_dir: str | Path = OUTPUT_DIR
) -> dict[str, pd.DataFrame]:
    """Parse reports, model with DuckDB, and write reviewed CSV outputs."""
    raw = parse_reports(raw_dir)
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DATABASE))
    connection.register("parsed_state", raw)
    connection.execute("CREATE OR REPLACE TABLE state_raw AS SELECT * FROM parsed_state")
    mart = connection.execute(SQL_PATH.read_text(encoding="utf-8")).df()
    connection.close()
    mart = add_priority_score(mart)

    region = mart.groupby("focus_group", as_index=False).agg(
        states_and_uts=("state", "nunique"),
        sub_centres=("sub_centres", "sum"),
        phcs=("phcs", "sum"),
        chcs=("chcs", "sum"),
        district_hospitals=("district_hospitals", "sum"),
        facilities_24x7=("facilities_24x7", "sum"),
        median_urban_mapping_pct=("urban_facility_mapping_pct", "median"),
        median_phc_three_nurse_readiness_pct=("phc_three_nurse_readiness_pct", "median"),
        median_imr=("imr", "median"),
        median_review_priority_score=("review_priority_score", "median"),
    )
    valid_population = mart["population_lakh"].notna()
    executive = pd.DataFrame(
        [
            {
                "report_status_date": "2025-12-31",
                "states_and_uts": len(mart),
                "focus_groups": mart["focus_group"].nunique(),
                "population_reporting_states": int(valid_population.sum()),
                "population_missing_or_zero_states": int((~valid_population).sum()),
                "sub_centres": int(mart["sub_centres"].sum()),
                "phcs": int(mart["phcs"].sum()),
                "chcs": int(mart["chcs"].sum()),
                "district_hospitals": int(mart["district_hospitals"].sum()),
                "facilities_24x7": int(mart["facilities_24x7"].sum()),
                "median_urban_mapping_pct": mart["urban_facility_mapping_pct"].median(),
                "median_phc_three_nurse_readiness_pct": mart[
                    "phc_three_nurse_readiness_pct"
                ].median(),
                "states_with_imr": int(mart["imr"].notna().sum()),
                "median_imr_reporting_states": mart["imr"].median(),
                "higher_priority_states": int(
                    mart["review_priority_band"].eq("Higher review priority").sum()
                ),
            }
        ]
    )
    mapping_over_100 = mart["urban_facility_mapping_pct"].gt(100)
    staffing_over_100 = mart["phc_three_nurse_readiness_pct"].gt(100)
    quality = pd.DataFrame(
        [
            ("parsed_state_ut_rows", len(mart), "PASS"),
            ("duplicate_state_rows", int(mart["state"].duplicated().sum()), "PASS"),
            ("missing_or_zero_population_rows", int((~valid_population).sum()), "REVIEW"),
            (
                "missing_imr_rows",
                int(mart["imr"].isna().sum()),
                "PASS" if mart["imr"].notna().all() else "REVIEW",
            ),
            ("missing_mmr_rows", int(mart["mmr"].isna().sum()), "REVIEW"),
            ("urban_mapping_above_100_pct_rows", int(mapping_over_100.sum()), "REVIEW"),
            (
                "phc_staffing_above_100_pct_rows",
                int(staffing_over_100.sum()),
                "PASS" if not staffing_over_100.any() else "REVIEW",
            ),
            (
                "insufficient_priority_component_rows",
                int(mart["review_priority_score"].isna().sum()),
                "PASS" if mart["review_priority_score"].notna().all() else "REVIEW",
            ),
            ("negative_facility_count_cells", int((mart[["sub_centres", "phcs", "chcs", "district_hospitals"]] < 0).sum().sum()), "PASS"),
        ],
        columns=["check_name", "issue_count", "check_status"],
    )
    dictionary = pd.DataFrame(
        [
            ("urban_facility_mapping_pct", "Cities with completed urban health-facility mapping / cities covered", "%", "Higher is better; values over 100 are retained source inconsistencies"),
            ("phc_three_nurse_readiness_pct", "PHCs reporting three staff nurses / PHCs", "%", "Staffing readiness proxy, not full workforce adequacy"),
            ("facilities_24x7_per_100k", "Reported rural/sub-district, UPHC, and UCHC 24x7 facilities per 100K Census-2011 population", "rate", "Uses dated population and does not measure beds, staffing quality, or travel time"),
            ("district_hospitals_per_million", "District hospitals per million Census-2011 population", "rate", "Facility count does not measure beds, quality, or travel time"),
            ("imr", "Infant mortality rate from SRS 2023", "per 1,000 live births", "Missing for some states/UTs"),
            ("review_priority_score", "Mean percentile of low 24x7 density, low PHC staffing readiness, low urban mapping, and high IMR", "0-100", "Screening index only; requires at least three components"),
        ],
        columns=["metric", "definition", "unit", "interpretation_boundary"],
    )
    metadata = pd.DataFrame(
        [
            {
                "source_name": "National Health Mission Quarterly MIS Report 2025-26",
                "status_date": "2025-12-31",
                "source_page": "https://nhm.gov.in/index4.php?lang=1&level=0&linkid=457&lid=686",
                "source_files": "G1.pdf; G2.pdf; G3.pdf; G4.pdf",
                "population_basis": "Census 2011 values reproduced in the official report",
                "health_indicator_basis": "SRS 2023; MMR SRS 2021-23; life expectancy 2019-23",
            }
        ]
    )
    outputs = {
        "executive_kpis": executive,
        "state_health_access": mart,
        "region_summary": region,
        "priority_summary": mart[
            [
                "state", "focus_group", "review_priority_score",
                "review_priority_band", "priority_component_count",
                "data_completeness_pct", "facilities_24x7_per_100k",
                "phc_three_nurse_readiness_pct", "urban_facility_mapping_pct",
                "imr", "u5mr",
            ]
        ],
        "data_quality": quality,
        "metric_dictionary": dictionary,
        "source_metadata": metadata,
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(destination / f"{name}.csv", index=False)
        print(f"Wrote {destination / f'{name}.csv'} ({len(frame):,} rows)")
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    build_outputs(args.raw_dir, args.output_dir)
