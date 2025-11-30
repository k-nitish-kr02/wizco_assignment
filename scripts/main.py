"""
Main execution script for user conversion analysis.

This script runs the complete analysis pipeline:
1. Load and validate data
2. Run funnel analysis
3. Perform segmentation analysis
4. Calculate behavioral metrics
5. Generate visualizations
6. Export results

Usage:
    python scripts/main.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_all_data, validate_data
from funnel_analysis import (
    build_funnel, 
    calculate_retention, 
    calculate_30day_upgrade_rate
)
from segmentation import (
    segment_by_country,
    segment_by_device,
    segment_by_source
)
from behavioral_metrics import (
    behavioral_metrics,
    high_intent_analysis,
    calculate_engagement_score
)
from visualization import (
    plot_funnel,
    plot_retention_curve,
    plot_segment_comparison,
    plot_behavioral_comparison,
    plot_intent_signals
)


def setup_directories():
    """Create output directories if they don't exist."""
    Path('outputs/figures').mkdir(parents=True, exist_ok=True)
    Path('outputs/tables').mkdir(parents=True, exist_ok=True)
    print("✓ Output directories ready")


def load_and_validate():
    """Load and validate all datasets."""
    print("\n" + "="*60)
    print("STEP 1: LOADING AND VALIDATING DATA")
    print("="*60)
    
    users, events, payments = load_all_data()
    validate_data(users, events, payments)
    
    return users, events, payments


def run_funnel_analysis(users, events, payments):
    """Run funnel analysis and export results."""
    print("\n" + "="*60)
    print("STEP 2: FUNNEL ANALYSIS")
    print("="*60)
    
    # Build funnel
    funnel = build_funnel(users, events, payments)
    print("\n📊 Conversion Funnel:")
    print(funnel[['Step', 'Users', 'Conversion_Rate', 'Pct_of_Signups']].to_string(index=False))
    
    # Save funnel data
    funnel[['Step', 'Users', 'Conversion_Rate', 'Pct_of_Signups']].to_csv(
        'outputs/tables/funnel_metrics.csv', index=False
    )
    print("\n✓ Saved to outputs/tables/funnel_metrics.csv")
    
    # Calculate retention
    retention = calculate_retention(users, events, weeks=12)
    print("\n📈 Weekly Retention (first 5 weeks):")
    print(retention.head().to_string(index=False))
    
    # Save retention data
    retention.to_csv('outputs/tables/retention_metrics.csv', index=False)
    print("✓ Saved to outputs/tables/retention_metrics.csv")
    
    # Calculate 30-day upgrade rate
    upgrade_30d = calculate_30day_upgrade_rate(users, payments)
    print(f"\n🎯 30-Day Upgrade Rate: {upgrade_30d['upgrade_rate_30d']:.2f}%")
    print(f"   ({upgrade_30d['upgraded_30d']} out of {upgrade_30d['total_users']} users)")
    
    # Generate visualizations
    print("\n📊 Generating funnel visualization...")
    plot_funnel(funnel, 'outputs/figures/funnel_chart.png')
    
    print("📊 Generating retention curve...")
    plot_retention_curve(retention, 'outputs/figures/retention_curve.png')
    
    return funnel, retention, upgrade_30d


def run_segmentation_analysis(users, events, payments):
    """Run segmentation analysis and export results."""
    print("\n" + "="*60)
    print("STEP 3: SEGMENTATION ANALYSIS")
    print("="*60)
    
    # Segment by country
    country_seg = segment_by_country(users, events, payments)
    print("\n🌍 Segmentation by Country:")
    print(country_seg[['country', 'Signups', 'Upgrade_Rate']].to_string(index=False))
    country_seg.to_csv('outputs/tables/segment_country.csv', index=False)
    
    # Segment by device
    device_seg = segment_by_device(users, events, payments)
    print("\n📱 Segmentation by Device:")
    print(device_seg[['device', 'Signups', 'Upgrade_Rate']].to_string(index=False))
    device_seg.to_csv('outputs/tables/segment_device.csv', index=False)
    
    # Segment by source
    source_seg = segment_by_source(users, events, payments)
    print("\n🔍 Segmentation by Source:")
    print(source_seg[['source', 'Signups', 'Upgrade_Rate']].to_string(index=False))
    source_seg.to_csv('outputs/tables/segment_source.csv', index=False)
    
    print("\n✓ Saved all segmentation data to outputs/tables/")
    
    # Generate visualizations
    print("\n📊 Generating segmentation visualizations...")
    plot_segment_comparison(country_seg, 'country', 'outputs/figures/segment_country.png')
    plot_segment_comparison(device_seg, 'device', 'outputs/figures/segment_device.png')
    plot_segment_comparison(source_seg, 'source', 'outputs/figures/segment_source.png')
    
    return country_seg, device_seg, source_seg


