-- =============================================================================
-- default_rate.sql
-- KPI-RM-01: Default Rate | KPI-RM-03: Delinquency Rate
-- Reference: 03_KPI_Framework.md §5 | 02_Business_Requirements.md RA-02, RA-03
-- =============================================================================

-- --------------------------------------------------------
-- 1. Portfolio-Level Default & Delinquency Rates
-- --------------------------------------------------------
SELECT
    COUNT(*)                                                            AS total_active_loans,

    COUNT(*) FILTER (WHERE loan_status = 'Defaulted')                  AS defaulted_loans,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE loan_status = 'Defaulted')
        / NULLIF(COUNT(*), 0), 2
    )                                                                   AS default_rate_pct,

    COUNT(*) FILTER (WHERE loan_status = 'Past Due')                    AS past_due_loans,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE loan_status = 'Past Due')
        / NULLIF(COUNT(*), 0), 2
    )                                                                   AS delinquency_rate_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE loan_status IN ('Past Due','Non-Performing','Defaulted'))
        / NULLIF(COUNT(*), 0), 2
    )                                                                   AS combined_stressed_rate_pct

FROM loans
WHERE loan_status NOT IN ('Closed');

-- --------------------------------------------------------
-- 2. Default Rate by Occupation Segment  (RA-03)
-- --------------------------------------------------------
SELECT
    c.occupation,
    COUNT(l.loan_id)                                                    AS total_loans,
    COUNT(l.loan_id) FILTER (WHERE l.loan_status = 'Defaulted')         AS defaults,
    ROUND(
        100.0 * COUNT(l.loan_id) FILTER (WHERE l.loan_status = 'Defaulted')
        / NULLIF(COUNT(l.loan_id), 0), 2
    )                                                                   AS default_rate_pct
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
WHERE l.loan_status NOT IN ('Closed')
GROUP BY c.occupation
ORDER BY default_rate_pct DESC;

-- --------------------------------------------------------
-- 3. Default Rate by Loan Type  (RA-02)
-- --------------------------------------------------------
SELECT
    loan_type,
    COUNT(*)                                                            AS total_loans,
    COUNT(*) FILTER (WHERE loan_status = 'Defaulted')                  AS defaults,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE loan_status = 'Defaulted')
        / NULLIF(COUNT(*), 0), 2
    )                                                                   AS default_rate_pct,
    SUM(outstanding_balance) FILTER (WHERE loan_status = 'Defaulted')  AS defaulted_balance
FROM loans
WHERE loan_status NOT IN ('Closed')
GROUP BY loan_type
ORDER BY default_rate_pct DESC;

-- --------------------------------------------------------
-- 4. Delinquency Buckets from loan_payments (30/60/90+ DPD)
-- --------------------------------------------------------
WITH latest_payment AS (
    SELECT
        loan_id,
        MAX(payment_date)   AS last_payment_date,
        MAX(days_past_due)  AS max_dpd
    FROM loan_payments
    GROUP BY loan_id
)
SELECT
    CASE
        WHEN max_dpd = 0           THEN 'Current (0 DPD)'
        WHEN max_dpd BETWEEN 1 AND 29  THEN '1-29 DPD'
        WHEN max_dpd BETWEEN 30 AND 59 THEN '30-59 DPD'
        WHEN max_dpd BETWEEN 60 AND 89 THEN '60-89 DPD'
        ELSE '90+ DPD'
    END                                                                 AS dpd_bucket,
    COUNT(*)                                                            AS loan_count,
    SUM(l.outstanding_balance)                                          AS total_exposure
FROM latest_payment lp
JOIN loans l ON lp.loan_id = l.loan_id
WHERE l.loan_status NOT IN ('Closed')
GROUP BY dpd_bucket
ORDER BY
    MIN(max_dpd);

-- --------------------------------------------------------
-- 5. Monthly Delinquency Trend
-- --------------------------------------------------------
SELECT
    DATE_TRUNC('month', payment_date)::DATE                             AS month,
    COUNT(DISTINCT loan_id)                                             AS loans_with_payment,
    COUNT(DISTINCT loan_id) FILTER (WHERE days_past_due > 0)           AS delinquent_loans,
    ROUND(
        100.0 * COUNT(DISTINCT loan_id) FILTER (WHERE days_past_due > 0)
        / NULLIF(COUNT(DISTINCT loan_id), 0), 2
    )                                                                   AS delinquency_rate_pct,
    AVG(days_past_due) FILTER (WHERE days_past_due > 0)                AS avg_dpd_delinquent
FROM loan_payments
GROUP BY DATE_TRUNC('month', payment_date)
ORDER BY month;
