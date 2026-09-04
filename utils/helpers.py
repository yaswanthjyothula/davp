"""
Utility helpers for F1 Historical Analytics.
STRICT CONSTRAINT ENFORCEMENT:
Zero hyphens or dashes ('-') in any user-facing text, dates, numbers, ranges, or labels.
All dates formatted with slashes ('YYYY/MM/DD') or written out ('DD Mon YYYY').
All ranges use 'to' ('1950 to 2026').
All negative deltas use 'Loss' / 'Down' / 'Deficit' or parentheses.
All missing values return 'N/A' (never '-' or '--').
"""

import re
import pandas as pd

def remove_hyphens(text):
    """
    Remove all hyphens and replace with appropriate motorsport formatting.
    """
    if text is None:
        return 'N/A'
    s = str(text)
    if s.strip() in ['-', '--', '---', '', 'nan', 'None', 'NAT']:
        return 'N/A'
    
    # Replace dates like 1950-05-13 -> 1950/05/13
    s = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1/\2/\3', s)
    
    # Replace year ranges like 1950-2024 -> 1950 to 2024
    s = re.sub(r'(\d+)\s*[-–—]\s*(\d+)', r'\1 to \2', s)
    
    # Replace compound F1 words
    replacements = {
        'Head-to-head': 'Head to Head',
        'head-to-head': 'head to head',
        'Pit-stop': 'Pit Stop',
        'pit-stop': 'pit stop',
        'Pit-stops': 'Pit Stops',
        'pit-stops': 'pit stops',
        'Pole-to-win': 'Pole to Win',
        'pole-to-win': 'pole to win',
        'Lap-by-lap': 'Lap by Lap',
        'lap-by-lap': 'lap by lap',
        'Pre-season': 'Preseason',
        'pre-season': 'preseason',
        'All-time': 'All Time',
        'all-time': 'all time',
        'Non-finish': 'Non Finish',
        'non-finish': 'non finish',
        'wheel-to-wheel': 'wheel to wheel',
        'Wheel-to-wheel': 'Wheel to Wheel',
        'back-to-back': 'back to back',
        'Back-to-back': 'Back to Back',
        'side-by-side': 'side by side',
        'Side-by-side': 'Side by Side',
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
        
    # Catch any remaining hyphens, em-dashes, en-dashes
    s = s.replace('-', ' ')
    s = s.replace('–', ' to ')
    s = s.replace('—', ' to ')
    # Normalize multiple spaces
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def format_f1_date(val):
    """Format any date to YYYY/MM/DD with no hyphens."""
    if pd.isna(val) or val is None or str(val).strip() in ['', 'N/A', 'nan']:
        return 'N/A'
    s = str(val).strip()
    s = s.replace('-', '/')
    return s

def format_delta(val, unit=''):
    """
    Format deltas without minus signs.
    E.g. +3 -> '+3', -2 -> 'Down 2', 0 -> 'Level'
    """
    try:
        num = float(val)
        if num > 0:
            return f'+{num:g} {unit}'.strip()
        elif num < 0:
            return f'Down {abs(num):g} {unit}'.strip()
        else:
            return 'Level'
    except (ValueError, TypeError):
        return 'N/A'

def format_grid_gain(grid, finish):
    """Calculate grid to finish gain without negative sign."""
    try:
        g = int(grid)
        f = int(finish)
        diff = g - f
        if diff > 0:
            return f'Gain {diff}'
        elif diff < 0:
            return f'Loss {abs(diff)}'
        else:
            return 'Level'
    except (ValueError, TypeError):
        return 'N/A'

def safe_display(val, default='N/A'):
    """Ensure no nulls or hyphens in displayed values."""
    if pd.isna(val) or val is None or str(val).strip() in ['', '-', '--', 'nan', 'None']:
        return default
    return remove_hyphens(str(val))
