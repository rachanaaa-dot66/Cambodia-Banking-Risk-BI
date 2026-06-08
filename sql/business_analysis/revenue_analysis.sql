-- =============================================================================
-- revenue_analysis.sql
-- KPI-BP-06: Revenue | KPI-BP-02: Total Deposits | KPI-BP-03: Total Loans Outstanding
-- KPI-BP-04/05: Deposit & Loan Growth Rates
-- Reference: 03_KPI_Framework.md §3 | 02_Business_Requirements.md BP-03, BP-05
-- =============================================================================

-- --------------------------------------------------------
-- 1. Total Deposits & Loans Outstanding  (KPI-BP-02, KPI-BP-03)
-- --------------------------------------------------------
SELECT
    SUM(a.current_balance)                                          AS total_deposits,
    (SELECT SUM(outstanding_balance) FROM loans
     WHERE loan_status NOT IN ('Closed'))                           AS total_loans_outstanding,
    COUNT(DISTINCT a.customer_id)                                   AS depositing_customers
FROM accounts a
WHERE a.account_status = 'Active';

-- --------------------------------------------------------
-- 2. Monthly Interest Income Estimate  (KPI-BP-06)
--    = SUM(outstanding_balance * monthly_rate) for active loans
-- --------------------------------------------------------
SELECT
    ROUND(
        SUM(outstanding_balance * (interest_rate / 100.0 / 12.0)),
        2
    )                                                               AS monthly_interest_income_est,
    ROUND(
        SUM(outstanding_balance * (interest_rate / 100.0)),
        2
    )                                                               AS annual_interest_income_est
FROM loans
WHERE loan_status IN ('Current', 'Past Due');

-- --------------------------------------------------------
-- 3. Revenue by Year (from loan payments — actual interest received)
-- --------------------------------------------------------
WITH payment_interest AS (
    SELECT
        lp.payment_id,
        lp.loan_id,
        lp.payment_date,
        lp.amount_paid,
        l.interest_rate,
        l.loan_amount,
        l.term_months,
        -- Approximate interest portion of each payment (annuity split)
        ROUND(
            lp.amount_paid * (l.interest_rate / 100.0 / 12.0)
            / ((l.interest_rate / 100.0 / 12.0) +
               CASE WHEN l.term_months > 0
                    THEN (1 - POWER(1 + l.interest_rate/100.0/12.0, -l.term_months))
                            / l.term_months
                    ELSE 0.001 END),
            2
        ) AS interest_income
    FROM loan_payments lp
    JOIN loans l ON lp.loan_id = l.loan_id
    WHERE lp.amount_paid > 0
)
SELECT
    EXTRACT(YEAR FROM payment_date)::INTEGER                        AS year,
    COUNT(*)                                                        AS payments_received,
    SUM(amount_paid)                                                AS total_payments,
    SUM(interest_income)                                            AS interest_income_est
FROM payment_interest
GROUP BY EXTRACT(YEAR FROM payment_date)
ORDER BY year;

-- --------------------------------------------------------
-- 4. Deposit Balance by Account Type  (BP-03)
-- --------------------------------------------------------
SELECT
    account_type,
    COUNT(*)                                                        AS accounts,
    SUM(current_balance)                                            AS total_balance,
    ROUND(AVG(current_balance), 2)                                  AS avg_balance,
    ROUND(
        100.0 * SUM(current_balance)
        / SUM(SUM(current_balance)) OVER (), 2
    )                                                               AS pct_of_deposits
FROM accounts
WHERE account_status = 'Active'
GROUP BY account_type
ORDER BY total_balance DESC;

-- --------------------------------------------------------
-- 5. Monthly Deposit Growth Rate  (KPI-BP-04) via Snapshots
-- --------------------------------------------------------
WITH monthly_deposits AS (
    SELECT
        snapshot_date                                               AS month,
        SUM(account_balance)                                        AS total_deposits
    FROM monthly_customer_snapshot
    GROUP BY snapshot_date
)
SELECT
    month,
    total_deposits,
    LAG(total_deposits) OVER (ORDER BY month)                       AS prev_month_deposits,
    ROUND(
        100.0 * (total_deposits - LAG(total_deposits) OVER (ORDER BY month))
        / NULLIF(LAG(total_deposits) OVER (ORDER BY month), 0),
        2
    )                                                               AS deposit_growth_pct
FROM monthly_deposits
ORDER BY month;

-- --------------------------------------------------------
-- 6. Monthly Loan Growth Rate  (KPI-BP-05) via Snapshots
-- --------------------------------------------------------
WITH monthly_loans AS (
    SELECT
        snapshot_date                                               AS month,
        SUM(total_loan_balance)                                     AS total_loans
    FROM monthly_customer_snapshot
    GROUP BY snapshot_date
)
SELECT
    month,
    total_loans,
    LAG(total_loans) OVER (ORDER BY month)                          AS prev_month_loans,
    ROUND(
        100.0 * (total_loans - LAG(total_loans) OVER (ORDER BY month))
        / NULLIF(LAG(total_loans) OVER (ORDER BY month), 0),
        2
    )                                                               AS loan_growth_pct
FROM monthly_loans
ORDER BY month;
