-- queries.sql
-- Example analytical queries against the loaded 'orders' table.
-- Demonstrates common SQL patterns used in reporting on ETL output.

-- 1. Total revenue and order count by region
SELECT
    region,
    COUNT(*)      AS order_count,
    ROUND(SUM(amount), 2) AS total_revenue,
    ROUND(AVG(amount), 2) AS avg_order_value
FROM orders
GROUP BY region
ORDER BY total_revenue DESC;

-- 2. Order counts by status
SELECT
    status,
    COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;

-- 3. Top 5 highest-value orders
SELECT order_id, customer_name, amount, region, status
FROM orders
ORDER BY amount DESC
LIMIT 5;

-- 4. Monthly order volume (uses window-function-friendly date grouping)
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(*) AS order_count,
    ROUND(SUM(amount), 2) AS monthly_revenue
FROM orders
GROUP BY order_month
ORDER BY order_month;

-- 5. Running total of revenue by date (window function example)
SELECT
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders
ORDER BY order_date
LIMIT 10;
