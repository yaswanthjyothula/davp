"""
Constructors Page for F1 Historical Analytics.
Historical database of Formula 1 teams.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    nats = loader.query("SELECT DISTINCT nationality FROM constructor_summary WHERE nationality IS NOT NULL ORDER BY nationality ASC")
    nat_options = [{'label': 'All Nationalities', 'value': 'ALL'}] + [
        {'label': n, 'value': n} for n in nats['nationality'].tolist()
    ]
    
    initial_df = loader.get_constructors_table()
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("HISTORICAL CONSTRUCTORS DATABASE", className="section-title"),
                    html.P("Complete archive of every constructor and team to compete in Formula 1 World Championship history.", className="section-subtitle")
                ]
            ),
            
            # Filters
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Search Constructor", className="filter-label"),
                            dcc.Input(
                                id="const-search",
                                type="text",
                                placeholder="Search team name...",
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
                                id="const-nat-filter",
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
                            html.Label("Championship Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="const-champ-filter",
                                options=[
                                    {'label': 'All Constructors', 'value': 'ALL'},
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
            
            # Table
            html.Div(
                className="chart-card",
                id="const-table-container",
                children=[create_f1_table(initial_df, table_id="const-table", page_size=20, export_btn_id="btn-export-constructors")]
            )
        ]
    )

@callback(
    Output("const-table-container", "children"),
    Input("const-search", "value"),
    Input("const-nat-filter", "value"),
    Input("const-champ-filter", "value")
)
def update_constructors_table(search, nat, champ):
    loader = DataLoader.get_instance()
    n = None if nat == "ALL" else nat
    c_only = (champ == "CHAMP")
    df = loader.get_constructors_table(nationality=n, champion_only=c_only, search=search)
    return create_f1_table(df, table_id="const-table", page_size=20, export_btn_id="btn-export-constructors")

@callback(
    Output("btn-export-constructors-download", "data"),
    Input("btn-export-constructors", "n_clicks"),
    State("const-search", "value"),
    State("const-nat-filter", "value"),
    State("const-champ-filter", "value"),
    prevent_initial_call=True
)
def export_constructors_csv(n_clicks, search, nat, champ):
    if not n_clicks:
        return None
    loader = DataLoader.get_instance()
    n = None if nat == "ALL" else nat
    c_only = (champ == "CHAMP")
    df = loader.get_constructors_table(nationality=n, champion_only=c_only, search=search)
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, "f1_constructors_historical.csv", index=False)
