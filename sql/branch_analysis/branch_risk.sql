-- =============================================================================
-- branch_risk.sql
-- KPI-BR-05: NPL Ratio by Branch | Branch-Level Credit Risk
-- Reference: 03_KPI_Framework.md §6 | 02_Business_Requirements.md BR-03, BR-04
-- =============================================================================

-- --------------------------------------------------------
-- 1. NPL Ratio by Branch  (KPI-BR-05)
-- --------------------------------------------------------
SELECT
    b.branch_id,
    b.branch_name,
    b.province,
    b.branch_type,

    COUNT(l.loan_id)                                                AS total_loans,
    SUM(l.outstanding_balance)                                      AS total_portfolio,

    COUNT(l.loan_id) FILTER (WHERE l.loan_status IN ('Non-Performing','Defaulted'))
                                                                    AS npl_count,
    COALESCE(
        SUM(l.outstanding_balance) FILTER (WHERE l.loan_status IN ('Non-Performing','Defaulted')),
        0
    )                                                               AS npl_balance,

    ROUND(
        100.0 * COALESCE(
            SUM(l.outstanding_balance) FILTER (WHERE l.loan_status IN ('Non-Performing','Defaulted')),
            0
        ) / NULLIF(SUM(l.outstanding_balance), 0),
        2
    )                                                               AS npl_ratio_pct,

    ROUND(AVG(cp.credit_score), 1)                                  AS avg_credit_score

FROM branches b
LEFT JOIN loans l ON b.branch_id = l.branch_id AND l.loan_status NOT IN ('Closed')
LEFT JOIN credit_profiles cp ON l.customer_id = cp.customer_id
GROUP BY b.branch_id, b.branch_name, b.province, b.branch_type
ORDER BY npl_ratio_pct DESC NULLS LAST;

-- --------------------------------------------------------
-- 2. Branch Risk Distribution — Customer Count by Risk Category
-- --------------------------------------------------------
SELECT
    b.branch_name,
    b.province,
    cp.risk_category,
    COUNT(DISTINCT cp.customer_id)                                  AS customers,
    ROUND(
        100.0 * COUNT(DISTINCT cp.customer_id)
        / SUM(COUNT(DISTINCT cp.customer_id)) OVER (PARTITION BY b.branch_name),
        2
    )                                                               AS pct_of_branch
FROM credit_profiles cp
JOIN customers c ON cp.customer_id = c.customer_id
JOIN branches  b ON c.branch_id    = b.branch_id
GROUP BY b.branch_name, b.province, cp.risk_category
ORDER BY b.branch_name,
    CASE cp.risk_category
        WHEN 'Very Low Risk'  THEN 1
        WHEN 'Low Risk'       THEN 2
        WHEN 'Medium Risk'    THEN 3
        WHEN 'High Risk'      THEN 4
        WHEN 'Very High Risk' THEN 5
    END;

-- --------------------------------------------------------
-- 3. Branches with Highest Delinquency (from payments)
-- --------------------------------------------------------
WITH branch_dpd AS (
    SELECT
        l.branch_id,
        COUNT(DISTINCT lp.loan_id)                                  AS loans_with_payment,
        COUNT(DISTINCT lp.loan_id) FILTER (WHERE lp.days_past_due > 30)
                                                                    AS loans_30dpd_plus,
        ROUND(AVG(lp.days_past_due) FILTER (WHERE lp.days_past_due > 0), 1)
                                                                    AS avg_dpd_delinquent
    FROM loan_payments lp
    JOIN loans l ON lp.loan_id = l.loan_id
    GROUP BY l.branch_id
)
SELECT
    b.branch_name,
    b.province,
    bd.loans_with_payment,
    bd.loans_30dpd_plus,
    ROUND(
        100.0 * bd.loans_30dpd_plus
        / NULLIF(bd.loans_with_payment, 0), 2
    )                                                               AS delinquency_30d_rate_pct,
    bd.avg_dpd_delinquent
FROM branch_dpd bd
JOIN branches b ON bd.branch_id = b.branch_id
ORDER BY delinquency_30d_rate_pct DESC;

-- --------------------------------------------------------
-- 4. Economic Event Impact — Branch Risk Before/After
--    Agricultural Stress 2024: Battambang, Takeo, Prey Veng
-- --------------------------------------------------------
SELECT
    c.province,
    CASE
        WHEN s.snapshot_date < DATE '2024-03-01' THEN 'Pre-Event (2021-2024 Feb)'
        WHEN s.snapshot_date <= DATE '2024-12-31' THEN 'During Event (2024)'
        ELSE 'Post-Event (2025)'
    END                                                             AS period,
    ROUND(AVG(s.credit_score), 1)                                   AS avg_credit_score,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE s.risk_category IN ('High Risk','Very High Risk'))
        / NULLIF(COUNT(*), 0), 2
    )                                                               AS high_risk_pct
FROM monthly_customer_snapshot s
JOIN customers c ON s.customer_id = c.customer_id
WHERE c.province IN ('Battambang','Takeo','Prey Veng')
  AND c.occupation = 'Farmer'
GROUP BY c.province, period
ORDER BY c.province, MIN(s.snapshot_date);
