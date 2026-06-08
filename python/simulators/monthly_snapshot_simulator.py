# =============================================================================
# monthly_snapshot_simulator.py  — OPTIMIZED (24 months / 5k customers)
# Phase 10 — Generate monthly_customer_snapshot
# Reference: 05_Simulation_Logic.md §18
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    SIM_START_DATE, SIM_END_DATE,
    get_risk_category, SCORE_MIN, SCORE_MAX,
    ECONOMIC_EVENTS, SCORE_DELTA, RANDOM_SEED, DATA_RAW,
)


def _months_in_range(start: date, end: date):
    cur = date(start.year, start.month, 1)
    while cur <= end:
        yield cur
        m = cur.month % 12 + 1
        y = cur.year + (1 if cur.month == 12 else 0)
        cur = date(y, m, 1)


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


def simulate_monthly_snapshots(
    customers_df:       pd.DataFrame,
    accounts_df:        pd.DataFrame,
    loans_df:           pd.DataFrame,
    credit_profiles_df: pd.DataFrame,
    loan_payments_df:   pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # ── Pre-compute payment outcomes per (customer, year, month) ────────
    def classify(r) -> str:
        if r.days_past_due >= 30 or r.amount_paid < r.amount_due * 0.5:
            return "missed"
        if r.days_past_due > 0 or r.amount_paid < r.amount_due * 0.99:
            return "late"
        return "on_time"

    PRIORITY = {"on_time": 0, "late": 1, "missed": 2}
    pmts = loan_payments_df.copy()
    pmts["payment_date"] = pd.to_datetime(pmts["payment_date"])
    pmts["year"]  = pmts["payment_date"].dt.year
    pmts["month"] = pmts["payment_date"].dt.month
    pmts["outcome"]  = pmts.apply(classify, axis=1)
    pmts["priority"] = pmts["outcome"].map(PRIORITY)
    loan_cust = loans_df.set_index("loan_id")["customer_id"].to_dict()
    pmts["customer_id"] = pmts["loan_id"].map(loan_cust)
    pmts.dropna(subset=["customer_id"], inplace=True)
    pmts["customer_id"] = pmts["customer_id"].astype(int)
    worst = (pmts.groupby(["customer_id","year","month"])["priority"]
               .max().reset_index())
    worst["outcome"] = worst["priority"].map({0:"on_time",1:"late",2:"missed"})
    outcome_lookup = {
        (int(r.customer_id), int(r.year), int(r.month)): r.outcome
        for r in worst.itertuples()
    }

    # ── Seed balances ────────────────────────────────────────────────────
    acc_bal  = accounts_df.groupby("customer_id")["current_balance"].sum().to_dict()
    loan_bal = (loans_df[loans_df["loan_status"].isin(["Current","Past Due","Non-Performing"])]
                .groupby("customer_id")["outstanding_balance"].sum().to_dict())

    def _inst(row):
        r = row["interest_rate"] / 100 / 12
        p, n = row["loan_amount"], row["term_months"]
        if r < 1e-9 or n <= 0: return p / max(n, 1)
        return p * r * (1+r)**n / ((1+r)**n - 1)

    monthly_inst = loans_df[loans_df["loan_status"].isin(["Current","Past Due","Non-Performing"])].copy()
    monthly_inst["inst"] = monthly_inst.apply(_inst, axis=1)
    cust_inst = monthly_inst.groupby("customer_id")["inst"].sum().to_dict()

    # ── Customer metadata ─────────────────────────────────────────────────
    cust_info = customers_df.set_index("customer_id")[
        ["occupation","province","monthly_income","join_date"]
    ].copy()
    cust_info["join_date"] = pd.to_datetime(cust_info["join_date"]).dt.date
    cust_dict = cust_info.to_dict("index")

    scores = credit_profiles_df.set_index("customer_id")["credit_score"].to_dict()

    # ── Main loop — 24 months ────────────────────────────────────────────
    months   = list(_months_in_range(SIM_START_DATE, SIM_END_DATE))
    all_rows = []
    cids     = list(cust_dict.keys())
    print(f"[snapshots] {len(months)} months × {len(cids):,} customers = ~{len(months)*len(cids):,} rows")

    for month_start in months:
        active_events = EVENT_INDEX.get((month_start.year, month_start.month), [])

        for cid in cids:
            info     = cust_dict[cid]
            if info["join_date"] > month_start:
                continue

            occ    = info["occupation"]
            prov   = info["province"]
            income = float(info["monthly_income"])

            # Income shock from events
            shock = 1.0
            event_penalty = 0
            for ev in active_events:
                if prov in [p.strip() for p in ev["affected_province"].split(",")]:
                    if occ == ev["affected_sector"]:
                        shock = max(0.5, shock * (1 + ev["income_shock"]))
                        event_penalty += ev["score_penalty"]

            # Account balance
            bal = acc_bal.get(cid, income * 2)
            bal = max(0, bal * (1 + rng.uniform(0.004, 0.012) * shock)
                      + rng.uniform(0.05, 0.20) * income * shock)
            acc_bal[cid] = bal

            # Loan balance
            loan = loan_bal.get(cid, 0.0)
            inst = cust_inst.get(cid, 0.0)
            outcome = outcome_lookup.get((cid, month_start.year, month_start.month))
            if outcome == "on_time":
                loan = max(0, loan - inst)
            elif outcome == "late":
                loan = max(0, loan - inst * rng.uniform(0.5, 0.9))
            loan_bal[cid] = loan

            # Credit score
            score = scores.get(cid, 600)
            if outcome:
                lo, hi = SCORE_DELTA[outcome]
                delta  = int(rng.integers(min(lo,hi), max(lo,hi)+1)) + event_penalty
                score  = int(np.clip(score + delta, SCORE_MIN, SCORE_MAX))
            scores[cid] = score

            all_rows.append((month_start, cid, round(bal,2), round(loan,2),
                             score, get_risk_category(score)))

    df = pd.DataFrame(all_rows, columns=[
        "snapshot_date","customer_id","account_balance",
        "total_loan_balance","credit_score","risk_category"
    ])
    print(f"[snapshots] Generated {len(df):,} rows")
    return df


def save_snapshots(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "monthly_customer_snapshot.csv")
    df.to_csv(path, index=False)
    print(f"[snapshots] Saved → {path}")
    return path
