"""
Sidebar Navigation component for F1 Historical Analytics.
Strictly zero hyphens in all labels and text.
"""

from dash import html
import dash

NAV_ITEMS = [
    {"label": "Overview", "path": "/dashboard/"},
    {"label": "Drivers", "path": "/dashboard/drivers"},
    {"label": "Driver Profile", "path": "/dashboard/driver_profile"},
    {"label": "Seasons", "path": "/dashboard/seasons"},
    {"label": "Races", "path": "/dashboard/races"},
    {"label": "Race Profile", "path": "/dashboard/race_profile"},
    {"label": "Circuits", "path": "/dashboard/circuits"},
    {"label": "Constructors", "path": "/dashboard/constructors"},
    {"label": "Constructor Profile", "path": "/dashboard/constructor_profile"},
    {"label": "Standings", "path": "/dashboard/standings"},
    {"label": "Sprint Races", "path": "/dashboard/sprint"},
    {"label": "Data Explorer", "path": "/dashboard/data_explorer"},
]

def create_sidebar(current_path="/dashboard/"):
    links = []
    for item in NAV_ITEMS:
        # Check active status
        is_active = (current_path == item["path"]) or (current_path == "" and item["path"] == "/dashboard/")
        cls_name = "nav-link active" if is_active else "nav-link"
        
        links.append(
            html.A(
                className=cls_name,
                href=item["path"],
                children=[
                    html.Span(item["label"]),
                ]
            )
        )
        
    return html.Aside(
        className="sidebar",
        children=[
            html.Div(
                className="sidebar-header",
                children=[
                    html.Img(src="/assets/images/f1_logo.svg", className="sidebar-logo", alt="Formula 1 Logo"),
                    html.Div(
                        children=[
                            html.Div("Formula 1 history", className="sidebar-brand-title"),
                        ]
                    )
                ]
            ),
            html.Nav(
                className="sidebar-nav",
                children=links
            )
        ]
    )
