# Simulation Logic Document

## Project Title

**Cambodia Banking Risk & Business Intelligence Platform**

---

# 1. Purpose

This document defines the rules, assumptions, and behavioral logic used to generate synthetic banking data for the Cambodia Banking Risk & Business Intelligence Platform.

The objective is to create realistic banking data that reflects customer behavior, lending activities, deposit growth, credit risk, and economic conditions commonly observed in Cambodia's banking and microfinance sectors.

Unlike random data generation, this simulation is designed to model relationships between customer characteristics, financial products, repayment behavior, and risk outcomes.

---

# 2. Simulation Period

## Timeline

```text
January 2021 – December 2025
```

### Economic Phases

| Year | Scenario                  |
| ---- | ------------------------- |
| 2021 | Economic Recovery         |
| 2022 | Stable Growth             |
| 2023 | Expansion Period          |
| 2024 | Agricultural Stress Event |
| 2025 | Tourism Slowdown Event    |

The simulation spans 60 monthly periods.

---

# 3. Customer Generation Logic

## Customer Volume

Target population:

```text
50,000 Customers
```

Customers are assigned to branches and provinces based on predefined distributions.

---

## Age Distribution

| Age Group | Percentage |
| --------- | ---------- |
| 18 – 24   | 15%        |
| 25 – 34   | 30%        |
| 35 – 44   | 25%        |
| 45 – 54   | 15%        |
| 55 – 65   | 15%        |

---

## Gender Distribution

| Gender | Percentage |
| ------ | ---------- |
| Male   | 50%        |
| Female | 50%        |

---

## Occupation Distribution

| Occupation         | Percentage |
| ------------------ | ---------- |
| Farmer             | 25%        |
| Private Employee   | 25%        |
| SME Owner          | 20%        |
| Factory Worker     | 10%        |
| Government Officer | 10%        |
| Freelancer         | 5%         |
| Student            | 5%         |

---

# 4. Geographic Distribution

Customers are distributed across key Cambodian provinces.

| Province         |
| ---------------- |
| Phnom Penh       |
| Siem Reap        |
| Battambang       |
| Kampong Cham     |
| Kandal           |
| Takeo            |
| Banteay Meanchey |
| Prey Veng        |

Each province exhibits unique economic characteristics and risk profiles.

---

# 5. Income Generation Logic

Income is generated based on occupation.

---

## Farmer

| Metric  | Value |
| ------- | ----- |
| Minimum | $150  |
| Average | $450  |
| Maximum | $800  |

---

## Factory Worker

| Metric  | Value |
| ------- | ----- |
| Minimum | $200  |
| Average | $400  |
| Maximum | $600  |

---

## Private Employee

| Metric  | Value  |
| ------- | ------ |
| Minimum | $300   |
| Average | $850   |
| Maximum | $1,500 |

---

## Government Officer

| Metric  | Value  |
| ------- | ------ |
| Minimum | $350   |
| Average | $700   |
| Maximum | $1,200 |

---

## SME Owner

| Metric  | Value  |
| ------- | ------ |
| Minimum | $500   |
| Average | $1,500 |
| Maximum | $5,000 |

---

## Freelancer

| Metric  | Value  |
| ------- | ------ |
| Minimum | $250   |
| Average | $900   |
| Maximum | $3,000 |

---

## Student

| Metric  | Value |
| ------- | ----- |
| Minimum | $0    |
| Maximum | $300  |

---

# 6. Banking Product Assignment Logic

## Account Products

### Savings Account

Assigned to approximately:

```text
95% of customers
```

---

### Fixed Deposit

Higher probability for:

* High-income customers
* Older customers

---

### Payroll Account

Higher probability for:

* Government Officers
* Private Employees
* Factory Workers

---

### Business Account

Primarily assigned to:

* SME Owners

---

# 7. Loan Assignment Logic

Not all customers receive loans.

Loan eligibility depends on:

* Age
* Income
* Occupation
* Credit Score
* Existing Debt

---

## Personal Loan

Common among:

* Private Employees
* Government Officers

---

## Agriculture Loan

Common among:

* Farmers

---

## SME Loan

Common among:

* SME Owners

---

## Housing Loan

Common among:

* Customers aged 30+
* Higher-income customers

---

## Vehicle Loan

Common among:

* Middle-income customers

---

# 8. Loan Amount Generation Logic

Loan size depends on income and loan type.

---

## Loan-to-Income Principle

Loan amounts are generated relative to annual income.

Example:

| Monthly Income | Typical Loan Range |
| -------------- | ------------------ |
| $300           | $2,000 – $8,000    |
| $700           | $5,000 – $20,000   |
| $1,500         | $10,000 – $50,000  |
| $3,000         | $20,000 – $100,000 |

