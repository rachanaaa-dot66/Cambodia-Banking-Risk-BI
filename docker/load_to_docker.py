#!/usr/bin/env python3
# =============================================================================
# load_to_docker.py
# Load processed CSVs into the Docker PostgreSQL container
# Run this from the project root after: docker compose up -d
#
# Usage:
#   python docker/load_to_docker.py
#   python docker/load_to_docker.py --data-dir data/processed
# =============================================================================

import os
import sys
import argparse

# Load order respects FK dependencies
LOAD_ORDER = [
    "branches",
    "customers",
    "accounts",
    "credit_profiles",
    "loans",
    "loan_payments",
    "transactions",
    "monthly_customer_snapshot",
    "economic_events",
]

DATE_COLS = {
    "branches":                  ["branch_open_date"],
    "customers":                 ["birth_date", "join_date"],
    "accounts":                  ["open_date"],
    "transactions":              ["transaction_date"],
    "loans":                     ["issue_date", "maturity_date"],
    "loan_payments":             ["payment_date"],
    "monthly_customer_snapshot": ["snapshot_date"],
    "economic_events":           ["start_date", "end_date"],
}


def main():
    parser = argparse.ArgumentParser(description="Load CSVs into Docker PostgreSQL")
    parser.add_argument("--host",     default=os.environ.get("PG_HOST",     "localhost"))
    parser.add_argument("--port",     default=int(os.environ.get("PG_PORT", 5432)), type=int)
    parser.add_argument("--dbname",   default=os.environ.get("PG_DBNAME",   "banking_risk_bi"))
    parser.add_argument("--user",     default=os.environ.get("PG_USER",     "banking_user"))
    parser.add_argument("--password", default=os.environ.get("PG_PASSWORD", "banking2024"))
    parser.add_argument("--data-dir", default="data/processed")
    args = parser.parse_args()

    try:
        import pandas as pd
        from sqlalchemy import create_engine, text
    except ImportError:
        print("Missing packages. Run:  pip install pandas sqlalchemy psycopg2-binary")
        sys.exit(1)

    url    = f"postgresql+psycopg2://{args.user}:{args.password}@{args.host}:{args.port}/{args.dbname}"
    engine = create_engine(url, pool_pre_ping=True)

    print(f"\nConnecting to postgresql://{args.host}:{args.port}/{args.dbname} ...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected OK\n")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nMake sure the container is running:  docker compose up -d")
        sys.exit(1)

    total = 0
    for table in LOAD_ORDER:
        path = os.path.join(args.data_dir, f"{table}.csv")
        if not os.path.exists(path):
            print(f"  [SKIP]  {table}.csv not found in {args.data_dir}")
            continue

        parse_dates = DATE_COLS.get(table, [])
        df = pd.read_csv(path, parse_dates=parse_dates)

        df.to_sql(table, con=engine, if_exists="append",
                  index=False, chunksize=5_000, method="multi")

        total += len(df)
        print(f"  ✓  {table:40s} {len(df):>8,} rows")

    print(f"\nTotal rows loaded: {total:,}")
    print("\nDone! Connect Power BI or DBeaver to:")
    print(f"  Host:     {args.host}:{args.port}")
    print(f"  Database: {args.dbname}")
    print(f"  User:     {args.user}")
    print(f"  Password: {args.password}")


if __name__ == "__main__":
    main()
