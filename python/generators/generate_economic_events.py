# =============================================================================
# generate_economic_events.py
# Phase 9 — Generate Economic Events Table
# Reference: 05_Simulation_Logic.md §16 | 06_Data_Generation_Roadmap.md §12
# =============================================================================

import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import ECONOMIC_EVENTS, DATA_RAW


def generate_economic_events() -> pd.DataFrame:
    """
    Build the economic_events table from the static definitions in config.
    Two events are defined per the simulation docs:
      - Agricultural Stress 2024 (Battambang, Takeo, Prey Veng / Farmers)
      - Tourism Slowdown 2025  (Siem Reap / SME Owners)
    """
    records = []
    for ev in ECONOMIC_EVENTS:
        records.append({
            "event_id":          ev["event_id"],
            "event_name":        ev["event_name"],
            "start_date":        ev["start_date"],
            "end_date":          ev["end_date"],
            "affected_province": ev["affected_province"],
            "affected_sector":   ev["affected_sector"],
            "severity":          ev["severity"],
        })

    df = pd.DataFrame(records)
    print(f"[economic_events] Generated {len(df)} events")
    print(df[["event_id", "event_name", "severity"]].to_string(index=False))
    return df


def save_economic_events(df: pd.DataFrame, output_dir: str = DATA_RAW) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "economic_events.csv")
    df.to_csv(path, index=False)
    print(f"[economic_events] Saved → {path}")
    return path


if __name__ == "__main__":
    df = generate_economic_events()
    save_economic_events(df)
