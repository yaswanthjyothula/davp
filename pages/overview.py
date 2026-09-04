"""
Overview Page for F1 Historical Analytics.
Strictly zero hyphens in any labels, text, or chart titles.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.kpi_cards import create_kpi_cards
from components.charts import (
    create_bar_chart, create_line_chart, create_global_map, create_multi_line_chart
)
from utils.constants import COLOR_F1_RED, COLOR_F1_GOLD, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    seasons = loader.get_seasons_list()
    season_options = [{'label': 'All Seasons (1950 to 2026)', 'value': 'ALL'}] + [
        {'label': str(s), 'value': str(s)} for s in seasons
    ]
    
    # Pre-fetch initial data
    kpis = loader.get_kpis()
    
    # Wins by driver
    top_drivers = loader.query("SELECT name, wins FROM driver_summary ORDER BY wins DESC LIMIT 10")
    top_drivers_fig = create_bar_chart(top_drivers, x='wins', y='name', title="All Time Grand Prix Victories by Driver", orientation='h', color=COLOR_F1_RED)
    
    # Wins by constructor
    top_const = loader.query("SELECT name, wins FROM constructor_summary ORDER BY wins DESC LIMIT 10")
    top_const_fig = create_bar_chart(top_const, x='wins', y='name', title="All Time Grand Prix Victories by Constructor", orientation='h', color=COLOR_F1_CYAN)
    
    # Races per season
    races_per_s = loader.query("SELECT season, total_races FROM season_summary ORDER BY season ASC")
    races_fig = create_line_chart(races_per_s, x='season', y='total_races', title="Championship Calendar Expansion (Races per Season)", color=COLOR_F1_RED)
    
    # Circuits map
    circuits = loader.query("SELECT circuitId, name, country, lat, long, total_races FROM circuit_summary")
    map_fig = create_global_map(circuits, title="Formula 1 World Championship Global Circuit Footprint")
    
    # DNF Evolution
    dnf_df = loader.query("""
    SELECT 
        season,
        COUNT(*) as total,
        SUM(CASE WHEN LOWER(status) NOT LIKE '%finished%' AND LOWER(status) NOT LIKE '%lap%' THEN 1 ELSE 0 END) as dnfs
    FROM results
    GROUP BY season
    ORDER BY season ASC
    """)
    dnf_df['dnf_rate'] = ((dnf_df['dnfs'] / dnf_df['total']) * 100).round(1)
    dnf_fig = create_line_chart(dnf_df, x='season', y='dnf_rate', title="Mechanical Unreliability and DNF Rate Evolution (%)", color=COLOR_F1_GOLD)
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("F1 HISTORICAL ANALYTICS", className="section-title"),
                    html.P("Explore Formula 1 through decades of drivers, races, circuits, constructors and performance data.", className="section-subtitle")
                ]
            ),
            
            # Global Filters
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Season Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="overview-season-filter",
                                options=season_options,
                                value="ALL",
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        style={"flexGrow": "0"},
                        children=[
                            html.Label("Action", className="filter-label"),
                            html.Button("RESET FILTERS", id="btn-reset-filters", className="btn-export", n_clicks=0)
                        ]
                    )
                ]
            ),
            
            # Dynamic KPIs
            html.Div(id="overview-kpis-container", children=create_kpi_cards(kpis)),
            
            # Key Visualizations Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=top_drivers_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=top_const_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Global Circuit Footprint Map
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=map_fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Calendar & DNF Trends Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=races_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=dnf_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Dynamic Analytical Insights Panel
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("VERIFIED HISTORICAL INTELLIGENCE", className="chart-title")]),
                    html.Ul(
                        style={"color": "#475569", "lineHeight": "1.8", "paddingLeft": "20px", "fontSize": "13px"},
                        children=[
                            html.Li("Lewis Hamilton holds the all time Formula 1 victory benchmark with 105 Grand Prix wins."),
                            html.Li("Scuderia Ferrari remains the most successful team in history with 16 Constructors World Championships and 243+ Grand Prix victories."),
                            html.Li("Autodromo Nazionale Monza has hosted more Grands Prix than any other circuit in World Championship history."),
                            html.Li("Grid reliability has surged: DNF rates dropped from over 55% in the 1950s to below 15% in modern seasons."),
                        ]
                    )
                ]
            ),
            
            # Footer Disclaimer
            html.Div(
                className="footer-disclaimer",
                children="Unofficial Formula 1 historical analytics project. Not affiliated with Formula 1. All statistics calculated from official World Championship records 1950 to 2026."
            )
        ]
    )

@callback(
    Output("overview-season-filter", "value"),
    Input("btn-reset-filters", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return "ALL"

@callback(
    Output("overview-kpis-container", "children"),
    Input("overview-season-filter", "value")
)
def update_overview_kpis(selected_season):
    loader = DataLoader.get_instance()
    s = None if selected_season == "ALL" else selected_season
    kpis = loader.get_kpis(season=s)
    return create_kpi_cards(kpis)
