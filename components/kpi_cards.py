"""
KPI Cards component for F1 Historical Analytics.
Theme: High precision F1 Motorsport telemetry metric cards.
Strictly zero hyphens in all labels and values.
"""

from dash import html
from utils.helpers import remove_hyphens

def create_kpi_cards(kpi_dict):
    """
    Renders 8 dynamic F1 metric cards with dominant typography, quiet labels, and technical context.
    """
    cards = [
        {
            "label": "Total Seasons",
            "value": f"{kpi_dict.get('total_seasons', 0):,}",
            "context": "1950 to 2026 Archive",
            "tag": "HISTORIC"
        },
        {
            "label": "Total Races",
            "value": f"{kpi_dict.get('total_races', 0):,}",
            "context": "Grands Prix contested",
            "tag": "COMPLETED"
        },
        {
            "label": "Total Drivers",
            "value": f"{kpi_dict.get('total_drivers', 0):,}",
            "context": "World Championship drivers",
            "tag": "DATABASE"
        },
        {
            "label": "Total Constructors",
            "value": f"{kpi_dict.get('total_constructors', 0):,}",
            "context": "Teams and constructor marques",
            "tag": "MARQUES"
        },
        {
            "label": "Total Circuits",
            "value": f"{kpi_dict.get('total_circuits', 0):,}",
            "context": "Tracks across 34 nations",
            "tag": "GLOBAL"
        },
        {
            "label": "Race Entries",
            "value": f"{kpi_dict.get('total_entries', 0):,}",
            "context": "Individual Grand Prix entries",
            "tag": "TELEMETRY"
        },
        {
            "label": "Total Victories",
            "value": f"{kpi_dict.get('total_wins', 0):,}",
            "context": "Official Grand Prix victories",
            "tag": "P1 BENCHMARK"
        },
        {
            "label": "Total Podiums",
            "value": f"{kpi_dict.get('total_podiums', 0):,}",
            "context": "Top three podium finishes",
            "tag": "AWARDS"
        },
    ]
    
    card_elements = []
    for c in cards:
        card_elements.append(
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
        
    return html.Div(className="kpi-grid", children=card_elements)
