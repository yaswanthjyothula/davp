"""
Historical Analytics & EDA Page for F1 Historical Analytics.
Deep empirical analysis answering the 11 core F1 historical questions.
Strictly zero hyphens in any labels, text, or table cells.
"""

from dash import html, dcc
import pandas as pd
from analysis.eda import get_11_eda_insights
from analysis.statistics import get_descriptive_stats
from components.tables import create_f1_table
from utils.helpers import remove_hyphens

def layout():
    insights = get_11_eda_insights()
    desc_stats_df = get_descriptive_stats()
    stats_table = create_f1_table(desc_stats_df, table_id="eda-stats-table", page_size=10)
    
    insight_cards = []
    for idx, item in enumerate(insights, 1):
        insight_cards.append(
            html.Div(
                className="chart-card",
                style={"borderLeft": "3px solid #E10600", "padding": "18px 24px", "marginBottom": "16px"},
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "6px"},
                        children=[
                            html.Span(f"Q{idx}", style={"color": "#E10600", "fontWeight": "900", "fontSize": "13px", "letterSpacing": "1px"}),
                            html.H4(remove_hyphens(item['question']), style={"fontSize": "15px", "fontWeight": "800", "color": "#0f172a", "margin": "0"}),
                        ]
                    ),
                    html.P(remove_hyphens(item['answer']), style={"color": "#64748b", "fontSize": "13px", "lineHeight": "1.6", "margin": "0"})
                ]
            )
        )
        
    return html.Div(
        className="page-body",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H1("HISTORICAL EDA & EMPIRICAL ANALYSIS", className="section-title"),
                    html.P("Rigorous statistical synthesis addressing 11 foundational research questions across 75 years of World Championship history.", className="section-subtitle")
                ]
            ),
            
            # Descriptive Statistics Section
            html.Div(
                className="chart-card",
                children=[
                    html.Div(className="chart-header", children=[html.H3("DESCRIPTIVE STATISTICS SUMMARY (ALL TIME DRIVERS)", className="chart-title")]),
                    stats_table
                ]
            ),
            
            # 11 Core Historical Questions Section
            html.Div(
                style={"marginTop": "28px"},
                children=[
                    html.H3("THE 11 FOUNDATIONAL HISTORICAL RESEARCH INQUIRIES", style={"fontSize": "18px", "fontWeight": "900", "letterSpacing": "1.5px", "textTransform": "uppercase", "marginBottom": "18px"}),
                    html.Div(children=insight_cards)
                ]
            )
        ]
    )
