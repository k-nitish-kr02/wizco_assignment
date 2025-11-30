-- ============================================
-- RETENTION ANALYSIS
-- PostgreSQL Queries
-- ============================================

-- ASSUMPTIONS:
-- 1. Week 0 = signup week (first 7 days after signup)
-- 2. A user is "retained" in week N if they have at least 1 event during that week
-- 3. Weeks are calculated as 7-day periods from signup date
-- 4. All timestamps are in consistent timezone

-- ============================================
-- 1. WEEKLY RETENTION COHORT ANALYSIS
-- ============================================

-- Calculate weekly retention for all users
WITH user_weeks AS (
    SELECT 
        u.user_id,
        u.signup_date,
        e.event_time,
        -- Calculate which week this event occurred in (0 = signup week)
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time IS NOT NULL
        AND e.event_time >= u.signup_date  -- Only count events after signup
),

retention_by_week AS (
    SELECT 
        week_number,
        COUNT(DISTINCT user_id) as active_users,
        COUNT(DISTINCT user_id) * 100.0 / (SELECT COUNT(*) FROM users) as retention_pct
    FROM user_weeks
    WHERE week_number >= 0  -- Only positive weeks
    GROUP BY week_number
)

SELECT 
    week_number,
    active_users,
    ROUND(retention_pct, 2) as retention_pct
FROM retention_by_week
WHERE week_number <= 12  -- First 12 weeks
ORDER BY week_number;


-- ============================================
-- 2. RETENTION BY SIGNUP COHORT (Monthly)
-- ============================================

-- Analyze retention grouped by signup month
WITH user_cohorts AS (
    SELECT 
        u.user_id,
        DATE_TRUNC('month', u.signup_date) as cohort_month,
        u.signup_date,
        e.event_time,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
),

cohort_retention AS (
    SELECT 
        cohort_month,
        week_number,
        COUNT(DISTINCT user_id) as active_users,
        COUNT(DISTINCT user_id) * 100.0 / 
            COUNT(DISTINCT user_id) FILTER (WHERE week_number = 0) OVER (PARTITION BY cohort_month) as retention_pct
    FROM user_cohorts
    WHERE week_number >= 0 AND week_number <= 12
    GROUP BY cohort_month, week_number
)

SELECT 
    cohort_month,
    week_number,
    active_users,
    ROUND(retention_pct, 2) as retention_pct
FROM cohort_retention
ORDER BY cohort_month, week_number;


-- ============================================
-- 3. DAY 1, DAY 7, DAY 30 RETENTION
-- ============================================

-- Classic retention metrics
WITH user_activity AS (
    SELECT 
        u.user_id,
        u.signup_date,
        -- Day 1 retention (returned on day 1 after signup)
        MAX(CASE 
            WHEN e.event_time::date = u.signup_date + INTERVAL '1 day' 
            THEN 1 ELSE 0 
        END) as returned_day1,
        -- Day 7 retention (any activity in first 7 days)
        MAX(CASE 
            WHEN e.event_time::date BETWEEN u.signup_date AND u.signup_date + INTERVAL '7 days'
            THEN 1 ELSE 0 
        END) as returned_day7,
        -- Day 30 retention (any activity in first 30 days)
        MAX(CASE 
            WHEN e.event_time::date BETWEEN u.signup_date AND u.signup_date + INTERVAL '30 days'
            THEN 1 ELSE 0 
        END) as returned_day30
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.signup_date
)

SELECT 
    COUNT(*) as total_users,
    SUM(returned_day1) as returned_day1,
    SUM(returned_day7) as returned_day7,
    SUM(returned_day30) as returned_day30,
    ROUND(SUM(returned_day1) * 100.0 / COUNT(*), 2) as day1_retention_pct,
    ROUND(SUM(returned_day7) * 100.0 / COUNT(*), 2) as day7_retention_pct,
    ROUND(SUM(returned_day30) * 100.0 / COUNT(*), 2) as day30_retention_pct
FROM user_activity;


-- ============================================
-- 4. RETENTION BY SEGMENT
-- ============================================

-- Retention by Country
WITH country_retention AS (
    SELECT 
        u.country,
        u.user_id,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
)

SELECT 
    country,
    week_number,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT user_id) * 100.0 / 
        COUNT(DISTINCT user_id) FILTER (WHERE week_number = 0) OVER (PARTITION BY country) as retention_pct
