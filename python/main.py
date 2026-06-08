#!/usr/bin/env python
# =============================================================================
# main.py
# Cambodia Banking Risk & Business Intelligence Platform
# Master Orchestrator — runs all 13 generation/simulation phases
# Reference: 06_Data_Generation_Roadmap.md §2 (Generation Strategy)
#
# Usage:
#   python main.py                        # full run
#   python main.py --phases 1 2 3         # specific phases only
#   python main.py --skip-load            # skip PostgreSQL load
#   python main.py --no-snapshots         # skip 3M+ snapshot table (faster dev)
# =============================================================================

import argparse
import os
import sys
import time

# Make sure relative imports work from any working directory
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from config.simulation_config import DATA_RAW, DATA_PROCESSED, RANDOM_SEED

# ---------------------------------------------------------------------------
# Phase runners
# ---------------------------------------------------------------------------

def phase_1_branches():
    from generators.generate_branches import generate_branches, save_branches
    df = generate_branches(seed=RANDOM_SEED)
    save_branches(df, DATA_RAW)
    return df


def phase_2_customers(branches_df):
    from generators.generate_customers import generate_customers, save_customers
    df = generate_customers(branches_df, seed=RANDOM_SEED)
    save_customers(df, DATA_RAW)
    return df


def phase_3_accounts(customers_df):
    from generators.generate_accounts import generate_accounts, save_accounts
    df = generate_accounts(customers_df, seed=RANDOM_SEED)
    save_accounts(df, DATA_RAW)
    return df


def phase_4_credit_profiles(customers_df):
    from generators.generate_credit_profiles import (
        generate_credit_profiles, save_credit_profiles
    )
    df = generate_credit_profiles(customers_df, seed=RANDOM_SEED)
    save_credit_profiles(df, DATA_RAW)
    return df


def phase_5_loans(customers_df, credit_profiles_df):
    from generators.generate_loans import generate_loans, save_loans
    df = generate_loans(customers_df, credit_profiles_df, seed=RANDOM_SEED)
    save_loans(df, DATA_RAW)
    return df


def phase_6_transactions(customers_df, accounts_df):
    from simulators.transaction_simulator import simulate_transactions, save_transactions
    df = simulate_transactions(customers_df, accounts_df, seed=RANDOM_SEED)
    save_transactions(df, DATA_RAW)
    return df


def phase_7_payments(loans_df, customers_df, credit_profiles_df):
    from simulators.payment_simulator import simulate_payments, save_payments
    df = simulate_payments(loans_df, customers_df, credit_profiles_df, seed=RANDOM_SEED)
    save_payments(df, DATA_RAW)
    return df


def phase_8_credit_scores(customers_df, credit_profiles_df,
                           loan_payments_df, loans_df):
    from simulators.credit_score_simulator import simulate_credit_scores
    df = simulate_credit_scores(
        customers_df, credit_profiles_df,
        loan_payments_df, loans_df, seed=RANDOM_SEED
    )
    # Overwrite credit_profiles with updated scores
    import os
    path = os.path.join(DATA_RAW, "credit_profiles.csv")
    df.to_csv(path, index=False)
    print(f"[credit_profiles] Updated → {path}")
    return df


def phase_9_economic_events():
    from generators.generate_economic_events import (
        generate_economic_events, save_economic_events
    )
    df = generate_economic_events()
    save_economic_events(df, DATA_RAW)
    return df


def phase_10_snapshots(customers_df, accounts_df, loans_df,
                        credit_profiles_df, loan_payments_df):
    from simulators.monthly_snapshot_simulator import (
        simulate_monthly_snapshots, save_snapshots
    )
    df = simulate_monthly_snapshots(
        customers_df, accounts_df, loans_df,
        credit_profiles_df, loan_payments_df, seed=RANDOM_SEED
    )
    save_snapshots(df, DATA_RAW)
    return df


def phase_11_clean():
    from etl.clean_data import clean_all
    return clean_all(DATA_RAW, DATA_PROCESSED)


def phase_12_validate():
    from etl.validate_data import validate_all
    return validate_all(DATA_PROCESSED)


def phase_13_load():
    from etl.load_postgres import get_engine, load_all, apply_constraints
    engine = get_engine()
    load_all(engine, DATA_PROCESSED)
    apply_constraints(engine)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _banner(phase: int, name: str):
    print(f"\n{'='*60}")
    print(f"  PHASE {phase}: {name}")
    print(f"{'='*60}")


def _elapsed(t0: float) -> str:
    s = time.time() - t0
    return f"{s/60:.1f} min" if s >= 60 else f"{s:.1f} s"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _s(key, state, fallback):
    """Safe state getter that avoids DataFrame bool ambiguity."""
    return state[key] if key in state else fallback

