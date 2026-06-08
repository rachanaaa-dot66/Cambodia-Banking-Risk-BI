# =============================================================================
# generate_credit_profiles.py
# Phase 4 — Generate Initial Credit Risk Characteristics
# Reference: 05_Simulation_Logic.md §9-§10 | 06_Data_Generation_Roadmap.md §7
# =============================================================================

import pandas as pd
import numpy as np
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    CREDIT_SCORE_RANGES, get_risk_category,
    SCORE_MIN, SCORE_MAX, RANDOM_SEED, DATA_RAW,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _initial_credit_score(rng, occupation: str, monthly_income: float,
                           age: int) -> int:
    """
    Derive credit score from occupation range (doc §9) then adjust for:
      - Income level  (+0 to +30 bonus for high earners)
      - Age           (25-50 prime band +10, very young/old slight penalty)
    """
    lo, hi = CREDIT_SCORE_RANGES.get(occupation, (500, 700))
    base   = int(rng.integers(lo, hi + 1))

    # Income adjustment
    if monthly_income >= 1500:  base += int(rng.integers(10, 31))
    elif monthly_income >= 700: base += int(rng.integers(0, 16))
    elif monthly_income < 250:  base -= int(rng.integers(0, 21))

    # Age adjustment
    if 25 <= age <= 50:         base += int(rng.integers(0, 11))
    elif age < 22 or age > 60:  base -= int(rng.integers(0, 11))

    return int(np.clip(base, SCORE_MIN, SCORE_MAX))


def _debt_to_income_ratio(rng, occupation: str, monthly_income: float) -> float:
    """
    Realistic DTI based on occupation risk tier (doc §9).
    Higher income → generally lower DTI.
    """
    if monthly_income <= 0:
        return round(float(rng.uniform(0.0, 0.20)), 4)

    base_dti = {
        "Student":            (0.00, 0.30),
        "Farmer":             (0.10, 0.55),
        "Factory Worker":     (0.10, 0.50),
        "Freelancer":         (0.10, 0.50),
        "Private Employee":   (0.10, 0.55),
        "Government Officer": (0.05, 0.45),
        "SME Owner":          (0.15, 0.60),
    }.get(occupation, (0.10, 0.50))

    lo, hi = base_dti
    # High earners generally lower DTI
    if monthly_income > 1500:
        hi = min(hi, 0.40)
    return round(float(rng.uniform(lo, hi)), 4)


def _previous_delinquency(rng, credit_score: int) -> int:
    """
    Delinquency history is inversely correlated with credit score (doc §9).
    """
    if credit_score >= 750: max_dlq = 0
    elif credit_score >= 650: max_dlq = 1
    elif credit_score >= 550: max_dlq = 3
    elif credit_score >= 450: max_dlq = 6
    else: max_dlq = 10
    return int(rng.integers(0, max_dlq + 1))


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_credit_profiles(
    customers_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Create one credit_profile record per customer.
    The profile captures the initial state at the start of the simulation.
    """
    rng = np.random.default_rng(seed)
    records = []

    for _, cust in customers_df.iterrows():
        occ    = cust["occupation"]
        income = float(cust["monthly_income"])
        age    = int(cust["age"])
        cid    = int(cust["customer_id"])

        score        = _initial_credit_score(rng, occ, income, age)
        risk_cat     = get_risk_category(score)
        dti          = _debt_to_income_ratio(rng, occ, income)
        delinquency  = _previous_delinquency(rng, score)

        records.append({
            "customer_id":                cid,
            "credit_score":               score,
            "risk_category":              risk_cat,
            "debt_to_income_ratio":       dti,
            "previous_delinquency_count": delinquency,
        })

    df = pd.DataFrame(records)
    print(f"[credit_profiles] Generated {len(df):,} profiles")
    print(df["risk_category"].value_counts().to_string())
    return df


def save_credit_profiles(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "credit_profiles.csv")
    df.to_csv(path, index=False)
    print(f"[credit_profiles] Saved → {path}")
    return path


if __name__ == "__main__":
    from generate_branches  import generate_branches
    from generate_customers import generate_customers
    branches  = generate_branches()
    customers = generate_customers(branches)
    df        = generate_credit_profiles(customers)
    save_credit_profiles(df)
