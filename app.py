"""
Main Entry Point for Formula 1 Historical Analytics & Cinematic Experience.
Unified Python Server (Flask + Plotly Dash).
Serves:
  /           -> Cinematic 571-frame 3D storytelling landing page
  /dashboard/ -> Comprehensive Formula 1 Historical Analytics Platform
Strictly zero hyphens in user text. F1 Torque typography applied universally.
"""

import os
import sys
from flask import Flask, send_from_directory, redirect
import dash
from dash import html, dcc, callback, Input, Output

# Ensure local modules can be imported
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from components.navbar import create_navbar
from components.sidebar import create_sidebar
from pages import (
    overview, drivers, driver_profile, seasons,
    races, race_profile, circuits,
    constructors, constructor_profile, standings,
    sprint, data_explorer
)

# 1. Initialize Flask Server
server = Flask(__name__, static_folder=BASE_DIR)
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@server.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@server.route('/')
def serve_landing_page():
    """Serves the cinematic landing page."""
    return send_from_directory(BASE_DIR, 'index.html')

@server.route('/dashboard')
def redirect_to_dashboard():
    """Redirects /dashboard to /dashboard/."""
    return redirect('/dashboard/')

@server.route('/<path:filename>')
def serve_static_root(filename):
    """Serves landing page static files (CSS, JS, images, sequential frames)."""
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, filename)
    return "Not Found", 404

# 2. Initialize Dash Application on Flask
app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dashboard/',
    requests_pathname_prefix='/dashboard/',
    suppress_callback_exceptions=True,
    title="F1 Historical Analytics",
    update_title=None,
    assets_folder=os.path.join(BASE_DIR, 'assets')
)

# 3. Main Dashboard Layout Shell
app.layout = html.Div(
    className="app-container",
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id="sidebar-container", children=create_sidebar("/dashboard/")),
        html.Main(
            className="main-content",
            children=[
                html.Div(id="navbar-container", children=create_navbar("Overview Analytics")),
                html.Div(id="page-content")
            ]
        )
    ]
)

# 4. Multi-Page Routing
PAGE_MAP = {
    '/dashboard/': (overview.layout, "Historical Overview"),
    '/dashboard/overview': (overview.layout, "Historical Overview"),
    '/dashboard/drivers': (drivers.layout, "Drivers Database"),
    '/dashboard/driver_profile': (driver_profile.layout, "Driver Telemetry Profile"),
    '/dashboard/seasons': (seasons.layout, "Historical Seasons Archive"),
    '/dashboard/races': (races.layout, "Historical Race Archive"),
    '/dashboard/race_profile': (race_profile.layout, "Grand Prix Race Profile"),
    '/dashboard/circuits': (circuits.layout, "Global Circuits Explorer"),
    '/dashboard/constructors': (constructors.layout, "Constructors Database"),
    '/dashboard/constructor_profile': (constructor_profile.layout, "Constructor Telemetry Profile"),
    '/dashboard/standings': (standings.layout, "World Championship Standings"),
    '/dashboard/sprint': (sprint.layout, "Sprint Race Telemetry"),
    '/dashboard/data_explorer': (data_explorer.layout, "Relational Data Explorer"),
}

@callback(
    Output("page-content", "children"),
    Output("navbar-container", "children"),
    Output("sidebar-container", "children"),
    Input("url", "pathname")
)
def route_dashboard(pathname):
    clean_path = pathname.rstrip('/') if pathname and pathname != '/dashboard/' else '/dashboard/'
    if clean_path in PAGE_MAP:
        layout_func, title = PAGE_MAP[clean_path]
    else:
        layout_func, title = overview.layout, "Historical Overview"
        
    return layout_func(), create_navbar(title), create_sidebar(clean_path)

if __name__ == '__main__':
    print("Starting Formula 1 Historical Analytics Platform...")
    print("Landing page available at: http://localhost:3000/")
    print("Dashboard available at:    http://localhost:3000/dashboard/")
    app.run(host='0.0.0.0', port=3000, debug=False)