def main():
    parser = argparse.ArgumentParser(
        description="Cambodia Banking Risk & BI Platform — Data Generation Engine"
    )
    parser.add_argument(
        "--phases", nargs="+", type=int,
        help="Run only specified phases (e.g. --phases 1 2 3). Default: all"
    )
    parser.add_argument(
        "--skip-load", action="store_true",
        help="Skip Phase 13 PostgreSQL load"
    )
    parser.add_argument(
        "--no-snapshots", action="store_true",
        help="Skip Phase 10 monthly snapshots (saves time during development)"
    )
    args = parser.parse_args()

    run_all   = args.phases is None
    run_phase = lambda n: run_all or n in args.phases

    t_total = time.time()
    state   = {}

    # ── Phase 1: Branches ──────────────────────────────────────────────────
    if run_phase(1):
        _banner(1, "Generate Branches")
        t = time.time()
        state["branches"] = phase_1_branches()
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 2: Customers ─────────────────────────────────────────────────
    if run_phase(2):
        _banner(2, "Generate Customers (50,000)")
        t = time.time()
        branches = state["branches"] if "branches" in state else _load_csv("branches")
        state["customers"] = phase_2_customers(branches)
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 3: Accounts ──────────────────────────────────────────────────
    if run_phase(3):
        _banner(3, "Generate Accounts")
        t = time.time()
        customers = state["customers"] if "customers" in state else _load_csv("customers")
        state["accounts"] = phase_3_accounts(customers)
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 4: Credit Profiles ───────────────────────────────────────────
    if run_phase(4):
        _banner(4, "Generate Credit Profiles")
        t = time.time()
        customers = state["customers"] if "customers" in state else _load_csv("customers")
        state["credit_profiles"] = phase_4_credit_profiles(customers)
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 5: Loans ─────────────────────────────────────────────────────
    if run_phase(5):
        _banner(5, "Generate Loan Portfolio")
        t = time.time()
        customers       = _s("customers", state, _load_csv("customers"))
        credit_profiles = state["credit_profiles"] if "credit_profiles" in state else _load_csv("credit_profiles")
        state["loans"] = phase_5_loans(customers, credit_profiles)
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 6: Transactions ──────────────────────────────────────────────
    if run_phase(6):
        _banner(6, "Simulate Monthly Transactions (60 months)")
        t = time.time()
        customers = state["customers"] if "customers" in state else _load_csv("customers")
        accounts  = _s("accounts", state, _load_csv("accounts"))
        state["transactions"] = phase_6_transactions(customers, accounts)
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 7: Loan Payments ─────────────────────────────────────────────
    if run_phase(7):
        _banner(7, "Simulate Loan Payments (60 months)")
        t = time.time()
        loans           = _s("loans", state, _load_csv("loans"))
        customers       = _s("customers", state, _load_csv("customers"))
        credit_profiles = _s("credit_profiles", state, _load_csv("credit_profiles"))
        state["loan_payments"] = phase_7_payments(loans, customers, credit_profiles)
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 8: Credit Score Migration ────────────────────────────────────
    if run_phase(8):
        _banner(8, "Update Credit Scores (monthly migration)")
        t = time.time()
        customers       = _s("customers", state, _load_csv("customers"))
        credit_profiles = _s("credit_profiles", state, _load_csv("credit_profiles"))
        loan_payments   = _s("loan_payments", state, _load_csv("loan_payments"))
        loans           = _s("loans", state, _load_csv("loans"))
        state["credit_profiles"] = phase_8_credit_scores(
            customers, credit_profiles, loan_payments, loans
        )
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 9: Economic Events ───────────────────────────────────────────
    if run_phase(9):
        _banner(9, "Generate Economic Events")
        t = time.time()
        state["economic_events"] = phase_9_economic_events()
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 10: Monthly Snapshots ────────────────────────────────────────
    if run_phase(10) and not args.no_snapshots:
        _banner(10, "Generate Monthly Customer Snapshots (3M+ rows)")
        t = time.time()
        customers       = _s("customers", state, _load_csv("customers"))
        accounts        = _s("accounts", state, _load_csv("accounts"))
        loans           = _s("loans", state, _load_csv("loans"))
        credit_profiles = _s("credit_profiles", state, _load_csv("credit_profiles"))
        loan_payments   = _s("loan_payments", state, _load_csv("loan_payments"))
        state["monthly_customer_snapshot"] = phase_10_snapshots(
            customers, accounts, loans, credit_profiles, loan_payments
        )
        print(f"  Done ({_elapsed(t)})")
    elif args.no_snapshots and run_phase(10):
        print("\n[Phase 10] Skipped (--no-snapshots flag)")

    # ── Phase 11: Clean ────────────────────────────────────────────────────
    if run_phase(11):
        _banner(11, "Clean Data (ETL Step 1)")
        t = time.time()
        phase_11_clean()
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 12: Validate ─────────────────────────────────────────────────
    if run_phase(12):
        _banner(12, "Validate Data (ETL Step 2)")
        t = time.time()
        phase_12_validate()
        print(f"  Done ({_elapsed(t)})")

    # ── Phase 13: Load PostgreSQL ──────────────────────────────────────────
    if run_phase(13) and not args.skip_load:
        _banner(13, "Load into PostgreSQL (ETL Step 3)")
        t = time.time()
        try:
            phase_13_load()
            print(f"  Done ({_elapsed(t)})")
        except Exception as e:
            print(f"  [ERROR] PostgreSQL load failed: {e}")
            print("  Tip: Set PG_HOST/PG_PORT/PG_DBNAME/PG_USER/PG_PASSWORD env vars")
    elif args.skip_load and run_phase(13):
        print("\n[Phase 13] Skipped (--skip-load flag)")

    print(f"\n{'='*60}")
    print(f"  ALL PHASES COMPLETE  —  total time: {_elapsed(t_total)}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Helper: load CSV from DATA_RAW into DataFrame
# ---------------------------------------------------------------------------

def _load_csv(table_name: str):
    import pandas as pd
    path = os.path.join(DATA_RAW, f"{table_name}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required input not found: {path}\n"
            f"Run the earlier phases first."
        )
    print(f"  [load] {path}")
    return pd.read_csv(path)


if __name__ == "__main__":
    main()
