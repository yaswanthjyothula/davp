"""
Plotly Chart Generators for F1 Historical Analytics.
Theme: F1 Dark Motorsport Aesthetics.
Strictly zero hyphens in any titles, axis labels, legends, or hover templates.
"""

import plotly.graph_objects as go
import plotly.express as px
from utils.constants import (
    FONT_FAMILY, COLOR_BG_CARD, COLOR_F1_RED, COLOR_F1_GOLD, 
    COLOR_F1_CYAN, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, PLOTLY_TEMPLATE
)
from utils.helpers import remove_hyphens

def apply_f1_theme(fig, title="", height=380):
    """Apply the F1 Torque dark theme to any Plotly figure."""
    clean_title = remove_hyphens(title)
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title={
            'text': clean_title,
            'font': {'family': FONT_FAMILY, 'size': 14, 'color': '#0f172a'},
            'x': 0.02,
            'y': 0.95
        },
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, color='#0f172a'),
        margin=dict(t=50, r=20, b=40, l=40),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font=dict(family=FONT_FAMILY, color='#0f172a'),
            bordercolor=COLOR_F1_RED
        )
    )
    fig.update_xaxes(
        gridcolor='#f1f5f9',
        linecolor='#cbd5e1',
        tickfont=dict(family=FONT_FAMILY, color='#64748b')
    )
    fig.update_yaxes(
        gridcolor='#f1f5f9',
        linecolor='#cbd5e1',
        tickfont=dict(family=FONT_FAMILY, color='#64748b')
    )
    return fig

def create_bar_chart(df, x, y, title="", color=COLOR_F1_RED, orientation='v', height=360):
    """Generate high performance bar chart."""
    fig = go.Figure()
    if orientation == 'h':
        fig.add_trace(go.Bar(
            y=df[y].apply(remove_hyphens),
            x=df[x],
            orientation='h',
            marker=dict(color=color, line=dict(color='rgba(255,255,255,0.1)', width=1)),
            hoverinfo="x+y"
        ))
    else:
        fig.add_trace(go.Bar(
            x=df[x].astype(str).apply(remove_hyphens),
            y=df[y],
            marker=dict(color=color, line=dict(color='rgba(255,255,255,0.1)', width=1)),
            hoverinfo="x+y"
        ))
    return apply_f1_theme(fig, title=title, height=height)

def create_line_chart(df, x, y, title="", color=COLOR_F1_RED, height=360):
    """Generate smooth line chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x].astype(str).apply(remove_hyphens),
        y=df[y],
        mode='lines+markers',
        line=dict(color=color, width=3, shape='spline'),
        marker=dict(size=6, color=color, line=dict(color='#fff', width=1)),
        hoverinfo="x+y"
    ))
    return apply_f1_theme(fig, title=title, height=height)

def create_multi_line_chart(df, x, y, group_col, title="", height=400):
    """Generate multi line chart with distinct colors."""
    fig = go.Figure()
    palette = [COLOR_F1_RED, COLOR_F1_CYAN, COLOR_F1_GOLD, '#FF8000', '#00A896', '#7C3AED', '#0F172A']
    
    groups = df[group_col].unique()
    for idx, g in enumerate(groups):
        sub_df = df[df[group_col] == g]
        c = palette[idx % len(palette)]
        fig.add_trace(go.Scatter(
            x=sub_df[x].astype(str).apply(remove_hyphens),
            y=sub_df[y],
            mode='lines+markers',
            name=remove_hyphens(str(g)),
            line=dict(color=c, width=2.5),
            marker=dict(size=5, color=c)
        ))
    return apply_f1_theme(fig, title=title, height=height)

def create_scatter_plot(df, x, y, title="", hover_name=None, height=380):
    """Generate scatter plot for correlations (e.g. grid vs finish)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode='markers',
        marker=dict(
            size=7,
            color=COLOR_F1_RED,
            opacity=0.65,
            line=dict(width=1, color='rgba(255,255,255,0.3)')
        ),
        text=df[hover_name].apply(remove_hyphens) if hover_name else None,
        hoverinfo="text+x+y" if hover_name else "x+y"
    ))
    return apply_f1_theme(fig, title=title, height=height)

def create_global_map(circuits_df, title="Global Circuit Footprint", height=480):
    """Generate interactive Plotly world map showing all F1 circuits."""
    fig = go.Figure(go.Scattergeo(
        lat=circuits_df['lat'],
        lon=circuits_df['long'],
        text=circuits_df['name'].apply(remove_hyphens) + ' (' + circuits_df['country'].apply(remove_hyphens) + ')<br>Total Races: ' + circuits_df['total_races'].astype(str),
        marker=dict(
            size=circuits_df['total_races'],
            sizemode='area',
            sizeref=2.*max(circuits_df['total_races'])/(35.**2),
            sizemin=4,
            color=COLOR_F1_RED,
            line=dict(width=1, color='#ffffff'),
            opacity=0.85
        ),
        hoverinfo='text'
    ))
    
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text=remove_hyphens(title), font=dict(family=FONT_FAMILY, size=15, color='#0f172a')),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            scope='world',
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor='#e2e8f0',
            showocean=True,
            oceancolor='#f1f5f9',
            showcountries=True,
            countrycolor='rgba(0,0,0,0.12)',
            coastlinecolor='rgba(0,0,0,0.18)',
            projection_type='equirectangular'
        ),
        margin=dict(t=40, r=0, b=0, l=0)
    )
    return fig

def create_radar_chart(categories, drivers_data, title="Head to Head Driver Telemetry", height=420):
    """Generate radar comparison chart for multiple drivers."""
    fig = go.Figure()
    palette = [COLOR_F1_RED, COLOR_F1_CYAN, COLOR_F1_GOLD, '#FF8000', '#00A896']
    
    clean_cats = [remove_hyphens(c) for c in categories]
    # Close the radar loop
    radar_cats = clean_cats + [clean_cats[0]]
    
    for idx, d in enumerate(drivers_data):
        vals = d['values'] + [d['values'][0]]
        c = palette[idx % len(palette)]
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_cats,
            fill='toself',
            name=remove_hyphens(d['name']),
            line=dict(color=c, width=2),
            fillcolor=f"rgba({int(c[1:3],16)}, {int(c[3:5],16)}, {int(c[5:7],16)}, 0.12)"
        ))
        
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text=remove_hyphens(title), font=dict(family=FONT_FAMILY, size=14, color='#0f172a')),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='#ffffff',
            radialaxis=dict(visible=True, range=[0, 100], linecolor='rgba(0,0,0,0.1)', tickfont=dict(color='#64748b')),
            angularaxis=dict(linecolor='rgba(0,0,0,0.12)', tickfont=dict(family=FONT_FAMILY, color='#0f172a'))
        ),
        margin=dict(t=50, r=40, b=40, l=40)
    )
    return fig
