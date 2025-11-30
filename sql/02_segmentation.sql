-- ============================================
-- 2. SEGMENTATION ANALYSIS
-- ============================================

-- By Country
WITH country_funnel AS (
    SELECT 
        u.country,
        COUNT(DISTINCT u.user_id) as signups,
        COUNT(DISTINCT CASE WHEN e.event_name = 'viewed_feature' THEN u.user_id END) as viewed_feature,
        COUNT(DISTINCT CASE WHEN e.event_time::date BETWEEN u.signup_date + INTERVAL '1 day' AND u.signup_date + INTERVAL '7 days' 
            THEN u.user_id END) as returned_7d,
        COUNT(DISTINCT p.user_id) as upgraded
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN payments p ON u.user_id = p.user_id
    GROUP BY u.country
)

SELECT 
    country,
    signups,
    viewed_feature,
    returned_7d,
    upgraded,
    viewed_feature * 100.0 / signups as viewed_rate,
    returned_7d * 100.0 / signups as return_rate,
    upgraded * 100.0 / signups as upgrade_rate
FROM country_funnel
ORDER BY upgrade_rate DESC;


-- By Device
WITH device_funnel AS (
    SELECT 
        u.device,
        COUNT(DISTINCT u.user_id) as signups,
        COUNT(DISTINCT CASE WHEN e.event_name = 'viewed_feature' THEN u.user_id END) as viewed_feature,
        COUNT(DISTINCT CASE WHEN e.event_time::date BETWEEN u.signup_date + INTERVAL '1 day' AND u.signup_date + INTERVAL '7 days' 
            THEN u.user_id END) as returned_7d,
        COUNT(DISTINCT p.user_id) as upgraded
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN payments p ON u.user_id = p.user_id
    GROUP BY u.device
)

SELECT 
    device,
    signups,
    viewed_feature,
    returned_7d,
    upgraded,
    viewed_feature * 100.0 / signups as viewed_rate,
    returned_7d * 100.0 / signups as return_rate,
    upgraded * 100.0 / signups as upgrade_rate
FROM device_funnel
ORDER BY upgrade_rate DESC;


-- By Source (Acquisition Channel)
WITH source_funnel AS (
    SELECT 
        u.source,
        COUNT(DISTINCT u.user_id) as signups,
        COUNT(DISTINCT CASE WHEN e.event_name = 'viewed_feature' THEN u.user_id END) as viewed_feature,
        COUNT(DISTINCT CASE WHEN e.event_time::date BETWEEN u.signup_date + INTERVAL '1 day' AND u.signup_date + INTERVAL '7 days' 
            THEN u.user_id END) as returned_7d,
        COUNT(DISTINCT p.user_id) as upgraded
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN payments p ON u.user_id = p.user_id
    GROUP BY u.source
)

SELECT 
    source,
    signups,
    viewed_feature,
    returned_7d,
    upgraded,
    viewed_feature * 100.0 / signups as viewed_rate,
    returned_7d * 100.0 / signups as return_rate,
    upgraded * 100.0 / signups as upgrade_rate
FROM source_funnel
ORDER BY upgrade_rate DESC;
