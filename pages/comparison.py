"""
Driver Comparison Page for F1 Historical Analytics.
Allows comparison between 2 to 5 drivers.
Strictly zero hyphens in any labels, text, or chart titles.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_radar_chart, create_multi_line_chart, create_bar_chart
from components.tables import create_f1_table
from utils.constants import COLOR_F1_RED, COLOR_F1_CYAN, COLOR_F1_GOLD
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    drivers = loader.get_drivers_list()
    driver_options = [{'label': d['name'], 'value': d['driverId']} for d in drivers]
    
    # Defaults: Hamilton, Schumacher, Verstappen
    defaults = []
    for d_id in ['hamilton', 'michael_schumacher', 'max_verstappen']:
        if any(d['driverId'] == d_id for d in drivers):
            defaults.append(d_id)
    if not defaults:
        defaults = [d['driverId'] for d in drivers[:3]]
        
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("DRIVER HEAD TO HEAD COMPARISON", className="section-title"),
                    html.P("Compare 2 to 5 Formula 1 drivers with multi dimensional radar analysis and era aware normalized metrics.", className="section-subtitle")
                ]
            ),
            
            # Multi-select bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"width": "100%"},
                        children=[
                            html.Label("Select Drivers (2 to 5 Drivers)", className="filter-label"),
                            dcc.Dropdown(
                                id="comparison-driver-selector",
                                options=driver_options,
                                value=defaults,
                                multi=True,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="comparison-content")
        ]
    )

@callback(
    Output("comparison-content", "children"),
    Input("comparison-driver-selector", "value")
)
def render_driver_comparison(driver_ids):
    if not driver_ids or len(driver_ids) < 2:
        return html.Div("Please select at least 2 drivers to compare.", style={"color": "#9FA6B2", "padding": "20px"})
    if len(driver_ids) > 5:
        driver_ids = driver_ids[:5]
        
    loader = DataLoader.get_instance()
    summary_df, timeline_df = loader.get_driver_comparison(driver_ids)
    if summary_df is None or summary_df.empty:
        return html.Div("No driver data found.", style={"color": "#9FA6B2"})
        
    # Build Radar Data
    categories = ['Win Rate %', 'Podium Rate %', 'Championships', 'Total Wins', 'Total Podiums']
    # Normalize values for radar 0-100
    max_wins = max(summary_df['wins'].max(), 1)
    max_podiums = max(summary_df['podiums'].max(), 1)
    max_champs = max(summary_df['championships'].max(), 1)
    
    radar_data = []
    for _, row in summary_df.iterrows():
        norm_wins = (row['wins'] / max_wins) * 100
        norm_pod = (row['podiums'] / max_podiums) * 100
        norm_champs = (row['championships'] / max_champs) * 100
        # win_rate and podium_rate already out of 100
        vals = [
            float(row['win_rate']),
            float(row['podium_rate']),
            round(norm_champs, 1),
            round(norm_wins, 1),
            round(norm_pod, 1)
        ]
        radar_data.append({
            'name': row['name'],
            'values': vals
        })
        
    radar_fig = create_radar_chart(categories, radar_data, title="Multidimensional Driver Benchmark")
    
    # Career points timeline
    timeline_fig = create_multi_line_chart(timeline_df, x='season', y='season_points', group_col='driver', title="Championship Points Scored by Season")
    
    # Head to head comparison table
    comp_metrics = ['championships', 'wins', 'podiums', 'poles', 'starts', 'points', 'win_rate', 'podium_rate', 'avg_finish', 'avg_grid']
    table_rows = []
    for m in comp_metrics:
        row_dict = {'Metric': remove_hyphens(m.replace('_', ' ').title())}
        for _, d in summary_df.iterrows():
            row_dict[remove_hyphens(d['name'])] = d[m]
        table_rows.append(row_dict)
    comp_table_df = pd.DataFrame(table_rows)
    table_elem = create_f1_table(comp_table_df, table_id="comparison-table", page_size=12)
    
    return html.Div(
        children=[
            # Visualizations
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=radar_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=timeline_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Head to Head Metric Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("HEAD TO HEAD STATISTICAL MATRIX", className="chart-title")]),
                    table_elem
                ]
            ),
            
            # Era Aware Intelligence Notes
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("ERA AWARE COMPARATIVE INTELLIGENCE", className="chart-title")]),
                    html.Ul(
                        style={"color": "#475569", "lineHeight": "1.8", "paddingLeft": "20px", "fontSize": "13px"},
                        children=[
                            html.Li("Calendar Expansion: Early eras had 7 to 11 races per year, while modern drivers compete in 22 to 24 Grands Prix annually."),
                            html.Li("Points System Inflation: Prior to 1960, a win was worth 8 points; 1961 to 1990 awarded 9 points; 1991 to 2009 awarded 10 points; 2010 to present awards 25 points. Raw points comparisons across eras are not equivalent."),
                            html.Li("Mechanical Reliability: Modern Grand Prix drivers enjoy over 85% mechanical finishing reliability compared to sub 50% in the 1950s and 1960s."),
                        ]
                    )
                ]
            )
        ]
    )
