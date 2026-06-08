# =============================================================================
# credit_score_simulator.py  — OPTIMIZED (vectorized, 24 months)
# Phase 8 — Monthly Credit Score Migration
# Reference: 05_Simulation_Logic.md §13
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    SCORE_DELTA, SCORE_MIN, SCORE_MAX, get_risk_category,
    ECONOMIC_EVENTS, RANDOM_SEED,
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


def simulate_credit_scores(
    customers_df:       pd.DataFrame,
    credit_profiles_df: pd.DataFrame,
    loan_payments_df:   pd.DataFrame,
    loans_df:           pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # ── Build outcome table (customer × month) ──────────────────────────
    PRIORITY = {"on_time": 0, "late": 1, "missed": 2}

    def classify(r) -> str:
        if r.days_past_due >= 30 or r.amount_paid < r.amount_due * 0.5:
            return "missed"
        if r.days_past_due > 0 or r.amount_paid < r.amount_due * 0.99:
            return "late"
        return "on_time"

    pmts = loan_payments_df.copy()
    pmts["payment_date"] = pd.to_datetime(pmts["payment_date"])
    pmts["year"]    = pmts["payment_date"].dt.year
    pmts["month"]   = pmts["payment_date"].dt.month
    pmts["outcome"] = pmts.apply(classify, axis=1)
    pmts["priority"]= pmts["outcome"].map(PRIORITY)

    loan_cust = loans_df.set_index("loan_id")["customer_id"].to_dict()
    pmts["customer_id"] = pmts["loan_id"].map(loan_cust)
    pmts.dropna(subset=["customer_id"], inplace=True)
    pmts["customer_id"] = pmts["customer_id"].astype(int)

    # Worst outcome per (customer, year, month)
    worst = (pmts.groupby(["customer_id","year","month"])["priority"]
               .max().reset_index())
    worst["outcome"] = worst["priority"].map({0:"on_time",1:"late",2:"missed"})
    outcome_lookup = {
        (int(r.customer_id), int(r.year), int(r.month)): r.outcome
        for r in worst.itertuples()
    }

    # ── Info lookups ────────────────────────────────────────────────────
    cust_info = customers_df.set_index("customer_id")[["occupation","province"]].to_dict("index")
    scores    = credit_profiles_df.set_index("customer_id")["credit_score"].to_dict()

    # ── Walk 24 months ──────────────────────────────────────────────────
    cur = date(2024, 1, 1)
    end = date(2025, 12, 31)
    while cur <= end:
        active_events = EVENT_INDEX.get((cur.year, cur.month), [])

        # Vectorize: build arrays of (customer_id, delta)
        cids    = list(scores.keys())
        deltas  = np.zeros(len(cids), dtype=int)

        for i, cid in enumerate(cids):
            outcome = outcome_lookup.get((cid, cur.year, cur.month))
            if outcome is None:
                # No loan — 20 % chance of tiny passive improvement
                if rng.random() < 0.20:
                    deltas[i] = int(rng.integers(1, 4))
                continue

            lo, hi = SCORE_DELTA[outcome]
            delta  = int(rng.integers(min(lo,hi), max(lo,hi)+1))

            # Economic event penalty
            info = cust_info.get(cid, {})
            for ev in active_events:
                if info.get("province","") in [p.strip() for p in ev["affected_province"].split(",")]:
                    if info.get("occupation","") == ev["affected_sector"]:
                        delta += ev["score_penalty"]
            deltas[i] = delta

        # Apply all deltas at once
        for i, cid in enumerate(cids):
            scores[cid] = int(np.clip(scores[cid] + deltas[i], SCORE_MIN, SCORE_MAX))

        m = cur.month % 12 + 1
        y = cur.year + (1 if cur.month == 12 else 0)
        cur = date(y, m, 1)

    # ── Rebuild updated profiles ─────────────────────────────────────────
    updated = credit_profiles_df.copy()
    updated["credit_score"]  = updated["customer_id"].map(scores)
    updated["risk_category"] = updated["credit_score"].apply(get_risk_category)
    print(f"[credit_scores] Updated {len(updated):,} profiles")
    print(updated["risk_category"].value_counts().to_string())
    return updated
