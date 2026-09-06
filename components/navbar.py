"""
Top Navbar component for F1 Historical Analytics.
Theme: Precision Motorsport Telemetry Header.
Strictly zero hyphens in user text.
Includes 'RETURN TO EXPERIENCE' button linking to '/'.
"""

from dash import html
from utils.helpers import remove_hyphens

def create_navbar(current_page_title="Historical Analytics"):
    clean_title = remove_hyphens(current_page_title)
    
    return html.Header(
        className="top-navbar",
        children=[
            # Left: Breadcrumb & Title
            html.Div(
                className="navbar-left",
                children=[
                    html.Div(
                        className="breadcrumb-trail",
                        children=[
                            html.Span("F1 INTELLIGENCE", className="breadcrumb-root"),
                            html.Span("/", className="breadcrumb-separator"),
                            html.H2(clean_title, className="navbar-title"),
                        ]
                    ),
                ]
            ),
            
            # Center: Global Context Telemetry Chip
            html.Div(
                className="navbar-center",
                children=[
                    html.Div(
                        className="navbar-telemetry-chip",
                        children=[
                            html.Span("75 SEASONS", className="chip-metric"),
                            html.Span("•", className="chip-dot"),
                            html.Span("1,125+ GRANDS PRIX", className="chip-metric"),
                            html.Span("•", className="chip-dot"),
                            html.Span("861 DRIVERS", className="chip-metric"),
                        ]
                    )
                ]
            ),
            
            # Right: Cinematic Return CTA
            html.Div(
                className="navbar-actions",
                children=[
                    html.A(
                        href="/",
                        className="btn-cinematic-return",
                        id="btn-back-to-experience",
                        title="Return to the 571 frame 3D cinematic scrollytelling experience",
                        children=[
                            html.Span("←", style={"fontSize": "14px", "fontWeight": "bold", "marginRight": "6px"}),
                            html.Span("RETURN TO EXPERIENCE", className="btn-text")
                        ]
                    )
                ]
            )
        ]
    )
