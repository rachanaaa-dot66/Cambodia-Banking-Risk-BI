-- =============================================================================
-- product_analysis.sql
-- KPI-CA-04: Product Adoption Rate | KPI-CA-05: Customer Lifetime Value
-- Reference: 03_KPI_Framework.md §4 | 02_Business_Requirements.md CA-05, BP-03
-- =============================================================================

-- --------------------------------------------------------
-- 1. Product Adoption Rate by Account Type  (KPI-CA-04)
-- --------------------------------------------------------
SELECT
    a.account_type,
    COUNT(DISTINCT a.customer_id)                                   AS customers_with_product,
    (SELECT COUNT(*) FROM customers WHERE customer_status = 'Active')
                                                                    AS total_active_customers,
    ROUND(
        100.0 * COUNT(DISTINCT a.customer_id)
        / NULLIF(
            (SELECT COUNT(*) FROM customers WHERE customer_status = 'Active'), 0
        ), 2
    )                                                               AS adoption_rate_pct
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.account_status != 'Closed'
  AND c.customer_status = 'Active'
GROUP BY a.account_type
ORDER BY adoption_rate_pct DESC;

-- --------------------------------------------------------
-- 2. Loan Product Adoption
-- --------------------------------------------------------
SELECT
    l.loan_type,
    COUNT(DISTINCT l.customer_id)                                   AS customers_with_loan,
    ROUND(
        100.0 * COUNT(DISTINCT l.customer_id)
        / NULLIF((SELECT COUNT(*) FROM customers WHERE customer_status = 'Active'), 0),
        2
    )                                                               AS loan_adoption_rate_pct,
    ROUND(AVG(l.loan_amount), 2)                                    AS avg_loan_amount,
    ROUND(AVG(l.interest_rate), 2)                                  AS avg_interest_rate
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
WHERE c.customer_status = 'Active'
  AND l.loan_status NOT IN ('Closed')
GROUP BY l.loan_type
ORDER BY customers_with_loan DESC;

-- --------------------------------------------------------
-- 3. Multi-Product Customers (cross-sell depth)
-- --------------------------------------------------------
WITH customer_products AS (
    SELECT
        customer_id,
        COUNT(DISTINCT account_type)                                AS product_count
    FROM accounts
    WHERE account_status != 'Closed'
    GROUP BY customer_id
)
SELECT
    product_count,
    COUNT(customer_id)                                              AS customers,
    ROUND(
        100.0 * COUNT(customer_id)
        / SUM(COUNT(customer_id)) OVER (), 2
    )                                                               AS pct_customers
FROM customer_products
GROUP BY product_count
ORDER BY product_count;

-- --------------------------------------------------------
-- 4. Customer Lifetime Value Estimate  (KPI-CA-05)
--    CLV = total payments received per customer
-- --------------------------------------------------------
WITH customer_payments AS (
    SELECT
        l.customer_id,
        SUM(lp.amount_paid)                                         AS total_paid
    FROM loan_payments lp
    JOIN loans l ON lp.loan_id = l.loan_id
    GROUP BY l.customer_id
),
customer_deposits AS (
    SELECT
        a.customer_id,
        SUM(a.current_balance)                                      AS deposit_balance
    FROM accounts a
    WHERE a.account_status = 'Active'
    GROUP BY a.customer_id
)
SELECT
    c.occupation,
    COUNT(c.customer_id)                                            AS customers,
    ROUND(AVG(COALESCE(cp.total_paid, 0)), 2)                       AS avg_loan_payments,
    ROUND(AVG(COALESCE(cd.deposit_balance, 0)), 2)                  AS avg_deposit_balance,
    ROUND(AVG(
        COALESCE(cp.total_paid, 0) * 0.7   -- interest portion estimate
        + COALESCE(cd.deposit_balance, 0) * 0.02   -- fee/spread estimate
    ), 2)                                                           AS estimated_clv
FROM customers c
LEFT JOIN customer_payments cp ON c.customer_id = cp.customer_id
LEFT JOIN customer_deposits cd ON c.customer_id = cd.customer_id
WHERE c.customer_status = 'Active'
GROUP BY c.occupation
ORDER BY estimated_clv DESC;

-- --------------------------------------------------------
-- 5. Product Mix by Province  (BP-04)
-- --------------------------------------------------------
SELECT
    c.province,
    a.account_type,
    COUNT(DISTINCT a.customer_id)                                   AS customers,
    SUM(a.current_balance)                                          AS total_balance
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.account_status = 'Active'
GROUP BY c.province, a.account_type
ORDER BY c.province, total_balance DESC;
