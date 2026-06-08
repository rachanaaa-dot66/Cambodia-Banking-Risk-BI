-- =============================================================================
-- customer_growth.sql
-- KPI-CA-01: Active Customers | KPI-CA-02: New Acquisition | KPI-CA-03: Retention
-- Reference: 03_KPI_Framework.md §4 | 02_Business_Requirements.md BP-01, CA-01-04
-- =============================================================================

-- --------------------------------------------------------
-- 1. Total Active Customers  (KPI-BP-01, KPI-CA-01)
-- --------------------------------------------------------
SELECT
    COUNT(DISTINCT customer_id)                                     AS total_customers,
    COUNT(DISTINCT customer_id) FILTER (WHERE customer_status = 'Active')
                                                                    AS active_customers,
    COUNT(DISTINCT customer_id) FILTER (WHERE customer_status = 'Inactive')
                                                                    AS inactive_customers,
    COUNT(DISTINCT customer_id) FILTER (WHERE customer_status = 'Closed')
                                                                    AS closed_customers
FROM customers;

-- --------------------------------------------------------
-- 2. New Customer Acquisition by Month  (KPI-CA-02)
-- --------------------------------------------------------
SELECT
    DATE_TRUNC('month', join_date)::DATE                            AS month,
    COUNT(customer_id)                                              AS new_customers,
    SUM(COUNT(customer_id)) OVER (ORDER BY DATE_TRUNC('month', join_date))
                                                                    AS cumulative_customers
FROM customers
GROUP BY DATE_TRUNC('month', join_date)
ORDER BY month;

-- --------------------------------------------------------
-- 3. New Customer Acquisition by Year & Province
-- --------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM join_date)::INTEGER                           AS year,
    province,
    COUNT(customer_id)                                              AS new_customers
FROM customers
GROUP BY EXTRACT(YEAR FROM join_date), province
ORDER BY year, new_customers DESC;

-- --------------------------------------------------------
-- 4. Customer Retention Rate by Year  (KPI-CA-03)
--    Retained = Active at end of year / Active at start of year
-- --------------------------------------------------------
WITH yearly AS (
    SELECT
        EXTRACT(YEAR FROM join_date)::INTEGER           AS cohort_year,
        customer_id,
        customer_status
    FROM customers
)
SELECT
    cohort_year,
    COUNT(customer_id)                                              AS cohort_size,
    COUNT(customer_id) FILTER (WHERE customer_status = 'Active')    AS retained,
    ROUND(
        100.0 * COUNT(customer_id) FILTER (WHERE customer_status = 'Active')
        / NULLIF(COUNT(customer_id), 0), 2
    )                                                               AS retention_rate_pct
FROM yearly
GROUP BY cohort_year
ORDER BY cohort_year;

-- --------------------------------------------------------
-- 5. Customers with Transactions in Last 90 Days  (KPI-CA-01 active definition)
--    Using MAX transaction_date proxy for "last 90 days before Dec-2025"
-- --------------------------------------------------------
SELECT
    COUNT(DISTINCT a.customer_id)                                   AS customers_transacted_last_90d
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
WHERE t.transaction_date >= DATE '2025-12-31' - INTERVAL '90 days';

-- --------------------------------------------------------
-- 6. Customer Segmentation by Occupation & Income Band  (CA-02, ST-02)
-- --------------------------------------------------------
SELECT
    occupation,
    CASE
        WHEN monthly_income < 300  THEN 'Low Income (<$300)'
        WHEN monthly_income < 700  THEN 'Lower-Mid ($300-699)'
        WHEN monthly_income < 1500 THEN 'Mid ($700-1499)'
        ELSE 'High (≥$1500)'
    END                                                             AS income_band,
    COUNT(customer_id)                                              AS customers,
    ROUND(AVG(monthly_income), 2)                                   AS avg_income
FROM customers
WHERE customer_status = 'Active'
GROUP BY occupation, income_band
ORDER BY occupation, MIN(monthly_income);

-- --------------------------------------------------------
-- 7. Monthly Active Customer Trend from Snapshots
-- --------------------------------------------------------
SELECT
    snapshot_date                                                   AS month,
    COUNT(DISTINCT customer_id)                                     AS active_customers,
    ROUND(AVG(credit_score), 1)                                     AS avg_credit_score,
    ROUND(AVG(account_balance), 2)                                  AS avg_account_balance
FROM monthly_customer_snapshot
GROUP BY snapshot_date
ORDER BY snapshot_date;
