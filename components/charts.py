"""
Plotly Chart Generators for F1 Historical Analytics.
Theme: Precision F1 Dark Motorsport Intelligence Workstation.
Strictly zero hyphens in any titles, axis labels, legends, or hover templates.
"""

import plotly.graph_objects as go
import plotly.express as px
from utils.constants import (
    FONT_FAMILY, FONT_DISPLAY, FONT_MONO, COLOR_BG_CARD, COLOR_F1_RED, COLOR_F1_GOLD, 
    COLOR_F1_CYAN, COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, PLOTLY_TEMPLATE
)
from utils.helpers import remove_hyphens

def apply_f1_theme(fig, title="", height=360):
    """Apply the F1 Dark Motorsport theme to any Plotly figure."""
    clean_title = remove_hyphens(title)
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title={
            'text': clean_title,
            'font': {'family': FONT_DISPLAY, 'size': 14, 'color': COLOR_TEXT_WHITE},
            'x': 0.02,
            'y': 0.96,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, color=COLOR_TEXT_WHITE),
        margin=dict(t=50, r=20, b=40, l=45),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#0E1013",
            font=dict(family=FONT_FAMILY, size=12, color='#FFFFFF'),
            bordercolor=COLOR_F1_RED
        )
    )
    fig.update_xaxes(
        gridcolor='rgba(255, 255, 255, 0.04)',
        linecolor='rgba(255, 255, 255, 0.12)',
        tickfont=dict(family=FONT_MONO, size=10, color=COLOR_TEXT_SECONDARY),
        showgrid=True,
        zeroline=False
    )
    fig.update_yaxes(
        gridcolor='rgba(255, 255, 255, 0.04)',
        linecolor='rgba(255, 255, 255, 0.12)',
        tickfont=dict(family=FONT_MONO, size=10, color=COLOR_TEXT_SECONDARY),
        showgrid=True,
        zeroline=False
    )
    return fig

