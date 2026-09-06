"""
Sidebar Navigation component for F1 Historical Analytics.
Theme: Precision Motorsport Telemetry Navigation System.
Strictly zero hyphens in all labels and text.
"""

from dash import html

NAV_GROUPS = [
    {
        "group_title": "CORE INTELLIGENCE",
        "items": [
            {
                "label": "Overview",
                "path": "/dashboard/",
                "icon_path": "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"
            },
            {
                "label": "Drivers Database",
                "path": "/dashboard/drivers",
                "icon_path": "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
            },
            {
                "label": "Driver Profile",
                "path": "/dashboard/driver_profile",
                "icon_path": "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z"
            },
            {
                "label": "Constructors",
                "path": "/dashboard/constructors",
                "icon_path": "M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-4.86 8.86l-3 3.87L9 13.14 6 17h12l-3.86-5.14z"
            },
            {
                "label": "Constructor Profile",
                "path": "/dashboard/constructor_profile",
                "icon_path": "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"
            },
        ]
    },
    {
        "group_title": "CHAMPIONSHIP ARCHIVE",
        "items": [
            {
                "label": "Seasons Archive",
                "path": "/dashboard/seasons",
                "icon_path": "M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z"
            },
            {
                "label": "Race Archive",
                "path": "/dashboard/races",
                "icon_path": "M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"
            },
            {
                "label": "Race Profile",
                "path": "/dashboard/race_profile",
                "icon_path": "M13 2.05v3.03c3.39.49 6 3.39 6 6.92 0 .9-.18 1.75-.48 2.54l2.6 1.53c.56-1.24.88-2.62.88-4.07 0-5.18-3.95-9.45-9-9.95zM12 19c-3.87 0-7-3.13-7-7 0-3.53 2.61-6.43 6-6.92V2.05c-5.06.5-9 4.76-9 9.95 0 5.52 4.47 10 9.99 10 3.31 0 6.24-1.61 8.01-4.09l-2.45-1.45C16.14 17.91 14.19 19 12 19z"
            },
            {
                "label": "Global Circuits",
                "path": "/dashboard/circuits",
                "icon_path": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"
            },
            {
                "label": "Standings",
                "path": "/dashboard/standings",
                "icon_path": "M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94.63 1.5 1.98 2.63 3.61 2.96V19H7v2h10v-2h-4v-3.1c1.63-.33 2.98-1.46 3.61-2.96C19.08 12.63 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm14 0c0 1.3-.84 2.4-2 2.82V7h2v1z"
            },
            {
                "label": "Sprint Races",
                "path": "/dashboard/sprint",
                "icon_path": "M7 2v11h3v9l7-12h-4l4-8z"
            },
        ]
    },
    {
        "group_title": "DATA SYSTEM",
        "items": [
            {
                "label": "Data Explorer",
                "path": "/dashboard/data_explorer",
                "icon_path": "M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"
            },
        ]
    }
]

def make_svg_icon(path_d, color="%239DA3AE"):
    return f"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='{color}'><path d='{path_d}'/></svg>"

def create_sidebar(current_path="/dashboard/"):
    nav_sections = []
    
    for group in NAV_GROUPS:
        links = []
        for item in group["items"]:
            is_active = (current_path == item["path"]) or (current_path == "" and item["path"] == "/dashboard/")
            cls_name = "nav-link active" if is_active else "nav-link"
            icon_color = "%23E10600" if is_active else "%239DA3AE"
            
            links.append(
                html.A(
                    className=cls_name,
                    href=item["path"],
                    children=[
                        html.Span(
                            className="nav-icon",
                            children=[
                                html.Img(
                                    src=make_svg_icon(item["icon_path"], icon_color),
                                    className="nav-svg-icon",
                                    alt=""
                                )
                            ]
                        ),
                        html.Span(item["label"], className="nav-text"),
                    ]
                )
            )
            
        nav_sections.append(
            html.Div(
                className="nav-group-container",
                children=[
                    html.Div(group["group_title"], className="nav-group-heading"),
                    html.Div(className="nav-group-links", children=links)
                ]
            )
        )
        
    return html.Aside(
        className="sidebar",
        children=[
            # Header Branding
            html.Div(
                className="sidebar-header",
                children=[
                    html.A(
                        href="/",
                        className="sidebar-brand-wrap",
                        title="Return to Formula 1 Cinematic Experience",
                        children=[
                            html.Img(src="/assets/images/f1_logo.svg", className="sidebar-logo", alt="Formula 1 Logo"),
                            html.Div(
                                className="sidebar-brand-text",
                                children=[
                                    html.Div("DATA INTELLIGENCE", className="sidebar-brand-title"),
                                    html.Div("1950 to 2026 Archive", className="sidebar-brand-subtitle"),
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Nav Tree
            html.Nav(
                className="sidebar-nav",
                children=nav_sections
            ),
            
            # Telemetry status footer
            html.Div(
                className="sidebar-footer",
                children=[
                    html.Div(
                        className="telemetry-status-pill",
                        children=[
                            html.Span(className="pulse-dot"),
                            html.Span("75 SEASONS CONNECTED", className="status-text")
                        ]
                    )
                ]
            )
        ]
    )
