"""
Data Explorer Page for F1 Historical Analytics.
Theme: Relational Database Telemetry Explorer with Dynamic CSV Export.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from utils.helpers import remove_hyphens

TABLE_OPTIONS = [
    {'label': 'Drivers (driver summary)', 'value': 'driver_summary'},
    {'label': 'Constructors (constructor summary)', 'value': 'constructor_summary'},
    {'label': 'Circuits (circuit summary)', 'value': 'circuit_summary'},
    {'label': 'Races (historical calendar)', 'value': 'races'},
    {'label': 'Race Results (all time entries)', 'value': 'results'},
    {'label': 'Qualifying Telemetry (single lap)', 'value': 'qualifying'},
    {'label': 'Driver Standings Archive', 'value': 'driver_standings'},
    {'label': 'Constructor Standings Archive', 'value': 'constructor_standings'},
    {'label': 'Pit Stops Telemetry', 'value': 'pit_stops'},
    {'label': 'Sprint Race Results', 'value': 'sprint_results'},
]

def layout():
    loader = DataLoader.get_instance()
    initial_df = loader.query("SELECT * FROM driver_summary LIMIT 200")
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("RELATIONAL DATA EXPLORER", className="section-title"),
                    html.P("Direct relational query inspection across all historical SQLite tables with dynamic schema viewing and instant CSV export.", className="section-subtitle")
                ]
            ),
            
            # Selectors bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"flex": "1 1 360px"},
                        children=[
                            html.Label("Select Relational Dataset Table", className="filter-label"),
                            dcc.Dropdown(
                                id="explorer-table-selector",
                                options=TABLE_OPTIONS,
                                value='driver_summary',
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        style={"flex": "1 1 200px"},
                        children=[
                            html.Label("Maximum Record Limit", className="filter-label"),
                            dcc.Dropdown(
                                id="explorer-limit-selector",
                                options=[
                                    {'label': '100 Records', 'value': 100},
                                    {'label': '250 Records', 'value': 250},
                                    {'label': '500 Records', 'value': 500},
                                    {'label': '1000 Records', 'value': 1000},
                                ],
                                value=250,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                ]
            ),
            
            # Table Container Card
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header",
                        children=[html.H3("RAW & PROCESSED RELATIONAL TABLE VIEWER", className="chart-title")]
                    ),
                    html.Div(
                        id="explorer-table-container",
                        children=[create_f1_table(initial_df, table_id="explorer-table", page_size=20, export_btn_id="btn-export-explorer")]
                    )
                ]
            )
        ]
    )

@callback(
    Output("explorer-table-container", "children"),
    Input("explorer-table-selector", "value"),
    Input("explorer-limit-selector", "value")
)
def update_explorer_table(table_name, limit):
    if not table_name:
        return html.Div("Please select a table.", className="empty-state-desc")
    loader = DataLoader.get_instance()
    sql = f"SELECT * FROM {table_name} LIMIT {int(limit)}"
    df = loader.query(sql)
    return create_f1_table(df, table_id="explorer-table", page_size=20, export_btn_id="btn-export-explorer")

@callback(
    Output("btn-export-explorer-download", "data"),
    Input("btn-export-explorer", "n_clicks"),
    State("explorer-table-selector", "value"),
    State("explorer-limit-selector", "value"),
    prevent_initial_call=True
)
def export_explorer_csv(n_clicks, table_name, limit):
    if not n_clicks or not table_name:
        return None
    loader = DataLoader.get_instance()
    sql = f"SELECT * FROM {table_name} LIMIT {int(limit)}"
    df = loader.query(sql)
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, f"f1_{table_name}_export.csv", index=False)
