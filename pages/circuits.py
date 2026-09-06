"""
Circuits Explorer Page for F1 Historical Analytics.
Theme: Global Circuit Footprint & Track Database (34 Nations).
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
    map_fig = create_global_map(circuits_df, title="FIA FORMULA ONE WORLD CHAMPIONSHIP CIRCUITS (1950 TO 2026)", height=500)
    table_elem = create_f1_table(circuits_df, table_id="circuits-table", page_size=20, export_btn_id="btn-export-circuits")
    
    # Circuit context metrics
    total_circuits = len(circuits_df)
    total_nations = circuits_df['country'].nunique() if 'country' in circuits_df.columns else 34
    top_circuit = circuits_df.iloc[0]['name'] if not circuits_df.empty else 'Monza'
    top_races = circuits_df.iloc[0]['total_races'] if not circuits_df.empty else 73
    
    kpis = [
        {"label": "Global Circuits", "value": str(total_circuits), "context": "Official Grand Prix circuits", "tag": "TRACKS"},
        {"label": "Host Nations", "value": str(total_nations), "context": "Countries across 5 continents", "tag": "TERRITORIES"},
        {"label": "Most Visited Circuit", "value": remove_hyphens(top_circuit), "context": f"{top_races} Grands Prix hosted", "tag": "RECORD VENUE"},
        {"label": "Inaugural Venue", "value": "Silverstone", "context": "May 13 1950 British Grand Prix", "tag": "HERITAGE"},
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
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("GLOBAL CIRCUITS EXPLORER", className="section-title"),
                    html.P("Geographic telemetry and historic records for every circuit, permanent road course, and street circuit to host a Formula 1 Grand Prix.", className="section-subtitle")
                ]
            ),
            
            # Quick Circuit KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))"}, children=kpi_cards),
            
            # Interactive Global Map Card
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=map_fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Circuits Database Table Card
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header",
                        children=[
                            html.H3("WORLD CHAMPIONSHIP CIRCUITS TELEMETRY DATABASE", className="chart-title")
                        ]
                    ),
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
