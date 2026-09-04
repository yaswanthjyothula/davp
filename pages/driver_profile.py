"""
Driver Profile Analytics Page for F1 Historical Analytics.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.kpi_cards import create_kpi_cards
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
            html.Div(
                className="section-header",
                children=[
                    html.H1("DRIVER ANALYTICS PROFILE", className="section-title"),
                    html.P("In depth telemetry, career progression, and complete Grand Prix history for any Formula 1 driver.", className="section-subtitle")
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
        return html.Div("Please select a driver.", style={"color": "#64748b"})
        
    loader = DataLoader.get_instance()
    summary, seasons_df, races_df = loader.get_driver_profile(driver_id)
    if not summary:
        return html.Div("Driver not found.", style={"color": "#64748b"})
        
    kpi_data = {
        'total_seasons': summary.get('championships', 0),
        'total_races': summary.get('starts', 0),
        'total_drivers': summary.get('wins', 0),
        'total_constructors': summary.get('podiums', 0),
        'total_circuits': summary.get('poles', 0),
        'total_entries': int(summary.get('points', 0)),
        'total_wins': summary.get('dnfs', 0),
        'total_podiums': int(summary.get('win_rate', 0)),
    }
    
    custom_kpis = [
        {"label": "Championships", "value": str(summary.get('championships', 0))},
        {"label": "Grand Prix Wins", "value": f"{summary.get('wins', 0):,}"},
        {"label": "Podium Finishes", "value": f"{summary.get('podiums', 0):,}"},
        {"label": "Pole Positions", "value": f"{summary.get('poles', 0):,}"},
        {"label": "Fastest Laps", "value": f"{summary.get('fastest_laps', 0):,}"},
        {"label": "Career Starts", "value": f"{summary.get('starts', 0):,}"},
        {"label": "Career Points", "value": f"{summary.get('points', 0):,.1f}"},
        {"label": "Win Rate (%)", "value": f"{summary.get('win_rate', 0)}%"},
    ]
    
    kpi_cards = []
    for c in custom_kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(c["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(c["value"]), className="kpi-value"),
                ]
            )
        )
        
    # Race history table
    table_elem = create_f1_table(races_df, table_id="driver-races-table", page_size=15, export_btn_id="btn-export-driver-races")
    
    return html.Div(
        children=[
            # Header card
            html.Div(
                className="chart-card",
                style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "marginBottom": "24px"},
                children=[
                    html.Div(
                        children=[
                            html.H2(remove_hyphens(summary['name']), style={"fontSize": "28px", "fontWeight": "900", "marginBottom": "6px", "letterSpacing": "1.5px", "color": "#0f172a"}),
                            html.Div(
                                style={"color": "#64748b", "fontSize": "13px", "display": "flex", "gap": "16px"},
                                children=[
                                    html.Span(f"Nationality: {remove_hyphens(summary['nationality'])}"),
                                    html.Span(f"Car Number: {summary['number']}"),
                                    html.Span(f"Career: {remove_hyphens(summary['career_years'])}"),
                                    html.Span(f"Code: {summary['code']}"),
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        style={"fontSize": "48px", "fontWeight": "900", "color": COLOR_F1_RED, "opacity": "0.4"},
                        children=f"#{summary['number']}" if summary['number'] != 'N/A' else ""
                    )
                ]
            ),
            
            # KPI Cards
            html.Div(className="kpi-grid", children=kpi_cards),
            
            # Full Race History Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("COMPLETE GRAND PRIX RACE CLASSIFICATION HISTORY", className="chart-title")]),
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
