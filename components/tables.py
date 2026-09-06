"""
DataTable component for F1 Historical Analytics.
Theme: High precision motorsport timing tower table.
Strictly zero hyphens in headers, cell contents, or export buttons.
"""

from dash import dash_table, html, dcc
from utils.constants import (
    FONT_FAMILY, FONT_DISPLAY, FONT_MONO, COLOR_F1_RED, 
    COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_BG_CARD, COLOR_BG_DARK, COLOR_BORDER
)
from utils.helpers import remove_hyphens

def create_f1_table(df, table_id="f1-table", page_size=15, export_btn_id=None):
    """
    Renders a styled, paginated, and sortable motorsport timing DataTable.
    """
    if df is None or df.empty:
        return html.Div(
            className="empty-state-container",
            children=[
                html.Div("NO RECORDS FOUND", className="empty-state-title"),
                html.Div("No telemetry records match the current filter selection.", className="empty-state-desc")
            ]
        )
        
    clean_df = df.copy()
    clean_df.columns = [remove_hyphens(str(col).replace('_', ' ').title()) for col in clean_df.columns]
    
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
            
    columns = [{"name": c, "id": c} for c in clean_df.columns]
    
    # Identify numeric and position columns for custom motorsport styling
    numeric_cols = [c for c in clean_df.columns if any(k in c.lower() for k in ['wins', 'starts', 'points', 'podiums', 'poles', 'laps', 'grid', 'round', 'season', 'position', 'total'])]
    
    style_cell_conditional = []
    for c in numeric_cols:
        style_cell_conditional.append({
            'if': {'column_id': c},
            'fontFamily': FONT_MONO,
            'fontVariantNumeric': 'tabular-nums',
            'letterSpacing': '0.5px'
        })
        
    style_data_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#111418',
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#0C0E11',
        },
        # Selected and active states: high contrast bold black text on white background
        {
            'if': {'state': 'selected'},
            'backgroundColor': '#FFFFFF',
            'color': '#000000',
            'fontWeight': '700'
        },
        {
            'if': {'state': 'active'},
            'backgroundColor': '#FFFFFF',
            'color': '#000000',
            'fontWeight': '700'
        },
        # Highlight winner / P1 rows subtly
        {
            'if': {
                'filter_query': '{Position} = 1 || {Position} = "1" || {Finish} = 1 || {Finish} = "1"',
            },
            'color': '#FFFFFF',
            'fontWeight': '700'
        }
    ]
    
    table = dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=clean_df.to_dict('records'),
        page_size=page_size,
        sort_action='native',
        filter_action='native',
        style_table={
            'overflowX': 'auto',
            'borderRadius': '6px',
            'border': '1px solid rgba(255, 255, 255, 0.08)'
        },
        style_header={
            'backgroundColor': '#15181D',
            'color': '#9DA3AE',
            'fontWeight': '800',
            'fontSize': '11px',
            'letterSpacing': '1.2px',
            'textTransform': 'uppercase',
            'borderBottom': '1px solid rgba(255, 255, 255, 0.12)',
            'fontFamily': FONT_DISPLAY,
            'padding': '11px 14px',
            'textAlign': 'left'
        },
        style_cell={
            'backgroundColor': '#0E1013',
            'color': '#E2E8F0',
            'fontFamily': FONT_FAMILY,
            'fontSize': '12.5px',
            'padding': '10px 14px',
            'borderBottom': '1px solid rgba(255, 255, 255, 0.04)',
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_filter={
            'backgroundColor': '#14171C',
            'color': '#F8FAFC',
            'fontSize': '11px',
            'fontFamily': FONT_FAMILY,
            'border': '1px solid rgba(255, 255, 255, 0.08)'
        },
        style_cell_conditional=style_cell_conditional,
        style_data_conditional=style_data_conditional
    )
    
    if export_btn_id:
        return html.Div(
            children=[
                dcc.Download(id=f"{export_btn_id}-download"),
                html.Div(
                    style={"display": "flex", "justifyContent": "flex-end", "marginBottom": "12px"},
                    children=[
                        html.Button(
                            children=[
                                html.Span("↓", style={"marginRight": "6px", "fontWeight": "bold"}),
                                html.Span("EXPORT CSV")
                            ],
                            id=export_btn_id,
                            className="btn-export",
                            n_clicks=0
                        )
                    ]
                ),
                table
            ]
        )
    return table
