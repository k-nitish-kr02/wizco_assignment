-- ============================================
-- 3. CONVERSION SIGNALS
-- ============================================

-- User behavior metrics comparison
WITH user_behavior AS (
    SELECT 
        u.user_id,
        CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END as is_upgraded,
        COUNT(e.event_name) as total_events,
        COUNT(DISTINCT e.event_name) as distinct_events,
        COUNT(DISTINCT e.event_time::date) as days_active,
        MIN(CASE WHEN e.event_name = 'viewed_feature' 
            THEN EXTRACT(EPOCH FROM (e.event_time - u.signup_date::timestamp)) / 86400 END) as days_to_first_feature,
        EXTRACT(EPOCH FROM (p.payment_date - u.signup_date)) / 86400 as days_to_upgrade
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN payments p ON u.user_id = p.user_id
    GROUP BY u.user_id, u.signup_date, p.user_id, p.payment_date
)

SELECT 
    is_upgraded,
    COUNT(*) as user_count,
    ROUND(AVG(total_events), 2) as avg_total_events,
    ROUND(AVG(distinct_events), 2) as avg_distinct_events,
    ROUND(AVG(days_active), 2) as avg_days_active,
    ROUND(AVG(days_to_first_feature), 2) as avg_days_to_first_feature,
    ROUND(AVG(days_to_upgrade), 2) as avg_days_to_upgrade
FROM user_behavior
GROUP BY is_upgraded
ORDER BY is_upgraded DESC;


-- High-intent behavior patterns
WITH user_actions AS (
    SELECT 
        u.user_id,
        CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END as upgraded,
        MAX(CASE WHEN e.event_name = 'clicked_upgrade' THEN 1 ELSE 0 END) as clicked_upgrade,
        MAX(CASE WHEN e.event_name = 'browsed_pricing' THEN 1 ELSE 0 END) as browsed_pricing,
        MAX(CASE WHEN e.event_name = 'used_advanced_feature' THEN 1 ELSE 0 END) as used_advanced,
        COUNT(DISTINCT CASE WHEN e.event_time::date <= u.signup_date + INTERVAL '2 days' 
            THEN e.event_name END) as distinct_events_3d
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN payments p ON u.user_id = p.user_id
    GROUP BY u.user_id, p.user_id
)

SELECT 
    'Clicked Upgrade' as behavior,
    SUM(CASE WHEN clicked_upgrade = 1 THEN upgraded ELSE 0 END) * 100.0 / 
        NULLIF(SUM(clicked_upgrade), 0) as conversion_rate
FROM user_actions

UNION ALL

SELECT 
    'Browsed Pricing' as behavior,
    SUM(CASE WHEN browsed_pricing = 1 THEN upgraded ELSE 0 END) * 100.0 / 
        NULLIF(SUM(browsed_pricing), 0) as conversion_rate
FROM user_actions

UNION ALL

SELECT 
    'Used Advanced Feature' as behavior,
    SUM(CASE WHEN used_advanced = 1 THEN upgraded ELSE 0 END) * 100.0 / 
        NULLIF(SUM(used_advanced), 0) as conversion_rate
FROM user_actions

UNION ALL

SELECT 
    '3+ Distinct Events in First 3 Days' as behavior,
    SUM(CASE WHEN distinct_events_3d >= 3 THEN upgraded ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN distinct_events_3d >= 3 THEN 1 ELSE 0 END), 0) as conversion_rate
FROM user_actions;
