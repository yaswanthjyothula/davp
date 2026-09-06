"""
Circuit Profile Page for F1 Historical Analytics.
Track history, telemetry, and driver win distributions.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_bar_chart
from utils.constants import COLOR_F1_RED
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    circuits = loader.get_circuits_list()
    circ_options = [{'label': f"{c['name']} ({c['country']})", 'value': c['circuitId']} for c in circuits]
    default_circuit = "monza" if any(c['circuitId'] == 'monza' for c in circuits) else circuits[0]['circuitId']
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("CIRCUIT ANALYTICS PROFILE", className="section-title"),
                    html.P("Historical track records, driver win distributions, and Grand Prix history for every circuit.", className="section-subtitle")
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
                            html.Label("Select Circuit", className="filter-label"),
                            dcc.Dropdown(
                                id="circuit-profile-selector",
                                options=circ_options,
                                value=default_circuit,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="circuit-profile-content")
        ]
    )

@callback(
    Output("circuit-profile-content", "children"),
    Input("circuit-profile-selector", "value")
)
def render_circuit_profile(circuit_id):
    if not circuit_id:
        return html.Div("Please select a circuit.", style={"color": "#9FA6B2"})
        
    loader = DataLoader.get_instance()
    circ_row, hist_df, wins_df = loader.get_circuit_profile(circuit_id)
    if not circ_row:
        return html.Div("Circuit not found.", style={"color": "#9FA6B2"})
        
    kpis = [
        {"label": "Circuit Name", "value": circ_row['name']},
        {"label": "Country", "value": circ_row['country']},
        {"label": "Host City", "value": circ_row['locality']},
        {"label": "Total Grands Prix", "value": str(circ_row['total_races'])},
        {"label": "Inaugural Grand Prix", "value": str(circ_row['first_race'])},
        {"label": "Most Recent Grand Prix", "value": str(circ_row['last_race'])},
    ]
    
    kpi_cards = []
    for k in kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(k["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(k["value"]), className="kpi-value", style={"fontSize": "20px" if len(str(k["value"])) > 10 else "28px"}),
                ]
            )
        )
        
    # Driver win chart at circuit
    wins_fig = create_bar_chart(wins_df, x='wins', y='driver', title=f"Most Grand Prix Victories at {circ_row['name']}", orientation='h', color=COLOR_F1_RED)
    
    # Historical race table
    hist_table = create_f1_table(hist_df, table_id="circuit-history-table", page_size=15)
    
    return html.Div(
        children=[
            # KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))"}, children=kpi_cards),
            
            # Wins Chart
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=wins_fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Historical Winners Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("HISTORICAL GRAND PRIX WINNERS AT THIS CIRCUIT", className="chart-title")]),
                    hist_table
                ]
            )
        ]
    )
