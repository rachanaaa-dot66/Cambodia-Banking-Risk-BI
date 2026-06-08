-- =============================================================================
-- npl_ratio.sql
-- KPI-RM-02: Non-Performing Loan Ratio
-- Reference: 03_KPI_Framework.md §5 | 02_Business_Requirements.md RA-01
-- =============================================================================

-- --------------------------------------------------------
-- 1. Overall NPL Ratio (current portfolio)
-- --------------------------------------------------------
SELECT
    COUNT(*)                                                        AS total_loans,
    SUM(outstanding_balance)                                        AS total_portfolio,

    COUNT(*) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
                                                                    AS npl_count,
    SUM(outstanding_balance) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
                                                                    AS npl_balance,

    ROUND(
        100.0 * SUM(outstanding_balance) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
        / NULLIF(SUM(outstanding_balance), 0),
        2
    )                                                               AS npl_ratio_pct

FROM loans
WHERE loan_status NOT IN ('Closed');

-- --------------------------------------------------------
-- 2. NPL Ratio by Loan Type
-- --------------------------------------------------------
SELECT
    loan_type,
    COUNT(*)                                                        AS loans,
    SUM(outstanding_balance)                                        AS portfolio,
    SUM(outstanding_balance) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
                                                                    AS npl_balance,
    ROUND(
        100.0 * SUM(outstanding_balance) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
        / NULLIF(SUM(outstanding_balance), 0),
        2
    )                                                               AS npl_ratio_pct
FROM loans
WHERE loan_status NOT IN ('Closed')
GROUP BY loan_type
ORDER BY npl_ratio_pct DESC;

-- --------------------------------------------------------
-- 3. NPL Ratio by Province  (RA-04)
-- --------------------------------------------------------
SELECT
    c.province,
    COUNT(l.loan_id)                                                AS loans,
    SUM(l.outstanding_balance)                                      AS portfolio,
    SUM(l.outstanding_balance) FILTER (WHERE l.loan_status IN ('Non-Performing','Defaulted'))
                                                                    AS npl_balance,
    ROUND(
        100.0 * SUM(l.outstanding_balance) FILTER (WHERE l.loan_status IN ('Non-Performing','Defaulted'))
        / NULLIF(SUM(l.outstanding_balance), 0),
        2
    )                                                               AS npl_ratio_pct
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
WHERE l.loan_status NOT IN ('Closed')
GROUP BY c.province
ORDER BY npl_ratio_pct DESC;

-- --------------------------------------------------------
-- 4. NPL Trend by Year (from loan issue dates as proxy)
-- --------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM issue_date)::INTEGER                          AS year,
    COUNT(*) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
                                                                    AS npl_loans,
    COUNT(*)                                                        AS total_loans,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE loan_status IN ('Non-Performing','Defaulted'))
        / NULLIF(COUNT(*), 0),
        2
    )                                                               AS npl_ratio_pct
FROM loans
WHERE loan_status NOT IN ('Closed')
GROUP BY EXTRACT(YEAR FROM issue_date)
ORDER BY year;

-- --------------------------------------------------------
-- 5. NPL Ratio — Monthly Trend from Snapshots  (RA-05)
-- --------------------------------------------------------
SELECT
    DATE_TRUNC('month', snapshot_date)::DATE                        AS month,
    COUNT(*) FILTER (WHERE risk_category IN ('High Risk','Very High Risk'))
                                                                    AS high_risk_customers,
    ROUND(
        100.0 * SUM(total_loan_balance) FILTER (WHERE risk_category IN ('High Risk','Very High Risk'))
        / NULLIF(SUM(total_loan_balance), 0),
        2
    )                                                               AS estimated_npl_ratio_pct
FROM monthly_customer_snapshot
GROUP BY DATE_TRUNC('month', snapshot_date)
ORDER BY month;
