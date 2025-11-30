"""
Visualization and plotting functions.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set default style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_funnel(funnel_data: pd.DataFrame, output_path: str = None):
    """
    Create funnel visualization.
    
    Args:
        funnel_data: DataFrame with funnel metrics (must have 'Step', 'Users', 'Pct_of_Signups')
        output_path: Optional path to save figure
    """
    plt.figure(figsize=(10, 6))
    steps = funnel_data['Step'].values
    user_counts = funnel_data['Users'].values

    bars = plt.barh(steps, user_counts, color=['#4CAF50', '#2196F3', '#FF9800', '#F44336'])
    plt.xlabel('Number of Users')
    plt.title('Conversion Funnel - User Drop-off by Stage')

    # Add value labels
    for i, (bar, count, pct) in enumerate(zip(bars, user_counts, funnel_data['Pct_of_Signups'])):
        plt.text(count + max(user_counts)*0.02, i, 
                 f'{count:,} ({pct:.1f}%)', 
                 va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_retention_curve(retention_data: pd.DataFrame, output_path: str = None):
    """
    Create retention curve visualization.
    
    Args:
        retention_data: DataFrame with retention metrics (must have 'Week', 'Retention_Pct')
        output_path: Optional path to save figure
    """
    plt.figure(figsize=(12, 6))
    plt.plot(retention_data['Week'], retention_data['Retention_Pct'], 
             marker='o', linewidth=2, markersize=8, color='#2196F3')
    plt.xlabel('Weeks Since Signup')
    plt.ylabel('Retention Rate (%)')
    plt.title('Weekly Retention Curve')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=retention_data['Retention_Pct'].mean(), color='r', 
                linestyle='--', alpha=0.5, label='Average')
    plt.legend()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_segment_comparison(segment_data: pd.DataFrame, 
                           segment_col: str,
                           output_path: str = None):
    """
    Create segment comparison visualization.
    
    Args:
        segment_data: DataFrame with segment metrics
        segment_col: Name of the segment column
        output_path: Optional path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Upgrade rate by segment
    segment_sorted = segment_data.sort_values('Upgrade_Rate', ascending=True)
    bars1 = ax1.barh(segment_sorted[segment_col], 
                      segment_sorted['Upgrade_Rate'],
                      color='#4CAF50')
    ax1.set_xlabel('Upgrade Rate (%)')
    ax1.set_title(f'Upgrade Rate by {segment_col.title()}')
    ax1.axvline(x=segment_data['Upgrade_Rate'].mean(), 
                color='r', linestyle='--', alpha=0.5, label='Average')
    ax1.legend()

    # Signups vs upgrade rate scatter
    ax2.scatter(segment_data['Signups'], 
                segment_data['Upgrade_Rate'],
                s=200, alpha=0.6, color='#2196F3')
    for _, row in segment_data.iterrows():
        ax2.annotate(row[segment_col], 
                    (row['Signups'], row['Upgrade_Rate']),
                    fontsize=9, ha='center')
    ax2.set_xlabel('Number of Signups')
    ax2.set_ylabel('Upgrade Rate (%)')
    ax2.set_title(f'Signups vs Conversion by {segment_col.title()}')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_behavioral_comparison(behavior_df: pd.DataFrame, output_path: str = None):
    """
    Visualize behavioral differences between upgraded and non-upgraded users.
    
    Args:
        behavior_df: DataFrame with behavioral metrics including 'is_upgraded' column
        output_path: Optional path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    metrics = ['total_events', 'distinct_events', 'days_active', 'days_to_feature']
    titles = ['Total Events', 'Distinct Event Types', 'Days Active', 'Days to First Feature View']

    for ax, metric, title in zip(axes.flat, metrics, titles):
        upgraded = behavior_df[behavior_df['is_upgraded'] == True][metric].dropna()
        not_upgraded = behavior_df[behavior_df['is_upgraded'] == False][metric].dropna()
        
        ax.hist([not_upgraded, upgraded], bins=20, label=['Not Upgraded', 'Upgraded'],
                alpha=0.7, color=['#F44336', '#4CAF50'])
        ax.set_xlabel(title)
        ax.set_ylabel('Number of Users')
        ax.set_title(f'{title} Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_intent_signals(intent_data: pd.DataFrame, baseline_rate: float, 
                       output_path: str = None):
    """
    Visualize conversion rates by high-intent behavior.
    
    Args:
        intent_data: DataFrame with intent signals (must have 'Behavior', 'Conversion_Rate')
        baseline_rate: Baseline conversion rate for comparison
        output_path: Optional path to save figure
    """
    plt.figure(figsize=(10, 6))
    bars = plt.barh(intent_data['Behavior'], 
                    intent_data['Conversion_Rate'],
                    color='#FF9800')
    plt.xlabel('Conversion Rate (%)')
    plt.title('Conversion Rate by High-Intent Behavior')
    plt.axvline(x=baseline_rate, 
                color='r', linestyle='--', alpha=0.5, 
                label=f'Baseline: {baseline_rate:.1f}%')

    # Add value labels
    for bar, rate in zip(bars, intent_data['Conversion_Rate']):
        plt.text(rate + 1, bar.get_y() + bar.get_height()/2, 
                 f'{rate:.1f}%', va='center', fontweight='bold')

    plt.legend()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_conversion_timeline(timeline_df: pd.DataFrame, output_path: str = None):
    """
    Visualize distribution of time to conversion.
    
    Args:
        timeline_df: DataFrame with conversion timeline (must have 'days_to_convert')
        output_path: Optional path to save figure
    """
    plt.figure(figsize=(12, 6))
    plt.hist(timeline_df['days_to_convert'], bins=30, color='#9C27B0', 
             alpha=0.7, edgecolor='black')
    plt.xlabel('Days to Convert')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Time to Conversion')
    plt.axvline(timeline_df['days_to_convert'].median(), color='r', 
                linestyle='--', linewidth=2, 
                label=f"Median: {timeline_df['days_to_convert'].median():.1f}d")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
