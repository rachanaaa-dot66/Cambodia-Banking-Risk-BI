# =============================================================================
# generate_customers.py
# Phase 2 — Generate 50,000 Customers
# Reference: 05_Simulation_Logic.md §3-§5 | 06_Data_Generation_Roadmap.md §5
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    CUSTOMER_TARGET, AGE_DISTRIBUTION, GENDER_DISTRIBUTION,
    OCCUPATION_DISTRIBUTION, MARITAL_STATUS_DISTRIBUTION,
    PROVINCE_WEIGHTS, INCOME_RANGES, INCOME_AVERAGES,
    SIM_START_DATE, RANDOM_SEED, DATA_RAW,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _weighted_choice(rng, choices: dict):
    """Return one key sampled from a {key: weight} dict."""
    keys   = list(choices.keys())
    probs  = np.array(list(choices.values()), dtype=float)
    probs /= probs.sum()
    return keys[rng.choice(len(keys), p=probs)]


def _age_from_distribution(rng) -> int:
    age_ranges = list(AGE_DISTRIBUTION.keys())
    weights    = list(AGE_DISTRIBUTION.values())
    weights    = np.array(weights) / sum(weights)
    chosen     = age_ranges[rng.choice(len(age_ranges), p=weights)]
    return int(rng.integers(chosen[0], chosen[1] + 1))


def _income_for_occupation(rng, occupation: str) -> float:
    """
    Generate income using a log-normal distribution anchored on the
    published min/average/max from Simulation_Logic §5.
    """
    lo, hi  = INCOME_RANGES[occupation]
    avg     = INCOME_AVERAGES[occupation]
    if lo == 0 and avg < 50:          # Student edge case
        return round(float(rng.uniform(0, hi)), 2)
    sigma   = 0.35
    mu      = np.log(max(avg, 1))
    income  = rng.lognormal(mu, sigma)
    income  = float(np.clip(income, lo, hi))
    return round(income, 2)


def _join_date(rng, sim_start: date = SIM_START_DATE) -> date:
    """
    Customers join from 1 year before sim start (2023-01-01) through sim end (2025-12-31).
    Slight right-skew so more customers join during the active sim window.
    """
    earliest   = date(sim_start.year - 1, 1, 1)   # 2023-01-01
    latest     = date(2025, 12, 31)
    span_days  = (latest - earliest).days
    day_offset = int(rng.beta(1.5, 1.0) * span_days)
    return earliest + timedelta(days=day_offset)


def _customer_status(rng, join_date: date) -> str:
    """
    ~88 % active, ~8 % inactive, ~4 % closed.
    Older customers have slightly higher churn probability.
    """
    age_years = (date(2025, 12, 31) - join_date).days / 365
    churn_add = min(age_years * 0.003, 0.06)
    p_active  = max(0.82, 0.88 - churn_add)
    p_inactive= 0.08 + churn_add / 2
    p_closed  = 1 - p_active - p_inactive
    roll      = rng.random()
    if roll < p_active:   return "Active"
    if roll < p_active + p_inactive: return "Inactive"
    return "Closed"


# ---------------------------------------------------------------------------
# Province → branch_id lookup
# ---------------------------------------------------------------------------

def _build_province_branch_map(branches_df: pd.DataFrame) -> dict:
    """Map province → list of branch_ids."""
    mapping = {}
    for _, row in branches_df.iterrows():
        mapping.setdefault(row["province"], []).append(row["branch_id"])
    return mapping


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_customers(
    branches_df: pd.DataFrame,
    n: int = CUSTOMER_TARGET,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate n synthetic customer records aligned to branch geography,
    occupation, income, and demographic distributions from the docs.
    """
    rng = np.random.default_rng(seed)
    province_branch_map = _build_province_branch_map(branches_df)

    provinces = list(PROVINCE_WEIGHTS.keys())
    prov_w    = np.array(list(PROVINCE_WEIGHTS.values()), dtype=float)
    prov_w   /= prov_w.sum()

    records = []
    for cid in range(1, n + 1):
        province   = provinces[rng.choice(len(provinces), p=prov_w)]
        # If province not in branch map fall back to Phnom Penh
        branch_ids = province_branch_map.get(province,
                     province_branch_map.get("Phnom Penh", [1]))
        branch_id  = int(rng.choice(branch_ids))

        gender     = _weighted_choice(rng, GENDER_DISTRIBUTION)
        occupation = _weighted_choice(rng, OCCUPATION_DISTRIBUTION)
        marital    = _weighted_choice(rng, MARITAL_STATUS_DISTRIBUTION)
        age        = _age_from_distribution(rng)
        birth_date = date(2025 - age, int(rng.integers(1, 13)),
                          int(rng.integers(1, 29)))
        income     = _income_for_occupation(rng, occupation)
        join_dt    = _join_date(rng)
        status     = _customer_status(rng, join_dt)

        records.append({
            "customer_id":     cid,
            "branch_id":       branch_id,
            "gender":          gender,
            "birth_date":      birth_date,
            "age":             age,
            "occupation":      occupation,
            "marital_status":  marital,
            "province":        province,
            "monthly_income":  income,
            "join_date":       join_dt,
            "customer_status": status,
        })

    df = pd.DataFrame(records)
    print(f"[customers] Generated {len(df):,} customers")
    print(df["occupation"].value_counts(normalize=True).round(3).to_string())
    return df


def save_customers(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "customers.csv")
    df.to_csv(path, index=False)
    print(f"[customers] Saved → {path}")
    return path


if __name__ == "__main__":
    from generate_branches import generate_branches
    branches_df = generate_branches()
    df = generate_customers(branches_df)
    save_customers(df)
