-- =============================================================================
-- 01_create_tables.sql
-- Runs automatically on first docker container start
-- =============================================================================

\echo 'Creating tables...'

CREATE TABLE IF NOT EXISTS branches (
    branch_id        INTEGER      NOT NULL,
    branch_name      VARCHAR(100) NOT NULL,
    province         VARCHAR(50)  NOT NULL,
    city             VARCHAR(50)  NOT NULL,
    branch_type      VARCHAR(20)  NOT NULL,
    branch_open_date DATE         NOT NULL,
    branch_manager   VARCHAR(100)
);

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
    customer_status VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id      INTEGER        NOT NULL,
    customer_id     INTEGER        NOT NULL,
    branch_id       INTEGER        NOT NULL,
    account_type    VARCHAR(50),
    open_date       DATE,
    current_balance DECIMAL(15,2),
    account_status  VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id     BIGINT         NOT NULL,
    account_id         INTEGER        NOT NULL,
    transaction_date   DATE           NOT NULL,
    transaction_type   VARCHAR(50),
    transaction_amount DECIMAL(15,2)
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id             INTEGER        NOT NULL,
    customer_id         INTEGER        NOT NULL,
    branch_id           INTEGER        NOT NULL,
    loan_type           VARCHAR(50),
    loan_amount         DECIMAL(15,2),
    interest_rate       DECIMAL(5,2),
    term_months         INTEGER,
    issue_date          DATE,
    maturity_date       DATE,
    outstanding_balance DECIMAL(15,2),
    loan_status         VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS loan_payments (
    payment_id    BIGINT         NOT NULL,
    loan_id       INTEGER        NOT NULL,
    payment_date  DATE           NOT NULL,
    amount_due    DECIMAL(15,2),
    amount_paid   DECIMAL(15,2),
    days_past_due INTEGER
);

CREATE TABLE IF NOT EXISTS credit_profiles (
    customer_id                 INTEGER       NOT NULL,
    credit_score                INTEGER,
    risk_category               VARCHAR(30),
    debt_to_income_ratio        DECIMAL(6,2),
    previous_delinquency_count  INTEGER
);

CREATE TABLE IF NOT EXISTS monthly_customer_snapshot (
    snapshot_date       DATE           NOT NULL,
    customer_id         INTEGER        NOT NULL,
    account_balance     DECIMAL(15,2),
    total_loan_balance  DECIMAL(15,2),
    credit_score        INTEGER,
    risk_category       VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS economic_events (
    event_id          INTEGER       NOT NULL,
    event_name        VARCHAR(100),
    start_date        DATE,
    end_date          DATE,
    affected_province VARCHAR(200),
    affected_sector   VARCHAR(50),
    severity          VARCHAR(20)
);

\echo 'Tables created.'
