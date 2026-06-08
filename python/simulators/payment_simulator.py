# =============================================================================
# payment_simulator.py
# Phase 7 — Simulate Monthly Loan Repayment Behaviour (2021-2025)
# Reference: 05_Simulation_Logic.md §12,§14,§15 | 06_Data_Generation_Roadmap.md §10
# =============================================================================

import pandas as pd
import numpy as np
import os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    SIM_START_DATE, SIM_END_DATE,
    PAYMENT_PROBS, DPD_RANGES, ECONOMIC_EVENTS,
    get_risk_category, RANDOM_SEED, DATA_RAW,
)


# ---------------------------------------------------------------------------
# Month iterator (shared helper)
# ---------------------------------------------------------------------------

def _months_in_range(start: date, end: date):
    cur = date(start.year, start.month, 1)
    while cur <= end:
        yield cur
        m = cur.month % 12 + 1
        y = cur.year + (1 if cur.month == 12 else 0)
        cur = date(y, m, 1)


# ---------------------------------------------------------------------------
# Economic event index
# ---------------------------------------------------------------------------

def _build_event_index() -> dict:
    idx = {}
    for ev in ECONOMIC_EVENTS:
        cur = date(ev["start_date"].year, ev["start_date"].month, 1)
        while cur <= ev["end_date"]:
            key = (cur.year, cur.month)
            idx.setdefault(key, []).append(ev)
            m = cur.month % 12 + 1
            y = cur.year + (1 if cur.month == 12 else 0)
            cur = date(y, m, 1)
    return idx


EVENT_INDEX = _build_event_index()


# ---------------------------------------------------------------------------
# Monthly instalment (flat principal + interest approximation)
# ---------------------------------------------------------------------------

def _monthly_instalment(loan_amount: float, annual_rate: float,
                         term_months: int) -> float:
    """Standard annuity formula. Falls back to flat principal if rate ~0."""
    if term_months <= 0:
        return 0.0
    r = annual_rate / 100 / 12
    if r < 1e-9:
        return round(loan_amount / term_months, 2)
    pmt = loan_amount * r * (1 + r) ** term_months / ((1 + r) ** term_months - 1)
    return round(pmt, 2)


# ---------------------------------------------------------------------------
# Payment outcome determination
# ---------------------------------------------------------------------------

def _payment_outcome(rng, risk_category: str, active_events: list,
                     occupation: str, province: str) -> str:
    """
    Returns 'on_time', 'late', or 'missed'.
    Economic events boost 'missed' probability for affected customers.
    """
    probs = dict(PAYMENT_PROBS.get(risk_category, PAYMENT_PROBS["Medium Risk"]))

    # Apply economic event delinquency boost
    for ev in active_events:
        affected_provs = [p.strip() for p in ev["affected_province"].split(",")]
        if province in affected_provs and occupation == ev["affected_sector"]:
            boost = ev["delinquency_boost"]
            probs["on_time"]  = max(0.10, probs["on_time"] - boost)
            probs["missed"]   = min(0.80, probs["missed"]  + boost * 0.6)
            probs["late"]     = min(0.50, probs["late"]    + boost * 0.4)

    # Renormalise
    total = sum(probs.values())
    outcomes = list(probs.keys())
    weights  = np.array([probs[k] / total for k in outcomes])

    return outcomes[rng.choice(len(outcomes), p=weights)]


# ---------------------------------------------------------------------------
# Main simulator
# ---------------------------------------------------------------------------

def simulate_payments(
    loans_df:    pd.DataFrame,
    customers_df: pd.DataFrame,
    credit_profiles_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    For each active loan in each month between issue_date and
    min(maturity_date, SIM_END_DATE), generate one loan_payment record.

    Payment amounts and days_past_due are derived from the outcome model
    defined in Simulation_Logic §12, §14, §15.
    """
    rng = np.random.default_rng(seed)

    # Build fast lookups
    cust_lookup = customers_df.set_index("customer_id")[
        ["occupation", "province", "monthly_income"]
    ].to_dict("index")

    risk_lookup = credit_profiles_df.set_index("customer_id")[
        "risk_category"
    ].to_dict()

    months = list(_months_in_range(SIM_START_DATE, SIM_END_DATE))
    records    = []
    payment_id = 1

    print(f"[payments] Simulating {len(loans_df):,} loans × up to {len(months)} months…")

    for _, loan in loans_df.iterrows():
        loan_id       = int(loan["loan_id"])
        cust_id       = int(loan["customer_id"])
        loan_amount   = float(loan["loan_amount"])
        annual_rate   = float(loan["interest_rate"])
        term_months   = int(loan["term_months"])
        issue_date    = pd.to_datetime(loan["issue_date"]).date()
        maturity_date = pd.to_datetime(loan["maturity_date"]).date()
        loan_status   = loan["loan_status"]

        # Defaulted / Closed loans don't produce further payment records
        if loan_status in ("Defaulted",):
            continue

        cust         = cust_lookup.get(cust_id, {})
        occ          = cust.get("occupation", "Private Employee")
        prov         = cust.get("province", "Phnom Penh")
        risk_cat     = risk_lookup.get(cust_id, "Medium Risk")
        instalment   = _monthly_instalment(loan_amount, annual_rate, term_months)

        for month_start in months:
            # Only generate payments within the loan's life
            if month_start < date(issue_date.year, issue_date.month, 1):
                continue
            if month_start > maturity_date:
                break

            active_events = EVENT_INDEX.get((month_start.year, month_start.month), [])
            outcome       = _payment_outcome(rng, risk_cat, active_events, occ, prov)

            dpd_lo, dpd_hi = DPD_RANGES[outcome]
            days_past_due  = int(rng.integers(dpd_lo, max(dpd_lo + 1, dpd_hi + 1)))

            # Payment date = due date ± dpd
            due_day      = min(28, int(rng.integers(1, 8)) + 20)   # 21–28th
            due_date     = month_start + timedelta(days=due_day)
            payment_date = due_date + timedelta(days=days_past_due)

            # Amount paid
            if outcome == "on_time":
                amount_paid = instalment
            elif outcome == "late":
                amount_paid = round(instalment * rng.uniform(0.80, 1.0), 2)
            else:   # missed
                amount_paid = round(instalment * rng.uniform(0.0, 0.40), 2)

            records.append({
                "payment_id":    payment_id,
                "loan_id":       loan_id,
                "payment_date":  payment_date,
                "amount_due":    instalment,
                "amount_paid":   amount_paid,
                "days_past_due": days_past_due,
            })
            payment_id += 1

    df = pd.DataFrame(records)
    print(f"[payments] Generated {len(df):,} payment records")
    return df


def save_payments(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "loan_payments.csv")
    df.to_csv(path, index=False)
    print(f"[payments] Saved → {path}")
    return path
