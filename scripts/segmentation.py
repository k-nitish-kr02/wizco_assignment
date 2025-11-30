"""
Segmentation analysis functions.
"""

import pandas as pd
from typing import Set


def segment_analysis(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                     payments_df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    """
    Analyze funnel performance by segment.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        segment_col: Column name to segment by (e.g., 'country', 'device', 'source')
        
    Returns:
        DataFrame with segment-level funnel metrics
    """
    upgraded_users = set(payments_df['user_id'])
    viewed_feature = set(events_df[events_df['event_name'] == 'viewed_feature']['user_id'])
    
    # Calculate returned within 7 days
    user_events = events_df.merge(users_df[['user_id', 'signup_date']], on='user_id')
    user_events['days_since_signup'] = (user_events['event_time'] - user_events['signup_date']).dt.days
    returned_7d = set(user_events[user_events['days_since_signup'].between(1, 7)]['user_id'])
    
    segment_stats = []
    
    for segment_value in users_df[segment_col].dropna().unique():
        segment_users = users_df[users_df[segment_col] == segment_value]
        segment_user_ids = set(segment_users['user_id'])
        
        signups = len(segment_user_ids)
        viewed = len(segment_user_ids & viewed_feature)
        returned = len(segment_user_ids & returned_7d)
        upgraded = len(segment_user_ids & upgraded_users)
        
        segment_stats.append({
            segment_col: segment_value,
            'Signups': signups,
            'Viewed_Feature': viewed,
            'Returned_7d': returned,
            'Upgraded': upgraded,
            'View_Rate': (viewed / signups * 100) if signups > 0 else 0,
            'Return_Rate': (returned / signups * 100) if signups > 0 else 0,
            'Upgrade_Rate': (upgraded / signups * 100) if signups > 0 else 0
        })
    
    return pd.DataFrame(segment_stats).sort_values('Upgrade_Rate', ascending=False)


def segment_by_country(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                       payments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Segment users by country.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        
    Returns:
        DataFrame with country-level metrics
    """
    return segment_analysis(users_df, events_df, payments_df, 'country')


def segment_by_device(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                      payments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Segment users by device type.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        
    Returns:
        DataFrame with device-level metrics
    """
    return segment_analysis(users_df, events_df, payments_df, 'device')


def segment_by_source(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                      payments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Segment users by acquisition source.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        
    Returns:
        DataFrame with source-level metrics
    """
    return segment_analysis(users_df, events_df, payments_df, 'source')