This creates realistic lending behavior.

---

# 9. Credit Score Generation Logic

## Initial Credit Score

Credit scores are influenced by:

* Income level
* Occupation
* Existing debt
* Account age
* Previous repayment history

---

## Example Ranges

| Customer Profile      | Credit Score Range |
| --------------------- | ------------------ |
| High Income SME Owner | 700 – 850          |
| Government Officer    | 650 – 800          |
| Private Employee      | 600 – 750          |
| Farmer                | 550 – 700          |
| Student               | 450 – 650          |

---

# 10. Risk Classification Logic

Customers are classified based on credit score.

| Credit Score | Risk Category  |
| ------------ | -------------- |
| 750 – 850    | Very Low Risk  |
| 650 – 749    | Low Risk       |
| 550 – 649    | Medium Risk    |
| 450 – 549    | High Risk      |
| Below 450    | Very High Risk |

---

# 11. Monthly Transaction Simulation

Customers generate monthly banking activity.

### Transaction Types

* Deposit
* Withdrawal
* Transfer
* Loan Payment
* Interest Credit

---

## Activity Frequency

Activity varies by:

* Occupation
* Account Type
* Income
* Customer Status

Active customers generate more transactions than inactive customers.

---

# 12. Loan Payment Simulation

Monthly repayments are simulated for active loans.

Each payment record includes:

* Scheduled amount
* Actual amount paid
* Days past due

---

## Payment Outcomes

### On-Time Payment

Most common outcome.

---

### Late Payment

Moderate probability.

Creates delinquency history.

---

### Missed Payment

Less common.

Increases risk and default probability.

---

# 13. Credit Score Migration Logic

Credit scores evolve over time.

---

## Positive Behavior

On-time payments:

```text
Credit Score +1 to +5 points
```

---

## Late Payments

```text
Credit Score -5 to -15 points
```

---

## Missed Payments

```text
Credit Score -15 to -30 points
```

---

## Default Event

```text
Credit Score -50 to -100 points
```

---

# 14. Delinquency Logic

Delinquency probability increases when:

* Income is low
* Debt-to-income ratio is high
* Credit score is low
* Economic conditions deteriorate

Delinquency is tracked using:

```text
days_past_due
```

---

# 15. Default Logic

Default events are not randomly assigned.

Default probability depends on:

| Factor               | Influence |
| -------------------- | --------- |
| Credit Score         | High      |
| Debt-to-Income Ratio | High      |
| Income Level         | High      |
| Delinquency History  | Very High |
| Economic Events      | Medium    |

---

## High-Risk Example

Customer:

* Income = $300
* Credit Score = 500
* Multiple missed payments
* High debt burden

Result:

```text
High Default Probability
```

---

# 16. Economic Event Simulation

Economic events introduce realistic external shocks.

---

## Event A: Agricultural Stress (2024)

### Affected Provinces

* Battambang
* Takeo
* Prey Veng

### Affected Occupation

* Farmers

### Effects

* Income decreases
* Missed payments increase
* Credit scores decline
* Delinquency rises

---

## Event B: Tourism Slowdown (2025)

### Affected Province

* Siem Reap

### Affected Segments

* Tourism SMEs
* Hospitality Businesses

### Effects

* Revenue declines
* Loan repayment quality deteriorates
* Risk increases

---

# 17. Customer Lifecycle Logic

Customers are not static.

Over time customers may:

* Become inactive
* Open new accounts
* Obtain new loans
* Close accounts
* Improve credit quality
* Deteriorate credit quality

This supports retention and lifecycle analysis.

---

# 18. Monthly Snapshot Logic

At the end of each month:

A customer snapshot record is created containing:

* Account balances
* Outstanding loan balances
* Credit score
* Risk category

This table supports:

* Trend analysis
* Forecasting
* Customer analytics
* Risk monitoring

---

# 19. Simulation Quality Principles

The simulation follows five principles:

### Realism

Customer behavior reflects plausible banking activity.

### Consistency

Relationships between variables remain logical.

### Traceability

Simulation assumptions are documented.

### Analytical Value

Generated data supports meaningful analysis.

### Reproducibility

Data can be regenerated using documented rules.

---

# 20. Simulation Summary

The Banking Risk & Business Intelligence Platform uses a behavior-driven simulation approach to model customer demographics, financial activity, lending behavior, repayment performance, credit risk, and economic shocks.

The resulting synthetic dataset is designed to resemble realistic banking operations and provide a robust foundation for business intelligence, risk analytics, forecasting, and strategic decision-making.
