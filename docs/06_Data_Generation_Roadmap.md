# Data Generation Roadmap

## Project Title

**Cambodia Banking Risk & Business Intelligence Platform**

---

# 1. Purpose

This document defines the implementation roadmap for generating synthetic banking data used in the Cambodia Banking Risk & Business Intelligence Platform.

The roadmap converts the business requirements, data model, KPI framework, and simulation logic into a structured data generation process.

The goal is to ensure that the generated dataset is realistic, consistent, scalable, and suitable for business intelligence and risk analytics.

---

# 2. Generation Strategy

The project follows a layered simulation approach.

```text
Reference Data
      ↓
Customer Generation
      ↓
Account Generation
      ↓
Credit Profile Generation
      ↓
Loan Portfolio Generation
      ↓
Monthly Activity Simulation
      ↓
Loan Payment Simulation
      ↓
Economic Event Simulation
      ↓
Monthly Snapshots
      ↓
PostgreSQL Data Warehouse
      ↓
Analytics & Power BI
```

---

# 3. Simulation Timeline

## Historical Period

```text
January 2021 → December 2025
```

### Total Months

```text
60 Months
```

All customer behavior, transactions, balances, and risk indicators evolve over this period.

---

# 4. Phase 1: Generate Branches

## Objective

Create the bank's branch network.

---

## Output Table

```text
branches
```

---

## Expected Volume

```text
15–20 branches
```

---

## Provinces

* Phnom Penh
* Siem Reap
* Battambang
* Kampong Cham
* Kandal
* Takeo
* Banteay Meanchey
* Prey Veng

---

## Example Branches

* Phnom Penh Central
* Phnom Penh South
* Siem Reap Main
* Battambang Central
* Kandal Branch

---

# 5. Phase 2: Generate Customers

## Objective

Create the bank's customer base.

---

## Output Table

```text
customers
```

---

## Target Volume

```text
50,000 Customers
```

---

## Generate

* Customer ID
* Age
* Gender
* Occupation
* Province
* Monthly Income
* Join Date
* Customer Status

---

## Distribution Rules

Use assumptions defined in:

```text
05_Simulation_Logic.md
```

---

# 6. Phase 3: Generate Accounts

## Objective

Assign banking products.

---

## Output Table

```text
accounts
```

---

## Generate

* Savings Accounts
* Fixed Deposits
* Payroll Accounts
* Business Accounts

---

## Rules

Savings account:

```text
~95% of customers
```

Business accounts:

```text
Primarily SME Owners
```

---

# 7. Phase 4: Generate Credit Profiles

## Objective

Create initial risk characteristics.

---

## Output Table

```text
credit_profiles
```

---

## Generate

* Credit Score
* Risk Category
* Debt-to-Income Ratio
* Previous Delinquency Count

---

## Logic

Based on:

* Income
* Occupation
* Existing Debt
* Account History

---

# 8. Phase 5: Generate Loans

## Objective

Create the initial loan portfolio.

---

## Output Table

```text
loans
```

---

## Generate

* Loan Type
* Loan Amount
* Interest Rate
* Term
* Outstanding Balance
* Loan Status

---

## Loan Types

* Personal Loan
* Housing Loan
* SME Loan
* Agriculture Loan
* Vehicle Loan

---

## Rules

Loan eligibility depends on:

* Income
* Credit Score
* Occupation
* Age

---

# 9. Phase 6: Generate Monthly Transactions

## Objective

Simulate customer banking activity.

---

## Output Table

```text
transactions
```

---

## Simulation Frequency

Monthly

---

## Transaction Types

* Deposit
* Withdrawal
* Transfer
* Loan Payment
* Interest Credit

---

## Logic

Activity depends on:

* Occupation
* Income
* Account Type
* Customer Status

---

# 10. Phase 7: Generate Loan Payments

## Objective

Simulate repayment behavior.

---

## Output Table

```text
loan_payments
```

---

## Monthly Events

Each month a borrower may:

### Pay On Time

Most common outcome.

---

### Pay Late

Creates delinquency history.

---

### Miss Payment

Increases risk.

---

## Generate

* Amount Due
* Amount Paid
* Days Past Due

---

# 11. Phase 8: Update Credit Scores

## Objective

Simulate changing risk profiles.

---

## Output Table

```text
credit_profiles
```

Updated monthly.

---

## Positive Events

On-time payments:

```text
+1 to +5 score
```

---

## Negative Events

Late payments:

```text
-5 to -15 score
```

Missed payments:

```text
-15 to -30 score
```

Default:

```text
-50 to -100 score
```

---

# 12. Phase 9: Apply Economic Events

## Objective

Introduce realistic external shocks.

---

## Output Table

```text
economic_events
```

---

## Event A

### Agricultural Stress

Year:

```text
2024
```

Impact:

* Farmers
* Battambang
* Takeo
* Prey Veng

Effects:

* Income reduction
* Higher delinquency
* Increased default probability

---

## Event B

### Tourism Slowdown

Year:

```text
2025
```

Impact:

* Siem Reap
* Tourism SMEs

Effects:

* Revenue decline
* Increased credit risk

---

# 13. Phase 10: Generate Monthly Snapshots

## Objective

Capture historical customer states.

---

## Output Table

```text
monthly_customer_snapshot
```

---

## Monthly Fields

* Snapshot Date
* Customer ID
* Total Balance
* Loan Balance
* Credit Score
* Risk Category

---

## Purpose

Supports:

* Trend Analysis
* Forecasting
* Customer Analytics
* Risk Monitoring

---

# 14. Phase 11: Load into PostgreSQL

## Objective

Create the analytical data warehouse.

---

## Load Tables

```text
branches
customers
accounts
transactions
loans
loan_payments
credit_profiles
monthly_customer_snapshot
economic_events
```

---

## Validation Checks

Verify:

* Primary Keys
* Foreign Keys
* Missing Values
* Duplicate Records
* Business Rule Consistency

---

# 15. Phase 12: Analytics Layer

## SQL Analysis

Develop queries for:

* Business Performance
* Customer Analytics
* Risk Analytics
* Branch Performance

---

## KPI Calculations

Implement metrics defined in:

```text
03_KPI_Framework.md
```

---

# 16. Phase 13: Power BI Dashboards

## Executive Dashboard

* Revenue
* Customers
* Deposits
* Loans

---

## Customer Dashboard

* Retention
* Segmentation
* Product Adoption

---

## Risk Dashboard

* NPL Ratio
* Default Rate
* Credit Score Trends
* Exposure at Risk

---

## Branch Dashboard

* Revenue by Branch
* Customer Growth
* NPL Ratio by Branch

---

# 17. Estimated Dataset Size

| Table                     | Estimated Rows |
| ------------------------- | -------------: |
| branches                  |             20 |
| customers                 |         50,000 |
| accounts                  |        70,000+ |
| credit_profiles           |         50,000 |
| loans                     |        30,000+ |
| loan_payments             |       500,000+ |
| transactions              |     1,000,000+ |
| monthly_customer_snapshot |     3,000,000+ |
| economic_events           |            <20 |

---

# 18. Success Criteria

The generated dataset should:

* Follow documented business rules.
* Reflect realistic banking behavior.
* Support KPI calculations.
* Enable business and risk analytics.
* Support Power BI dashboards.
* Provide a foundation for forecasting and predictive modeling.

---

# 19. Roadmap Summary

The data generation process follows a structured simulation framework that progressively builds a realistic banking environment from customer creation through monthly financial activity, credit risk evolution, economic shocks, and analytical reporting.

This roadmap serves as the implementation blueprint for the Python-based simulation engine and subsequent PostgreSQL data warehouse.
