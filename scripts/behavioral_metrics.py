"""
Behavioral signal and metrics calculations.
"""

import pandas as pd
import numpy as np
from typing import Set


def behavioral_metrics(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                       payments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate behavioral metrics for upgraded vs non-upgraded users.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        
    Returns:
        DataFrame with user-level behavioral metrics
    """
    upgraded_users = set(payments_df['user_id'])
    
    user_metrics = []
    
    for user_id in users_df['user_id']:
        user_events = events_df[events_df['user_id'] == user_id]
        user_data = users_df[users_df['user_id'] == user_id].iloc[0]
        
        is_upgraded = user_id in upgraded_users
        total_events = len(user_events)
        distinct_events = user_events['event_name'].nunique()
        
        if len(user_events) > 0:
            days_active = user_events['event_time'].dt.date.nunique()
            first_event = user_events['event_time'].min()
            days_to_first_event = (first_event - user_data['signup_date']).days
            
            # Days to first feature view
            feature_view = user_events[user_events['event_name'] == 'viewed_feature']
            days_to_feature = np.nan
            if len(feature_view) > 0:
                days_to_feature = (feature_view['event_time'].min() - user_data['signup_date']).days
        else:
            days_active = 0
            days_to_first_event = np.nan
            days_to_feature = np.nan
        
        user_metrics.append({
            'user_id': user_id,
            'is_upgraded': is_upgraded,
            'total_events': total_events,
            'distinct_events': distinct_events,
            'days_active': days_active,
            'days_to_feature': days_to_feature
        })
    
    return pd.DataFrame(user_metrics)


def high_intent_analysis(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                        payments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify high-intent behaviors and their conversion rates.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
        
    Returns:
        DataFrame with high-intent behaviors and conversion rates
    """
    upgraded_users = set(payments_df['user_id'])
    
    behaviors = {
        'clicked_upgrade': 'clicked_upgrade',
        'browsed_pricing': 'browsed_pricing',
        'used_advanced_feature': 'used_advanced_feature'
    }
    
    results = []
    
    for behavior_name, event_name in behaviors.items():
        users_with_behavior = set(events_df[events_df['event_name'] == event_name]['user_id'])
        converted = len(users_with_behavior & upgraded_users)
        total = len(users_with_behavior)
        
        if total > 0:
            conversion_rate = (converted / total) * 100
            results.append({
                'Behavior': behavior_name,
                'Users': total,
                'Converted': converted,
                'Conversion_Rate': conversion_rate
            })
    
    # Add early engagement signal
    user_events = events_df.merge(users_df[['user_id', 'signup_date']], on='user_id')
    user_events['days_since_signup'] = (user_events['event_time'] - user_events['signup_date']).dt.days
    
    early_engaged = user_events[user_events['days_since_signup'] <= 2].groupby('user_id')['event_name'].nunique()
    highly_engaged_users = set(early_engaged[early_engaged >= 3].index)
    
    converted = len(highly_engaged_users & upgraded_users)
    total = len(highly_engaged_users)
    
    if total > 0:
        results.append({
            'Behavior': '3+ distinct events in first 3 days',
            'Users': total,
            'Converted': converted,
            'Conversion_Rate': (converted / total) * 100
        })
    
    return pd.DataFrame(results).sort_values('Conversion_Rate', ascending=False)


def calculate_session_metrics(events_df: pd.DataFrame, 
                              session_gap_minutes: int = 30) -> pd.DataFrame:
    """
    Calculate session-level metrics.
    
    Args:
        events_df: Events dataframe
        session_gap_minutes: Minutes of inactivity to define new session
        
    Returns:
        DataFrame with session metrics per user
    """
    events_sorted = events_df.sort_values(['user_id', 'event_time'])
    
    # Calculate time since last event
    events_sorted['time_since_last'] = events_sorted.groupby('user_id')['event_time'].diff()
    
    # Mark new sessions
    events_sorted['new_session'] = (
        events_sorted['time_since_last'].isna() | 
        (events_sorted['time_since_last'].dt.total_seconds() > session_gap_minutes * 60)
    )
    
    # Assign session IDs
    events_sorted['session_id'] = events_sorted.groupby('user_id')['new_session'].cumsum()
    
    # Calculate session metrics
    session_metrics = events_sorted.groupby('user_id').agg({
        'session_id': 'max',  # Total sessions
        'event_name': 'count'  # Total events
    }).rename(columns={
        'session_id': 'total_sessions',
        'event_name': 'total_events'
    })
    
    session_metrics['avg_events_per_session'] = (
        session_metrics['total_events'] / session_metrics['total_sessions']
    )
    
    return session_metrics.reset_index()


def calculate_engagement_score(users_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate user engagement scores based on multiple factors.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        
    Returns:
        DataFrame with engagement scores per user
    """
    user_engagement = []
    
    for user_id in users_df['user_id']:
        user_events = events_df[events_df['user_id'] == user_id]
        
        if len(user_events) == 0:
            engagement_score = 0
        else:
            # Factors: total events, distinct events, days active
            total_events = len(user_events)
            distinct_events = user_events['event_name'].nunique()
            days_active = user_events['event_time'].dt.date.nunique()
            
            # Weighted score (normalized)
            engagement_score = (
                total_events * 0.4 + 
                distinct_events * 5 * 0.3 + 
                days_active * 3 * 0.3
            )
        
        user_engagement.append({
            'user_id': user_id,
            'engagement_score': engagement_score
        })
    
    return pd.DataFrame(user_engagement)
