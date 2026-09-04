"""
Seasons Page for F1 Historical Analytics.
Complete season explorer from 1950 to latest available season.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_bar_chart, create_multi_line_chart
from utils.constants import COLOR_F1_RED, COLOR_F1_GOLD, COLOR_F1_CYAN
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
                    html.H1("HISTORICAL SEASONS ARCHIVE", className="section-title"),
                    html.P("Explore every Formula 1 World Championship season from 1950 to present day.", className="section-subtitle")
                ]
            ),
            
            # Selector bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "320px"},
                        children=[
                            html.Label("Select Championship Season", className="filter-label"),
                            dcc.Dropdown(
                                id="season-page-selector",
                                options=season_options,
                                value=default_season,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="season-page-content")
        ]
    )

@callback(
    Output("season-page-content", "children"),
    Input("season-page-selector", "value")
)
def render_season_content(season):
    if not season:
        return html.Div("Select a season.", style={"color": "#9FA6B2"})
        
    loader = DataLoader.get_instance()
    summary, calendar_df, d_standings, c_standings = loader.get_season_details(season)
    
    kpis = [
        {"label": "Driver Champion", "value": summary.get('driver_champion', 'N/A')},
        {"label": "Constructor Champion", "value": summary.get('constructor_champion', 'N/A')},
        {"label": "Total Grands Prix", "value": str(summary.get('total_races', 0))},
        {"label": "Participating Drivers", "value": str(summary.get('total_drivers', 0))},
        {"label": "Teams / Constructors", "value": str(summary.get('total_constructors', 0))},
        {"label": "Total Points Awarded", "value": f"{summary.get('total_points', 0):,.0f}"},
    ]
    
    kpi_cards = []
    for k in kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(k["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(k["value"]), className="kpi-value", style={"fontSize": "20px" if len(str(k["value"])) > 12 else "28px"}),
                ]
            )
        )
        
    # Top 5 Driver Points Bar Chart
    top_d = d_standings.head(8)
    d_fig = create_bar_chart(top_d, x='points', y='driver', title=f"Top Driver Championship Points {season}", orientation='h', color=COLOR_F1_RED)
    
    # Top 5 Constructor Points Bar Chart
    top_c = c_standings.head(8)
    c_fig = create_bar_chart(top_c, x='points', y='constructor', title=f"Top Constructor Championship Points {season}", orientation='h', color=COLOR_F1_CYAN)
    
    # Tables
    cal_table = create_f1_table(calendar_df, table_id="season-cal-table", page_size=12)
    d_table = create_f1_table(d_standings, table_id="season-d-standings-table", page_size=12)
    c_table = create_f1_table(c_standings, table_id="season-c-standings-table", page_size=12)
    
    return html.Div(
        children=[
            # KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))"}, children=kpi_cards),
            
            # Charts
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=d_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=c_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Race Calendar Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3(f"{season} GRAND PRIX RACE CALENDAR", className="chart-title")]),
                    cal_table
                ]
            ),
            
            # Standings Tables Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.Div(className="chart-header", children=[html.H3("DRIVER WORLD CHAMPIONSHIP STANDINGS", className="chart-title")]),
                            d_table
                        ]
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.Div(className="chart-header", children=[html.H3("CONSTRUCTOR WORLD CHAMPIONSHIP STANDINGS", className="chart-title")]),
                            c_table
                        ]
                    ),
                ]
            )
        ]
    )
