-- =============================================================================
-- exposure_analysis.sql
-- KPI-RM-05: Exposure at Risk | KPI-RM-04: Average Credit Score
-- KPI-RM-06: Risk Distribution
-- Reference: 03_KPI_Framework.md §5 | 02_Business_Requirements.md RA-04, RA-05
-- =============================================================================

-- --------------------------------------------------------
-- 1. Exposure at Risk — High & Very High Risk Customers
-- --------------------------------------------------------
SELECT
    cp.risk_category,
    COUNT(DISTINCT cp.customer_id)                                  AS customers,
    SUM(l.outstanding_balance)                                      AS exposure_at_risk,
    ROUND(AVG(cp.credit_score), 1)                                  AS avg_credit_score,
    ROUND(AVG(cp.debt_to_income_ratio), 4)                          AS avg_dti
FROM credit_profiles cp
JOIN loans l ON cp.customer_id = l.customer_id
WHERE cp.risk_category IN ('High Risk', 'Very High Risk')
  AND l.loan_status NOT IN ('Closed')
GROUP BY cp.risk_category
ORDER BY exposure_at_risk DESC;

-- --------------------------------------------------------
-- 2. Risk Distribution — Customer Count & Exposure
-- --------------------------------------------------------
SELECT
    cp.risk_category,
    COUNT(DISTINCT cp.customer_id)                                  AS customer_count,
    ROUND(
        100.0 * COUNT(DISTINCT cp.customer_id)
        / SUM(COUNT(DISTINCT cp.customer_id)) OVER (), 2
    )                                                               AS pct_customers,
    COALESCE(SUM(l.outstanding_balance), 0)                         AS total_exposure,
    ROUND(AVG(cp.credit_score), 1)                                  AS avg_credit_score
FROM credit_profiles cp
LEFT JOIN loans l ON cp.customer_id = l.customer_id
    AND l.loan_status NOT IN ('Closed')
GROUP BY cp.risk_category
ORDER BY
    CASE cp.risk_category
        WHEN 'Very Low Risk'  THEN 1
        WHEN 'Low Risk'       THEN 2
        WHEN 'Medium Risk'    THEN 3
        WHEN 'High Risk'      THEN 4
        WHEN 'Very High Risk' THEN 5
        ELSE 6
    END;

-- --------------------------------------------------------
-- 3. Average Credit Score by Occupation & Province
-- --------------------------------------------------------
SELECT
    c.occupation,
    c.province,
    COUNT(cp.customer_id)                                           AS customers,
    ROUND(AVG(cp.credit_score), 1)                                  AS avg_credit_score,
    MIN(cp.credit_score)                                            AS min_score,
    MAX(cp.credit_score)                                            AS max_score,
    ROUND(AVG(cp.debt_to_income_ratio), 4)                          AS avg_dti
FROM credit_profiles cp
JOIN customers c ON cp.customer_id = c.customer_id
GROUP BY c.occupation, c.province
ORDER BY avg_credit_score;

-- --------------------------------------------------------
-- 4. Credit Score Migration — 2021 → 2025 (via snapshots)
-- --------------------------------------------------------
WITH first_snap AS (
    SELECT
        customer_id,
        credit_score AS initial_score
    FROM monthly_customer_snapshot
    WHERE snapshot_date = (SELECT MIN(snapshot_date) FROM monthly_customer_snapshot)
),
last_snap AS (
    SELECT
        customer_id,
        credit_score AS final_score
    FROM monthly_customer_snapshot
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM monthly_customer_snapshot)
)
SELECT
    CASE
        WHEN (ls.final_score - fs.initial_score) >= 50  THEN 'Improved Significantly'
        WHEN (ls.final_score - fs.initial_score) >= 10  THEN 'Improved'
        WHEN (ls.final_score - fs.initial_score) >= -9  THEN 'Stable'
        WHEN (ls.final_score - fs.initial_score) >= -49 THEN 'Deteriorated'
        ELSE 'Deteriorated Significantly'
    END                                                             AS migration_band,
    COUNT(*)                                                        AS customer_count,
    ROUND(AVG(ls.final_score - fs.initial_score), 1)                AS avg_score_change
FROM first_snap fs
JOIN last_snap  ls ON fs.customer_id = ls.customer_id
GROUP BY migration_band
ORDER BY MIN(ls.final_score - fs.initial_score) DESC;

-- --------------------------------------------------------
-- 5. Exposure at Risk — Monthly Trend (RA-05)
-- --------------------------------------------------------
SELECT
    DATE_TRUNC('month', s.snapshot_date)::DATE                      AS month,
    SUM(s.total_loan_balance) FILTER (WHERE s.risk_category IN ('High Risk','Very High Risk'))
                                                                    AS high_risk_exposure,
    SUM(s.total_loan_balance)                                        AS total_loan_exposure,
    ROUND(
        100.0 * SUM(s.total_loan_balance)
            FILTER (WHERE s.risk_category IN ('High Risk','Very High Risk'))
        / NULLIF(SUM(s.total_loan_balance), 0),
        2
    )                                                               AS ear_ratio_pct
FROM monthly_customer_snapshot s
GROUP BY DATE_TRUNC('month', s.snapshot_date)
ORDER BY month;
