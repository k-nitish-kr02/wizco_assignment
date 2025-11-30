-- ============================================
-- 1. PRODUCT FUNNEL ANALYSIS
-- ============================================

-- ASSUMPTIONS:
-- 1. A "returned visit" is any event occurring 1-7 days after signup
-- 2. Weekly retention measures users with ANY event in each week after signup
-- 3. "Days active" counts distinct dates with events
-- 4. All timestamps are in consistent timezone

-- Step 1: Create base funnel with all steps
WITH funnel_base AS (
    SELECT 
        u.user_id,
        u.signup_date,
        u.country,
        u.device,
        u.source,
        -- Step 2: Viewed feature
        MAX(CASE WHEN e.event_name = 'viewed_feature' THEN 1 ELSE 0 END) as viewed_feature,
        -- Step 3: Returned within 7 days
        MAX(CASE WHEN e.event_time::date BETWEEN u.signup_date + INTERVAL '1 day' AND u.signup_date + INTERVAL '7 days' 
            THEN 1 ELSE 0 END) as returned_7d,
        -- Step 4: Upgraded
        MAX(CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END) as upgraded
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN payments p ON u.user_id = p.user_id
    GROUP BY u.user_id, u.signup_date, u.country, u.device, u.source
)

-- Calculate funnel metrics
SELECT 
    'Step 1: Signed Up' as step,
    1 as step_number,
    COUNT(*) as users,
    COUNT(*) * 100.0 / COUNT(*) as pct_of_signups,
    NULL as conversion_from_previous
FROM funnel_base

UNION ALL

SELECT 
    'Step 2: Viewed Feature' as step,
    2 as step_number,
    SUM(viewed_feature) as users,
    SUM(viewed_feature) * 100.0 / COUNT(*) as pct_of_signups,
    SUM(viewed_feature) * 100.0 / COUNT(*) as conversion_from_previous
FROM funnel_base

UNION ALL

SELECT 
    'Step 3: Returned within 7 days' as step,
    3 as step_number,
    SUM(returned_7d) as users,
    SUM(returned_7d) * 100.0 / COUNT(*) as pct_of_signups,
    SUM(returned_7d) * 100.0 / NULLIF(SUM(viewed_feature), 0) as conversion_from_previous
FROM funnel_base

UNION ALL

SELECT 
    'Step 4: Upgraded' as step,
    4 as step_number,
    SUM(upgraded) as users,
    SUM(upgraded) * 100.0 / COUNT(*) as pct_of_signups,
    SUM(upgraded) * 100.0 / NULLIF(SUM(returned_7d), 0) as conversion_from_previous
FROM funnel_base

ORDER BY step_number;


-- ============================================
-- Weekly Retention Analysis
-- ============================================

WITH user_weeks AS (
    SELECT 
        u.user_id,
        u.signup_date,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400)) as week_number
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time IS NOT NULL
)

SELECT 
    week_number,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT user_id) * 100.0 / (SELECT COUNT(*) FROM users) as retention_pct
FROM user_weeks
WHERE week_number >= 0 AND week_number <= 12
GROUP BY week_number
ORDER BY week_number;


-- ============================================
-- 30-Day Upgrade Rate
-- ============================================

SELECT 
    COUNT(DISTINCT p.user_id) as upgraded_30d,
    COUNT(DISTINCT u.user_id) as total_users,
    COUNT(DISTINCT p.user_id) * 100.0 / COUNT(DISTINCT u.user_id) as upgrade_rate_30d
FROM users u
LEFT JOIN payments p ON u.user_id = p.user_id 
    AND p.payment_date <= u.signup_date + INTERVAL '30 days';
