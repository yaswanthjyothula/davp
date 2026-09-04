"""
DataTable component for F1 Historical Analytics.
Theme: High contrast motorsport table.
Strictly zero hyphens in headers, cell contents, or export buttons.
"""

from dash import dash_table, html, dcc
from utils.constants import FONT_FAMILY, COLOR_F1_RED, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED
from utils.helpers import remove_hyphens

def create_f1_table(df, table_id="f1-table", page_size=15, export_btn_id=None):
    """
    Renders styled, paginated, and sortable Dash DataTable.
    """
    if df is None or df.empty:
        return html.Div("No records found.", style={"color": COLOR_TEXT_MUTED, "padding": "20px"})
        
    # Clean DataFrame columns and cells of hyphens
    clean_df = df.copy()
    clean_df.columns = [remove_hyphens(str(col).replace('_', ' ').title()) for col in clean_df.columns]
    
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
            
    columns = [{"name": c, "id": c} for c in clean_df.columns]
    
    table = dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=clean_df.to_dict('records'),
        page_size=page_size,
        sort_action='native',
        filter_action='native',
        style_table={'overflowX': 'auto', 'borderRadius': '6px'},
        style_header={
            'backgroundColor': '#f8fafc',
            'color': '#475569',
            'fontWeight': '800',
            'fontSize': '11px',
            'letterSpacing': '1px',
            'textTransform': 'uppercase',
            'borderBottom': '1px solid #e2e8f0',
            'fontFamily': FONT_FAMILY,
            'padding': '12px 14px',
        },
        style_cell={
            'backgroundColor': '#ffffff',
            'color': '#0f172a',
            'fontFamily': FONT_FAMILY,
            'fontSize': '12px',
            'padding': '10px 14px',
            'borderBottom': '1px solid #f1f5f9',
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#fcfcfd',
            }
        ]
    )
    
    if export_btn_id:
        return html.Div(
            children=[
                dcc.Download(id=f"{export_btn_id}-download"),
                html.Div(id=export_btn_id, style={"display": "none"}),
                table
            ]
        )
    return table
