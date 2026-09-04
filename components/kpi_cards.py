"""
KPI Cards component for F1 Historical Analytics.
Strictly zero hyphens in all labels and values.
"""

from dash import html
from utils.helpers import remove_hyphens

def create_kpi_cards(kpi_dict):
    """
    Renders 8 dynamic F1 metric cards.
    """
    cards = [
        {"label": "Total Seasons", "value": f"{kpi_dict.get('total_seasons', 0):,}"},
        {"label": "Total Races", "value": f"{kpi_dict.get('total_races', 0):,}"},
        {"label": "Total Drivers", "value": f"{kpi_dict.get('total_drivers', 0):,}"},
        {"label": "Total Constructors", "value": f"{kpi_dict.get('total_constructors', 0):,}"},
        {"label": "Total Circuits", "value": f"{kpi_dict.get('total_circuits', 0):,}"},
        {"label": "Total Race Entries", "value": f"{kpi_dict.get('total_entries', 0):,}"},
        {"label": "Total Wins", "value": f"{kpi_dict.get('total_wins', 0):,}"},
        {"label": "Total Podiums", "value": f"{kpi_dict.get('total_podiums', 0):,}"},
    ]
    
    card_elements = []
    for c in cards:
        card_elements.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(c["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(c["value"]), className="kpi-value"),
                ]
            )
        )
        
    return html.Div(className="kpi-grid", children=card_elements)
