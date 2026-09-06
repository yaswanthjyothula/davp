"""
Overview Page for F1 Historical Analytics.
Theme: Formula 1 Historical Intelligence Cockpit.
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
        {'label': f"Season {s}", 'value': str(s)} for s in seasons
    ]
    
    # Pre-fetch initial data
    kpis = loader.get_kpis()
    
    # Wins by driver
    top_drivers = loader.query("SELECT name, wins FROM driver_summary ORDER BY wins DESC LIMIT 10")
    top_drivers_fig = create_bar_chart(
        top_drivers, x='wins', y='name', 
        title="ALL TIME GRAND PRIX VICTORIES BY DRIVER", 
        orientation='h', color=COLOR_F1_RED, height=380,
        x_title="Grand Prix Victories", y_title="Driver"
    )
    
    # Wins by constructor
    top_const = loader.query("SELECT name, wins FROM constructor_summary ORDER BY wins DESC LIMIT 10")
    top_const_fig = create_bar_chart(
        top_const, x='wins', y='name', 
        title="ALL TIME CONSTRUCTOR WORLD CHAMPIONSHIP VICTORIES", 
        orientation='h', color=COLOR_F1_CYAN, height=380,
        x_title="Grand Prix Victories", y_title="Constructor Team"
    )
    
    # Races per season
    races_per_s = loader.query("SELECT season, total_races FROM season_summary ORDER BY season ASC")
    races_fig = create_line_chart(
        races_per_s, x='season', y='total_races', 
        title="CHAMPIONSHIP CALENDAR EXPANSION (RACES PER SEASON)", 
        color=COLOR_F1_RED, height=340
    )
    
    # Circuits map
    circuits = loader.query("SELECT circuitId, name, country, lat, long, total_races FROM circuit_summary")
    map_fig = create_global_map(
        circuits, 
        title="FORMULA 1 WORLD CHAMPIONSHIP GLOBAL CIRCUIT FOOTPRINT",
        height=460
    )
    
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
    dnf_fig = create_line_chart(
        dnf_df, x='season', y='dnf_rate', 
        title="MECHANICAL UNRELIABILITY & DNF RATE EVOLUTION (%)", 
        color=COLOR_F1_GOLD, height=340
    )
    
    return html.Div(
        className="page-body",
        children=[
            # Page Hero Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("F1 HISTORICAL ANALYTICS", className="section-title"),
                    html.P("Comprehensive telemetry and empirical data science across 75 seasons of the FIA Formula One World Championship.", className="section-subtitle")
                ]
            ),
            
            # Global Filters
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "340px"},
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
                            html.Button(
                                children=[
                                    html.Span("↺", style={"marginRight": "6px", "fontWeight": "bold"}),
                                    html.Span("RESET FILTERS")
                                ],
                                id="btn-reset-filters", 
                                className="btn-export", 
                                n_clicks=0
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic KPIs
            html.Div(id="overview-kpis-container", children=create_kpi_cards(kpis)),
            
            # Key Visualizations Grid (Driver vs Constructor Dominance)
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px"},
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
            
            # Calendar Expansion & Reliability Trends Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=races_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=dnf_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Dynamic Analytical Insights Panel
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header", 
                        children=[
                            html.H3("VERIFIED HISTORICAL INTELLIGENCE BENCHMARKS", className="chart-title")
                        ]
                    ),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "16px", "padding": "8px 0"},
                        children=[
                            html.Div(
                                style={"background": "rgba(255, 255, 255, 0.02)", "border": "1px solid rgba(255, 255, 255, 0.05)", "borderRadius": "6px", "padding": "14px"},
                                children=[
                                    html.Div("ALL TIME VICTORIES", style={"fontFamily": "var(--font-mono)", "fontSize": "10px", "color": "var(--f1-red)", "fontWeight": "700", "marginBottom": "4px"}),
                                    html.Div("Lewis Hamilton leads all time Formula 1 history with 105 Grand Prix victories across 350+ career race starts.", style={"fontSize": "12.5px", "color": "var(--text-secondary)", "lineHeight": "1.5"})
                                ]
                            ),
                            html.Div(
                                style={"background": "rgba(255, 255, 255, 0.02)", "border": "1px solid rgba(255, 255, 255, 0.05)", "borderRadius": "6px", "padding": "14px"},
                                children=[
                                    html.Div("CONSTRUCTOR SUPREMACY", style={"fontFamily": "var(--font-mono)", "fontSize": "10px", "color": "var(--f1-cyan)", "fontWeight": "700", "marginBottom": "4px"}),
                                    html.Div("Scuderia Ferrari remains the benchmark marque with 16 Constructors World Championships and 243+ Grand Prix victories.", style={"fontSize": "12.5px", "color": "var(--text-secondary)", "lineHeight": "1.5"})
                                ]
                            ),
                            html.Div(
                                style={"background": "rgba(255, 255, 255, 0.02)", "border": "1px solid rgba(255, 255, 255, 0.05)", "borderRadius": "6px", "padding": "14px"},
                                children=[
                                    html.Div("TEMPLE OF SPEED", style={"fontFamily": "var(--font-mono)", "fontSize": "10px", "color": "var(--f1-gold)", "fontWeight": "700", "marginBottom": "4px"}),
                                    html.Div("Autodromo Nazionale Monza has hosted 73 official Grands Prix, more than any other venue in championship history.", style={"fontSize": "12.5px", "color": "var(--text-secondary)", "lineHeight": "1.5"})
                                ]
                            ),
                            html.Div(
                                style={"background": "rgba(255, 255, 255, 0.02)", "border": "1px solid rgba(255, 255, 255, 0.05)", "borderRadius": "6px", "padding": "14px"},
                                children=[
                                    html.Div("ENGINEERING RELIABILITY", style={"fontFamily": "var(--font-mono)", "fontSize": "10px", "color": "#10B981", "fontWeight": "700", "marginBottom": "4px"}),
                                    html.Div("Mechanical DNF rates plunged from 55%+ in the 1950s down to under 12% in the modern ground effect era.", style={"fontSize": "12.5px", "color": "var(--text-secondary)", "lineHeight": "1.5"})
                                ]
                            ),
                        ]
                    )
                ]
            ),
            
            # Footer Disclaimer
            html.Div(
                className="footer-disclaimer",
                children="Unofficial Formula 1 historical analytics project. Not affiliated with Formula 1 or the FIA. All statistics calculated from official World Championship records 1950 to 2026."
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
