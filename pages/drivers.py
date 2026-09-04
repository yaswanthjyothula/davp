"""
Drivers Database Page for F1 Historical Analytics.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    nats = loader.query("SELECT DISTINCT nationality FROM driver_summary WHERE nationality IS NOT NULL ORDER BY nationality ASC")
    nat_options = [{'label': 'All Nationalities', 'value': 'ALL'}] + [
        {'label': n, 'value': n} for n in nats['nationality'].tolist()
    ]
    
    initial_df = loader.get_drivers_table()
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("HISTORICAL DRIVERS DATABASE", className="section-title"),
                    html.P("Complete historical record of every driver to enter a Formula 1 World Championship Grand Prix.", className="section-subtitle")
                ]
            ),
            
            # Filter bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Search Driver", className="filter-label"),
                            dcc.Input(
                                id="drivers-search",
                                type="text",
                                placeholder="Search by name or code...",
                                className="dash-dropdown",
                                style={"padding": "8px 12px", "width": "100%"}
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Nationality", className="filter-label"),
                            dcc.Dropdown(
                                id="drivers-nat-filter",
                                options=nat_options,
                                value="ALL",
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Minimum Wins", className="filter-label"),
                            dcc.Dropdown(
                                id="drivers-min-wins",
                                options=[
                                    {'label': 'Any Wins', 'value': 0},
                                    {'label': '1+ Wins', 'value': 1},
                                    {'label': '5+ Wins', 'value': 5},
                                    {'label': '10+ Wins', 'value': 10},
                                    {'label': '25+ Wins', 'value': 25},
                                    {'label': '50+ Wins', 'value': 50},
                                ],
                                value=0,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Championship Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="drivers-champ-filter",
                                options=[
                                    {'label': 'All Drivers', 'value': 'ALL'},
                                    {'label': 'World Champions Only', 'value': 'CHAMP'},
                                ],
                                value='ALL',
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                ]
            ),
            
            # Table Container
            html.Div(
                className="chart-card",
                id="drivers-table-container",
                children=[create_f1_table(initial_df, table_id="drivers-table", page_size=20, export_btn_id="btn-export-drivers")]
            )
        ]
    )

@callback(
    Output("drivers-table-container", "children"),
    Input("drivers-search", "value"),
    Input("drivers-nat-filter", "value"),
    Input("drivers-min-wins", "value"),
    Input("drivers-champ-filter", "value")
)
def update_drivers_table(search, nat, min_wins, champ):
    loader = DataLoader.get_instance()
    n = None if nat == "ALL" else nat
    c_only = (champ == "CHAMP")
    df = loader.get_drivers_table(nationality=n, min_wins=min_wins, champion_only=c_only, search=search)
    return create_f1_table(df, table_id="drivers-table", page_size=20, export_btn_id="btn-export-drivers")

@callback(
    Output("btn-export-drivers-download", "data"),
    Input("btn-export-drivers", "n_clicks"),
    State("drivers-search", "value"),
    State("drivers-nat-filter", "value"),
    State("drivers-min-wins", "value"),
    State("drivers-champ-filter", "value"),
    prevent_initial_call=True
)
def export_drivers_csv(n_clicks, search, nat, min_wins, champ):
    if not n_clicks:
        return None
    loader = DataLoader.get_instance()
    n = None if nat == "ALL" else nat
    c_only = (champ == "CHAMP")
    df = loader.get_drivers_table(nationality=n, min_wins=min_wins, champion_only=c_only, search=search)
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, "f1_drivers_historical.csv", index=False)
