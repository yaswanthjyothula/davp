"""
Circuits Explorer Page for F1 Historical Analytics.
Global map and circuit database.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_global_map
from components.tables import create_f1_table
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    circuits_df = loader.query("SELECT * FROM circuit_summary ORDER BY total_races DESC")
    map_fig = create_global_map(circuits_df, title="FIA Formula One World Championship Circuits (1950 to 2026)")
    table_elem = create_f1_table(circuits_df, table_id="circuits-table", page_size=20, export_btn_id="btn-export-circuits")
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("GLOBAL CIRCUITS EXPLORER", className="section-title"),
                    html.P("Every circuit and street course to host a Formula 1 Grand Prix across 34 nations.", className="section-subtitle")
                ]
            ),
            
            # Interactive Global Map
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=map_fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Circuits Database Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("WORLD CHAMPIONSHIP CIRCUITS DATABASE", className="chart-title")]),
                    table_elem
                ]
            )
        ]
    )

@callback(
    Output("btn-export-circuits-download", "data"),
    Input("btn-export-circuits", "n_clicks"),
    prevent_initial_call=True
)
def export_circuits_csv(n_clicks):
    if not n_clicks:
        return None
    loader = DataLoader.get_instance()
    df = loader.query("SELECT * FROM circuit_summary ORDER BY total_races DESC")
    clean_df = df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, "f1_circuits_historical.csv", index=False)
