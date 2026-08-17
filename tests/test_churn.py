import numpy as np

from portfolio_app.churn import (
    make_churn_data,
    score_customer,
    threshold_metrics,
    train_churn_model,
)


def test_data_is_reproducible():
    first = make_churn_data(n=100, seed=7)
    second = make_churn_data(n=100, seed=7)
    assert first.equals(second)
    assert first["customer_id"].is_unique


def test_model_and_single_customer_score():
    data = make_churn_data(n=2_000)
    result = train_churn_model(data)
    metrics = threshold_metrics(result, threshold=0.50)
    assert result.auc > 0.78
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert metrics["confusion_matrix"].sum() == len(result.y_test)

    customer = data.iloc[0].drop(labels=["customer_id", "Churn"]).to_dict()
    probability = score_customer(result.model, customer)
    assert np.isfinite(probability)
    assert 0 <= probability <= 1
