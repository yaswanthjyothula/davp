"""
Constants for F1 Historical Analytics Platform.
Zero hyphens in all labels, strings, and era definitions.
"""

FONT_FAMILY = "Formula1-Regular, Formula1, sans-serif"

# White Motorsport Palette
COLOR_BG_DARK = "#ffffff"
COLOR_BG_CARD = "#ffffff"
COLOR_BG_CARD_HOVER = "#fbfcfd"
COLOR_F1_RED = "#E10600"
COLOR_F1_GOLD = "#D97706"
COLOR_F1_CYAN = "#0284C7"
COLOR_TEXT_WHITE = "#0f172a"
COLOR_TEXT_MUTED = "#64748b"
COLOR_BORDER = "#e2e8f0"
COLOR_BORDER_RED = "rgba(225, 6, 0, 0.35)"

# Constructor Colors
CONSTRUCTOR_COLORS = {
    'ferrari': '#E10600',
    'scuderia ferrari': '#E10600',
    'mclaren': '#FF8000',
    'mercedes': '#00A896',
    'red_bull': '#1E40AF',
    'red bull': '#1E40AF',
    'williams': '#0284C7',
    'alpine': '#0093CC',
    'renault': '#CA8A04',
    'aston_martin': '#047857',
    'aston martin': '#047857',
    'alfa': '#BE123C',
    'alfa romeo': '#BE123C',
    'sauber': '#16A34A',
    'haas': '#475569',
    'alphatauri': '#334155',
    'toro_rosso': '#2563EB',
    'toro rosso': '#2563EB',
    'racing_point': '#DB2777',
    'force_india': '#EA580C',
    'lotus_f1': '#B45309',
    'lotus': '#B45309',
    'team lotus': '#B45309',
    'brawn': '#65A30D',
    'benetton': '#0D9488',
    'brabham': '#15803D',
    'tyrrell': '#1E3A8A',
    'cooper': '#065F46',
    'brm': '#1F2937',
    'maserati': '#1E293B',
    'matra': '#1D4ED8',
    'vanwall': '#14532D',
}

# Historical Eras (strictly using 'to' with NO hyphens)
ERAS = [
    {'name': 'All History', 'start': 1950, 'end': 2026, 'label': '1950 to 2026'},
    {'name': 'Early Formula 1', 'start': 1950, 'end': 1960, 'label': '1950 to 1960'},
    {'name': 'Classic Era', 'start': 1961, 'end': 1976, 'label': '1961 to 1976'},
    {'name': 'Ground Effect and Turbo', 'start': 1977, 'end': 1988, 'label': '1977 to 1988'},
    {'name': 'High Tech V10 Era', 'start': 1989, 'end': 2005, 'label': '1989 to 2005'},
    {'name': 'V8 Era', 'start': 2006, 'end': 2013, 'label': '2006 to 2013'},
    {'name': 'Turbo Hybrid Era', 'start': 2014, 'end': 2021, 'label': '2014 to 2021'},
    {'name': 'Ground Effect 2.0', 'start': 2022, 'end': 2026, 'label': '2022 to 2026'},
]

# Standard Plotly F1 White Theme Template
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': FONT_FAMILY, 'color': '#0f172a'},
        'title': {'font': {'family': FONT_FAMILY, 'size': 15, 'color': '#0f172a'}},
        'xaxis': {
            'gridcolor': '#f1f5f9',
            'linecolor': '#cbd5e1',
            'tickfont': {'family': FONT_FAMILY, 'color': '#64748b'},
            'title': {'font': {'family': FONT_FAMILY, 'color': '#475569'}},
        },
        'yaxis': {
            'gridcolor': '#f1f5f9',
            'linecolor': '#cbd5e1',
            'tickfont': {'family': FONT_FAMILY, 'color': '#64748b'},
            'title': {'font': {'family': FONT_FAMILY, 'color': '#475569'}},
        },
        'legend': {
            'font': {'family': FONT_FAMILY, 'color': '#0f172a'},
            'bgcolor': 'rgba(255, 255, 255, 0.92)',
            'bordercolor': '#e2e8f0',
        },
        'margin': {'t': 40, 'r': 20, 'b': 40, 'l': 40},
    }
}
