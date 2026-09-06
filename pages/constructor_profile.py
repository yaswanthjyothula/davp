"""
Constructor Profile Page for F1 Historical Analytics.
Theme: Constructor Telemetry, Points Progression & Driver Contributions.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_line_chart, create_bar_chart
from components.tables import create_f1_table
from utils.constants import COLOR_F1_RED, COLOR_F1_CYAN, CONSTRUCTOR_COLORS
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    consts = loader.get_constructors_list()
    const_options = [{'label': c['name'], 'value': c['constructorId']} for c in consts]
    default_const = "ferrari" if any(c['constructorId'] == 'ferrari' for c in consts) else consts[0]['constructorId']
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("CONSTRUCTOR TELEMETRY PROFILE", className="section-title"),
                    html.P("Championship progression, driver contributions, and career performance telemetry for every constructor.", className="section-subtitle")
                ]
            ),
            
            # Selector bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "400px"},
                        children=[
                            html.Label("Select Constructor", className="filter-label"),
                            dcc.Dropdown(
                                id="const-profile-selector",
                                options=const_options,
                                value=default_const,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="const-profile-content")
        ]
    )

@callback(
    Output("const-profile-content", "children"),
    Input("const-profile-selector", "value")
)
def render_constructor_profile(constructor_id):
    if not constructor_id:
        return html.Div("Please select a constructor from the dropdown.", className="empty-state-desc")
        
    loader = DataLoader.get_instance()
    summary, seasons_df, drivers_df = loader.get_constructor_profile(constructor_id)
    if not summary:
        return html.Div("Constructor record not found.", className="empty-state-desc")
        
    kpis = [
        {"label": "Championships", "value": str(summary.get('championships', 0)), "context": "Constructors World Titles", "tag": "TITLES"},
        {"label": "Grand Prix Victories", "value": f"{summary.get('wins', 0):,}", "context": "Official race wins", "tag": "P1 WINS"},
        {"label": "Podium Finishes", "value": f"{summary.get('podiums', 0):,}", "context": "Top 3 race finishes", "tag": "PODIUMS"},
        {"label": "Pole Positions", "value": f"{summary.get('poles', 0):,}", "context": "Qualifying P1 starts", "tag": "POLES"},
        {"label": "Grand Prix Starts", "value": f"{summary.get('starts', 0):,}", "context": "Championship race starts", "tag": "STARTS"},
        {"label": "Total Points", "value": f"{summary.get('points', 0):,.1f}", "context": "Championship points scored", "tag": "POINTS"},
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
        
    team_key = summary['name'].lower()
    team_color = CONSTRUCTOR_COLORS.get(team_key, COLOR_F1_RED)
    
    # Points by season chart
    pts_fig = create_line_chart(
        seasons_df, x='season', y='points', 
        title="CHAMPIONSHIP POINTS SCORED BY SEASON", 
        color=team_color, height=340
    )
    
    # Driver contribution chart
    driver_fig = create_bar_chart(
        drivers_df, x='points', y='driver', 
        title="TOP DRIVER POINTS CONTRIBUTION ALL TIME", 
        orientation='h', color=COLOR_F1_CYAN, height=340
    )
    
    # Seasons table
    seasons_table = create_f1_table(seasons_df, table_id="const-seasons-table", page_size=15)
    
    return html.Div(
        children=[
            # Team Telemetry Hero Card
            html.Div(
                className="chart-card",
                style={
                    "position": "relative",
                    "overflow": "hidden",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "padding": "24px 30px",
                    "background": "linear-gradient(135deg, rgba(20, 23, 28, 0.95) 0%, rgba(14, 16, 19, 0.98) 100%)",
                    "marginBottom": "20px"
                },
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "6px"},
                                children=[
                                    html.Span(remove_hyphens(summary.get('nationality', 'Unknown')), style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": team_color, "fontWeight": "700", "letterSpacing": "1px", "textTransform": "uppercase"}),
                                    html.Span("•", style={"color": "var(--text-dim)", "fontSize": "10px"}),
                                    html.Span(f"ACTIVE: {remove_hyphens(summary.get('career_years', 'Historic'))}", style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--text-secondary)"}),
                                ]
                            ),
                            html.H2(
                                remove_hyphens(summary['name']),
                                style={
                                    "fontFamily": "var(--font-display)",
                                    "fontSize": "32px",
                                    "fontWeight": "900",
                                    "letterSpacing": "1.2px",
                                    "color": "var(--text-white)",
                                    "textTransform": "uppercase",
                                    "lineHeight": "1.1"
                                }
                            ),
                        ]
                    ),
                    # Team Watermark Acronym
                    html.Div(
                        style={
                            "fontFamily": "var(--font-display)",
                            "fontSize": "60px",
                            "fontWeight": "900",
                            "color": team_color,
                            "opacity": "0.18",
                            "letterSpacing": "2px"
                        },
                        children=remove_hyphens(summary['name'][:4]).upper()
                    )
                ]
            ),
            
            # KPI Cards Grid
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))"}, children=kpi_cards),
            
            # Progression & Driver Contribution Charts
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px", "marginBottom": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=pts_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=driver_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Seasons Breakdown Table Card
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header",
                        children=[html.H3("CHAMPIONSHIP SEASONS PERFORMANCE BREAKDOWN", className="chart-title")]
                    ),
                    seasons_table
                ]
            )
        ]
    )