def run_behavioral_analysis(users, events, payments, funnel):
    """Run behavioral analysis and export results."""
    print("\n" + "="*60)
    print("STEP 4: BEHAVIORAL ANALYSIS")
    print("="*60)
    
    # Calculate behavioral metrics
    behavior = behavioral_metrics(users, events, payments)
    
    # Compare upgraded vs non-upgraded
    print("\n🔍 Behavioral Comparison (Upgraded vs Non-Upgraded):")
    comparison = behavior.groupby('is_upgraded').agg({
        'total_events': 'mean',
        'distinct_events': 'mean',
        'days_active': 'mean',
        'days_to_feature': 'mean'
    }).round(2)
    print(comparison)
    
    behavior.to_csv('outputs/tables/behavioral_metrics.csv', index=False)
    print("\n✓ Saved to outputs/tables/behavioral_metrics.csv")
    
    # High-intent analysis
    intent = high_intent_analysis(users, events, payments)
    print("\n🎯 High-Intent Behaviors:")
    print(intent.to_string(index=False))
    
    intent.to_csv('outputs/tables/high_intent_signals.csv', index=False)
    print("✓ Saved to outputs/tables/high_intent_signals.csv")
    
    # Calculate engagement scores
    engagement = calculate_engagement_score(users, events)
    engagement.to_csv('outputs/tables/engagement_scores.csv', index=False)
    
    # Generate visualizations
    print("\n📊 Generating behavioral visualizations...")
    plot_behavioral_comparison(behavior, 'outputs/figures/behavioral_comparison.png')
    
    baseline_rate = funnel.iloc[3]['Pct_of_Signups']
    plot_intent_signals(intent, baseline_rate, 'outputs/figures/high_intent_signals.png')
    
    return behavior, intent, engagement


def generate_summary():
    """Generate executive summary."""
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    
    print("\n📁 Generated Files:")
    print("\n  Tables (outputs/tables/):")
    print("    • funnel_metrics.csv")
    print("    • retention_metrics.csv")
    print("    • segment_country.csv")
    print("    • segment_device.csv")
    print("    • segment_source.csv")
    print("    • behavioral_metrics.csv")
    print("    • high_intent_signals.csv")
    print("    • engagement_scores.csv")
    
    print("\n  Visualizations (outputs/figures/):")
    print("    • funnel_chart.png")
    print("    • retention_curve.png")
    print("    • segment_country.png")
    print("    • segment_device.png")
    print("    • segment_source.png")
    print("    • behavioral_comparison.png")
    print("    • high_intent_signals.png")
    
    print("\n✅ All analyses completed successfully!")
    print("📊 Review the report in reports/ for full insights and recommendations")


def main():
    """Main execution function."""
    print("🚀 Starting User Conversion Analysis Pipeline")
    print("="*60)
    
    # Setup
    setup_directories()
    
    # Load data
    users, events, payments = load_and_validate()
    
    # Run analyses
    funnel, retention, upgrade_30d = run_funnel_analysis(users, events, payments)
    country_seg, device_seg, source_seg = run_segmentation_analysis(users, events, payments)
    behavior, intent, engagement = run_behavioral_analysis(users, events, payments, funnel)
    
    # Summary
    generate_summary()
    
    return {
        'users': users,
        'events': events,
        'payments': payments,
        'funnel': funnel,
        'retention': retention,
        'segments': {
            'country': country_seg,
            'device': device_seg,
            'source': source_seg
        },
        'behavior': behavior,
        'intent': intent,
        'engagement': engagement
    }


if __name__ == '__main__':
    results = main()
