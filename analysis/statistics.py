"""
Statistical methods, distributions, quartiles, and outlier detection for F1 Historical Analytics.
Strictly zero hyphens in all outputs and metric labels.
"""

import pandas as pd
import numpy as np
from services.data_loader import DataLoader
from utils.helpers import remove_hyphens

def get_descriptive_stats():
    """
    Compute comprehensive summary statistics for drivers, constructors, and races.
    """
    loader = DataLoader.get_instance()
    drivers = loader.query("SELECT wins, podiums, poles, starts, points, avg_finish, avg_grid, win_rate FROM driver_summary")
    
    desc = drivers.describe().round(2).to_dict()
    
    metrics = ['starts', 'wins', 'podiums', 'poles', 'points', 'win_rate']
    rows = []
    for m in metrics:
        if m in desc:
            rows.append({
                'Metric': remove_hyphens(m.replace('_', ' ').title()),
                'Mean': desc[m]['mean'],
                'Median': desc[m]['50%'],
                'Std Dev': desc[m]['std'],
                'Min': desc[m]['min'],
                'Max': desc[m]['max'],
                'Q1 (25%)': desc[m]['25%'],
                'Q3 (75%)': desc[m]['75%'],
            })
    return pd.DataFrame(rows)

def detect_outliers_iqr(series):
    """
    Perform Tukey's IQR Outlier Detection.
    """
    clean_s = series.dropna()
    q1 = clean_s.quantile(0.25)
    q3 = clean_s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = clean_s[(clean_s < lower_bound) | (clean_s > upper_bound)]
    return {
        'q1': round(float(q1), 2),
        'q3': round(float(q3), 2),
        'iqr': round(float(iqr), 2),
        'lower_bound': round(float(lower_bound), 2),
        'upper_bound': round(float(upper_bound), 2),
        'outlier_count': len(outliers),
    }
