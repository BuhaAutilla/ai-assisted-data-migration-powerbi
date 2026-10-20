SET search_path TO migration_demo;

-- 1. Migration completeness
SELECT
    (SELECT COUNT(*) FROM legacy_customers) AS source_customers,
    (SELECT COUNT(DISTINCT legacy_client_id) FROM target_customers) AS migrated_customers,
    ROUND(
        100.0 * (SELECT COUNT(DISTINCT legacy_client_id) FROM target_customers)
        / NULLIF((SELECT COUNT(*) FROM legacy_customers), 0), 2
    ) AS customer_migration_rate_pct;

-- 2. Missing customers
SELECT lc.client_id, lc.client_name
FROM legacy_customers lc
LEFT JOIN target_customers tc ON tc.legacy_client_id = lc.client_id
WHERE tc.legacy_client_id IS NULL
ORDER BY lc.client_id;

-- 3. Duplicate customers
SELECT legacy_client_id, COUNT(*) AS target_rows
FROM target_customers
GROUP BY legacy_client_id
HAVING COUNT(*) > 1
ORDER BY target_rows DESC, legacy_client_id;

-- 4. Invalid emails
SELECT customer_id, legacy_client_id, email_address
FROM target_customers
WHERE email_address IS NULL
   OR email_address !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';

-- 5. Referential-integrity violations
SELECT o.order_key, o.legacy_order_id, o.customer_id
FROM target_orders o
LEFT JOIN target_customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;

-- 6. Amount reconciliation after USD-to-CLP normalization
WITH expected AS (
    SELECT
        order_id,
        CASE WHEN currency = 'USD' THEN ROUND(amount * 900, 0)
             ELSE ROUND(amount, 0)
        END AS expected_amount_clp
    FROM legacy_orders
)
SELECT
    o.legacy_order_id,
    e.expected_amount_clp,
    o.amount_clp,
    o.amount_clp - e.expected_amount_clp AS difference_clp
FROM target_orders o
JOIN expected e ON e.order_id = o.legacy_order_id
WHERE ABS(o.amount_clp - e.expected_amount_clp) > 1
ORDER BY ABS(o.amount_clp - e.expected_amount_clp) DESC;

-- 7. Order migration rate
SELECT
    COUNT(*) AS source_orders,
    COUNT(t.legacy_order_id) AS migrated_orders,
    ROUND(100.0 * COUNT(t.legacy_order_id) / NULLIF(COUNT(*), 0), 2)
        AS order_migration_rate_pct
FROM legacy_orders l
LEFT JOIN target_orders t ON t.legacy_order_id = l.order_id;

