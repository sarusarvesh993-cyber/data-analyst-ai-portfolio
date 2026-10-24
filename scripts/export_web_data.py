"""Export reviewed Python analytics into deterministic, browser-safe JSON snapshots.

The Vercel frontend never trains a model or calls a Python service at runtime.
Run this script intentionally after reviewing source/model changes.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
import statsmodels

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "public" / "data"
ASSETS = ROOT / "public" / "assets"
DOWNLOADS = ROOT / "public" / "downloads"

from portfolio_app.ab_testing import analyze_ab_test, decision, required_sample_per_arm
from portfolio_app.churn import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    feature_importance,
    make_churn_data,
    score_customer,
    threshold_metrics,
    train_churn_model,
)
from portfolio_app.forecast import build_forecast, load_retail_sales, monthly_seasonality


def clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).strftime("%Y-%m-%d")
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        if not math.isfinite(number):
            return None
        # Avoid platform-specific negative zero in exported snapshots.
        return 0.0 if number == 0 else number
    if pd.isna(value):
        return None
    return str(value) if isinstance(value, np.str_) else value


def records(frame: pd.DataFrame, columns: list[str] | None = None) -> list[dict[str, Any]]:
    selected = frame if columns is None else frame.loc[:, columns]
    return [{str(key): clean(value) for key, value in row.items()} for row in selected.to_dict("records")]


def write_json(name: str, payload: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n"
    (OUT / name).write_text(text, encoding="utf-8")


def load_csv(folder: str, filename: str, columns: list[str] | None = None) -> list[dict[str, Any]]:
    return records(pd.read_csv(ROOT / folder / "outputs" / filename), columns)


def export_churn() -> dict[str, Any]:
    data = make_churn_data()
    result = train_churn_model(data)
    preprocessor = result.model.named_steps["preprocessor"]
    classifier = result.model.named_steps["classifier"]
    scaler = preprocessor.named_transformers_["numeric"]
    encoder = preprocessor.named_transformers_["categorical"]
    coefficients = classifier.coef_[0]

    numeric = {
        feature: {
            "mean": clean(scaler.mean_[index]),
            "scale": clean(scaler.scale_[index]),
            "coefficient": clean(coefficients[index]),
        }
        for index, feature in enumerate(NUMERIC_FEATURES)
    }
    categorical: dict[str, dict[str, float]] = {}
    offset = len(NUMERIC_FEATURES)
    for feature, categories in zip(CATEGORICAL_FEATURES, encoder.categories_, strict=True):
        categorical[feature] = {
            str(category): clean(coefficients[offset + index]) for index, category in enumerate(categories)
        }
        offset += len(categories)
    if offset != len(coefficients):
        raise RuntimeError("Churn coefficient export did not cover every model feature")

    thresholds = []
    for step in range(4, 17):
        threshold = step / 20
        metric = threshold_metrics(result, threshold)
        thresholds.append({
            "threshold": threshold,
            "precision": clean(metric["precision"]),
            "recall": clean(metric["recall"]),
            "f1": clean(metric["f1"]),
            "flagged": metric["flagged"],
            "confusionMatrix": records(pd.DataFrame(metric["confusion_matrix"])),
        })
    # Convert the two-row matrices to plain nested arrays for the client.
    for item, step in zip(thresholds, range(4, 17), strict=True):
        matrix = threshold_metrics(result, step / 20)["confusion_matrix"]
        item["confusionMatrix"] = [[int(value) for value in row] for row in matrix.tolist()]

    contract = data.groupby("Contract", as_index=False)["Churn"].mean()
    tenure = (
        data.assign(tenure_band=pd.cut(data["tenure"], [0, 12, 24, 48, 72], labels=["1–12", "13–24", "25–48", "49–72"]))
        .groupby("tenure_band", observed=True, as_index=False)["Churn"].mean()
    )
    default_customer = {
        "tenure": 8, "MonthlyCharges": 85.0, "SeniorCitizen": 0, "Dependents": 0,
        "Contract": "Month-to-month", "InternetService": "DSL", "TechSupport": "No",
        "OnlineSecurity": "No", "PaymentMethod": "Electronic check",
    }
    payload = {
        "records": len(data),
        "observedChurn": clean(data["Churn"].mean()),
        "holdoutRows": len(result.y_test),
        "auc": clean(result.auc),
        "modelName": result.model_name,
        "thresholds": thresholds,
        "contractRates": records(contract),
        "tenureRates": records(tenure),
        "importance": records(feature_importance(result).head(10)),
        "model": {"intercept": clean(classifier.intercept_[0]), "numeric": numeric, "categorical": categorical},
        "reference": {"customer": default_customer, "probability": clean(score_customer(result.model, default_customer))},
    }
    write_json("churn.json", payload)
    return {"auc": payload["auc"], "referenceProbability": payload["reference"]["probability"]}


def export_forecast() -> dict[str, Any]:
    series = load_retail_sales(ROOT / "portfolio_app" / "data" / "retail_sales_monthly.csv")
    result = build_forecast(series, horizon=24, test_months=24)
    history = series.iloc[-60:]
    payload = {
        "latestDate": clean(series.index.max()),
        "latestSales": clean(series.iloc[-1]),
        "metrics": {"mae": clean(result.mae), "rmse": clean(result.rmse), "naiveMae": clean(result.naive_mae), "improvementPct": clean(result.improvement_pct)},
        "history": [{"date": clean(date), "value": clean(value)} for date, value in history.items()],
        "future": [{
            "date": clean(date), "forecast": clean(result.future_forecast.loc[date]),
            "lower": clean(result.lower_80.loc[date]), "upper": clean(result.upper_80.loc[date]),
        } for date in result.future_forecast.index],
        "backtest": [{
            "date": clean(date), "actual": clean(result.actual_test.loc[date]),
            "forecast": clean(result.backtest_forecast.loc[date]), "naive": clean(result.naive_forecast.loc[date]),
        } for date in result.actual_test.index],
        "seasonality": records(monthly_seasonality(series)),
    }
    write_json("forecast.json", payload)
    return {"improvementPct": payload["metrics"]["improvementPct"], "latestDate": payload["latestDate"]}


def export_ab_reference() -> dict[str, Any]:
    result = analyze_ab_test(100_000, 11_522, 100_000, 12_802, 0.05)
    outcome, explanation = decision(result, 0.005, 0.05)
    payload = {
        "result": {key: clean(value) for key, value in result.__dict__.items()},
        "outcome": outcome,
        "explanation": explanation,
        "sampleReferences": [
            {"baseline": 0.10, "relativeMde": 0.10, "alpha": 0.05, "power": power,
             "perArm": required_sample_per_arm(0.10, 0.10, 0.05, power)}
            for power in (0.80, 0.85, 0.90, 0.95)
        ],
    }
    write_json("ab-test-reference.json", payload)
    return payload["sampleReferences"][0]


def export_ecommerce() -> None:
    folder = "04-ecommerce-sql"
    files = {
        "kpis": "executive_kpis.csv", "monthly": "monthly_performance.csv", "cohorts": "cohort_retention.csv",
        "states": "delivery_by_state.csv", "delivery": "delivery_experience.csv", "categories": "category_performance.csv",
        "quality": "data_quality.csv",
    }
    payload = {key: load_csv(folder, filename) for key, filename in files.items()}
    sql_dir = ROOT / folder / "sql"
    payload["sql"] = {path.name: path.read_text(encoding="utf-8") for path in sorted(sql_dir.glob("*.sql"))}
    write_json("ecommerce.json", payload)


def export_segmentation() -> None:
    folder = "05-customer-segmentation"
    files = {
        "kpis": "executive_kpis.csv", "segments": "segment_summary.csv", "clusters": "cluster_summary.csv",
        "comparison": "segment_cluster_comparison.csv", "validation": "model_validation.csv",
        "monthly": "monthly_performance.csv", "countries": "country_summary.csv", "quality": "data_quality.csv",
        "metadata": "feature_metadata.csv",
    }
    payload = {key: load_csv(folder, filename) for key, filename in files.items()}
    payload["customers"] = load_csv(folder, "customer_segments.csv", [
        "customer_id", "country", "recency_days", "frequency", "monetary_value", "average_order_value",
        "return_rate_pct", "rfm_segment", "cluster_name",
    ])
    write_json("segmentation.json", payload)


def export_finance() -> None:
    folder = "06-financial-planning"
    files = {
        "kpis": "executive_kpis.csv", "departments": "department_summary.csv", "funds": "fund_summary.csv",
        "expenses": "expense_summary.csv", "drivers": "variance_drivers.csv",
        "corporatePlan": "corporate_plan.csv", "corporateMonthly": "corporate_monthly.csv",
        "quality": "data_quality.csv", "metadata": "source_metadata.csv",
    }
    payload = {key: load_csv(folder, filename) for key, filename in files.items()}
    payload["mart"] = load_csv(folder, "planning_mart.csv", [
        "dept_rollup_name", "fund_name", "program_name", "expense_category", "budget", "expenditures",
        "expected_spend_to_date", "remaining_budget", "utilization_pct", "pace_variance", "pace_status",
    ])
    write_json("finance.json", payload)


def export_healthcare() -> None:
    folder = "07-healthcare-access"
    files = {
        "kpis": "executive_kpis.csv", "states": "state_health_access.csv", "regions": "region_summary.csv",
        "priorities": "priority_summary.csv", "quality": "data_quality.csv", "dictionary": "metric_dictionary.csv",
        "metadata": "source_metadata.csv",
    }
    write_json("healthcare.json", {key: load_csv(folder, filename) for key, filename in files.items()})


def copy_public_files() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    asset_map = {
        "01-customer-churn/assets/roc.png": "churn-roc.png",
        "01-customer-churn/assets/importance.png": "churn-importance.png",
        "02-sales-forecasting/assets/forecast.png": "forecast-backtest.png",
        "03-ab-test/assets/lift_ci.png": "ab-lift-ci.png",
        "04-ecommerce-sql/assets/cohort_retention.png": "ecommerce-cohorts.png",
        "05-customer-segmentation/assets/power_bi_companion.png": "segmentation-power-bi.png",
        "06-financial-planning/assets/power_bi_companion.png": "finance-power-bi.png",
        "06-financial-planning/assets/corporate_plan.png": "finance-corporate-plan.png",
        "07-healthcare-access/assets/power_bi_companion.png": "healthcare-power-bi.png",
        "07-healthcare-access/assets/priority_screen.png": "healthcare-priority.png",
    }
    for source, target in asset_map.items():
        shutil.copyfile(ROOT / source, ASSETS / target)
    download_map = {
        "05-customer-segmentation/power-bi/measures.dax": "customer-segmentation-measures.dax",
        "05-customer-segmentation/power-bi/theme.json": "customer-segmentation-theme.json",
        "05-customer-segmentation/power-bi/README.md": "customer-segmentation-power-bi.md",
        "06-financial-planning/power-bi/measures.dax": "financial-planning-measures.dax",
        "06-financial-planning/power-bi/theme.json": "financial-planning-theme.json",
        "06-financial-planning/power-bi/README.md": "financial-planning-power-bi.md",
        "06-financial-planning/assets/project_06_fpa_model.xlsx": "financial-planning-model.xlsx",
        "07-healthcare-access/power-bi/measures.dax": "healthcare-access-measures.dax",
        "07-healthcare-access/power-bi/theme.json": "healthcare-access-theme.json",
        "07-healthcare-access/power-bi/README.md": "healthcare-access-power-bi.md",
        "07-healthcare-access/sql/01_healthcare_mart.sql": "healthcare-access-mart.sql",
    }
    for source, target in download_map.items():
        shutil.copyfile(ROOT / source, DOWNLOADS / target)


def main() -> None:
    reference = {
        "churn": export_churn(),
        "forecast": export_forecast(),
        "abTest": export_ab_reference(),
    }
    export_ecommerce()
    export_segmentation()
    export_finance()
    export_healthcare()
    copy_public_files()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    write_json("manifest.json", {
        "schemaVersion": 1,
        "sourceCommit": commit,
        "runtime": "Static browser snapshots; no Streamlit or Python service required",
        "python": {"sklearn": sklearn.__version__, "statsmodels": statsmodels.__version__, "pandas": pd.__version__},
        "reference": reference,
    })
    print(json.dumps(reference, indent=2))
    print(f"Exported browser snapshots to {OUT}")


if __name__ == "__main__":
    main()
