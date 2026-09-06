"""
Seasons Page for F1 Historical Analytics.
Theme: Historical Seasons Archive (1950 to 2026).
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_bar_chart
from utils.constants import COLOR_F1_RED, COLOR_F1_CYAN, COLOR_F1_GOLD
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    seasons = loader.get_seasons_list()
    season_options = [{'label': f"Season {s}", 'value': s} for s in seasons]
    default_season = seasons[0] if seasons else 2024
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("HISTORICAL SEASONS ARCHIVE", className="section-title"),
                    html.P("Explore official World Championship seasons from the inaugural 1950 British Grand Prix to modern ground effect regulations.", className="section-subtitle")
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
            
            # Dynamic Content Container
            html.Div(id="season-page-content")
        ]
    )

@callback(
    Output("season-page-content", "children"),
    Input("season-page-selector", "value")
)
def render_season_content(season):
    if not season:
        return html.Div("Select a season.", className="empty-state-desc")
        
    loader = DataLoader.get_instance()
    summary, calendar_df, d_standings, c_standings = loader.get_season_details(season)
    
    kpis = [
        {
            "label": "Driver Champion", 
            "value": summary.get('driver_champion', 'N/A'),
            "context": f"{season} Drivers World Champion",
            "tag": "CHAMPION"
        },
        {
            "label": "Constructor Champion", 
            "value": summary.get('constructor_champion', 'N/A'),
            "context": f"{season} Constructors World Champion",
            "tag": "MARQUE"
        },
        {
            "label": "Total Grands Prix", 
            "value": str(summary.get('total_races', 0)),
            "context": "Calendar rounds held",
            "tag": "ROUNDS"
        },
        {
            "label": "Grid Drivers", 
            "value": str(summary.get('total_drivers', 0)),
            "context": "Drivers participating",
            "tag": "DRIVERS"
        },
        {
            "label": "Constructors", 
            "value": str(summary.get('total_constructors', 0)),
            "context": "Teams contesting",
            "tag": "TEAMS"
        },
        {
            "label": "Total Points Awarded", 
            "value": f"{summary.get('total_points', 0):,.0f}",
            "context": "Championship points scored",
            "tag": "POINTS"
        },
    ]
    
    kpi_cards = []
    for k in kpis:
        val_str = remove_hyphens(str(k["value"]))
        font_size = "22px" if len(val_str) > 14 else "32px"
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        className="kpi-header-row",
                        children=[
                            html.Span(remove_hyphens(k["label"]), className="kpi-label"),
                            html.Span(k["tag"], className="kpi-tag")
                        ]
                    ),
                    html.Div(val_str, className="kpi-value", style={"fontSize": font_size}),
                    html.Div(remove_hyphens(k["context"]), className="kpi-context")
                ]
            )
        )
        
    # Top 8 Driver Points Bar Chart
    top_d = d_standings.head(8) if d_standings is not None else pd.DataFrame()
    d_fig = create_bar_chart(
        top_d, x='points', y='driver', 
        title=f"DRIVER CHAMPIONSHIP STANDINGS BENCHMARK ({season})", 
        orientation='h', color=COLOR_F1_RED, height=340
    )
    
    # Top 8 Constructor Points Bar Chart
    top_c = c_standings.head(8) if c_standings is not None else pd.DataFrame()
    c_fig = create_bar_chart(
        top_c, x='points', y='constructor', 
        title=f"CONSTRUCTOR CHAMPIONSHIP STANDINGS BENCHMARK ({season})", 
        orientation='h', color=COLOR_F1_CYAN, height=340
    )
    
    # Tables
    cal_table = create_f1_table(calendar_df, table_id="season-cal-table", page_size=12)
    d_table = create_f1_table(d_standings, table_id="season-d-standings-table", page_size=12)
    c_table = create_f1_table(c_standings, table_id="season-c-standings-table", page_size=12)
    
    return html.Div(
        children=[
            # KPI Cards Grid
            html.Div(className="kpi-grid", children=kpi_cards),
            
            # Points Progression Charts Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px", "marginBottom": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=d_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=c_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Official Race Calendar Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header", 
                        children=[
                            html.H3(f"{season} GRAND PRIX RACE CALENDAR & RESULTS", className="chart-title")
                        ]
                    ),
                    cal_table
                ]
            ),
            
            # Standings Tables Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px"},
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.Div(
                                className="chart-header", 
                                children=[html.H3(f"{season} DRIVERS WORLD CHAMPIONSHIP", className="chart-title")]
                            ),
                            d_table
                        ]
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.Div(
                                className="chart-header", 
                                children=[html.H3(f"{season} CONSTRUCTORS WORLD CHAMPIONSHIP", className="chart-title")]
                            ),
                            c_table
                        ]
                    ),
                ]
            )
        ]
    )
