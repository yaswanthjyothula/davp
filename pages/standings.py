"""
Standings Page for F1 Historical Analytics.
Championship standings explorer for Drivers and Constructors.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_bar_chart
from utils.constants import COLOR_F1_RED, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    seasons = loader.get_seasons_list()
    season_options = [{'label': str(s), 'value': s} for s in seasons]
    default_season = seasons[0] if seasons else 2024
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("WORLD CHAMPIONSHIP STANDINGS", className="section-title"),
                    html.P("Official World Championship points standings for every season since 1950.", className="section-subtitle")
                ]
            ),
            
            # Selectors
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "250px"},
                        children=[
                            html.Label("Championship Season", className="filter-label"),
                            dcc.Dropdown(
                                id="standings-season-selector",
                                options=season_options,
                                value=default_season,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "250px"},
                        children=[
                            html.Label("Championship Category", className="filter-label"),
                            dcc.Dropdown(
                                id="standings-type-selector",
                                options=[
                                    {'label': 'Driver Championship', 'value': 'driver'},
                                    {'label': 'Constructor Championship', 'value': 'constructor'},
                                ],
                                value='driver',
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                ]
            ),
            
            # Dynamic Container
            html.Div(id="standings-content")
        ]
    )

@callback(
    Output("standings-content", "children"),
    Input("standings-season-selector", "value"),
    Input("standings-type-selector", "value")
)
def render_standings_content(season, champ_type):
    if not season:
        return html.Div("Please select a season.", style={"color": "#9FA6B2"})
        
    loader = DataLoader.get_instance()
    if champ_type == 'driver':
        sql = """
        SELECT position, driverName as driver, constructorName as constructor, total_points as points, wins
        FROM driver_standings
        WHERE season = ?
        ORDER BY position ASC
        """
        df = loader.query(sql, [int(season)])
        title = f"{season} FIA Formula One Drivers World Championship Standings"
        chart_color = COLOR_F1_RED
        x_col = 'driver'
    else:
        sql = """
        SELECT position, constructorName as constructor, points, wins
        FROM constructor_standings
        WHERE season = ?
        ORDER BY position ASC
        """
        df = loader.query(sql, [int(season)])
        title = f"{season} FIA Formula One Constructors World Championship Standings"
        chart_color = COLOR_F1_CYAN
        x_col = 'constructor'
        
    if df.empty:
        return html.Div("No standings records for this season.", style={"color": "#9FA6B2"})
        
    # Top 10 chart
    top_df = df.head(10)
    fig = create_bar_chart(top_df, x='points', y=x_col, title=f"Top 10 Points Classification ({season})", orientation='h', color=chart_color)
    
    table_elem = create_f1_table(df, table_id="standings-table", page_size=25, export_btn_id="btn-export-standings")
    
    return html.Div(
        children=[
            # Points Chart
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Standings Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3(remove_hyphens(title), className="chart-title")]),
                    table_elem
                ]
            )
        ]
    )

@callback(
    Output("btn-export-standings-download", "data"),
    Input("btn-export-standings", "n_clicks"),
    State("standings-season-selector", "value"),
    State("standings-type-selector", "value"),
    prevent_initial_call=True
)
def export_standings_csv(n_clicks, season, champ_type):
    if not n_clicks or not season:
        return None
    loader = DataLoader.get_instance()
    table_name = "driver_standings" if champ_type == "driver" else "constructor_standings"
    df = loader.query(f"SELECT * FROM {table_name} WHERE season = ? ORDER BY position ASC", [int(season)])
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, f"f1_{table_name}_{season}.csv", index=False)