FROM country_retention
WHERE week_number >= 0 AND week_number <= 12
GROUP BY country, week_number
ORDER BY country, week_number;


-- Retention by Device
WITH device_retention AS (
    SELECT 
        u.device,
        u.user_id,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
)

SELECT 
    device,
    week_number,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT user_id) * 100.0 / 
        COUNT(DISTINCT user_id) FILTER (WHERE week_number = 0) OVER (PARTITION BY device) as retention_pct
FROM device_retention
WHERE week_number >= 0 AND week_number <= 12
GROUP BY device, week_number
ORDER BY device, week_number;


-- Retention by Source
WITH source_retention AS (
    SELECT 
        u.source,
        u.user_id,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
)

SELECT 
    source,
    week_number,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT user_id) * 100.0 / 
        COUNT(DISTINCT user_id) FILTER (WHERE week_number = 0) OVER (PARTITION BY source) as retention_pct
FROM source_retention
WHERE week_number >= 0 AND week_number <= 12
GROUP BY source, week_number
ORDER BY source, week_number;


-- ============================================
-- 5. RETENTION CURVES COMPARISON
-- ============================================

-- Compare retention across different user segments side-by-side
WITH all_retention AS (
    -- Overall retention
    SELECT 
        'Overall' as segment_type,
        'All Users' as segment_value,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number,
        COUNT(DISTINCT u.user_id) as active_users
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
    GROUP BY week_number
    
    UNION ALL
    
    -- By country
    SELECT 
        'Country' as segment_type,
        u.country as segment_value,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number,
        COUNT(DISTINCT u.user_id) as active_users
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
    GROUP BY u.country, week_number
    
    UNION ALL
    
    -- By device
    SELECT 
        'Device' as segment_type,
        u.device as segment_value,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number,
        COUNT(DISTINCT u.user_id) as active_users
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
    GROUP BY u.device, week_number
)

SELECT 
    segment_type,
    segment_value,
    week_number,
    active_users,
    ROUND(active_users * 100.0 / 
        FIRST_VALUE(active_users) OVER (
            PARTITION BY segment_type, segment_value 
            ORDER BY week_number
        ), 2) as retention_pct
FROM all_retention
WHERE week_number >= 0 AND week_number <= 12
ORDER BY segment_type, segment_value, week_number;


-- ============================================
-- 6. RETENTION DROPOFF ANALYSIS
-- ============================================

-- Identify week-over-week retention drops
WITH weekly_retention AS (
    SELECT 
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - u.signup_date)) / (7 * 86400))::INTEGER as week_number,
        COUNT(DISTINCT u.user_id) as active_users
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    WHERE e.event_time >= u.signup_date
    GROUP BY week_number
)

SELECT 
    week_number,
    active_users,
    LAG(active_users) OVER (ORDER BY week_number) as prev_week_users,
    active_users - LAG(active_users) OVER (ORDER BY week_number) as user_change,
    ROUND(
        (active_users - LAG(active_users) OVER (ORDER BY week_number)) * 100.0 / 
        NULLIF(LAG(active_users) OVER (ORDER BY week_number), 0), 
        2
    ) as pct_change
FROM weekly_retention
WHERE week_number >= 0 AND week_number <= 12
ORDER BY week_number;


-- ============================================
-- 7. POWER USER RETENTION
-- ============================================

-- Retention for highly engaged users (top 25% by activity)
WITH user_engagement AS (
    SELECT 
        u.user_id,
        u.signup_date,
        COUNT(e.event_name) as total_events,
        NTILE(4) OVER (ORDER BY COUNT(e.event_name) DESC) as engagement_quartile
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.signup_date
),

power_user_activity AS (
    SELECT 
        ue.user_id,
        ue.signup_date,
        ue.engagement_quartile,
        e.event_time,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - ue.signup_date)) / (7 * 86400))::INTEGER as week_number
    FROM user_engagement ue
    LEFT JOIN events e ON ue.user_id = e.user_id
    WHERE e.event_time >= ue.signup_date
)

