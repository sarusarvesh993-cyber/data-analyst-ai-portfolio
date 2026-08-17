"""Data generation and modeling utilities for the churn project.

The bundled project uses a seeded synthetic dataset. That limitation is made
explicit in the UI and documentation; results are demonstrations of method,
not estimates for a real telecom company.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 42
TARGET = "Churn"
NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "SeniorCitizen", "Dependents"]
CATEGORICAL_FEATURES = [
    "Contract",
    "InternetService",
    "TechSupport",
    "OnlineSecurity",
    "PaymentMethod",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass
class ChurnModelResult:
    """Fitted model plus holdout results used by the dashboard."""

    model: Pipeline
    y_test: pd.Series
    probabilities: np.ndarray
    auc: float
    model_name: str = "Logistic regression"


def make_churn_data(n: int = 5_000, seed: int = SEED) -> pd.DataFrame:
    """Create the same reproducible sample used by the churn notebook."""
    rng = np.random.default_rng(seed)
    tenure = rng.integers(1, 73, n)
    monthly = np.round(rng.uniform(20, 120, n), 2)
    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"], n, p=[0.5, 0.3, 0.2]
    )
    internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.4, 0.4, 0.2])
    tech = rng.choice(["Yes", "No"], n, p=[0.5, 0.5])
    security = rng.choice(["Yes", "No"], n, p=[0.5, 0.5])
    payment = rng.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        n,
        p=[0.4, 0.3, 0.15, 0.15],
    )
    senior = rng.choice([0, 1], n, p=[0.7, 0.3])
    dependents = rng.choice([0, 1], n, p=[0.7, 0.3])

    logit = np.full(n, -3.0)
    logit += (contract == "Month-to-month") * 1.8
    logit -= (contract == "Two year") * 1.8
    logit += (internet == "Fiber optic") * 1.2
    logit += (tech == "No") * 0.8
    logit += (security == "No") * 0.7
    logit += (payment == "Electronic check") * 0.9
    logit += senior * 0.6
    logit += (tenure < 12) * 1.0
    logit += (monthly - 70) / 30.0
    churn_probability = 1.0 / (1.0 + np.exp(-logit))

    return pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(1, n + 1)],
            "tenure": tenure,
            "MonthlyCharges": monthly,
            "Contract": contract,
            "InternetService": internet,
            "TechSupport": tech,
            "OnlineSecurity": security,
            "PaymentMethod": payment,
            "SeniorCitizen": senior,
            "Dependents": dependents,
            TARGET: rng.binomial(1, churn_probability),
        }
    )


def train_churn_model(df: pd.DataFrame, seed: int = SEED) -> ChurnModelResult:
    """Fit the simpler winning model and evaluate it on a stratified holdout."""
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES],
        df[TARGET],
        test_size=0.20,
        random_state=seed,
        stratify=df[TARGET],
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1_000,
                    class_weight="balanced",
                    random_state=seed,
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]
    return ChurnModelResult(
        model=model,
        y_test=y_test,
        probabilities=probabilities,
        auc=float(roc_auc_score(y_test, probabilities)),
    )


def threshold_metrics(result: ChurnModelResult, threshold: float = 0.50) -> dict:
    """Return decision metrics for a selected operating threshold."""
    predicted = (result.probabilities >= threshold).astype(int)
    matrix = confusion_matrix(result.y_test, predicted)
    return {
        "auc": result.auc,
        "precision": float(precision_score(result.y_test, predicted, zero_division=0)),
        "recall": float(recall_score(result.y_test, predicted, zero_division=0)),
        "f1": float(f1_score(result.y_test, predicted, zero_division=0)),
        "confusion_matrix": matrix,
        "flagged": int(predicted.sum()),
    }


def score_customer(model: Pipeline, customer: dict) -> float:
    """Score one customer represented by the dashboard form."""
    row = pd.DataFrame([customer], columns=FEATURES)
    return float(model.predict_proba(row)[0, 1])


def feature_importance(result: ChurnModelResult) -> pd.DataFrame:
    """Return standardized logistic coefficients with readable feature names."""
    preprocessor = result.model.named_steps["preprocessor"]
    names = preprocessor.get_feature_names_out()
    coefficients = result.model.named_steps["classifier"].coef_[0]
    cleaned = [
        name.replace("numeric__", "").replace("categorical__", "")
        for name in names
    ]
    return (
        pd.DataFrame(
            {
                "feature": cleaned,
                "coefficient": coefficients,
                "importance": np.abs(coefficients),
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
