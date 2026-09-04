"""
Race Profile Page for F1 Historical Analytics.
Deep Grand Prix classification and telemetry.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from services.data_loader import DataLoader
from components.tables import create_f1_table
from components.charts import create_scatter_plot, create_bar_chart
from utils.constants import COLOR_F1_RED, COLOR_F1_GOLD, COLOR_F1_CYAN
from utils.helpers import remove_hyphens

def layout():
    loader = DataLoader.get_instance()
    seasons = loader.get_seasons_list()
    season_options = [{'label': str(s), 'value': s} for s in seasons]
    default_season = 2021 if 2021 in seasons else seasons[0]
    
    # Rounds for default season
    races = loader.query("SELECT round, raceName FROM races WHERE season = ? ORDER BY round ASC", [default_season])
    round_options = [{'label': f"Round {r['round']}: {r['raceName']}", 'value': r['round']} for r in races.to_dict('records')]
    default_round = races.iloc[-1]['round'] if not races.empty else 1
    
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("GRAND PRIX CLASSIFICATION & TELEMETRY", className="section-title"),
                    html.P("Detailed classification, telemetry, grid progression, and fastest laps for every Grand Prix.", className="section-subtitle")
                ]
            ),
            
            # Selectors
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "200px"},
                        children=[
                            html.Label("Championship Season", className="filter-label"),
                            dcc.Dropdown(
                                id="race-profile-season",
                                options=season_options,
                                value=default_season,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    ),
                    html.Div(
                        className="filter-group",
                        style={"minWidth": "300px"},
                        children=[
                            html.Label("Select Grand Prix Round", className="filter-label"),
                            dcc.Dropdown(
                                id="race-profile-round",
                                options=round_options,
                                value=default_round,
                                clearable=False,
                                className="dash-dropdown"
                            )
                        ]
                    )
                ]
            ),
            
            # Dynamic Container
            html.Div(id="race-profile-content")
        ]
    )

@callback(
    Output("race-profile-round", "options"),
    Output("race-profile-round", "value"),
    Input("race-profile-season", "value")
)
def update_round_options(season):
    if not season:
        return [], None
    loader = DataLoader.get_instance()
    races = loader.query("SELECT round, raceName FROM races WHERE season = ? ORDER BY round ASC", [int(season)])
    options = [{'label': f"Round {r['round']}: {remove_hyphens(r['raceName'])}", 'value': r['round']} for r in races.to_dict('records')]
    val = options[0]['value'] if options else None
    return options, val

@callback(
    Output("race-profile-content", "children"),
    Input("race-profile-season", "value"),
    Input("race-profile-round", "value")
)
def render_race_profile(season, round_num):
    if not season or not round_num:
        return html.Div("Please select a season and round.", style={"color": "#9FA6B2"})
        
    loader = DataLoader.get_instance()
    race_row, res_df = loader.get_race_profile(season, round_num)
    if not race_row or res_df is None or res_df.empty:
        return html.Div("Race results not found.", style={"color": "#9FA6B2"})
        
    winner = res_df.iloc[0]['driver'] if not res_df.empty else 'N/A'
    winning_team = res_df.iloc[0]['constructor'] if not res_df.empty else 'N/A'
    
    pole_row = res_df[res_df['grid'] == 1]
    pole_driver = pole_row.iloc[0]['driver'] if not pole_row.empty else 'N/A'
    
    fl_row = res_df[res_df['fastest_lap'] != 'N/A']
    fl_driver = fl_row.iloc[0]['driver'] if not fl_row.empty else 'N/A'
    fl_time = fl_row.iloc[0]['fastest_lap'] if not fl_row.empty else 'N/A'
    
    kpis = [
        {"label": "Grand Prix Winner", "value": winner},
        {"label": "Winning Constructor", "value": winning_team},
        {"label": "Pole Position", "value": pole_driver},
        {"label": "Fastest Lap", "value": f"{fl_driver} ({fl_time})" if fl_driver != 'N/A' else 'N/A'},
    ]
    
    kpi_cards = []
    for k in kpis:
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(remove_hyphens(k["label"]), className="kpi-label"),
                    html.Div(remove_hyphens(k["value"]), className="kpi-value", style={"fontSize": "18px"}),
                ]
            )
        )
        
    # Grid vs finish scatter
    valid_grid = res_df[res_df['grid'] > 0].copy()
    scatter_fig = create_scatter_plot(valid_grid, x='grid', y='position', title="Grid Position vs Official Race Classification", hover_name='driver')
    scatter_fig.update_yaxes(autorange="reversed")
    
    # Points bar chart
    top_pts = res_df[res_df['points'] > 0].copy()
    pts_fig = create_bar_chart(top_pts, x='points', y='driver', title="Championship Points Awarded", orientation='h', color=COLOR_F1_RED)
    
    table_elem = create_f1_table(res_df, table_id="race-class-table", page_size=25, export_btn_id="btn-export-race-results")
    
    return html.Div(
        children=[
            # Race title header
            html.Div(
                className="chart-card",
                children=[
                    html.H2(f"{season} {remove_hyphens(race_row['raceName'])}", style={"fontSize": "26px", "fontWeight": "900", "marginBottom": "6px"}),
                    html.Div(
                        style={"color": "#9FA6B2", "fontSize": "13px", "display": "flex", "gap": "20px"},
                        children=[
                            html.Span(f"Circuit: {remove_hyphens(race_row['circuitName'])}"),
                            html.Span(f"Date: {race_row['date']}"),
                            html.Span(f"Round: {race_row['round']}"),
                        ]
                    )
                ]
            ),
            
            # KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))"}, children=kpi_cards),
            
            # Charts
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=scatter_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=pts_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Full Race Classification Table
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("OFFICIAL RACE CLASSIFICATION", className="chart-title")]),
                    table_elem
                ]
            )
        ]
    )

@callback(
    Output("btn-export-race-results-download", "data"),
    Input("btn-export-race-results", "n_clicks"),
    State("race-profile-season", "value"),
    State("race-profile-round", "value"),
    prevent_initial_call=True
)
def export_race_classification(n_clicks, season, round_num):
    if not n_clicks or not season or not round_num:
        return None
    loader = DataLoader.get_instance()
    _, res_df = loader.get_race_profile(season, round_num)
    clean_df = res_df.copy()
    for col in clean_df.columns:
        if clean_df[col].dtype == 'object':
            clean_df[col] = clean_df[col].astype(str).apply(remove_hyphens)
    return dcc.send_data_frame(clean_df.to_csv, f"f1_race_results_{season}_round{round_num}.csv", index=False)
