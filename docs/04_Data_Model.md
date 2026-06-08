# Data Model & Data Dictionary

## Project Title

**Cambodia Banking Risk & Business Intelligence Platform**

---

# 1. Purpose

This document defines the logical data model, table structures, relationships, and data dictionary for the Banking Risk & Business Intelligence Platform.

The objective is to create a realistic banking data warehouse capable of supporting:

* Business Intelligence
* Customer Analytics
* Credit Risk Analytics
* Branch Performance Analysis
* Forecasting
* Dashboard Reporting

---

# 2. Data Architecture Overview

The platform uses a relational database design based on core banking entities.

The data model is designed to support historical analysis from 2021–2025 and future analytical extensions.

---

# 3. Entity Relationship Overview

```text
Branch
│
├── Customer
│      │
│      ├── Account
│      │      │
│      │      └── Transaction
│      │
│      ├── Loan
│      │      │
│      │      └── Loan Payment
│      │
│      └── Credit Profile
│
└── Economic Events
```

---

# 4. Core Tables

The project consists of nine primary tables:

| Table Name                | Purpose                    |
| ------------------------- | -------------------------- |
| branches                  | Branch information         |
| customers                 | Customer information       |
| accounts                  | Banking accounts           |
| transactions              | Customer transactions      |
| loans                     | Loan portfolio             |
| loan_payments             | Loan repayment history     |
| credit_profiles           | Credit risk information    |
| monthly_customer_snapshot | Monthly historical metrics |
| economic_events           | Simulated economic events  |

---

# 5. Table: branches

## Description

Stores branch-level information.

### Primary Key

```text
branch_id
```

### Columns

| Column           | Data Type    | Description              |
| ---------------- | ------------ | ------------------------ |
| branch_id        | INTEGER      | Unique branch identifier |
| branch_name      | VARCHAR(100) | Branch name              |
| province         | VARCHAR(50)  | Province                 |
| city             | VARCHAR(50)  | City                     |
| branch_type      | VARCHAR(20)  | Urban or Rural           |
| branch_open_date | DATE         | Opening date             |
| branch_manager   | VARCHAR(100) | Branch manager           |

---

# 6. Table: customers

## Description

Stores customer demographic and profile information.

### Primary Key

```text
customer_id
```

### Foreign Key

```text
branch_id → branches.branch_id
```

### Columns

| Column          | Data Type     | Description              |
| --------------- | ------------- | ------------------------ |
| customer_id     | INTEGER       | Customer identifier      |
| branch_id       | INTEGER       | Assigned branch          |
| gender          | VARCHAR(10)   | Gender                   |
| birth_date      | DATE          | Date of birth            |
| age             | INTEGER       | Customer age             |
| occupation      | VARCHAR(50)   | Occupation               |
| marital_status  | VARCHAR(20)   | Marital status           |
| province        | VARCHAR(50)   | Residence province       |
| monthly_income  | DECIMAL(12,2) | Monthly income (USD)     |
| join_date       | DATE          | Customer onboarding date |
| customer_status | VARCHAR(20)   | Active, Inactive, Closed |

---

# 7. Table: accounts

## Description

Stores banking account information.

### Primary Key

```text
account_id
```

### Foreign Key

```text
customer_id → customers.customer_id
branch_id → branches.branch_id
```

### Columns

| Column          | Data Type     | Description             |
| --------------- | ------------- | ----------------------- |
| account_id      | INTEGER       | Account identifier      |
| customer_id     | INTEGER       | Customer owner          |
| branch_id       | INTEGER       | Branch                  |
| account_type    | VARCHAR(50)   | Account type            |
| open_date       | DATE          | Account opening date    |
| current_balance | DECIMAL(15,2) | Current balance         |
| account_status  | VARCHAR(20)   | Active, Dormant, Closed |

### Account Types

* Savings
* Fixed Deposit
* Payroll
* Business

---

# 8. Table: transactions

## Description

Stores customer transaction history.

### Primary Key

```text
transaction_id
```

### Foreign Key

```text
account_id → accounts.account_id
```

### Columns

| Column             | Data Type     | Description            |
| ------------------ | ------------- | ---------------------- |
| transaction_id     | BIGINT        | Transaction identifier |
| account_id         | INTEGER       | Account identifier     |
| transaction_date   | DATE          | Transaction date       |
| transaction_type   | VARCHAR(50)   | Transaction category   |
| transaction_amount | DECIMAL(15,2) | Transaction amount     |

### Transaction Types

* Deposit
* Withdrawal
* Transfer
* Loan Payment
* Interest Credit

---

# 9. Table: loans

## Description

Stores customer loan information.

### Primary Key

```text
loan_id
```

### Foreign Key

```text
customer_id → customers.customer_id
branch_id → branches.branch_id
```

### Columns

