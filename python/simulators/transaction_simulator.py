# =============================================================================
# transaction_simulator.py  — OPTIMIZED for 5k customers / 24 months
# Phase 6 — Simulate Monthly Customer Transactions (2024-2025)
# Reference: 05_Simulation_Logic.md §11
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    SIM_START_DATE, SIM_END_DATE, TXN_FREQ, TXN_TYPE_WEIGHTS,
    ECONOMIC_EVENTS, RANDOM_SEED, DATA_RAW,
)


def _build_event_index() -> dict:
    idx = {}
    for ev in ECONOMIC_EVENTS:
        cur = date(ev["start_date"].year, ev["start_date"].month, 1)
        while cur <= ev["end_date"]:
            idx.setdefault((cur.year, cur.month), []).append(ev)
            m = cur.month % 12 + 1
            y = cur.year + (1 if cur.month == 12 else 0)
            cur = date(y, m, 1)
    return idx

EVENT_INDEX = _build_event_index()


def _months_in_range(start: date, end: date):
    cur = date(start.year, start.month, 1)
    while cur <= end:
        yield cur
        m = cur.month % 12 + 1
        y = cur.year + (1 if cur.month == 12 else 0)
        cur = date(y, m, 1)


def simulate_transactions(
    customers_df: pd.DataFrame,
    accounts_df:  pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Build customer info lookup
    cust_lookup = customers_df.set_index("customer_id")[
        ["occupation", "monthly_income", "province", "customer_status"]
    ].to_dict("index")

    # Only active/dormant accounts
    active_accs = accounts_df[accounts_df["account_status"] != "Closed"].copy()
    active_accs["open_date"] = pd.to_datetime(active_accs["open_date"]).dt.date

    txn_types   = list(TXN_TYPE_WEIGHTS.keys())
    txn_weights = np.array(list(TXN_TYPE_WEIGHTS.values()), dtype=float)
    txn_weights /= txn_weights.sum()

    months = list(_months_in_range(SIM_START_DATE, SIM_END_DATE))
    print(f"[transactions] {len(months)} months × {len(active_accs):,} accounts")

    all_records = []
    txn_id = 1

    for month_start in months:
        active_events = EVENT_INDEX.get((month_start.year, month_start.month), [])

        for row in active_accs.itertuples(index=False):
            if row.open_date > month_start:
                continue

            cust   = cust_lookup.get(row.customer_id, {})
            occ    = cust.get("occupation", "Private Employee")
            income = float(cust.get("monthly_income", 400))
            prov   = cust.get("province", "Phnom Penh")
            status = cust.get("customer_status", "Active")

            act_mult   = 1.0 if status == "Active" else 0.15
            event_mult = 1.0
            for ev in active_events:
                if prov in [p.strip() for p in ev["affected_province"].split(",")]:
                    if occ == ev["affected_sector"]:
                        event_mult *= max(0.4, 1 + ev["income_shock"])

            lo, hi = TXN_FREQ.get(occ, (3, 8))
            n = int(rng.integers(
                max(1, int(lo * act_mult * event_mult)),
                max(2, int(hi * act_mult * event_mult) + 1)
            ))

            for _ in range(n):
                day_off  = int(rng.integers(0, 28))
                txn_date = month_start + timedelta(days=day_off)
                txn_type = txn_types[rng.choice(len(txn_types), p=txn_weights)]
                lo_m, hi_m = {
                    "Deposit":         (0.05, 0.60),
                    "Withdrawal":      (0.05, 0.50),
                    "Transfer":        (0.03, 0.40),
                    "Loan Payment":    (0.08, 0.25),
                    "Interest Credit": (0.002, 0.02),
                }.get(txn_type, (0.05, 0.30))
                amount = round(float(rng.uniform(lo_m, hi_m) * max(income, 50)), 2)

                all_records.append((txn_id, row.account_id, txn_date, txn_type, amount))
                txn_id += 1

    df = pd.DataFrame(all_records,
                      columns=["transaction_id","account_id","transaction_date",
                                "transaction_type","transaction_amount"])
    print(f"[transactions] Generated {len(df):,} rows")
    return df


def save_transactions(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "transactions.csv")
    df.to_csv(path, index=False)
    print(f"[transactions] Saved → {path}")
    return path
