# =============================================================================
# generate_accounts.py
# Phase 3 — Assign Banking Products to Customers
# Reference: 05_Simulation_Logic.md §6 | 06_Data_Generation_Roadmap.md §6
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    ACCOUNT_PRODUCTS, SIM_START_DATE, RANDOM_SEED, DATA_RAW,
)

# ---------------------------------------------------------------------------
# Account open date logic
# ---------------------------------------------------------------------------

def _account_open_date(rng, customer_join_date: date) -> date:
    """Account opens on or shortly after customer joins (0–30 days)."""
    offset = int(rng.integers(0, 31))
    return customer_join_date + timedelta(days=offset)


def _initial_balance(rng, account_type: str, monthly_income: float) -> float:
    """
    Seed balance based on account type and income.
    Savings: 0.5–3× income | FD: 3–12× | Payroll: 0.5–1.5× | Business: 2–10×
    """
    multipliers = {
        "Savings":       (0.5,  3.0),
        "Fixed Deposit": (3.0, 12.0),
        "Payroll":       (0.5,  1.5),
        "Business":      (2.0, 10.0),
    }
    lo, hi = multipliers.get(account_type, (0.5, 2.0))
    return round(float(rng.uniform(lo, hi) * monthly_income), 2)


def _account_status(rng, open_date: date) -> str:
    """
    Active ~88 %, Dormant ~8 %, Closed ~4 %.
    Older accounts have slightly higher dormant/closed probability.
    """
    age_years = (date(2025, 12, 31) - open_date).days / 365
    p_active  = max(0.80, 0.88 - age_years * 0.005)
    p_dormant = 0.08 + age_years * 0.003
    p_closed  = 1 - p_active - p_dormant
    roll = rng.random()
    if roll < p_active:              return "Active"
    if roll < p_active + p_dormant:  return "Dormant"
    return "Closed"


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_accounts(
    customers_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    For each customer, create accounts based on occupation and income rules:
      - Savings:       ~95 % of all customers
      - Fixed Deposit: high-income (≥$800) or age ≥35, prob 30 %
      - Payroll:       GOV/Private/Factory, prob 70 %
      - Business:      SME Owners, prob 80 %
    """
    rng = np.random.default_rng(seed)
    records = []
    account_id = 1

    for _, cust in customers_df.iterrows():
        occupation   = cust["occupation"]
        income       = cust["monthly_income"]
        age          = cust["age"]
        join_date    = pd.to_datetime(cust["join_date"]).date()
        cust_id      = int(cust["customer_id"])
        branch_id    = int(cust["branch_id"])

        # ----- Savings  ------------------------------------------------
        if rng.random() < 0.95:
            open_dt = _account_open_date(rng, join_date)
            records.append({
                "account_id":      account_id,
                "customer_id":     cust_id,
                "branch_id":       branch_id,
                "account_type":    "Savings",
                "open_date":       open_dt,
                "current_balance": _initial_balance(rng, "Savings", income),
                "account_status":  _account_status(rng, open_dt),
            })
            account_id += 1

        # ----- Fixed Deposit  ------------------------------------------
        eligible_fd = (income >= 800 or age >= 35)
        if eligible_fd and rng.random() < 0.30:
            open_dt = _account_open_date(rng, join_date)
            records.append({
                "account_id":      account_id,
                "customer_id":     cust_id,
                "branch_id":       branch_id,
                "account_type":    "Fixed Deposit",
                "open_date":       open_dt,
                "current_balance": _initial_balance(rng, "Fixed Deposit", income),
                "account_status":  _account_status(rng, open_dt),
            })
            account_id += 1

        # ----- Payroll  ------------------------------------------------
        if occupation in ["Government Officer", "Private Employee", "Factory Worker"]:
            if rng.random() < 0.70:
                open_dt = _account_open_date(rng, join_date)
                records.append({
                    "account_id":      account_id,
                    "customer_id":     cust_id,
                    "branch_id":       branch_id,
                    "account_type":    "Payroll",
                    "open_date":       open_dt,
                    "current_balance": _initial_balance(rng, "Payroll", income),
                    "account_status":  _account_status(rng, open_dt),
                })
                account_id += 1

        # ----- Business  -----------------------------------------------
        if occupation == "SME Owner" and rng.random() < 0.80:
            open_dt = _account_open_date(rng, join_date)
            records.append({
                "account_id":      account_id,
                "customer_id":     cust_id,
                "branch_id":       branch_id,
                "account_type":    "Business",
                "open_date":       open_dt,
                "current_balance": _initial_balance(rng, "Business", income),
                "account_status":  _account_status(rng, open_dt),
            })
            account_id += 1

    df = pd.DataFrame(records)
    print(f"[accounts] Generated {len(df):,} accounts")
    print(df["account_type"].value_counts().to_string())
    return df


def save_accounts(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "accounts.csv")
    df.to_csv(path, index=False)
    print(f"[accounts] Saved → {path}")
    return path


if __name__ == "__main__":
    from generate_branches  import generate_branches
    from generate_customers import generate_customers
    branches  = generate_branches()
    customers = generate_customers(branches)
    df        = generate_accounts(customers)
    save_accounts(df)
