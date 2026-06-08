-- =============================================================================
-- create_tables.sql
-- Cambodia Banking Risk & Business Intelligence Platform
-- Reference: 04_Data_Model.md §5-§13
-- =============================================================================

-- --------------------------------------------------------
-- 1. branches
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS branches (
    branch_id        INTEGER      NOT NULL,
    branch_name      VARCHAR(100) NOT NULL,
    province         VARCHAR(50)  NOT NULL,
    city             VARCHAR(50)  NOT NULL,
    branch_type      VARCHAR(20)  NOT NULL,   -- Urban | Rural
    branch_open_date DATE         NOT NULL,
    branch_manager   VARCHAR(100)
);

-- --------------------------------------------------------
-- 2. customers
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id     INTEGER        NOT NULL,
    branch_id       INTEGER        NOT NULL,
    gender          VARCHAR(10),
    birth_date      DATE,
    age             INTEGER,
    occupation      VARCHAR(50),
    marital_status  VARCHAR(20),
    province        VARCHAR(50),
    monthly_income  DECIMAL(12,2),
    join_date       DATE,
    customer_status VARCHAR(20)    -- Active | Inactive | Closed
);

-- --------------------------------------------------------
-- 3. accounts
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    account_id      INTEGER        NOT NULL,
    customer_id     INTEGER        NOT NULL,
    branch_id       INTEGER        NOT NULL,
    account_type    VARCHAR(50),               -- Savings | Fixed Deposit | Payroll | Business
    open_date       DATE,
    current_balance DECIMAL(15,2),
    account_status  VARCHAR(20)                -- Active | Dormant | Closed
);

-- --------------------------------------------------------
-- 4. transactions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id     BIGINT         NOT NULL,
    account_id         INTEGER        NOT NULL,
    transaction_date   DATE           NOT NULL,
    transaction_type   VARCHAR(50),             -- Deposit | Withdrawal | Transfer | Loan Payment | Interest Credit
    transaction_amount DECIMAL(15,2)
);

-- --------------------------------------------------------
-- 5. loans
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS loans (
    loan_id             INTEGER        NOT NULL,
    customer_id         INTEGER        NOT NULL,
    branch_id           INTEGER        NOT NULL,
    loan_type           VARCHAR(50),             -- Personal | Housing | SME | Agriculture | Vehicle
    loan_amount         DECIMAL(15,2),
    interest_rate       DECIMAL(5,2),
    term_months         INTEGER,
    issue_date          DATE,
    maturity_date       DATE,
    outstanding_balance DECIMAL(15,2),
    loan_status         VARCHAR(30)              -- Current | Past Due | Non-Performing | Defaulted | Closed
);

-- --------------------------------------------------------
-- 6. loan_payments
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS loan_payments (
    payment_id    BIGINT         NOT NULL,
    loan_id       INTEGER        NOT NULL,
    payment_date  DATE           NOT NULL,
    amount_due    DECIMAL(15,2),
    amount_paid   DECIMAL(15,2),
    days_past_due INTEGER
);

-- --------------------------------------------------------
-- 7. credit_profiles  (one record per customer)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS credit_profiles (
    customer_id                 INTEGER       NOT NULL,
    credit_score                INTEGER,
    risk_category               VARCHAR(30),   -- Very Low Risk | Low Risk | Medium Risk | High Risk | Very High Risk
    debt_to_income_ratio        DECIMAL(6,2),
    previous_delinquency_count  INTEGER
);

-- --------------------------------------------------------
-- 8. monthly_customer_snapshot
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS monthly_customer_snapshot (
    snapshot_date       DATE           NOT NULL,
    customer_id         INTEGER        NOT NULL,
    account_balance     DECIMAL(15,2),
    total_loan_balance  DECIMAL(15,2),
    credit_score        INTEGER,
    risk_category       VARCHAR(30)
);

-- --------------------------------------------------------
-- 9. economic_events
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS economic_events (
    event_id          INTEGER       NOT NULL,
    event_name        VARCHAR(100),
    start_date        DATE,
    end_date          DATE,
    affected_province VARCHAR(50),
    affected_sector   VARCHAR(50),
    severity          VARCHAR(20)    -- Low | Medium | High
);
