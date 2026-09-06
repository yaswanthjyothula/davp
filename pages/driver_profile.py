"""
Driver Profile Analytics Page for F1 Historical Analytics.
Theme: Driver Career Telemetry & Grand Prix Classification Archive.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_line_chart, create_bar_chart, create_scatter_plot
from components.tables import create_f1_table
from utils.constants import COLOR_F1_RED, COLOR_F1_GOLD, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    drivers = loader.get_drivers_list()
    driver_options = [{'label': d['name'], 'value': d['driverId']} for d in drivers]
    default_driver = "hamilton" if any(d['driverId'] == 'hamilton' for d in drivers) else drivers[0]['driverId']
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("DRIVER TELEMETRY PROFILE", className="section-title"),
                    html.P("In depth career trajectory, championship progression, and complete Grand Prix classification history.", className="section-subtitle")
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
                            html.Label("Select Driver", className="filter-label"),
                            dcc.Dropdown(
                                id="driver-profile-selector",
                                options=driver_options,
                                value=default_driver,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="driver-profile-content")
        ]
    )

@callback(
    Output("driver-profile-content", "children"),
    Input("driver-profile-selector", "value")
)
def render_driver_profile(driver_id):
    if not driver_id:
        return html.Div("Please select a driver from the dropdown.", className="empty-state-desc")
        
    loader = DataLoader.get_instance()
    summary, seasons_df, races_df = loader.get_driver_profile(driver_id)
    if not summary:
        return html.Div("Driver telemetry record not found.", className="empty-state-desc")
        
    custom_kpis = [
        {"label": "Championships", "value": str(summary.get('championships', 0)), "context": "World titles won", "tag": "TITLES"},
        {"label": "Grand Prix Victories", "value": f"{summary.get('wins', 0):,}", "context": "Official race wins", "tag": "P1 WINS"},
        {"label": "Podium Finishes", "value": f"{summary.get('podiums', 0):,}", "context": "Top 3 race finishes", "tag": "PODIUMS"},
        {"label": "Pole Positions", "value": f"{summary.get('poles', 0):,}", "context": "Fastest qualifying lap", "tag": "POLES"},
        {"label": "Career Starts", "value": f"{summary.get('starts', 0):,}", "context": "Grand Prix race starts", "tag": "STARTS"},
        {"label": "Career Points", "value": f"{summary.get('points', 0):,.1f}", "context": "Total points accumulated", "tag": "POINTS"},
        {"label": "Win Rate", "value": f"{summary.get('win_rate', 0)}%", "context": "Victory to start ratio", "tag": "EFFICIENCY"},
        {"label": "DNFs Recorded", "value": f"{summary.get('dnfs', 0):,}", "context": "Retirements / unclassified", "tag": "RELIABILITY"},
    ]
    
    kpi_cards = []
    for c in custom_kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        className="kpi-header-row",
                        children=[
                            html.Span(remove_hyphens(c["label"]), className="kpi-label"),
                            html.Span(c["tag"], className="kpi-tag")
                        ]
                    ),
                    html.Div(remove_hyphens(c["value"]), className="kpi-value"),
                    html.Div(remove_hyphens(c["context"]), className="kpi-context")
                ]
            )
        )
        
    # Visualizations if data is available
    chart_components = []
    if seasons_df is not None and not seasons_df.empty:
        pts_fig = create_line_chart(
            seasons_df, x='season', y='points', 
            title="CHAMPIONSHIP POINTS PROGRESSION BY SEASON", 
            color=COLOR_F1_RED, height=320
        )
        wins_fig = create_bar_chart(
            seasons_df, x='season', y='wins', 
            title="GRAND PRIX VICTORIES BY SEASON", 
            color=COLOR_F1_GOLD, height=320
        )
        chart_components = [
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px", "marginBottom": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=pts_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=wins_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            )
        ]
        
    # Race history table
    table_elem = create_f1_table(races_df, table_id="driver-races-table", page_size=15, export_btn_id="btn-export-driver-races")
    
    car_num_str = f"#{summary['number']}" if summary['number'] != 'N/A' and summary['number'] else ""
    code_str = f"[{summary['code']}]" if summary['code'] != 'N/A' and summary['code'] else ""
    
    return html.Div(
        children=[
            # Hero Driver Banner
            html.Div(
                className="chart-card",
                style={
                    "position": "relative", 
                    "overflow": "hidden", 
                    "display": "flex", 
                    "alignItems": "center", 
                    "justifyContent": "space-between", 
                    "padding": "26px 32px",
                    "background": "linear-gradient(135deg, rgba(20, 23, 28, 0.95) 0%, rgba(14, 16, 19, 0.98) 100%)",
                    "marginBottom": "20px"
                },
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "6px"},
                                children=[
                                    html.Span(remove_hyphens(summary['nationality']), style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--f1-red)", "fontWeight": "700", "letterSpacing": "1px", "textTransform": "uppercase"}),
                                    html.Span("•", style={"color": "var(--text-dim)", "fontSize": "10px"}),
                                    html.Span(f"ACTIVE: {remove_hyphens(summary['career_years'])}", style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--text-secondary)", "letterSpacing": "0.5px"}),
                                    html.Span(code_str, style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--text-muted)"}),
                                ]
                            ),
                            html.H2(
                                remove_hyphens(summary['name']), 
                                style={
                                    "fontFamily": "var(--font-display)", 
                                    "fontSize": "34px", 
                                    "fontWeight": "900", 
                                    "letterSpacing": "1.5px", 
                                    "color": "var(--text-white)", 
                                    "textTransform": "uppercase",
                                    "lineHeight": "1.1"
                                }
                            ),
                        ]
                    ),
                    # Large Watermark Driver Car Number
                    html.Div(
                        style={
                            "fontFamily": "var(--font-display)", 
                            "fontSize": "64px", 
                            "fontWeight": "900", 
                            "color": "var(--f1-red)", 
                            "opacity": "0.22",
                            "userSelect": "none",
                            "letterSpacing": "1px"
                        },
                        children=car_num_str
                    )
                ]
            ),
            
            # KPI Cards Grid
            html.Div(className="kpi-grid", children=kpi_cards),
            
            # Dynamic Progression Charts
            html.Div(children=chart_components),
            
            # Full Race Classification Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header", 
                        children=[
                            html.H3("COMPLETE GRAND PRIX RACE CLASSIFICATION HISTORY", className="chart-title")
                        ]
                    ),
                    table_elem
                ]
            )
        ]
    )

@callback(
    Output("btn-export-driver-races-download", "data"),
    Input("btn-export-driver-races", "n_clicks"),
    State("driver-profile-selector", "value"),
    prevent_initial_call=True
)
def export_driver_races(n_clicks, driver_id):
    if not n_clicks or not driver_id:
        return None
    loader = DataLoader.get_instance()
    _, _, races_df = loader.get_driver_profile(driver_id)
    clean_df = races_df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, f"{driver_id}_races_history.csv", index=False)
