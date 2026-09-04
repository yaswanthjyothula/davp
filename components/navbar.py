"""
Top Navbar component for F1 Historical Analytics.
Strictly zero hyphens in user text.
Includes 'BACK' button linking to '/'.
"""

from dash import html
from utils.helpers import remove_hyphens

def create_navbar(current_page_title="Historical Analytics"):
    return html.Header(
        className="top-navbar",
        children=[
            html.Div(
                className="navbar-title-wrap",
                children=[
                    html.H2(remove_hyphens(current_page_title), className="navbar-title"),
                    html.Span("1950 to 2026 Archive", className="navbar-badge"),
                ]
            ),
            html.Div(
                className="navbar-actions",
                children=[
                    # Button returning to cinematic landing page
                    html.A(
                        children=[
                            html.Span("←", style={"fontSize": "14px", "fontWeight": "bold"}),
                            html.Span("BACK")
                        ],
                        href="/",
                        className="btn-landing",
                        id="btn-back-to-experience",
                        title="Return to the cinematic 3D storytelling landing page"
                    ),
                ]
            )
        ]
    )
