"""
Data validation and data quality checks for F1 Historical Analytics.
Strictly returns clean text with zero hyphens.
"""

import pandas as pd
from utils.helpers import remove_hyphens, format_f1_date

def validate_dataset(dfs):
    """
    Perform deep validation across all tables in the dataset.
    Returns a structured dictionary of quality metrics.
    """
    summary = {}
    total_records = 0
    total_missing = 0
    
    for name, df in dfs.items():
        if df is None or df.empty:
            summary[name] = {
                'rows': 0,
                'columns': 0,
                'missing_values': 0,
                'duplicates': 0,
                'status': 'Empty',
            }
            continue
            
        rows = len(df)
        cols = len(df.columns)
        null_count = int(df.isna().sum().sum())
        dup_count = int(df.duplicated().sum())
        total_records += rows
        total_missing += null_count
        
        summary[name] = {
            'rows': rows,
            'columns': cols,
            'missing_values': null_count,
            'duplicates': dup_count,
            'status': 'Validated',
        }
    
    # Calculate overall health score
    completeness = 100.0
    if total_records > 0:
        total_cells = sum(s['rows'] * s['columns'] for s in summary.values())
        completeness = round(((total_cells - total_missing) / max(total_cells, 1)) * 100, 2)
        
    return {
        'tables': summary,
        'total_records': total_records,
        'total_missing': total_missing,
        'completeness_score': f"{completeness}%",
        'data_source': remove_hyphens("FIA World Championship Official Historical Records / Jolpica Ergast API"),
        'last_audited': format_f1_date(pd.Timestamp.now().strftime('%Y/%m/%d')),
    }
