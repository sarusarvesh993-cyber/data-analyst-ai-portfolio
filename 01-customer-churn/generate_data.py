"""
Generate a synthetic-but-realistic customer churn dataset.
Seeded -> fully reproducible (same numbers every run). No external download, no cost.
Output: data/churn.csv
"""
import numpy as np
import pandas as pd
import os

SEED = 42
N = 5000

def main():
    rng = np.random.default_rng(SEED)
    tenure = rng.integers(1, 73, N)                       # months
    monthly = np.round(rng.uniform(20, 120, N), 2)        # $/month
    contract = rng.choice(["Month-to-month", "One year", "Two year"], N, p=[0.5, 0.3, 0.2])
    internet = rng.choice(["DSL", "Fiber optic", "No"], N, p=[0.4, 0.4, 0.2])
    tech = rng.choice(["Yes", "No"], N, p=[0.5, 0.5])
    security = rng.choice(["Yes", "No"], N, p=[0.5, 0.5])
    payment = rng.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
                         N, p=[0.4, 0.3, 0.15, 0.15])
    senior = rng.choice([0, 1], N, p=[0.7, 0.3])
    dependents = rng.choice([0, 1], N, p=[0.7, 0.3])

    # Logistic "truth": combine real-world churn drivers.
    logit = -3.0
    logit += (contract == "Month-to-month") * 1.8
    logit += (contract == "Two year") * -1.8
    logit += (internet == "Fiber optic") * 1.2
    logit += (tech == "No") * 0.8
    logit += (security == "No") * 0.7
    logit += (payment == "Electronic check") * 0.9
    logit += senior * 0.6
    logit += (tenure < 12) * 1.0
    logit += (monthly - 70) / 30.0
    p = 1.0 / (1.0 + np.exp(-logit))
    churn = rng.binomial(1, p)

    df = pd.DataFrame({
        "tenure": tenure,
        "MonthlyCharges": monthly,
        "Contract": contract,
        "InternetService": internet,
        "TechSupport": tech,
        "OnlineSecurity": security,
        "PaymentMethod": payment,
        "SeniorCitizen": senior,
        "Dependents": dependents,
        "Churn": churn,
    })
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/churn.csv", index=False)
    print(f"Wrote data/churn.csv  shape={df.shape}  churn_rate={df['Churn'].mean():.1%}")

if __name__ == "__main__":
    main()
