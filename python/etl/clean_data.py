# =============================================================================
# clean_data.py
# ETL Step 1 — Data Cleaning & Standardisation
# Reference: 06_Data_Generation_Roadmap.md §14 (Validation Checks)
# =============================================================================

import pandas as pd
import numpy as np
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import DATA_RAW, DATA_PROCESSED


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def _drop_exact_duplicates(df: pd.DataFrame, label: str) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    if dropped:
        print(f"  [{label}] Dropped {dropped} exact duplicate rows")
    return df


def _report_nulls(df: pd.DataFrame, label: str):
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        print(f"  [{label}] Null counts:\n{nulls.to_string()}")


# ---------------------------------------------------------------------------
# Per-table cleaners
# ---------------------------------------------------------------------------

def clean_branches(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "branches")
    df["branch_open_date"] = pd.to_datetime(df["branch_open_date"]).dt.date
    df["branch_type"]      = df["branch_type"].str.strip().str.title()
    _report_nulls(df, "branches")
    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "customers")
    df["birth_date"] = pd.to_datetime(df["birth_date"]).dt.date
    df["join_date"]  = pd.to_datetime(df["join_date"]).dt.date
    df["monthly_income"] = df["monthly_income"].clip(lower=0)
    df["age"]            = df["age"].clip(lower=18, upper=80)
    df["gender"]         = df["gender"].str.strip().str.title()
    df["customer_status"]= df["customer_status"].str.strip().str.title()
    df["occupation"]     = df["occupation"].str.strip()
    _report_nulls(df, "customers")
    return df


def clean_accounts(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "accounts")
    df["open_date"]       = pd.to_datetime(df["open_date"]).dt.date
    df["current_balance"] = df["current_balance"].clip(lower=0)
    df["account_type"]    = df["account_type"].str.strip()
    df["account_status"]  = df["account_status"].str.strip().str.title()
    _report_nulls(df, "accounts")
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "transactions")
    df["transaction_date"]   = pd.to_datetime(df["transaction_date"]).dt.date
    df["transaction_amount"] = df["transaction_amount"].clip(lower=0.01)
    df["transaction_type"]   = df["transaction_type"].str.strip()
    _report_nulls(df, "transactions")
    return df


def clean_loans(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "loans")
    df["issue_date"]    = pd.to_datetime(df["issue_date"]).dt.date
    df["maturity_date"] = pd.to_datetime(df["maturity_date"]).dt.date
    df["loan_amount"]          = df["loan_amount"].clip(lower=100)
    df["outstanding_balance"]  = df["outstanding_balance"].clip(lower=0)
    df["interest_rate"]        = df["interest_rate"].clip(lower=0, upper=40)
    df["term_months"]          = df["term_months"].clip(lower=3)
    df["loan_type"]            = df["loan_type"].str.strip()
    df["loan_status"]          = df["loan_status"].str.strip()
    _report_nulls(df, "loans")
    return df


def clean_loan_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "loan_payments")
    df["payment_date"] = pd.to_datetime(df["payment_date"]).dt.date
    df["amount_due"]   = df["amount_due"].clip(lower=0)
    df["amount_paid"]  = df["amount_paid"].clip(lower=0)
    df["days_past_due"]= df["days_past_due"].clip(lower=0)
    _report_nulls(df, "loan_payments")
    return df


def clean_credit_profiles(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "credit_profiles")
    df["credit_score"]            = df["credit_score"].clip(lower=300, upper=850)
    df["debt_to_income_ratio"]    = df["debt_to_income_ratio"].clip(lower=0, upper=1)
    df["previous_delinquency_count"] = df["previous_delinquency_count"].clip(lower=0)
    df["risk_category"]           = df["risk_category"].str.strip()
    _report_nulls(df, "credit_profiles")
    return df


def clean_snapshots(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "monthly_customer_snapshot")
    df["snapshot_date"]      = pd.to_datetime(df["snapshot_date"]).dt.date
    df["account_balance"]    = df["account_balance"].clip(lower=0)
    df["total_loan_balance"] = df["total_loan_balance"].clip(lower=0)
    df["credit_score"]       = df["credit_score"].clip(lower=300, upper=850)
    _report_nulls(df, "monthly_customer_snapshot")
    return df


def clean_economic_events(df: pd.DataFrame) -> pd.DataFrame:
    df = _drop_exact_duplicates(df, "economic_events")
    df["start_date"] = pd.to_datetime(df["start_date"]).dt.date
    df["end_date"]   = pd.to_datetime(df["end_date"]).dt.date
    _report_nulls(df, "economic_events")
    return df


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

TABLE_CLEANERS = {
    "branches":                  clean_branches,
    "customers":                 clean_customers,
    "accounts":                  clean_accounts,
    "transactions":              clean_transactions,
    "loans":                     clean_loans,
    "loan_payments":             clean_loan_payments,
    "credit_profiles":           clean_credit_profiles,
    "monthly_customer_snapshot": clean_snapshots,
    "economic_events":           clean_economic_events,
}


def clean_all(raw_dir: str = DATA_RAW, processed_dir: str = DATA_PROCESSED) -> dict:
    os.makedirs(processed_dir, exist_ok=True)
    cleaned = {}
    for table_name, cleaner_fn in TABLE_CLEANERS.items():
        src = os.path.join(raw_dir, f"{table_name}.csv")
        if not os.path.exists(src):
            print(f"  [SKIP] {src} not found")
            continue
        print(f"Cleaning {table_name}…")
        df = pd.read_csv(src)
        df = cleaner_fn(df)
        dst = os.path.join(processed_dir, f"{table_name}.csv")
        df.to_csv(dst, index=False)
        print(f"  → {dst}  ({len(df):,} rows)")
        cleaned[table_name] = df
    return cleaned


if __name__ == "__main__":
    clean_all()