SELECT 
    CASE 
        WHEN engagement_quartile = 1 THEN 'Top 25% (Power Users)'
        WHEN engagement_quartile = 2 THEN '25-50%'
        WHEN engagement_quartile = 3 THEN '50-75%'
        WHEN engagement_quartile = 4 THEN 'Bottom 25%'
    END as user_segment,
    week_number,
    COUNT(DISTINCT user_id) as active_users,
    ROUND(
        COUNT(DISTINCT user_id) * 100.0 / 
        FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (
            PARTITION BY engagement_quartile 
            ORDER BY week_number
        ), 
        2
    ) as retention_pct
FROM power_user_activity
WHERE week_number >= 0 AND week_number <= 12
GROUP BY engagement_quartile, week_number
ORDER BY engagement_quartile, week_number;


-- ============================================
-- 8. STICKINESS RATIO
-- ============================================

-- DAU/MAU ratio (Daily Active Users / Monthly Active Users)
-- Measures how "sticky" the product is

WITH daily_users AS (
    SELECT 
        e.event_time::date as event_date,
        COUNT(DISTINCT e.user_id) as dau
    FROM events e
    GROUP BY e.event_time::date
),

monthly_users AS (
    SELECT 
        DATE_TRUNC('month', e.event_time) as event_month,
        e.event_time::date as event_date,
        COUNT(DISTINCT e.user_id) OVER (
            PARTITION BY DATE_TRUNC('month', e.event_time)
        ) as mau
    FROM events e
)

SELECT 
    d.event_date,
    d.dau,
    m.mau,
    ROUND(d.dau * 100.0 / NULLIF(m.mau, 0), 2) as stickiness_ratio
FROM daily_users d
JOIN monthly_users m ON d.event_date = m.event_date
ORDER BY d.event_date DESC
LIMIT 30;


-- ============================================
-- 9. RETENTION FOR PAID VS FREE USERS
-- ============================================

-- Compare retention between users who upgraded vs those who didn't
WITH user_status AS (
    SELECT 
        u.user_id,
        u.signup_date,
        CASE WHEN p.user_id IS NOT NULL THEN 'Paid' ELSE 'Free' END as user_type
    FROM users u
    LEFT JOIN payments p ON u.user_id = p.user_id
),

retention_by_type AS (
    SELECT 
        us.user_type,
        FLOOR(EXTRACT(EPOCH FROM (e.event_time::date - us.signup_date)) / (7 * 86400))::INTEGER as week_number,
        COUNT(DISTINCT us.user_id) as active_users
    FROM user_status us
    LEFT JOIN events e ON us.user_id = e.user_id
    WHERE e.event_time >= us.signup_date
    GROUP BY us.user_type, week_number
)

SELECT 
    user_type,
    week_number,
    active_users,
    ROUND(
        active_users * 100.0 / 
        FIRST_VALUE(active_users) OVER (
            PARTITION BY user_type 
            ORDER BY week_number
        ), 
        2
    ) as retention_pct
FROM retention_by_type
WHERE week_number >= 0 AND week_number <= 12
ORDER BY user_type, week_number;


-- ============================================
-- 10. RESURRECTION ANALYSIS
-- ============================================

-- Users who became inactive but then returned
WITH user_activity_gaps AS (
    SELECT 
        u.user_id,
        u.signup_date,
        e.event_time::date as event_date,
        LAG(e.event_time::date) OVER (PARTITION BY u.user_id ORDER BY e.event_time) as prev_event_date,
        e.event_time::date - LAG(e.event_time::date) OVER (PARTITION BY u.user_id ORDER BY e.event_time) as days_gap
    FROM users u
    JOIN events e ON u.user_id = e.user_id
)

SELECT 
    CASE 
        WHEN days_gap >= 30 THEN 'Resurrected (30+ day gap)'
        WHEN days_gap >= 14 THEN 'Returned (14-29 day gap)'
        WHEN days_gap >= 7 THEN 'Returned (7-13 day gap)'
        ELSE 'Regular Active'
    END as user_status,
    COUNT(DISTINCT user_id) as user_count,
    ROUND(AVG(days_gap), 1) as avg_gap_days
FROM user_activity_gaps
WHERE days_gap IS NOT NULL
GROUP BY 
    CASE 
        WHEN days_gap >= 30 THEN 'Resurrected (30+ day gap)'
        WHEN days_gap >= 14 THEN 'Returned (14-29 day gap)'
        WHEN days_gap >= 7 THEN 'Returned (7-13 day gap)'
        ELSE 'Regular Active'
    END
ORDER BY avg_gap_days DESC;