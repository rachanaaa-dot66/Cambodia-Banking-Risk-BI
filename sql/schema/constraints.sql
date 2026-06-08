-- =============================================================================
-- constraints.sql
-- Cambodia Banking Risk & Business Intelligence Platform
-- Reference: 04_Data_Model.md §14 (Relationship Summary)
-- Run AFTER data is loaded (constraints applied post-insert for performance)
-- =============================================================================

-- --------------------------------------------------------
-- Primary Keys
-- --------------------------------------------------------
ALTER TABLE branches                  ADD PRIMARY KEY (branch_id);
ALTER TABLE customers                 ADD PRIMARY KEY (customer_id);
ALTER TABLE accounts                  ADD PRIMARY KEY (account_id);
ALTER TABLE transactions              ADD PRIMARY KEY (transaction_id);
ALTER TABLE loans                     ADD PRIMARY KEY (loan_id);
ALTER TABLE loan_payments             ADD PRIMARY KEY (payment_id);
ALTER TABLE credit_profiles           ADD PRIMARY KEY (customer_id);
ALTER TABLE economic_events           ADD PRIMARY KEY (event_id);

-- Composite PK for snapshot (doc §12)
ALTER TABLE monthly_customer_snapshot
    ADD PRIMARY KEY (snapshot_date, customer_id);

-- --------------------------------------------------------
-- Foreign Keys  (doc §14)
-- --------------------------------------------------------

-- customers → branches
ALTER TABLE customers
    ADD CONSTRAINT fk_customers_branch
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id);

-- accounts → customers, branches
ALTER TABLE accounts
    ADD CONSTRAINT fk_accounts_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE accounts
    ADD CONSTRAINT fk_accounts_branch
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id);

-- transactions → accounts
ALTER TABLE transactions
    ADD CONSTRAINT fk_transactions_account
    FOREIGN KEY (account_id) REFERENCES accounts(account_id);

-- loans → customers, branches
ALTER TABLE loans
    ADD CONSTRAINT fk_loans_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE loans
    ADD CONSTRAINT fk_loans_branch
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id);

-- loan_payments → loans
ALTER TABLE loan_payments
    ADD CONSTRAINT fk_payments_loan
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id);

-- credit_profiles → customers  (1-to-1)
ALTER TABLE credit_profiles
    ADD CONSTRAINT fk_credit_profiles_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- monthly_customer_snapshot → customers
ALTER TABLE monthly_customer_snapshot
    ADD CONSTRAINT fk_snapshot_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- --------------------------------------------------------
-- Check Constraints
-- --------------------------------------------------------
ALTER TABLE customers    ADD CONSTRAINT chk_age        CHECK (age BETWEEN 18 AND 100);
ALTER TABLE loans        ADD CONSTRAINT chk_loan_amt   CHECK (loan_amount > 0);
ALTER TABLE loans        ADD CONSTRAINT chk_maturity   CHECK (maturity_date > issue_date);
ALTER TABLE credit_profiles ADD CONSTRAINT chk_score   CHECK (credit_score BETWEEN 300 AND 850);
ALTER TABLE credit_profiles ADD CONSTRAINT chk_dti     CHECK (debt_to_income_ratio BETWEEN 0 AND 2);

-- --------------------------------------------------------
-- Performance Indexes
-- --------------------------------------------------------

-- Transaction lookups
CREATE INDEX idx_txn_account_date   ON transactions (account_id, transaction_date);
CREATE INDEX idx_txn_date           ON transactions (transaction_date);
CREATE INDEX idx_txn_type           ON transactions (transaction_type);

-- Loan lookups
CREATE INDEX idx_loan_customer      ON loans (customer_id);
CREATE INDEX idx_loan_branch        ON loans (branch_id);
CREATE INDEX idx_loan_status        ON loans (loan_status);
CREATE INDEX idx_loan_type          ON loans (loan_type);

-- Payment lookups
CREATE INDEX idx_pmt_loan_date      ON loan_payments (loan_id, payment_date);
CREATE INDEX idx_pmt_dpd            ON loan_payments (days_past_due);

-- Customer lookups
CREATE INDEX idx_cust_branch        ON customers (branch_id);
CREATE INDEX idx_cust_province      ON customers (province);
CREATE INDEX idx_cust_status        ON customers (customer_status);
CREATE INDEX idx_cust_join          ON customers (join_date);

-- Account lookups
CREATE INDEX idx_acc_customer       ON accounts (customer_id);
CREATE INDEX idx_acc_type           ON accounts (account_type);
CREATE INDEX idx_acc_status         ON accounts (account_status);

-- Snapshot lookups
CREATE INDEX idx_snap_cust          ON monthly_customer_snapshot (customer_id);
CREATE INDEX idx_snap_date          ON monthly_customer_snapshot (snapshot_date);
CREATE INDEX idx_snap_risk          ON monthly_customer_snapshot (risk_category);

-- Credit profile lookups
CREATE INDEX idx_cp_risk            ON credit_profiles (risk_category);
CREATE INDEX idx_cp_score           ON credit_profiles (credit_score);
