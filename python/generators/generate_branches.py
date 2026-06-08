# =============================================================================
# generate_branches.py
# Phase 1 — Generate Branch Network
# Reference: 06_Data_Generation_Roadmap.md §4
# =============================================================================

import pandas as pd
import numpy as np
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import (
    BRANCHES, SIM_START_DATE, RANDOM_SEED, DATA_RAW
)

CAMBODIAN_NAMES = [
    "Sokha Chea", "Dara Pich", "Mony Keo", "Ratha Heng", "Bopha Sim",
    "Vibol Chan", "Chenda Nuth", "Piseth Sar", "Sreymom Lim", "Kosal Pen",
    "Leakena Ros", "Vannak Ouk", "Sreynoch Mao", "Phirum Sok", "Dina Yim",
    "Ratana Chhun", "Veasna Khun", "Sophea Teng", "Makara Hout", "Kunthea Vong",
]


def generate_branches(seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Build the branches table from the static branch list defined in config.
    Branch open dates are staggered between 2015-01-01 and SIM_START_DATE
    so every branch pre-exists the simulation window.
    """
    rng = np.random.default_rng(seed)

    records = []
    earliest_open = date(2018, 1, 1)
    span_days = (SIM_START_DATE - earliest_open).days

    for idx, (name, province, city, b_type) in enumerate(BRANCHES, start=1):
        open_offset = int(rng.integers(0, span_days))
        open_date   = earliest_open + timedelta(days=open_offset)
        manager     = CAMBODIAN_NAMES[idx % len(CAMBODIAN_NAMES)]

        records.append({
            "branch_id":        idx,
            "branch_name":      name,
            "province":         province,
            "city":             city,
            "branch_type":      b_type,
            "branch_open_date": open_date,
            "branch_manager":   manager,
        })

    df = pd.DataFrame(records)
    return df


def save_branches(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "branches.csv")
    df.to_csv(path, index=False)
    print(f"[branches] Saved {len(df)} rows → {path}")
    return path


if __name__ == "__main__":
    df = generate_branches()
    save_branches(df)
    print(df.to_string(index=False))
