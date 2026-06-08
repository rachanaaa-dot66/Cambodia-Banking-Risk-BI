-- =============================================================================
-- branch_performance.sql
-- KPI-BR-01: Revenue by Branch | KPI-BR-02: Loan Portfolio by Branch
-- KPI-BR-03: Deposits by Branch | KPI-BR-04: Customer Growth by Branch
-- Reference: 03_KPI_Framework.md §6 | 02_Business_Requirements.md BR-01-04
-- =============================================================================

-- --------------------------------------------------------
-- 1. Branch Scorecard — Customers, Deposits, Loans  (KPI-BR-01 to 04)
-- --------------------------------------------------------
SELECT
    b.branch_id,
    b.branch_name,
    b.province,
    b.branch_type,

    -- Customers
    COUNT(DISTINCT c.customer_id)                                   AS total_customers,
    COUNT(DISTINCT c.customer_id) FILTER (WHERE c.customer_status = 'Active')
                                                                    AS active_customers,

    -- Deposits  (KPI-BR-03)
    COALESCE(SUM(a.current_balance) FILTER (WHERE a.account_status = 'Active'), 0)
                                                                    AS total_deposits,

    -- Loans  (KPI-BR-02)
    COALESCE(SUM(l.outstanding_balance) FILTER (WHERE l.loan_status NOT IN ('Closed')), 0)
                                                                    AS total_loans_outstanding,

    -- Revenue estimate  (KPI-BR-01)
    ROUND(
        COALESCE(SUM(l.outstanding_balance * l.interest_rate / 100.0 / 12.0)
            FILTER (WHERE l.loan_status IN ('Current','Past Due')), 0),
        2
    )                                                               AS monthly_interest_income_est

FROM branches b
LEFT JOIN customers c  ON b.branch_id = c.branch_id
LEFT JOIN accounts  a  ON b.branch_id = a.branch_id
LEFT JOIN loans     l  ON b.branch_id = l.branch_id
GROUP BY b.branch_id, b.branch_name, b.province, b.branch_type
ORDER BY total_deposits DESC;

-- --------------------------------------------------------
-- 2. Branch Customer Growth by Year  (KPI-BR-04)
-- --------------------------------------------------------
SELECT
    b.branch_name,
    b.province,
    EXTRACT(YEAR FROM c.join_date)::INTEGER                         AS year,
    COUNT(c.customer_id)                                            AS new_customers
FROM customers c
JOIN branches b ON c.branch_id = b.branch_id
GROUP BY b.branch_name, b.province, EXTRACT(YEAR FROM c.join_date)
ORDER BY b.branch_name, year;

-- --------------------------------------------------------
-- 3. Top 10 Branches by Deposit Volume
-- --------------------------------------------------------
SELECT
    b.branch_name,
    b.province,
    b.branch_type,
    SUM(a.current_balance)                                          AS total_deposits,
    COUNT(DISTINCT a.customer_id)                                   AS depositing_customers,
    ROUND(AVG(a.current_balance), 2)                                AS avg_balance_per_account
FROM accounts a
JOIN branches b ON a.branch_id = b.branch_id
WHERE a.account_status = 'Active'
GROUP BY b.branch_name, b.province, b.branch_type
ORDER BY total_deposits DESC
LIMIT 10;

-- --------------------------------------------------------
-- 4. Branch Loan Portfolio — Monthly Trend (via snapshot proxy)
-- --------------------------------------------------------
SELECT
    b.branch_name,
    b.province,
    EXTRACT(YEAR FROM l.issue_date)::INTEGER                        AS year,
    COUNT(l.loan_id)                                                AS loans_issued,
    SUM(l.loan_amount)                                              AS total_originated,
    SUM(l.outstanding_balance) FILTER (WHERE l.loan_status NOT IN ('Closed'))
                                                                    AS current_outstanding
FROM loans l
JOIN branches b ON l.branch_id = b.branch_id
GROUP BY b.branch_name, b.province, EXTRACT(YEAR FROM l.issue_date)
ORDER BY b.branch_name, year;

-- --------------------------------------------------------
-- 5. Urban vs Rural Branch Comparison
-- --------------------------------------------------------
SELECT
    b.branch_type,
    COUNT(DISTINCT b.branch_id)                                     AS branches,
    COUNT(DISTINCT c.customer_id)                                   AS customers,
    SUM(a.current_balance)                                          AS total_deposits,
    SUM(l.outstanding_balance) FILTER (WHERE l.loan_status NOT IN ('Closed'))
                                                                    AS total_loans,
    ROUND(AVG(cp.credit_score), 1)                                  AS avg_credit_score
FROM branches b
LEFT JOIN customers c       ON b.branch_id = c.branch_id
LEFT JOIN accounts  a       ON a.customer_id = c.customer_id AND a.account_status = 'Active'
LEFT JOIN loans     l       ON l.customer_id = c.customer_id
LEFT JOIN credit_profiles cp ON cp.customer_id = c.customer_id
GROUP BY b.branch_type;
