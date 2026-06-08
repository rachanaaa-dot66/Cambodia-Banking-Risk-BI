# =============================================================================
# generate_loans.py
# Phase 5 — Generate Initial Loan Portfolio
# Reference: 05_Simulation_Logic.md §7-§8 | 06_Data_Generation_Roadmap.md §8
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    LOAN_ELIGIBILITY, LOAN_TYPES, LOAN_INCOME_MULTIPLIERS,
    SIM_START_DATE, RANDOM_SEED, DATA_RAW,
)

# Attempt import; provide a fallback if dateutil not installed
try:
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


def _add_months(d: date, n: int) -> date:
    if HAS_DATEUTIL:
        return d + relativedelta(months=n)
    # Simple fallback
    month = d.month - 1 + n
    year  = d.year + month // 12
    month = month % 12 + 1
    day   = min(d.day, [31,28,31,30,31,30,31,31,30,31,30,31][month-1])
    return date(year, month, day)


# ---------------------------------------------------------------------------
# Loan type eligibility  (doc §7)
# ---------------------------------------------------------------------------

def _eligible_loan_types(occupation: str, age: int, income: float,
                          credit_score: int, dti: float) -> list:
    """Return list of loan types this customer qualifies for."""
    eligible = []

    # Basic eligibility gate  (doc §7 intro)
    if (age < LOAN_ELIGIBILITY["min_age"] or
            credit_score < LOAN_ELIGIBILITY["min_credit_score"] or
            dti > LOAN_ELIGIBILITY["max_dti"]):
        return []

    cfg = LOAN_TYPES

    # Personal Loan
    if occupation in cfg["Personal Loan"]["eligible_occupations"]:
        eligible.append("Personal Loan")

    # Agriculture Loan
    if occupation in cfg["Agriculture Loan"]["eligible_occupations"]:
        eligible.append("Agriculture Loan")

    # SME Loan
    if occupation in cfg["SME Loan"]["eligible_occupations"]:
        eligible.append("SME Loan")

    # Housing Loan  (age ≥30, income ≥$400)
    if age >= cfg["Housing Loan"]["min_age"] and income >= cfg["Housing Loan"]["min_income"]:
        eligible.append("Housing Loan")

    # Vehicle Loan  (income in range)
    lo, hi = cfg["Vehicle Loan"]["income_range"]
    if lo <= income <= hi:
        eligible.append("Vehicle Loan")

    return eligible


def _loan_amount(rng, loan_type: str, monthly_income: float) -> float:
    """
    Loan amount = income × multiplier drawn from Loan-to-Income range (doc §8).
    """
    lo_mult, hi_mult = LOAN_INCOME_MULTIPLIERS[loan_type]
    annual_income    = monthly_income * 12
    multiplier       = rng.uniform(lo_mult, hi_mult)
    raw              = annual_income * multiplier / 12  # back to monthly base
    # Cap/floor for realism
    amount = rng.uniform(monthly_income * lo_mult, monthly_income * hi_mult)
    # Round to nearest 100
    return round(float(amount / 100) * 100, 2)


def _loan_issue_date(rng, customer_join_date: date) -> date:
    """Loan is issued between join date and mid-2025."""
    earliest  = customer_join_date + timedelta(days=30)
    latest    = date(2025, 6, 30)
    if earliest >= latest:
        return earliest
    span  = (latest - earliest).days
    offset= int(rng.integers(0, span))
    return earliest + timedelta(days=offset)


