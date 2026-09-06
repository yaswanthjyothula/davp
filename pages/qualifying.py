"""
Qualifying Analytics Page for F1 Historical Analytics.
Pole positions, qualifying consistency, and pole to win conversion rates.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_bar_chart, create_scatter_plot
from components.tables import create_f1_table
from utils.constants import COLOR_F1_RED, COLOR_F1_GOLD
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    
    # Most poles
    top_poles = loader.query("SELECT name, poles FROM driver_summary WHERE poles > 0 ORDER BY poles DESC LIMIT 10")
    poles_fig = create_bar_chart(top_poles, x='poles', y='name', title="All Time Pole Positions Benchmark", orientation='h', color=COLOR_F1_GOLD)
    
    # Pole to win conversion
    pole_conv = loader.query("""
    SELECT 
        driverName as driver,
        COUNT(*) as poles,
        SUM(CASE WHEN positionOrder = 1 THEN 1 ELSE 0 END) as pole_wins
    FROM results
    WHERE grid = 1
    GROUP BY driverId
    HAVING poles >= 10
    ORDER BY (CAST(pole_wins AS FLOAT) / poles) DESC
    LIMIT 10
    """)
    pole_conv['conversion_rate'] = ((pole_conv['pole_wins'] / pole_conv['poles']) * 100).round(1)
    conv_fig = create_bar_chart(pole_conv, x='conversion_rate', y='driver', title="Pole to Win Conversion Rate (%) (Minimum 10 Poles)", orientation='h', color=COLOR_F1_RED)
    
    # Scatter: qual pos vs finish pos
    qual_df = loader.get_qualifying_analytics()
    scatter_fig = create_scatter_plot(qual_df, x='qual_pos', y='finish_pos', title="Qualifying Grid Position vs Final Race Classification", hover_name='driver')
    scatter_fig.update_xaxes(range=[0.5, 24.5])
    scatter_fig.update_yaxes(range=[24.5, 0.5])
    
    table_elem = create_f1_table(pole_conv, table_id="pole-conversion-table", page_size=10)
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("QUALIFYING & POLE POSITION ANALYTICS", className="section-title"),
                    html.P("Empirical analysis of single lap qualifying pace, grid correlation, and victory conversion efficiency.", className="section-subtitle")
                ]
            ),
            
            # Charts Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=poles_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=conv_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Grid vs Finish Correlation Chart
            html.Div(
                className="chart-card",
                children=[dcc.Graph(figure=scatter_fig, config={'displayModeBar': False, 'scrollZoom': False})]
            ),
            
            # Conversion Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("POLE POSITION CONVERSION EFFICIENCY TABLE", className="chart-title")]),
                    table_elem
                ]
            )
        ]
    )
