-- =============================================================================
-- 02_constraints.sql
-- Applied after tables are created
-- =============================================================================

\echo 'Applying constraints and indexes...'

-- Primary Keys
ALTER TABLE branches                  ADD PRIMARY KEY (branch_id);
ALTER TABLE customers                 ADD PRIMARY KEY (customer_id);
ALTER TABLE accounts                  ADD PRIMARY KEY (account_id);
ALTER TABLE transactions              ADD PRIMARY KEY (transaction_id);
ALTER TABLE loans                     ADD PRIMARY KEY (loan_id);
ALTER TABLE loan_payments             ADD PRIMARY KEY (payment_id);
ALTER TABLE credit_profiles           ADD PRIMARY KEY (customer_id);
ALTER TABLE economic_events           ADD PRIMARY KEY (event_id);
ALTER TABLE monthly_customer_snapshot ADD PRIMARY KEY (snapshot_date, customer_id);

-- Foreign Keys
ALTER TABLE customers     ADD CONSTRAINT fk_customers_branch    FOREIGN KEY (branch_id)   REFERENCES branches(branch_id);
ALTER TABLE accounts      ADD CONSTRAINT fk_accounts_customer   FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE accounts      ADD CONSTRAINT fk_accounts_branch     FOREIGN KEY (branch_id)   REFERENCES branches(branch_id);
ALTER TABLE transactions  ADD CONSTRAINT fk_transactions_account FOREIGN KEY (account_id) REFERENCES accounts(account_id);
ALTER TABLE loans         ADD CONSTRAINT fk_loans_customer      FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE loans         ADD CONSTRAINT fk_loans_branch        FOREIGN KEY (branch_id)   REFERENCES branches(branch_id);
ALTER TABLE loan_payments ADD CONSTRAINT fk_payments_loan       FOREIGN KEY (loan_id)     REFERENCES loans(loan_id);
ALTER TABLE credit_profiles ADD CONSTRAINT fk_cp_customer       FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE monthly_customer_snapshot ADD CONSTRAINT fk_snap_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- Indexes
CREATE INDEX idx_cust_branch    ON customers (branch_id);
CREATE INDEX idx_cust_province  ON customers (province);
CREATE INDEX idx_cust_status    ON customers (customer_status);
CREATE INDEX idx_acc_customer   ON accounts  (customer_id);
CREATE INDEX idx_acc_type       ON accounts  (account_type);
CREATE INDEX idx_txn_account    ON transactions (account_id);
CREATE INDEX idx_txn_date       ON transactions (transaction_date);
CREATE INDEX idx_loan_customer  ON loans (customer_id);
CREATE INDEX idx_loan_status    ON loans (loan_status);
CREATE INDEX idx_pmt_loan       ON loan_payments (loan_id);
CREATE INDEX idx_pmt_dpd        ON loan_payments (days_past_due);
CREATE INDEX idx_snap_cust      ON monthly_customer_snapshot (customer_id);
CREATE INDEX idx_snap_date      ON monthly_customer_snapshot (snapshot_date);
CREATE INDEX idx_cp_risk        ON credit_profiles (risk_category);

\echo 'Constraints and indexes applied.'
