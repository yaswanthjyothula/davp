"""
Pit Stops Page for F1 Historical Analytics.
Duration analytics and strategy distribution (2011 to 2026).
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_bar_chart, create_scatter_plot
from utils.constants import COLOR_F1_RED, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    
    # Avg stop duration by constructor (filter out extreme outliers > 15s)
    const_pit = loader.query("""
    SELECT 
        res.constructorName as constructor,
        COUNT(*) as total_stops,
        ROUND(AVG(p.duration_sec), 2) as avg_duration_sec,
        ROUND(MIN(p.duration_sec), 2) as fastest_stop_sec
    FROM pit_stops p
    JOIN results res ON p.season = res.season AND p.round = res.round AND p.driverId = res.driverId
    WHERE p.duration_sec > 1.5 AND p.duration_sec < 10.0
    GROUP BY res.constructorId
    HAVING total_stops >= 50
    ORDER BY avg_duration_sec ASC
    LIMIT 10
    """)
    const_fig = create_bar_chart(const_pit, x='avg_duration_sec', y='constructor', title="Average Stationary Pit Stop Duration by Constructor (Seconds)", orientation='h', color=COLOR_F1_CYAN)
    
    # Stops by season
    season_pit = loader.query("""
    SELECT 
        season,
        COUNT(*) as total_stops,
        ROUND(AVG(duration_sec), 2) as avg_duration
    FROM pit_stops
    WHERE duration_sec > 1.5 AND duration_sec < 15.0
    GROUP BY season
    ORDER BY season ASC
    """)
    season_fig = create_bar_chart(season_pit, x='season', y='total_stops', title="Total Recorded Pit Stops by Season", color=COLOR_F1_RED)
    
    table_elem = create_f1_table(const_pit, table_id="pit-stops-summary-table", page_size=10)
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("PIT STOP TELEMETRY & STRATEGY", className="section-title"),
                    html.P("Stationary pit stop duration benchmarks and constructor servicing efficiency (recorded since 2011).", className="section-subtitle")
                ]
            ),
            
            # Charts Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=const_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=season_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("CONSTRUCTOR PIT STOP BENCHMARKS", className="chart-title")]),
                    table_elem
                ]
            )
        ]
    )
