"""
Funnel analysis calculation functions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Set


def build_funnel(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                 payments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the 4-step conversion funnel.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        
    Returns:
        DataFrame with funnel metrics including users, conversion rates, and user sets
    """
    # Step 1: All signups
    step1 = set(users_df['user_id'])
    
    # Step 2: Viewed feature
    step2 = set(events_df[events_df['event_name'] == 'viewed_feature']['user_id'])
    
    # Step 3: Returned within 7 days
    user_events = events_df.merge(users_df[['user_id', 'signup_date']], on='user_id')
    user_events['days_since_signup'] = (user_events['event_time'] - user_events['signup_date']).dt.days
    step3 = set(user_events[user_events['days_since_signup'].between(1, 7)]['user_id'])
    
    # Step 4: Upgraded
    step4 = set(payments_df['user_id'])
    
    funnel_data = {
        'Step': ['1. Signed Up', '2. Viewed Feature', '3. Returned 7d', '4. Upgraded'],
        'Users': [len(step1), len(step2), len(step3), len(step4)],
        'Sets': [step1, step2, step3, step4]
    }
    
    funnel_df = pd.DataFrame(funnel_data)
    funnel_df['Conversion_Rate'] = funnel_df['Users'] / funnel_df['Users'].shift(1) * 100
    funnel_df['Pct_of_Signups'] = funnel_df['Users'] / funnel_df['Users'].iloc[0] * 100
    
    return funnel_df


def calculate_retention(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                       weeks: int = 12) -> pd.DataFrame:
    """
    Calculate weekly retention rates.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        weeks: Number of weeks to track (default: 12)
        
    Returns:
        DataFrame with weekly retention metrics
    """
    user_events = events_df.merge(users_df[['user_id', 'signup_date']], on='user_id')
    user_events['week_number'] = ((user_events['event_time'] - user_events['signup_date']).dt.days // 7)
    
    retention_data = []
    total_users = len(users_df)
    
    for week in range(weeks + 1):
        active_users = user_events[user_events['week_number'] == week]['user_id'].nunique()
        retention_pct = (active_users / total_users) * 100
        retention_data.append({
            'Week': week,
            'Active_Users': active_users,
            'Retention_Pct': retention_pct
        })
    
    return pd.DataFrame(retention_data)


def calculate_conversion_rate(numerator: int, denominator: int) -> float:
    """
    Calculate conversion rate as percentage.
    
    Args:
        numerator: Number of converted users
        denominator: Total number of users
        
    Returns:
        Conversion rate as percentage
    """
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100


def calculate_30day_upgrade_rate(users_df: pd.DataFrame, 
                                 payments_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate 30-day upgrade rate.
    
    Args:
        users_df: Users dataframe
        payments_df: Payments dataframe
        
    Returns:
        Dictionary with upgrade metrics
    """
    # Merge to get signup dates
    conversion_data = payments_df.merge(
        users_df[['user_id', 'signup_date']], 
        on='user_id'
    )
    
    # Calculate days to conversion
    conversion_data['days_to_convert'] = (
        conversion_data['payment_date'] - conversion_data['signup_date']
    ).dt.days
    
    # Count upgrades within 30 days
    upgrades_30d = conversion_data[conversion_data['days_to_convert'] <= 30]['user_id'].nunique()
    total_users = len(users_df)
    
    return {
        'upgraded_30d': upgrades_30d,
        'total_users': total_users,
        'upgrade_rate_30d': calculate_conversion_rate(upgrades_30d, total_users)
    }
