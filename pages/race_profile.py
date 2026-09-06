"""
Race Profile Page for F1 Historical Analytics.
Theme: Deep Grand Prix Classification & Telemetry.
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
    season_options = [{'label': f"Season {s}", 'value': s} for s in seasons]
    default_season = 2021 if 2021 in seasons else seasons[0]
    
    # Rounds for default season
    races = loader.query("SELECT round, raceName FROM races WHERE season = ? ORDER BY round ASC", [default_season])
    round_options = [{'label': f"Round {r['round']}: {remove_hyphens(r['raceName'])}", 'value': r['round']} for r in races.to_dict('records')]
    default_round = races.iloc[-1]['round'] if not races.empty else 1
    
    return html.Div(
        className="page-body",
        children=[
            # Header
            html.Div(
                className="section-header",
                children=[
                    html.H1("GRAND PRIX CLASSIFICATION & TELEMETRY", className="section-title"),
                    html.P("In depth Grand Prix telemetry, starting grid vs finish position deltas, points distribution, and fastest lap records.", className="section-subtitle")
                ]
            ),
            
            # Selectors bar
            html.Div(
                className="filter-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        style={"maxWidth": "220px"},
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
                        style={"minWidth": "320px", "flexGrow": "2"},
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
            
            # Dynamic Content Container
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
        return html.Div("Please select a season and round from the selectors.", className="empty-state-desc")
        
    loader = DataLoader.get_instance()
    race_row, res_df = loader.get_race_profile(season, round_num)
    if not race_row or res_df is None or res_df.empty:
        return html.Div("Race results record not found.", className="empty-state-desc")
        
    winner = res_df.iloc[0]['driver'] if not res_df.empty else 'N/A'
    winning_team = res_df.iloc[0]['constructor'] if not res_df.empty else 'N/A'
    
    pole_row = res_df[res_df['grid'] == 1]
    pole_driver = pole_row.iloc[0]['driver'] if not pole_row.empty else 'N/A'
    
    fl_row = res_df[res_df['fastest_lap'] != 'N/A']
    fl_driver = fl_row.iloc[0]['driver'] if not fl_row.empty else 'N/A'
    fl_time = fl_row.iloc[0]['fastest_lap'] if not fl_row.empty else 'N/A'
    
    kpis = [
        {"label": "Grand Prix Winner", "value": winner, "context": winning_team, "tag": "P1 FINISH"},
        {"label": "Winning Constructor", "value": winning_team, "context": "Winning constructor", "tag": "MARQUE"},
        {"label": "Pole Position", "value": pole_driver, "context": "Grid P1 starter", "tag": "POLE"},
        {"label": "Fastest Lap Time", "value": fl_time if fl_time != 'N/A' else 'N/A', "context": f"Set by {fl_driver}" if fl_driver != 'N/A' else 'Not recorded', "tag": "LAP RECORD"},
    ]
    
    kpi_cards = []
    for k in kpis:
        val_str = remove_hyphens(str(k["value"]))
        font_size = "22px" if len(val_str) > 14 else "32px"
        kpi_cards.append(
            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        className="kpi-header-row",
                        children=[
                            html.Span(remove_hyphens(k["label"]), className="kpi-label"),
                            html.Span(k["tag"], className="kpi-tag")
                        ]
                    ),
                    html.Div(val_str, className="kpi-value", style={"fontSize": font_size}),
                    html.Div(remove_hyphens(k["context"]), className="kpi-context")
                ]
            )
        )
        
    # Grid vs finish scatter
    valid_grid = res_df[res_df['grid'] > 0].copy()
    scatter_fig = create_scatter_plot(
        valid_grid, x='grid', y='position', 
        title="GRID POSITION VS OFFICIAL RACE CLASSIFICATION", 
        hover_name='driver', height=340
    )
    scatter_fig.update_yaxes(autorange="reversed")
    
    # Points bar chart
    top_pts = res_df[res_df['points'] > 0].copy()
    pts_fig = create_bar_chart(
        top_pts, x='points', y='driver', 
        title="CHAMPIONSHIP POINTS AWARDED", 
        orientation='h', color=COLOR_F1_RED, height=340
    )
    
    table_elem = create_f1_table(res_df, table_id="race-class-table", page_size=25, export_btn_id="btn-export-race-results")
    
    return html.Div(
        children=[
            # Grand Prix Banner Card
            html.Div(
                className="chart-card",
                style={
                    "position": "relative", 
                    "overflow": "hidden", 
                    "display": "flex", 
                    "alignItems": "center", 
                    "justifyContent": "space-between",
                    "padding": "24px 30px",
                    "background": "linear-gradient(135deg, rgba(20, 23, 28, 0.95) 0%, rgba(14, 16, 19, 0.98) 100%)",
                    "marginBottom": "20px"
                },
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "6px"},
                                children=[
                                    html.Span(f"ROUND {race_row['round']}", style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--f1-red)", "fontWeight": "700", "letterSpacing": "1px"}),
                                    html.Span("•", style={"color": "var(--text-dim)", "fontSize": "10px"}),
                                    html.Span(f"SEASON {season}", style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--text-secondary)"}),
                                    html.Span("•", style={"color": "var(--text-dim)", "fontSize": "10px"}),
                                    html.Span(f"DATE: {race_row['date']}", style={"fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "var(--text-muted)"}),
                                ]
                            ),
                            html.H2(
                                remove_hyphens(race_row['raceName']), 
                                style={
                                    "fontFamily": "var(--font-display)", 
                                    "fontSize": "32px", 
                                    "fontWeight": "900", 
                                    "letterSpacing": "1.2px", 
                                    "color": "var(--text-white)", 
                                    "textTransform": "uppercase",
                                    "lineHeight": "1.1",
                                    "marginBottom": "4px"
                                }
                            ),
                            html.Div(
                                style={"fontFamily": "var(--font-body)", "fontSize": "13px", "color": "var(--text-secondary)"},
                                children=f"Venue: {remove_hyphens(race_row['circuitName'])}"
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "fontFamily": "var(--font-display)", 
                            "fontSize": "58px", 
                            "fontWeight": "900", 
                            "color": "var(--f1-gold)", 
                            "opacity": "0.22",
                            "letterSpacing": "1px"
                        },
                        children=f"R{race_row['round']}"
                    )
                ]
            ),
            
            # Key Race KPIs
            html.Div(className="kpi-grid", style={"gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))"}, children=kpi_cards),
            
            # Visual Analytics Grid
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(460px, 1fr))", "gap": "20px", "marginBottom": "20px"},
                children=[
                    html.Div(className="chart-card", children=[dcc.Graph(figure=scatter_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                    html.Div(className="chart-card", children=[dcc.Graph(figure=pts_fig, config={'displayModeBar': False, 'scrollZoom': False})]),
                ]
            ),
            
            # Full Race Classification Table Card
            html.Div(
                className="chart-card",
                children=[
                    html.Div(
                        className="chart-header", 
                        children=[html.H3("OFFICIAL GRAND PRIX CLASSIFICATION & TELEMETRY", className="chart-title")]
                    ),
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
