"""
Sprint Races Page for F1 Historical Analytics.
Theme: Dedicated Saturday Sprint Race Telemetry & Points Tracker (2021 to 2026).
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_bar_chart
from utils.constants import COLOR_F1_RED
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    sprint_seasons = loader.query("SELECT DISTINCT season FROM sprint_results ORDER BY season DESC")
    season_options = [{'label': 'All Sprint Seasons (2021 to 2026)', 'value': 'ALL'}] + [
        {'label': f"Season {s}", 'value': str(s)} for s in sprint_seasons['season'].tolist()
    ]
    
    initial_df = loader.query("""
    SELECT 
        season,
        round,
        driverName as driver,
        constructorName as constructor,
        position,
        points,
        grid,
        laps,
        status
    FROM sprint_results
    ORDER BY season DESC, round DESC, position ASC
    """)
    
    # Most Sprint points all time
    sprint_leaders = loader.query("""
    SELECT driverName as driver, SUM(points) as total_sprint_points, SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as sprint_wins
    FROM sprint_results
    GROUP BY driverId
    ORDER BY total_sprint_points DESC
    LIMIT 8
    """)
    leaders_fig = create_bar_chart(
        sprint_leaders, x='total_sprint_points', y='driver', 
        title="ALL TIME SPRINT CHAMPIONSHIP POINTS LEADERS (2021 TO 2026)", 
        orientation='h', color=COLOR_F1_RED, height=350
    )
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("SPRINT RACE CLASSIFICATION & TELEMETRY", className="section-title"),
                    html.P("Official results and championship points for all Saturday Sprint sessions introduced to the Formula 1 format in 2021.", className="section-subtitle")
                ]
            ),
            
            # Filter bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "320px"},
                        children=[
                            html.Label("Sprint Season Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="sprint-season-filter",
                                options=season_options,
                                value="ALL",
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Leaderboard Chart Card
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=leaders_fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Classification Table Card
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header",
                        children=[html.H3("OFFICIAL SPRINT RACE CLASSIFICATION TELEMETRY", className="chart-title")]
                    ),
                    html.Div(
                        id="sprint-table-container",
                        children=[create_f1_table(initial_df, table_id="sprint-table", page_size=20, export_btn_id="btn-export-sprints")]
                    )
                ]
            )
        ]
    )

@callback(
    Output("sprint-table-container", "children"),
    Input("sprint-season-filter", "value")
)
def update_sprint_table(season):
    loader = DataLoader.get_instance()
    where_str = "WHERE season = ?" if season != "ALL" else ""
    params = [int(season)] if season != "ALL" else []
    
    sql = f"""
    SELECT 
        season,
        round,
        driverName as driver,
        constructorName as constructor,
        position,
        points,
        grid,
        laps,
        status
    FROM sprint_results
    {where_str}
    ORDER BY season DESC, round DESC, position ASC
    """
    df = loader.query(sql, params)
    return create_f1_table(df, table_id="sprint-table", page_size=20, export_btn_id="btn-export-sprints")

@callback(
    Output("btn-export-sprints-download", "data"),
    Input("btn-export-sprints", "n_clicks"),
    State("sprint-season-filter", "value"),
    prevent_initial_call=True
)
def export_sprints_csv(n_clicks, season):
    if not n_clicks:
        return None
    loader = DataLoader.get_instance()
    where_str = "WHERE season = ?" if season != "ALL" else ""
    params = [int(season)] if season != "ALL" else []
    sql = f"""
    SELECT 
        season,
        round,
        driverName as driver,
        constructorName as constructor,
        position,
        points,
        grid,
        laps,
        status
    FROM sprint_results
    {where_str}
    ORDER BY season DESC, round DESC, position ASC
    """
    df = loader.query(sql, params)
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, "f1_sprint_results.csv", index=False)
