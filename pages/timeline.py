"""
Timeline & Era Analysis Page for F1 Historical Analytics.
Era comparison across 7 foundational periods of technical evolution.
Strictly zero hyphens in any labels, text, or chart titles.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from services.data_loader import DataLoader
from components.charts import create_bar_chart
from components.tables import create_f1_table
from utils.constants import ERAS, COLOR_F1_RED, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    era_options = [{'label': e['name'] + ' (' + e['label'] + ')', 'value': e['name']} for e in ERAS]
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("ERA & REGULATION EVOLUTION", className="section-title"),
                    html.P("Analyze statistical benchmarks, championship dominance, and mechanical reliability across 7 distinct regulatory eras.", className="section-subtitle")
                ]
            ),
            
            # Era Selector
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "400px"},
                        children=[
                            html.Label("Select Regulatory Era", className="filter-label"),
                            dcc.Dropdown(
                                id="era-page-selector",
                                options=era_options,
                                value=ERAS[0]['name'],
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="era-page-content")
        ]
    )

@callback(
    Output("era-page-content", "children"),
    Input("era-page-selector", "value")
)
def render_era_content(selected_era_name):
    target_era = next((e for e in ERAS if e['name'] == selected_era_name), ERAS[0])
    start_year = target_era['start']
    end_year = target_era['end']
    
    loader = DataLoader.get_instance()
    
    # Era Stats
    sql_kpi = """
    SELECT 
        COUNT(DISTINCT r.season || '_' || r.round) as total_races,
        COUNT(DISTINCT res.driverId) as total_drivers,
        COUNT(DISTINCT res.constructorId) as total_constructors,
        SUM(CASE WHEN LOWER(res.status) NOT LIKE '%finished%' AND LOWER(res.status) NOT LIKE '%lap%' THEN 1 ELSE 0 END) as total_dnfs,
        COUNT(*) as total_entries
    FROM results res
    JOIN races r ON res.season = r.season AND res.round = r.round
    WHERE r.season >= ? AND r.season <= ?
    """
    kpi_df = loader.query(sql_kpi, [start_year, end_year])
    k_row = kpi_df.iloc[0] if not kpi_df.empty else {}
    
    dnf_pct = round((k_row.get('total_dnfs', 0) / max(k_row.get('total_entries', 1), 1)) * 100, 1)
    
    kpis = [
        {"label": "Regulatory Era", "value": target_era['name']},
        {"label": "Championship Span", "value": target_era['label']},
        {"label": "Total Grands Prix", "value": f"{k_row.get('total_races', 0):,}"},
        {"label": "Active Drivers", "value": f"{k_row.get('total_drivers', 0):,}"},
        {"label": "Active Constructors", "value": f"{k_row.get('total_constructors', 0):,}"},
        {"label": "Average DNF Rate", "value": f"{dnf_pct}%"},
    ]
    
    kpi_cards = []
    for k in kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(k["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(k["value"]), className="kpi-value", style={"fontSize": "18px" if len(str(k["value"])) > 10 else "28px"}),
                ]
            )
        )
        
    # Top drivers in this era
    sql_drivers = """
    SELECT 
        res.driverName as driver,
        COUNT(*) as starts,
        SUM(CASE WHEN res.positionOrder = 1 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN res.positionOrder <= 3 THEN 1 ELSE 0 END) as podiums
    FROM results res
    WHERE res.season >= ? AND res.season <= ?
    GROUP BY res.driverId
    ORDER BY wins DESC, podiums DESC
    LIMIT 8
    """
    drivers_era = loader.query(sql_drivers, [start_year, end_year])
    drivers_fig = create_bar_chart(drivers_era, x='wins', y='driver', title=f"Top Grand Prix Winners ({target_era['label']})", orientation='h', color=COLOR_F1_RED)
    
    # Top constructors in this era
    sql_const = """
    SELECT 
        res.constructorName as constructor,
        SUM(CASE WHEN res.positionOrder = 1 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN res.positionOrder <= 3 THEN 1 ELSE 0 END) as podiums
    FROM results res
    WHERE res.season >= ? AND res.season <= ?
    GROUP BY res.constructorId
    ORDER BY wins DESC, podiums DESC
    LIMIT 8
    """
    const_era = loader.query(sql_const, [start_year, end_year])
    const_fig = create_bar_chart(const_era, x='wins', y='constructor', title=f"Constructor Victories ({target_era['label']})", orientation='h', color=COLOR_F1_CYAN)
    
    table_elem = create_f1_table(drivers_era, table_id="era-drivers-table", page_size=10)
    
    return html.Div(
        children=[
            # KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))"}, children=kpi_cards),
            
            # Charts Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=drivers_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=const_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Top Drivers Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("ERA DRIVER BENCHMARK CLASSIFICATION", className="chart-title")]),
                    table_elem
                ]
            )
        ]
    )
