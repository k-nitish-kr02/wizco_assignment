-- ============================================
-- 5. EVENT SEQUENCE ANALYSIS (TIME TO CONVERT)
-- ============================================

-- Conversion timeline analysis
-- Analyze time to conversion and conversion patterns over time

WITH conversion_timeline AS (
    SELECT 
        p.user_id,
        u.signup_date,
        p.payment_date,
        EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 as days_to_convert,
        CASE 
            WHEN EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 <= 1 THEN '0-1 days'
            WHEN EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 <= 3 THEN '2-3 days'
            WHEN EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 <= 7 THEN '4-7 days'
            WHEN EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 <= 14 THEN '8-14 days'
            WHEN EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 <= 30 THEN '15-30 days'
            ELSE '30+ days'
        END as conversion_bucket
    FROM payments p
    JOIN users u ON p.user_id = u.user_id
)

SELECT 
    conversion_bucket,
    COUNT(*) as conversions,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as pct_of_conversions
FROM conversion_timeline
GROUP BY conversion_bucket
ORDER BY MIN(days_to_convert);
