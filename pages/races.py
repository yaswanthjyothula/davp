"""
Races Page for F1 Historical Analytics.
Filterable historical race calendar with 1,125+ Grands Prix.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    seasons = loader.get_seasons_list()
    season_options = [{'label': 'All Seasons', 'value': 'ALL'}] + [
        {'label': str(s), 'value': str(s)} for s in seasons
    ]
    
    circuits = loader.get_circuits_list()
    circ_options = [{'label': 'All Circuits', 'value': 'ALL'}] + [
        {'label': f"{c['name']} ({c['country']})", 'value': c['circuitId']} for c in circuits
    ]
    
    initial_races = loader.query("""
    SELECT 
        r.season,
        r.round,
        r.raceName as race,
        r.circuitName as circuit,
        r.date,
        (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winner,
        (SELECT constructorName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winning_team,
        (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND grid = 1 LIMIT 1) as pole_driver
    FROM races r
    ORDER BY r.season DESC, r.round DESC
    LIMIT 300
    """)
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("HISTORICAL RACE ARCHIVE", className="section-title"),
                    html.P("Every official Formula 1 World Championship Grand Prix from 1950 to present day.", className="section-subtitle")
                ]
            ),
            
            # Filters
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Season Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="races-season-filter",
                                options=season_options,
                                value="ALL",
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Circuit Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="races-circuit-filter",
                                options=circ_options,
                                value="ALL",
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Search Grand Prix", className="filter-label"),
                            dcc.Input(
                                id="races-search",
                                type="text",
                                placeholder="Search race name...",
                                className="dash-dropdown",
                                style={"padding": "8px 12px", "width": "100%"}
                            )
                        ]
                    ),
                ]
            ),
            
            # Races Table
            html.Div(
                className="chart-card",
                id="races-table-container",
                children=[create_f1_table(initial_races, table_id="races-table", page_size=20, export_btn_id="btn-export-races")]
            )
        ]
    )

@callback(
    Output("races-table-container", "children"),
    Input("races-season-filter", "value"),
    Input("races-circuit-filter", "value"),
    Input("races-search", "value")
)
def update_races_table(season, circuit, search):
    loader = DataLoader.get_instance()
    where_clauses = []
    params = []
    
    if season and season != "ALL":
        where_clauses.append("r.season = ?")
        params.append(int(season))
    if circuit and circuit != "ALL":
        where_clauses.append("r.circuitId = ?")
        params.append(circuit)
    if search:
        where_clauses.append("r.raceName LIKE ?")
        params.append(f"%{search}%")
        
    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    sql = f"""
    SELECT 
        r.season,
        r.round,
        r.raceName as race,
        r.circuitName as circuit,
        r.date,
        (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winner,
        (SELECT constructorName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winning_team,
        (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND grid = 1 LIMIT 1) as pole_driver
    FROM races r
    {where_str}
    ORDER BY r.season DESC, r.round DESC
    LIMIT 300
    """
    df = loader.query(sql, params)
    return create_f1_table(df, table_id="races-table", page_size=20, export_btn_id="btn-export-races")

@callback(
    Output("btn-export-races-download", "data"),
    Input("btn-export-races", "n_clicks"),
    State("races-season-filter", "value"),
    State("races-circuit-filter", "value"),
    State("races-search", "value"),
    prevent_initial_call=True
)
def export_races_csv(n_clicks, season, circuit, search):
    if not n_clicks:
        return None
    loader = DataLoader.get_instance()
    where_clauses = []
    params = []
    if season and season != "ALL":
        where_clauses.append("r.season = ?")
        params.append(int(season))
    if circuit and circuit != "ALL":
        where_clauses.append("r.circuitId = ?")
        params.append(circuit)
    if search:
        where_clauses.append("r.raceName LIKE ?")
        params.append(f"%{search}%")
        
    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    sql = f"""
    SELECT 
        r.season,
        r.round,
        r.raceName as race,
        r.circuitName as circuit,
        r.date,
        (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winner,
        (SELECT constructorName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winning_team,
        (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND grid = 1 LIMIT 1) as pole_driver
    FROM races r
    {where_str}
    ORDER BY r.season DESC, r.round DESC
    """
    df = loader.query(sql, params)
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, "f1_races_archive.csv", index=False)
