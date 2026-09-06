"""
Constants for F1 Historical Analytics Platform.
Zero hyphens in all labels, strings, and era definitions.
"""

FONT_FAMILY = "Formula1-Regular, Formula1, sans-serif"

# Dark Motorsport Palette & Design Tokens
FONT_FAMILY = "'Barlow', 'Formula1', -apple-system, BlinkMacSystemFont, sans-serif"
FONT_DISPLAY = "'Barlow Condensed', 'Formula1-Bold', sans-serif"
FONT_MONO = "'JetBrains Mono', 'Roboto Mono', monospace"

# Deep Graphite Workstation Palette
COLOR_BG_DARK = "#08090A"
COLOR_BG_SURFACE = "#0E1013"
COLOR_BG_CARD = "#14171C"
COLOR_BG_CARD_HOVER = "#1B2026"
COLOR_BG_INPUT = "#16191F"

COLOR_F1_RED = "#E10600"
COLOR_F1_RED_HOVER = "#FF1801"
COLOR_F1_RED_GLOW = "rgba(225, 6, 0, 0.25)"
COLOR_F1_GOLD = "#FFB800"
COLOR_F1_CYAN = "#00F0FF"

COLOR_TEXT_WHITE = "#F8FAFC"
COLOR_TEXT_SECONDARY = "#9DA3AE"
COLOR_TEXT_MUTED = "#5F6672"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_BORDER_FOCUS = "rgba(255, 255, 255, 0.18)"
COLOR_BORDER_RED = "rgba(225, 6, 0, 0.4)"

# Constructor Colors
CONSTRUCTOR_COLORS = {
    'ferrari': '#E10600',
    'scuderia ferrari': '#E10600',
    'mclaren': '#FF8000',
    'mercedes': '#00F0FF',
    'red_bull': '#1E40AF',
    'red bull': '#1E40AF',
    'williams': '#0284C7',
    'alpine': '#0093CC',
    'renault': '#FFD700',
    'aston_martin': '#047857',
    'aston martin': '#047857',
    'alfa': '#BE123C',
    'alfa romeo': '#BE123C',
    'sauber': '#10B981',
    'haas': '#94A3B8',
    'alphatauri': '#38BDF8',
    'toro_rosso': '#2563EB',
    'toro rosso': '#2563EB',
    'racing_point': '#EC4899',
    'force_india': '#F97316',
    'lotus_f1': '#B45309',
    'lotus': '#B45309',
    'team lotus': '#B45309',
    'brawn': '#84CC16',
    'benetton': '#0D9488',
    'brabham': '#15803D',
    'tyrrell': '#3B82F6',
    'cooper': '#059669',
    'brm': '#374151',
    'maserati': '#1E293B',
    'matra': '#2563EB',
    'vanwall': '#166534',
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

# Unified Dark Motorsport Plotly Theme Template
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': FONT_FAMILY, 'color': COLOR_TEXT_WHITE},
        'title': {'font': {'family': FONT_DISPLAY, 'size': 15, 'color': COLOR_TEXT_WHITE}},
        'xaxis': {
            'gridcolor': 'rgba(255, 255, 255, 0.05)',
            'linecolor': 'rgba(255, 255, 255, 0.12)',
            'tickfont': {'family': FONT_MONO, 'color': COLOR_TEXT_SECONDARY, 'size': 11},
            'title': {'font': {'family': FONT_FAMILY, 'color': COLOR_TEXT_SECONDARY, 'size': 12}},
            'zerolinecolor': 'rgba(255, 255, 255, 0.08)',
        },
        'yaxis': {
            'gridcolor': 'rgba(255, 255, 255, 0.05)',
            'linecolor': 'rgba(255, 255, 255, 0.12)',
            'tickfont': {'family': FONT_MONO, 'color': COLOR_TEXT_SECONDARY, 'size': 11},
            'title': {'font': {'family': FONT_FAMILY, 'color': COLOR_TEXT_SECONDARY, 'size': 12}},
            'zerolinecolor': 'rgba(255, 255, 255, 0.08)',
        },
        'legend': {
            'font': {'family': FONT_FAMILY, 'color': COLOR_TEXT_WHITE, 'size': 11},
            'bgcolor': 'rgba(14, 16, 20, 0.85)',
            'bordercolor': 'rgba(255, 255, 255, 0.1)',
            'borderwidth': 1,
        },
        'hoverlabel': {
            'bgcolor': '#0E1013',
            'font': {'family': FONT_FAMILY, 'color': '#FFFFFF', 'size': 12},
            'bordercolor': COLOR_F1_RED,
        },
        'margin': {'t': 45, 'r': 20, 'b': 40, 'l': 40},
    }
}
