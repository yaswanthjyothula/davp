"""
Constructor Profile Page for F1 Historical Analytics.
Team history, points progression, and driver contributions.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_line_chart, create_bar_chart
from components.tables import create_f1_table
from utils.constants import COLOR_F1_RED, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    consts = loader.get_constructors_list()
    const_options = [{'label': c['name'], 'value': c['constructorId']} for c in consts]
    default_const = "ferrari" if any(c['constructorId'] == 'ferrari' for c in consts) else consts[0]['constructorId']
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("CONSTRUCTOR ANALYTICS PROFILE", className="section-title"),
                    html.P("Championship progression, driver contributions, and performance telemetry for every constructor.", className="section-subtitle")
                ]
            ),
            
            # Selector
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
        return html.Div("Please select a constructor.", style={"color": "#9FA6B2"})
        
    loader = DataLoader.get_instance()
    summary, seasons_df, drivers_df = loader.get_constructor_profile(constructor_id)
    if not summary:
        return html.Div("Constructor not found.", style={"color": "#9FA6B2"})
        
    kpis = [
        {"label": "Championships", "value": str(summary.get('championships', 0))},
        {"label": "Grand Prix Victories", "value": f"{summary.get('wins', 0):,}"},
        {"label": "Podium Finishes", "value": f"{summary.get('podiums', 0):,}"},
        {"label": "Pole Positions", "value": f"{summary.get('poles', 0):,}"},
        {"label": "Grand Prix Starts", "value": f"{summary.get('starts', 0):,}"},
        {"label": "Total Points", "value": f"{summary.get('points', 0):,.1f}"},
    ]
    
    kpi_cards = []
    for k in kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(k["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(k["value"]), className="kpi-value"),
                ]
            )
        )
        
    # Points by season chart
    pts_fig = create_line_chart(seasons_df, x='season', y='points', title="Championship Points Scored by Season", color=COLOR_F1_RED)
    
    # Driver contribution chart
    driver_fig = create_bar_chart(drivers_df, x='points', y='driver', title="Top Driver Points Contribution", orientation='h', color=COLOR_F1_CYAN)
    
    # Seasons table
    seasons_table = create_f1_table(seasons_df, table_id="const-seasons-table", page_size=15)
    
    return html.Div(
        children=[
            # Header Card
            html.Div(
                className="chart-card",
                children=[
                    html.H2(remove_hyphens(summary['name']), style={"fontSize": "28px", "fontWeight": "900", "marginBottom": "6px"}),
                    html.Div(
                        style={"color": "#9FA6B2", "fontSize": "13px", "display": "flex", "gap": "20px"},
                        children=[
                            html.Span(f"Nationality: {remove_hyphens(summary['nationality'])}"),
                            html.Span(f"Championship Participation: {remove_hyphens(summary['career_years'])}"),
                            html.Span(f"Total Seasons: {summary['total_seasons']}"),
                        ]
                    )
                ]
            ),
            
            # KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))"}, children=kpi_cards),
            
            # Charts Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=pts_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=driver_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Season breakdown table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("ANNUAL CHAMPIONSHIP PARTICIPATION RECORD", className="chart-title")]),
                    seasons_table
                ]
            )
        ]
    )