| Column              | Data Type     | Description          |
| ------------------- | ------------- | -------------------- |
| loan_id             | INTEGER       | Loan identifier      |
| customer_id         | INTEGER       | Borrower             |
| branch_id           | INTEGER       | Lending branch       |
| loan_type           | VARCHAR(50)   | Loan category        |
| loan_amount         | DECIMAL(15,2) | Original loan amount |
| interest_rate       | DECIMAL(5,2)  | Annual interest rate |
| term_months         | INTEGER       | Loan term            |
| issue_date          | DATE          | Loan issue date      |
| maturity_date       | DATE          | Maturity date        |
| outstanding_balance | DECIMAL(15,2) | Remaining balance    |
| loan_status         | VARCHAR(30)   | Current loan status  |

### Loan Types

* Personal Loan
* Housing Loan
* SME Loan
* Agriculture Loan
* Vehicle Loan

### Loan Status

* Current
* Past Due
* Non-Performing
* Defaulted
* Closed

---

# 10. Table: loan_payments

## Description

Stores monthly repayment history.

### Primary Key

```text
payment_id
```

### Foreign Key

```text
loan_id → loans.loan_id
```

### Columns

| Column        | Data Type     | Description        |
| ------------- | ------------- | ------------------ |
| payment_id    | BIGINT        | Payment identifier |
| loan_id       | INTEGER       | Loan identifier    |
| payment_date  | DATE          | Payment date       |
| amount_due    | DECIMAL(15,2) | Scheduled payment  |
| amount_paid   | DECIMAL(15,2) | Actual payment     |
| days_past_due | INTEGER       | Days overdue       |

---

# 11. Table: credit_profiles

## Description

Stores customer risk characteristics.

### Primary Key

```text
customer_id
```

### Foreign Key

```text
customer_id → customers.customer_id
```

### Columns

| Column                     | Data Type    | Description                  |
| -------------------------- | ------------ | ---------------------------- |
| customer_id                | INTEGER      | Customer identifier          |
| credit_score               | INTEGER      | Credit score                 |
| risk_category              | VARCHAR(30)  | Risk classification          |
| debt_to_income_ratio       | DECIMAL(6,2) | DTI ratio                    |
| previous_delinquency_count | INTEGER      | Historical delinquency count |

### Risk Categories

* Very Low Risk
* Low Risk
* Medium Risk
* High Risk
* Very High Risk

---

# 12. Table: monthly_customer_snapshot

## Description

Stores monthly customer-level historical metrics.

This table supports trend analysis, forecasting, retention analysis, and risk monitoring.

### Composite Key

```text
snapshot_date
customer_id
```

### Columns

| Column             | Data Type     | Description           |
| ------------------ | ------------- | --------------------- |
| snapshot_date      | DATE          | Snapshot month        |
| customer_id        | INTEGER       | Customer identifier   |
| account_balance    | DECIMAL(15,2) | Total balances        |
| total_loan_balance | DECIMAL(15,2) | Outstanding loans     |
| credit_score       | INTEGER       | Monthly score         |
| risk_category      | VARCHAR(30)   | Monthly risk category |

---

# 13. Table: economic_events

## Description

Stores simulated economic events affecting customer behavior and credit quality.

### Primary Key

```text
event_id
```

### Columns

| Column            | Data Type    | Description                  |
| ----------------- | ------------ | ---------------------------- |
| event_id          | INTEGER      | Event identifier             |
| event_name        | VARCHAR(100) | Event name                   |
| start_date        | DATE         | Event start                  |
| end_date          | DATE         | Event end                    |
| affected_province | VARCHAR(50)  | Impacted province            |
| affected_sector   | VARCHAR(50)  | Impacted occupation/industry |
| severity          | VARCHAR(20)  | Event severity               |

---

# 14. Relationship Summary

| Parent Table | Child Table               | Relationship |
| ------------ | ------------------------- | ------------ |
| branches     | customers                 | One-to-Many  |
| branches     | accounts                  | One-to-Many  |
| branches     | loans                     | One-to-Many  |
| customers    | accounts                  | One-to-Many  |
| customers    | loans                     | One-to-Many  |
| customers    | credit_profiles           | One-to-One   |
| accounts     | transactions              | One-to-Many  |
| loans        | loan_payments             | One-to-Many  |
| customers    | monthly_customer_snapshot | One-to-Many  |

---

# 15. Data Warehouse Design Considerations

The model is designed to support:

### Business Intelligence

* KPI monitoring
* Executive dashboards
* Trend analysis

### Customer Analytics

* Customer segmentation
* Retention analysis
* Product adoption

### Risk Analytics

* Credit scoring
* Delinquency analysis
* NPL monitoring

### Forecasting

* Deposit forecasting
* Loan forecasting
* Risk forecasting

---

# 16. Data Model Summary

The Banking Risk & Business Intelligence Platform uses a relational banking data model designed to simulate realistic banking operations in Cambodia.

The model integrates customer, account, transaction, loan, repayment, and risk data to provide a comprehensive analytical environment supporting business intelligence, customer analytics, and risk management use cases.