def create_bar_chart(df, x, y, title="", color=COLOR_F1_RED, orientation='v', height=360):
    """Generate high precision motorsport bar chart."""
    fig = go.Figure()
    if orientation == 'h':
        # Clean categories
        y_vals = df[y].apply(remove_hyphens)
        fig.add_trace(go.Bar(
            y=y_vals,
            x=df[x],
            orientation='h',
            marker=dict(
                color=color,
                opacity=0.88,
                line=dict(color='rgba(255, 255, 255, 0.15)', width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Victories/Metric: <b>%{x:,}</b><extra></extra>"
        ))
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:
        x_vals = df[x].astype(str).apply(remove_hyphens)
        fig.add_trace(go.Bar(
            x=x_vals,
            y=df[y],
            marker=dict(
                color=color,
                opacity=0.88,
                line=dict(color='rgba(255, 255, 255, 0.15)', width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Value: <b>%{y:,}</b><extra></extra>"
        ))
    return apply_f1_theme(fig, title=title, height=height)

def create_line_chart(df, x, y, title="", color=COLOR_F1_RED, height=360):
    """Generate smooth telemetry line chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x].astype(str).apply(remove_hyphens),
        y=df[y],
        mode='lines+markers',
        line=dict(color=color, width=2.5, shape='spline'),
        marker=dict(size=6, color=color, line=dict(color='#08090A', width=1.5)),
        hovertemplate="Season %{x}<br>Recorded: <b>%{y}</b><extra></extra>"
    ))
    return apply_f1_theme(fig, title=title, height=height)

def create_multi_line_chart(df, x, y, group_col, title="", height=400):
    """Generate multi line chart with distinct motorsport contrast colors."""
    fig = go.Figure()
    palette = [COLOR_F1_RED, COLOR_F1_CYAN, COLOR_F1_GOLD, '#FF7300', '#10B981', '#8B5CF6', '#F43F5E']
    
    groups = df[group_col].unique()
    for idx, g in enumerate(groups):
        sub_df = df[df[group_col] == g]
        c = palette[idx % len(palette)]
        fig.add_trace(go.Scatter(
            x=sub_df[x].astype(str).apply(remove_hyphens),
            y=sub_df[y],
            mode='lines+markers',
            name=remove_hyphens(str(g)),
            line=dict(color=c, width=2.2),
            marker=dict(size=5, color=c, line=dict(color='#08090A', width=1)),
            hovertemplate=f"<b>{remove_hyphens(str(g))}</b><br>%{{x}}: <b>%{{y}}</b><extra></extra>"
        ))
    return apply_f1_theme(fig, title=title, height=height)

def create_scatter_plot(df, x, y, title="", hover_name=None, height=380):
    """Generate scatter plot for motorsport telemetry correlations (e.g. grid vs finish)."""
    fig = go.Figure()
    text_vals = df[hover_name].apply(remove_hyphens) if hover_name else None
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode='markers',
        marker=dict(
            size=8,
            color=COLOR_F1_RED,
            opacity=0.75,
            line=dict(width=1, color='rgba(255, 255, 255, 0.4)')
        ),
        text=text_vals,
        hovertemplate="<b>%{text}</b><br>Grid: P%{x}<br>Finish: P%{y}<extra></extra>" if hover_name else "Grid: P%{x}<br>Finish: P%{y}<extra></extra>"
    ))
    return apply_f1_theme(fig, title=title, height=height)

def create_global_map(circuits_df, title="Global Circuit Footprint", height=480):
    """Generate dark monochromatic world map showing all F1 circuit venues."""
    fig = go.Figure(go.Scattergeo(
        lat=circuits_df['lat'],
        lon=circuits_df['long'],
        text=circuits_df['name'].apply(remove_hyphens) + ' (' + circuits_df['country'].apply(remove_hyphens) + ')<br>Total Grands Prix: ' + circuits_df['total_races'].astype(str),
        marker=dict(
            size=circuits_df['total_races'],
            sizemode='area',
            sizeref=2.*max(circuits_df['total_races'])/(38.**2),
            sizemin=5,
            color=COLOR_F1_RED,
            line=dict(width=1, color='#FFFFFF'),
            opacity=0.88
        ),
        hovertemplate="<b>%{text}</b><extra></extra>"
    ))
    
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(
            text=remove_hyphens(title),
            font=dict(family=FONT_DISPLAY, size=15, color=COLOR_TEXT_WHITE),
            x=0.02,
            y=0.96
        ),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            scope='world',
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor='#14171C',
            showocean=True,
            oceancolor='#090B0D',
            showcountries=True,
            countrycolor='rgba(255, 255, 255, 0.08)',
            coastlinecolor='rgba(255, 255, 255, 0.12)',
            projection_type='equirectangular'
        ),
        margin=dict(t=40, r=0, b=0, l=0)
    )
    return fig

def create_radar_chart(categories, drivers_data, title="Head to Head Driver Telemetry", height=420):
    """Generate radar comparison chart for multiple drivers in dark telemetry styling."""
    fig = go.Figure()
    palette = [COLOR_F1_RED, COLOR_F1_CYAN, COLOR_F1_GOLD, '#FF7300', '#10B981']
    
    clean_cats = [remove_hyphens(c) for c in categories]
    radar_cats = clean_cats + [clean_cats[0]]
    
    for idx, d in enumerate(drivers_data):
        vals = d['values'] + [d['values'][0]]
        c = palette[idx % len(palette)]
        r_val, g_val, b_val = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_cats,
            fill='toself',
            name=remove_hyphens(d['name']),
            line=dict(color=c, width=2),
            fillcolor=f"rgba({r_val}, {g_val}, {b_val}, 0.15)",
            hovertemplate="<b>" + remove_hyphens(d['name']) + "</b><br>%{theta}: <b>%{r}</b><extra></extra>"
        ))
        
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(
            text=remove_hyphens(title),
            font=dict(family=FONT_DISPLAY, size=14, color=COLOR_TEXT_WHITE),
            x=0.02,
            y=0.96
        ),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='rgba(14, 16, 20, 0.7)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                linecolor='rgba(255, 255, 255, 0.08)',
                gridcolor='rgba(255, 255, 255, 0.06)',
                tickfont=dict(family=FONT_MONO, size=9, color=COLOR_TEXT_MUTED)
            ),
            angularaxis=dict(
                linecolor='rgba(255, 255, 255, 0.12)',
                gridcolor='rgba(255, 255, 255, 0.06)',
                tickfont=dict(family=FONT_DISPLAY, size=11, color=COLOR_TEXT_WHITE)
            )
        ),
        margin=dict(t=50, r=40, b=40, l=40)
    )
    return fig