def _outstanding_balance(rng, loan_amount: float, issue_date: date,
                          term_months: int) -> float:
    """
    Approximate remaining balance based on elapsed months
    (straight-line for simplicity; close enough for synthetic data).
    """
    elapsed = max(0, (date(2025, 12, 31) - issue_date).days // 30)
    fraction_remaining = max(0.0, 1 - elapsed / term_months)
    noise = rng.uniform(0.95, 1.05)
    return round(loan_amount * fraction_remaining * noise, 2)


def _loan_status(rng, outstanding: float, loan_amount: float,
                 credit_score: int) -> str:
    """
    Assign loan status consistent with credit score and repayment progress.
    """
    paid_off = (outstanding <= 0)
    if paid_off:
        return "Closed"

    roll = rng.random()
    if credit_score >= 700:
        thresholds = [0.88, 0.05, 0.04, 0.03]   # Current, PastDue, NP, Default
    elif credit_score >= 600:
        thresholds = [0.78, 0.12, 0.06, 0.04]
    elif credit_score >= 500:
        thresholds = [0.65, 0.18, 0.10, 0.07]
    else:
        thresholds = [0.50, 0.22, 0.15, 0.13]

    if roll < thresholds[0]:                            return "Current"
    if roll < thresholds[0] + thresholds[1]:            return "Past Due"
    if roll < thresholds[0] + thresholds[1] + thresholds[2]: return "Non-Performing"
    return "Defaulted"


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_loans(
    customers_df: pd.DataFrame,
    credit_profiles_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate loan records for ~60 % of eligible customers (doc §7 intro).
    Each borrower may have one primary loan; high-income SME Owners may have two.
    """
    rng = np.random.default_rng(seed)

    # Merge credit profile into customers for easy lookup
    merged = customers_df.merge(credit_profiles_df, on="customer_id")

    records    = []
    loan_id    = 1
    loan_types_cfg = LOAN_TYPES

    for _, row in merged.iterrows():
        occupation  = row["occupation"]
        age         = int(row["age"])
        income      = float(row["monthly_income"])
        credit_score= int(row["credit_score"])
        dti         = float(row["debt_to_income_ratio"])
        cust_id     = int(row["customer_id"])
        branch_id   = int(row["branch_id"])
        join_date   = pd.to_datetime(row["join_date"]).date()

        eligible = _eligible_loan_types(occupation, age, income, credit_score, dti)
        if not eligible:
            continue

        # Penetration roll — ~60 % of eligible customers take a loan
        if rng.random() > LOAN_ELIGIBILITY["loan_penetration"]:
            continue

        # Pick primary loan type (weighted toward occupation-matched type)
        chosen_type = rng.choice(eligible)

        # Rates and terms from config
        rate_lo, rate_hi   = loan_types_cfg[chosen_type]["rate_range"]
        term_lo, term_hi   = loan_types_cfg[chosen_type]["term_range"]
        interest_rate      = round(float(rng.uniform(rate_lo, rate_hi)), 2)
        term_months        = int(rng.integers(term_lo // 12, term_hi // 12 + 1) * 12)

        issue_date         = _loan_issue_date(rng, join_date)
        maturity_date      = _add_months(issue_date, term_months)
        loan_amount        = _loan_amount(rng, chosen_type, income)
        outstanding        = _outstanding_balance(rng, loan_amount, issue_date, term_months)
        status             = _loan_status(rng, outstanding, loan_amount, credit_score)

        records.append({
            "loan_id":             loan_id,
            "customer_id":         cust_id,
            "branch_id":           branch_id,
            "loan_type":           chosen_type,
            "loan_amount":         loan_amount,
            "interest_rate":       interest_rate,
            "term_months":         term_months,
            "issue_date":          issue_date,
            "maturity_date":       maturity_date,
            "outstanding_balance": outstanding,
            "loan_status":         status,
        })
        loan_id += 1

        # SME Owners with high income may have a second loan (SME + Housing)
        if occupation == "SME Owner" and income >= 2000 and len(eligible) > 1 and rng.random() < 0.25:
            second_types = [t for t in eligible if t != chosen_type]
            if second_types:
                sec_type   = rng.choice(second_types)
                rate_lo2, rate_hi2 = loan_types_cfg[sec_type]["rate_range"]
                term_lo2, term_hi2 = loan_types_cfg[sec_type]["term_range"]
                ir2    = round(float(rng.uniform(rate_lo2, rate_hi2)), 2)
                term2  = int(rng.integers(term_lo2 // 12, term_hi2 // 12 + 1) * 12)
                iss2   = _loan_issue_date(rng, join_date)
                mat2   = _add_months(iss2, term2)
                amt2   = _loan_amount(rng, sec_type, income)
                out2   = _outstanding_balance(rng, amt2, iss2, term2)
                sts2   = _loan_status(rng, out2, amt2, credit_score)
                records.append({
                    "loan_id":             loan_id,
                    "customer_id":         cust_id,
                    "branch_id":           branch_id,
                    "loan_type":           sec_type,
                    "loan_amount":         amt2,
                    "interest_rate":       ir2,
                    "term_months":         term2,
                    "issue_date":          iss2,
                    "maturity_date":       mat2,
                    "outstanding_balance": out2,
                    "loan_status":         sts2,
                })
                loan_id += 1

    df = pd.DataFrame(records)
    print(f"[loans] Generated {len(df):,} loans")
    print(df["loan_type"].value_counts().to_string())
    print(df["loan_status"].value_counts().to_string())
    return df


def save_loans(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "loans.csv")
    df.to_csv(path, index=False)
    print(f"[loans] Saved → {path}")
    return path


if __name__ == "__main__":
    from generate_branches       import generate_branches
    from generate_customers      import generate_customers
    from generate_credit_profiles import generate_credit_profiles
    branches  = generate_branches()
    customers = generate_customers(branches)
    profiles  = generate_credit_profiles(customers)
    df        = generate_loans(customers, profiles)
    save_loans(df)
