"""Load and interrogate reviewed Project 07 healthcare-access outputs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "07-healthcare-access" / "outputs"
FILES = {
    "kpis": "executive_kpis.csv",
    "states": "state_health_access.csv",
    "regions": "region_summary.csv",
    "priorities": "priority_summary.csv",
    "quality": "data_quality.csv",
    "dictionary": "metric_dictionary.csv",
    "metadata": "source_metadata.csv",
}
REQUIRED = {
    "kpis": {"states_and_uts", "phcs", "facilities_24x7", "report_status_date"},
    "states": {
        "state", "focus_group", "phcs", "chcs", "district_hospitals",
        "facilities_24x7_per_100k", "review_priority_score",
    },
    "regions": {"focus_group", "states_and_uts", "phcs", "median_imr"},
    "priorities": {"state", "review_priority_score", "review_priority_band"},
    "quality": {"check_name", "issue_count", "check_status"},
    "dictionary": {"metric", "definition", "interpretation_boundary"},
    "metadata": {"source_name", "status_date", "source_page"},
}


def load_outputs(output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> dict[str, pd.DataFrame]:
    directory = Path(output_dir)
    outputs: dict[str, pd.DataFrame] = {}
    for key, filename in FILES.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing healthcare output: {path}")
        frame = pd.read_csv(path)
        missing = REQUIRED[key] - set(frame.columns)
        if missing:
            raise ValueError(f"{filename} is missing columns: {sorted(missing)}")
        outputs[key] = frame
    return outputs


def filter_states(
    states: pd.DataFrame,
    focus_groups: list[str] | tuple[str, ...] | None = None,
    priority_bands: list[str] | tuple[str, ...] | None = None,
    minimum_completeness_pct: float = 0.0,
) -> pd.DataFrame:
    if not 0 <= minimum_completeness_pct <= 100:
        raise ValueError("minimum_completeness_pct must be between 0 and 100")
    filtered = states.loc[
        states["data_completeness_pct"].ge(minimum_completeness_pct)
    ].copy()
    if focus_groups:
        filtered = filtered.loc[filtered["focus_group"].isin(focus_groups)]
    if priority_bands:
        filtered = filtered.loc[
            filtered["review_priority_band"].isin(priority_bands)
        ]
    return filtered


def priority_export(states: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "state", "focus_group", "review_priority_score", "review_priority_band",
        "priority_component_count", "data_completeness_pct",
        "facilities_24x7_per_100k", "phc_three_nurse_readiness_pct",
        "urban_facility_mapping_pct", "imr", "u5mr",
    ]
    return states[columns].sort_values(
        ["review_priority_score", "data_completeness_pct"],
        ascending=[False, False], na_position="last",
    )
