"""
Data loading and cleaning functions for user conversion analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple


def load_users(data_path: str = "data/raw/users.csv") -> pd.DataFrame:
    """
    Load users data from CSV file.
    
    Args:
        data_path: Path to users CSV file
        
    Returns:
        DataFrame with users data, signup_date converted to datetime
    """
    df = pd.read_csv(data_path)
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    return df


def load_events(data_path: str = "data/raw/events.csv") -> pd.DataFrame:
    """
    Load events data from CSV file.
    
    Args:
        data_path: Path to events CSV file
        
    Returns:
        DataFrame with events data, event_time converted to datetime
    """
    df = pd.read_csv(data_path)
    df['event_time'] = pd.to_datetime(df['event_time'])
    return df


def load_payments(data_path: str = "data/raw/payments.csv") -> pd.DataFrame:
    """
    Load payments data from CSV file.
    
    Args:
        data_path: Path to payments CSV file
        
    Returns:
        DataFrame with payments data, payment_date converted to datetime
    """
    df = pd.read_csv(data_path)
    df['payment_date'] = pd.to_datetime(df['payment_date'])
    return df


def load_all_data(
    users_path: str = "data/raw/users.csv",
    events_path: str = "data/raw/events.csv",
    payments_path: str = "data/raw/payments.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all datasets at once.
    
    Args:
        users_path: Path to users CSV file
        events_path: Path to events CSV file
        payments_path: Path to payments CSV file
        
    Returns:
        Tuple of (users_df, events_df, payments_df)
    """
    users = load_users(users_path)
    events = load_events(events_path)
    payments = load_payments(payments_path)
    
    print("Data loaded successfully!")
    print(f"Users: {len(users):,}, Events: {len(events):,}, Payments: {len(payments):,}")
    
    return users, events, payments


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess data.
    
    Args:
        df: Input dataframe
        
    Returns:
        Cleaned dataframe
    """
    df_cleaned = df.copy()
    
    # Remove duplicates
    df_cleaned = df_cleaned.drop_duplicates()
    
    # Remove rows with missing critical values
    df_cleaned = df_cleaned.dropna(subset=df_cleaned.columns[:2])
    
    return df_cleaned


def validate_data(users_df: pd.DataFrame, events_df: pd.DataFrame, 
                  payments_df: pd.DataFrame) -> None:
    """
    Validate loaded data for common issues.
    
    Args:
        users_df: Users dataframe
        events_df: Events dataframe
        payments_df: Payments dataframe
    """
    print("\n=== DATA VALIDATION ===")
    
    # Check for duplicates
    print(f"Duplicate users: {users_df['user_id'].duplicated().sum()}")
    print(f"Duplicate events: {events_df.duplicated().sum()}")
    print(f"Duplicate payments: {payments_df.duplicated().sum()}")
    
    # Check for missing values
    print(f"\nMissing values in users:\n{users_df.isnull().sum()}")
    print(f"\nMissing values in events:\n{events_df.isnull().sum()}")
    print(f"\nMissing values in payments:\n{payments_df.isnull().sum()}")
    
    # Check data integrity
    event_users = set(events_df['user_id'].unique())
    payment_users = set(payments_df['user_id'].unique())
    all_users = set(users_df['user_id'].unique())
    
    print(f"\nEvents from unknown users: {len(event_users - all_users)}")
    print(f"Payments from unknown users: {len(payment_users - all_users)}")
    
    print("\n=== VALIDATION COMPLETE ===\n")
