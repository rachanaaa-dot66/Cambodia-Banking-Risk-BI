# Cambodia Banking Risk & Business Intelligence Platform

A full end-to-end synthetic banking analytics project simulating a medium-sized commercial bank in Cambodia. Covers data generation, ETL, PostgreSQL data warehouse, SQL analytics, and Power BI dashboards.

---

## Project Structure

```
Banking-Risk-BI-Platform/
├── docs/                        ← Project documentation (6 docs)
├── data/
│   ├── raw/                     ← Generated CSVs (output of python/main.py)
│   ├── processed/               ← Cleaned & validated CSVs
│   └── warehouse/               ← Archive / exports
├── python/
│   ├── config/
│   │   └── simulation_config.py ← All simulation parameters
│   ├── generators/              ← Phases 1–5, 9
│   ├── simulators/              ← Phases 6–8, 10
│   ├── etl/                     ← Phases 11–13
│   └── main.py                  ← Master orchestrator
├── sql/
│   ├── schema/                  ← DDL: create_tables.sql, constraints.sql
│   ├── business_analysis/       ← Customer growth, revenue, product KPIs
│   ├── risk_analysis/           ← NPL, default rate, exposure
│   └── branch_analysis/         ← Branch performance & risk
├── powerbi/                     ← Banking_Risk_BI.pbix + screenshots
├── reports/                     ← PDF reports
└── assets/                      ← ERD, architecture diagrams
```

---

## Simulation Overview

| Parameter | Value |
|---|---|
| Simulation Period | Jan 2024 – Dec 2025 (24 months) |
| Target Customers | 5,000 |
| Branches | 20 (8 provinces) |
| Estimated Transactions | ~100,000 |
| Estimated Loan Payments | ~50,000 |
| Estimated Snapshots | ~120,000 |
| Expected Runtime | ~2–3 minutes |

### Economic Phases

| Year | Phase |
|---|---|
| 2021 | Economic Recovery |
| 2022 | Stable Growth |
| 2023 | Expansion Period |
| 2024 | Agricultural Stress Event (Battambang, Takeo, Prey Veng) |
| 2025 | Tourism Slowdown Event (Siem Reap) |

---

## Quick Start

### 1. Install dependencies

```bash
pip install pandas numpy python-dateutil sqlalchemy psycopg2-binary
```

### 2. Run full simulation

```bash
cd python
python main.py
```

### 3. Run specific phases only

```bash
python main.py --phases 1 2 3 4 5   # generators only
python main.py --phases 6 7 8       # simulators only
python main.py --phases 11 12       # clean + validate only
python main.py --no-snapshots       # skip 3M snapshot table (dev mode)
python main.py --skip-load          # skip PostgreSQL load
```

### 4. PostgreSQL connection

Set environment variables before running Phase 13:

```bash
export PG_HOST=localhost
export PG_PORT=5432
export PG_DBNAME=banking_risk_bi
export PG_USER=postgres
export PG_PASSWORD=yourpassword
```

Or create the DB first:

```sql
CREATE DATABASE banking_risk_bi;
```

Then run the schema:

```bash
psql -d banking_risk_bi -f sql/schema/create_tables.sql
```

---

## Generation Phases

| Phase | Script | Output |
|---|---|---|
| 1 | `generate_branches.py` | `branches.csv` (20 rows) |
| 2 | `generate_customers.py` | `customers.csv` (50,000 rows) |
| 3 | `generate_accounts.py` | `accounts.csv` (70,000+ rows) |
| 4 | `generate_credit_profiles.py` | `credit_profiles.csv` (50,000 rows) |
| 5 | `generate_loans.py` | `loans.csv` (30,000+ rows) |
| 6 | `transaction_simulator.py` | `transactions.csv` (1,000,000+ rows) |
| 7 | `payment_simulator.py` | `loan_payments.csv` (500,000+ rows) |
| 8 | `credit_score_simulator.py` | Updated `credit_profiles.csv` |
| 9 | `generate_economic_events.py` | `economic_events.csv` (2 rows) |
| 10 | `monthly_snapshot_simulator.py` | `monthly_customer_snapshot.csv` (3,000,000+ rows) |
| 11 | `clean_data.py` | Processed CSVs |
| 12 | `validate_data.py` | Validation report |
| 13 | `load_postgres.py` | PostgreSQL warehouse |

---

## KPI Framework

### Business Performance
- **KPI-BP-01** Total Customers
- **KPI-BP-02** Total Deposits
- **KPI-BP-03** Total Loans Outstanding
- **KPI-BP-04** Deposit Growth Rate
- **KPI-BP-05** Loan Growth Rate
- **KPI-BP-06** Revenue (Interest + Fee Income)

### Customer Analytics
- **KPI-CA-01** Active Customers
- **KPI-CA-02** New Customer Acquisition
- **KPI-CA-03** Customer Retention Rate
- **KPI-CA-04** Product Adoption Rate
- **KPI-CA-05** Customer Lifetime Value

### Risk Management
- **KPI-RM-01** Default Rate
- **KPI-RM-02** NPL Ratio
- **KPI-RM-03** Delinquency Rate
- **KPI-RM-04** Average Credit Score
- **KPI-RM-05** Exposure at Risk
- **KPI-RM-06** Risk Distribution

### Branch Performance
- **KPI-BR-01** Revenue by Branch
- **KPI-BR-02** Loan Portfolio by Branch
- **KPI-BR-03** Deposits by Branch
- **KPI-BR-04** Customer Growth by Branch
- **KPI-BR-05** NPL Ratio by Branch

---

## Technology Stack

| Category | Technology |
|---|---|
| Data Generation | Python (pandas, numpy) |
| Database | PostgreSQL |
| Analytics | SQL |
| Visualization | Power BI |
| Documentation | Markdown |

---

## Documentation

| Doc | Title |
|---|---|
| `docs/01_Project_Charter.md` | Project overview, objectives, scope |
| `docs/02_Business_Requirements.md` | Business questions & stakeholder needs |
| `docs/03_KPI_Framework.md` | All KPI definitions & formulas |
| `docs/04_Data_Model.md` | Entity relationships & data dictionary |
| `docs/05_Simulation_Logic.md` | Behavioral rules & assumptions |
| `docs/06_Data_Generation_Roadmap.md` | Implementation blueprint |
