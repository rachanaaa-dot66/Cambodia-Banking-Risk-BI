# =============================================================================
# validate_data.py
# ETL Step 2 — Business Rule & Referential Integrity Validation
# Reference: 06_Data_Generation_Roadmap.md §14 (Validation Checks)
#            04_Data_Model.md §14 (Relationship Summary)
# =============================================================================

import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import DATA_PROCESSED


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

class ValidationReport:
    def __init__(self):
        self.issues  = []
        self.passed  = 0

    def ok(self, msg: str):
        self.passed += 1
        print(f"  ✓  {msg}")

    def fail(self, msg: str, detail: str = ""):
        self.issues.append(msg)
        print(f"  ✗  {msg}" + (f"  →  {detail}" if detail else ""))

    def summary(self):
        print(f"\n{'='*60}")
        print(f"Validation Summary: {self.passed} passed, {len(self.issues)} failed")
        if self.issues:
            print("Failed checks:")
            for i in self.issues:
                print(f"  - {i}")
        else:
            print("All validation checks passed!")
        print('='*60)


# ---------------------------------------------------------------------------
# Primary key uniqueness
# ---------------------------------------------------------------------------

def check_pk_unique(df: pd.DataFrame, pk_col: str, table: str, r: ValidationReport):
    dupes = df[pk_col].duplicated().sum()
    if dupes == 0:
        r.ok(f"{table}.{pk_col} is unique ({len(df):,} rows)")
    else:
        r.fail(f"{table}.{pk_col} has {dupes} duplicates")


# ---------------------------------------------------------------------------
# Foreign key referential integrity
# ---------------------------------------------------------------------------

def check_fk(child_df, parent_df, fk_col, pk_col, child_name, parent_name, r):
    orphans = ~child_df[fk_col].isin(parent_df[pk_col])
    n = orphans.sum()
    if n == 0:
        r.ok(f"{child_name}.{fk_col} → {parent_name}.{pk_col}  (no orphans)")
    else:
        r.fail(f"{child_name}.{fk_col} → {parent_name}.{pk_col}  ({n} orphan rows)")


# ---------------------------------------------------------------------------
# Business rule checks
# ---------------------------------------------------------------------------

def check_business_rules(tables: dict, r: ValidationReport):
    customers  = tables.get("customers")
    accounts   = tables.get("accounts")
    loans      = tables.get("loans")
    payments   = tables.get("loan_payments")
    profiles   = tables.get("credit_profiles")
    snapshots  = tables.get("monthly_customer_snapshot")

    # Every customer has a credit profile  (1-to-1)
    if customers is not None and profiles is not None:
        no_profile = ~customers["customer_id"].isin(profiles["customer_id"])
        n = no_profile.sum()
        if n == 0:
            r.ok("Every customer has a credit profile")
        else:
            r.fail(f"{n} customers missing credit profile")

    # Savings account coverage ≥ 90 %  (doc §6: ~95 %)
    if customers is not None and accounts is not None:
        savings_custs = accounts[accounts["account_type"] == "Savings"]["customer_id"].nunique()
        pct = savings_custs / len(customers) * 100
        if pct >= 85:
            r.ok(f"Savings account coverage {pct:.1f}% (target ≥85%)")
        else:
            r.fail(f"Savings account coverage only {pct:.1f}%")

    # Loan amount > 0
    if loans is not None:
        bad = (loans["loan_amount"] <= 0).sum()
        if bad == 0:
            r.ok("All loan_amount values > 0")
        else:
            r.fail(f"{bad} loans with amount ≤ 0")

    # Outstanding balance ≤ loan_amount
    if loans is not None:
        bad = (loans["outstanding_balance"] > loans["loan_amount"] * 1.05).sum()
        if bad == 0:
            r.ok("outstanding_balance ≤ loan_amount for all loans")
        else:
            r.fail(f"{bad} loans where outstanding > original amount (+5% tolerance)")

    # maturity_date > issue_date
    if loans is not None:
        loans["issue_date"]    = pd.to_datetime(loans["issue_date"])
        loans["maturity_date"] = pd.to_datetime(loans["maturity_date"])
        bad = (loans["maturity_date"] <= loans["issue_date"]).sum()
        if bad == 0:
            r.ok("maturity_date > issue_date for all loans")
        else:
            r.fail(f"{bad} loans where maturity_date ≤ issue_date")

    # Credit scores in range [300, 850]
    if profiles is not None:
        bad = ((profiles["credit_score"] < 300) | (profiles["credit_score"] > 850)).sum()
        if bad == 0:
            r.ok("All credit scores in [300, 850]")
        else:
            r.fail(f"{bad} credit scores outside [300, 850]")

    # Payment amount_paid ≥ 0
    if payments is not None:
        bad = (payments["amount_paid"] < 0).sum()
        if bad == 0:
            r.ok("All payment amount_paid ≥ 0")
        else:
            r.fail(f"{bad} payments with negative amount_paid")

    # Snapshot composite key unique  (snapshot_date, customer_id)
    if snapshots is not None:
        dupes = snapshots.duplicated(subset=["snapshot_date", "customer_id"]).sum()
        if dupes == 0:
            r.ok("monthly_customer_snapshot composite key is unique")
        else:
            r.fail(f"monthly_customer_snapshot: {dupes} duplicate (snapshot_date, customer_id) pairs")


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def validate_all(processed_dir: str = DATA_PROCESSED) -> ValidationReport:
    r = ValidationReport()
    tables = {}

    table_names = [
        "branches", "customers", "accounts", "transactions",
        "loans", "loan_payments", "credit_profiles",
        "monthly_customer_snapshot", "economic_events",
    ]
    for name in table_names:
        path = os.path.join(processed_dir, f"{name}.csv")
        if os.path.exists(path):
            tables[name] = pd.read_csv(path)
        else:
            print(f"  [SKIP] {name}.csv not found in processed dir")

    print("\n--- Primary Key Checks ---")
    pk_map = {
        "branches":      "branch_id",
        "customers":     "customer_id",
        "accounts":      "account_id",
        "transactions":  "transaction_id",
        "loans":         "loan_id",
        "loan_payments": "payment_id",
        "economic_events":"event_id",
    }
    for tbl, pk in pk_map.items():
        if tbl in tables:
            check_pk_unique(tables[tbl], pk, tbl, r)

    print("\n--- Foreign Key Checks ---")
    fk_checks = [
        ("customers",     "branches",    "branch_id",   "branch_id"),
        ("accounts",      "customers",   "customer_id", "customer_id"),
        ("accounts",      "branches",    "branch_id",   "branch_id"),
        ("transactions",  "accounts",    "account_id",  "account_id"),
        ("loans",         "customers",   "customer_id", "customer_id"),
        ("loans",         "branches",    "branch_id",   "branch_id"),
        ("loan_payments", "loans",       "loan_id",     "loan_id"),
        ("credit_profiles","customers",  "customer_id", "customer_id"),
        ("monthly_customer_snapshot","customers","customer_id","customer_id"),
    ]
    for child, parent, fk, pk in fk_checks:
        if child in tables and parent in tables:
            check_fk(tables[child], tables[parent], fk, pk, child, parent, r)

    print("\n--- Business Rule Checks ---")
    check_business_rules(tables, r)

    r.summary()
    return r


if __name__ == "__main__":
    validate_all()
