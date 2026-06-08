# =============================================================================
# load_postgres.py
# ETL Step 3 — Load Processed CSVs into PostgreSQL
# Reference: 06_Data_Generation_Roadmap.md §14
# =============================================================================

import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.simulation_config import DATA_PROCESSED

try:
    from sqlalchemy import create_engine, text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    print("[load_postgres] sqlalchemy not installed. Run: pip install sqlalchemy psycopg2-binary")


# ---------------------------------------------------------------------------
# Connection factory
# ---------------------------------------------------------------------------

def get_engine(
    host:     str = "localhost",
    port:     int = 5432,
    dbname:   str = "banking_risk_bi",
    user:     str = "postgres",
    password: str = "postgres",
):
    """
    Build a SQLAlchemy engine for PostgreSQL.
    Connection parameters can be overridden via environment variables:
      PG_HOST, PG_PORT, PG_DBNAME, PG_USER, PG_PASSWORD
    """
    if not HAS_SQLALCHEMY:
        raise RuntimeError("sqlalchemy / psycopg2 not available")

    host     = os.environ.get("PG_HOST",     host)
    port     = int(os.environ.get("PG_PORT", port))
    dbname   = os.environ.get("PG_DBNAME",   dbname)
    user     = os.environ.get("PG_USER",     user)
    password = os.environ.get("PG_PASSWORD", password)

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(url, pool_pre_ping=True)


# ---------------------------------------------------------------------------
# Load order respects FK dependencies
# ---------------------------------------------------------------------------

LOAD_ORDER = [
    "branches",
    "customers",
    "accounts",
    "transactions",
    "credit_profiles",
    "loans",
    "loan_payments",
    "monthly_customer_snapshot",
    "economic_events",
]

# Columns that should be parsed as dates
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


def load_table(
    engine,
    table_name: str,
    processed_dir: str = DATA_PROCESSED,
    if_exists: str = "replace",   # 'replace' | 'append' | 'fail'
) -> int:
    """Load a single CSV into PostgreSQL. Returns row count."""
    path = os.path.join(processed_dir, f"{table_name}.csv")
    if not os.path.exists(path):
        print(f"  [SKIP] {path} not found")
        return 0

    parse_dates = DATE_COLS.get(table_name, [])
    df = pd.read_csv(path, parse_dates=parse_dates)

    df.to_sql(
        table_name,
        con=engine,
        if_exists=if_exists,
        index=False,
        chunksize=10_000,
        method="multi",
    )
    print(f"  ✓  {table_name:35s} {len(df):>10,} rows loaded")
    return len(df)


def load_all(
    engine=None,
    processed_dir: str = DATA_PROCESSED,
    if_exists: str = "replace",
):
    """Load all tables into PostgreSQL in dependency order."""
    if engine is None:
        engine = get_engine()

    print(f"\nConnecting to PostgreSQL…")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connection OK\n")

    total_rows = 0
    for table in LOAD_ORDER:
        rows = load_table(engine, table, processed_dir, if_exists)
        total_rows += rows

    print(f"\nTotal rows loaded: {total_rows:,}")
    return total_rows


# ---------------------------------------------------------------------------
# Post-load: add primary and foreign key constraints
# ---------------------------------------------------------------------------

PK_SQL = """
ALTER TABLE branches                  ADD PRIMARY KEY (branch_id);
ALTER TABLE customers                 ADD PRIMARY KEY (customer_id);
ALTER TABLE accounts                  ADD PRIMARY KEY (account_id);
ALTER TABLE transactions              ADD PRIMARY KEY (transaction_id);
ALTER TABLE loans                     ADD PRIMARY KEY (loan_id);
ALTER TABLE loan_payments             ADD PRIMARY KEY (payment_id);
ALTER TABLE credit_profiles           ADD PRIMARY KEY (customer_id);
ALTER TABLE economic_events           ADD PRIMARY KEY (event_id);
"""

FK_SQL = """
ALTER TABLE customers    ADD FOREIGN KEY (branch_id)   REFERENCES branches(branch_id);
ALTER TABLE accounts     ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE accounts     ADD FOREIGN KEY (branch_id)   REFERENCES branches(branch_id);
ALTER TABLE transactions ADD FOREIGN KEY (account_id)  REFERENCES accounts(account_id);
ALTER TABLE loans        ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE loans        ADD FOREIGN KEY (branch_id)   REFERENCES branches(branch_id);
ALTER TABLE loan_payments ADD FOREIGN KEY (loan_id)    REFERENCES loans(loan_id);
ALTER TABLE credit_profiles ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE monthly_customer_snapshot ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
"""

INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_txn_account   ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_txn_date      ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_loan_customer ON loans(customer_id);
CREATE INDEX IF NOT EXISTS idx_pmt_loan      ON loan_payments(loan_id);
CREATE INDEX IF NOT EXISTS idx_snap_cust     ON monthly_customer_snapshot(customer_id);
CREATE INDEX IF NOT EXISTS idx_snap_date     ON monthly_customer_snapshot(snapshot_date);
"""


def apply_constraints(engine=None):
    """Apply PKs, FKs and indexes after all tables have been loaded."""
    if engine is None:
        engine = get_engine()

    with engine.begin() as conn:
        print("Applying primary keys…")
        for stmt in PK_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"  [WARN] {e}")

        print("Applying foreign keys…")
        for stmt in FK_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"  [WARN] {e}")

        print("Creating indexes…")
        for stmt in INDEX_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"  [WARN] {e}")

    print("Constraints and indexes applied.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load processed CSVs into PostgreSQL")
    parser.add_argument("--host",     default="localhost")
    parser.add_argument("--port",     default=5432, type=int)
    parser.add_argument("--dbname",   default="banking_risk_bi")
    parser.add_argument("--user",     default="postgres")
    parser.add_argument("--password", default="postgres")
    parser.add_argument("--if-exists",default="replace",
                        choices=["replace", "append", "fail"])
    parser.add_argument("--no-constraints", action="store_true",
                        help="Skip applying PK/FK/index constraints")
    args = parser.parse_args()

    engine = get_engine(args.host, args.port, args.dbname, args.user, args.password)
    load_all(engine, if_exists=args.if_exists)
    if not args.no_constraints:
        apply_constraints(engine)
