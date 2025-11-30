# User Behavior & Conversion Analysis

## Project Overview

This project analyzes user behavior, conversion funnels, and upgrade patterns for an AI content generation web application. The analysis helps product leadership understand:

- How users behave after signup
- Where they drop off in the journey
- Which behaviors correlate with upgrading to a paid plan
- How this varies across different user segments

## Quick Start

```bash
# 1. Clone or navigate to project directory
cd user-conversion-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run complete analysis
python scripts/main.py

# OR use Jupyter notebook
jupyter notebook notebooks/analysis_notebook.ipynb
```

## Project Structure

```
user-conversion-analysis/
├── data/
│   ├── raw/              # Original CSV files
│   │   ├── users.csv
│   │   ├── events.csv
│   │   └── payments.csv
│   └── processed/        # Cleaned/transformed data (generated)
├── sql/                  # SQL queries for PostgreSQL
│   ├── 01_funnel_analysis.sql
│   ├── 02_segmentation.sql
│   ├── 03_behavioral_signals.sql
│   ├── 04_retention.sql
│   └── 05_conversion_timeline.sql
├── scripts/              # Python analysis modules
│   ├── data_loader.py          # Data loading & validation
│   ├── funnel_analysis.py      # Funnel calculations
│   ├── segmentation.py         # Segment analysis
│   ├── behavioral_metrics.py   # Behavioral signals
│   ├── visualization.py        # Plotting functions
│   └── main.py                 # Main execution script
├── notebooks/            # Jupyter notebooks
│   └── analysis_notebook.ipynb # Complete analysis workflow
├── outputs/              # Generated outputs
│   ├── figures/          # Visualizations (PNG)
│   └── tables/           # Data exports (CSV)
├── reports/              # Final deliverables
│   └── User_Conversion_Analysis_Report.md
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Dataset Description

### 1. `users.csv`
- **user_id**: Unique identifier
- **signup_date**: Date of signup (YYYY-MM-DD)
- **country**: User's country
- **device**: Primary device (mobile, desktop, tablet)
- **source**: Acquisition source (ads, organic, referral, social, partner)

### 2. `events.csv`
- **user_id**: User who performed the event
- **event_name**: Action type (visited_homepage, viewed_feature, etc.)
- **event_time**: Timestamp (YYYY-MM-DD HH:MM:SS)

### 3. `payments.csv`
- **user_id**: User who upgraded
- **plan_type**: monthly or annual
- **amount**: Payment amount
- **payment_date**: Date of payment (YYYY-MM-DD)

## Analysis Workflow

### Option 1: Run Complete Pipeline

```bash
python scripts/main.py
```

This will:
1. Load and validate all data
2. Run funnel analysis
3. Perform segmentation analysis
4. Calculate behavioral metrics
5. Generate all visualizations
6. Export results to `outputs/`

### Option 2: Use Jupyter Notebook

```bash
jupyter notebook notebooks/analysis_notebook.ipynb
```

The notebook provides:
- Step-by-step analysis with explanations
- Interactive visualizations
- Detailed insights and interpretations
- All code cells ready to run

### Option 3: Custom Analysis

```python
from scripts.data_loader import load_all_data
from scripts.funnel_analysis import build_funnel

# Load data
users, events, payments = load_all_data()

# Run specific analysis
funnel = build_funnel(users, events, payments)
print(funnel)
```

## Key Analyses

### 1. Product Funnel
4-step conversion funnel:
1. Signed up
2. Viewed a feature
3. Returned within 7 days
4. Upgraded to paid

**Output**: `outputs/tables/funnel_metrics.csv`, `outputs/figures/funnel_chart.png`

### 2. Segmentation
Analyze funnel performance across:
- Country
- Device type
- Acquisition source

**Output**: `outputs/tables/segment_*.csv`, `outputs/figures/segment_*.png`

### 3. Behavioral Signals
Compare upgraded vs non-upgraded users on:
- Event counts
- Feature diversity
- Days active
- Time to first action

**Output**: `outputs/tables/behavioral_metrics.csv`, `outputs/figures/behavioral_comparison.png`

### 4. Retention
Weekly retention tracking for 12 weeks post-signup

**Output**: `outputs/tables/retention_metrics.csv`, `outputs/figures/retention_curve.png`

## SQL Queries

All SQL queries are PostgreSQL-compatible and can be run directly on a database:

```sql
-- Example: Run funnel analysis
psql -d your_database -f sql/01_funnel_analysis.sql
```

Or use Python with SQLAlchemy:

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://user:password@localhost/dbname')
query = open('sql/01_funnel_analysis.sql').read()
result = pd.read_sql(query, engine)
```

## Deliverables

### 1. Report
- **Location**: `reports/User_Conversion_Analysis_Report.md`
- **Contents**: 
  - Funnel analysis with conversion rates
  - Segment comparison and insights
  - Behavioral signals and high-intent actions
  - Actionable recommendations

### 2. SQL Queries
- **Location**: `sql/` directory
- **Files**: All queries organized by analysis type

### 3. Analysis Notebook
- **Location**: `notebooks/analysis_notebook.ipynb`
- **Contents**: Complete analysis with visualizations

### 4. Outputs
- **Tables**: `outputs/tables/*.csv`
- **Visualizations**: `outputs/figures/*.png`

## Requirements

- **Python**: 3.8 or higher
- **PostgreSQL**: 12+ (optional, for SQL queries)
- **Packages**: See `requirements.txt`

## Troubleshooting

### Import Errors

If you get module import errors:

```bash
# Make sure you're in the project root
cd user-conversion-analysis

# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from scripts directory
cd scripts && python main.py
```

### Memory Issues

For large datasets:

```python
# Load data in chunks
users = pd.read_csv('data/raw/users.csv', chunksize=10000)

# Or use Dask for larger-than-memory datasets
import dask.dataframe as dd
users = dd.read_csv('data/raw/users.csv')
```

### Missing Data Files

Ensure all three CSV files are in `data/raw/`:
- users.csv
- events.csv
- payments.csv

## Key Assumptions

1. All timestamps are in consistent timezone (UTC assumed)
2. "Returned within 7 days" = any event on days 1-7 after signup
3. Events on signup day (day 0) count for engagement but not "return"
4. All event types count equally
5. Conversion window focus: 30 days

## Contact

For questions or issues with this analysis, please contact the analytics team.

---

**Last Updated**: November 2024  
**Version**: 1.0