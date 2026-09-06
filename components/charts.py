"""
Plotly Chart Generators for F1 Historical Analytics.
Theme: Precision F1 Dark Motorsport Intelligence Workstation.
Strictly zero hyphens in any titles, axis labels, legends, or hover templates.
Includes explicit X and Y axis labeling across all telemetry charts.
"""

import plotly.graph_objects as go
import plotly.express as px
from utils.constants import (
    FONT_FAMILY, FONT_DISPLAY, FONT_MONO, COLOR_BG_CARD, COLOR_F1_RED, COLOR_F1_GOLD, 
    COLOR_F1_CYAN, COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, PLOTLY_TEMPLATE
)
from utils.helpers import remove_hyphens

def format_axis_title(col_name):
    """
    Format database column or metric name into an explicit, human readable axis title.
    Strictly zero hyphens.
    """
    if not col_name:
        return ""
    col_clean = str(col_name).strip().lower()
    
    mapping = {
        'wins': 'Grand Prix Victories',
        'driver': 'Driver',
        'name': 'Driver / Constructor Name',
        'constructor': 'Constructor Team',
        'season': 'Championship Season',
        'year': 'Championship Season',
        'total_races': 'Total Grands Prix Held',
        'races': 'Total Grands Prix',
        'points': 'Championship Points',
        'season_points': 'Season Championship Points',
        'total_sprint_points': 'Total Sprint Points',
        'sprint_wins': 'Sprint Victories',
        'poles': 'Total Pole Positions',
        'conversion_rate': 'Pole to Win Conversion Rate (%)',
        'grid': 'Starting Grid Position',
        'qual_pos': 'Qualifying Grid Position',
        'finish_pos': 'Official Race Finish Position',
        'position': 'Official Finish Position',
        'dnf_rate': 'Retirement / DNF Rate (%)',
        'dnfs': 'Mechanical Retirements',
        'total_stops': 'Total Recorded Pit Stops',
        'avg_duration_sec': 'Average Pit Stop Duration (Seconds)',
        'round': 'Championship Round',
        'starts': 'Career Race Starts',
        'podiums': 'Podium Finishes',
        'fastest_lap': 'Fastest Lap Time',
    }
    
    if col_clean in mapping:
        return mapping[col_clean]
    
    return remove_hyphens(str(col_name).replace('_', ' ').title())

def apply_f1_theme(fig, title="", height=360, x_title=None, y_title=None):
    """
    Apply the F1 Dark Motorsport theme to any Plotly figure with explicit X and Y axis labels.
    """
    clean_title = remove_hyphens(title)
    
    # Dynamically scale margins based on whether axes have titles
    bottom_margin = 64 if x_title else 42
    left_margin = 78 if y_title else 50
    
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        dragmode=False,
        title={
            'text': clean_title,
            'font': {'family': FONT_DISPLAY, 'size': 13.5, 'color': COLOR_TEXT_WHITE},
            'x': 0.02,
            'y': 0.96,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, color=COLOR_TEXT_WHITE),
        margin=dict(t=50, r=25, b=bottom_margin, l=left_margin),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#0E1013",
            font=dict(family=FONT_FAMILY, size=12, color='#FFFFFF'),
            bordercolor=COLOR_F1_RED
        )
    )
    
    xaxis_config = dict(
        gridcolor='rgba(255, 255, 255, 0.04)',
        linecolor='rgba(255, 255, 255, 0.12)',
        tickfont=dict(family=FONT_MONO, size=10, color=COLOR_TEXT_SECONDARY),
        showgrid=True,
        zeroline=False,
        fixedrange=True
    )
    if x_title:
        clean_x = remove_hyphens(str(x_title)).upper()
        xaxis_config['title'] = dict(
            text=clean_x,
            font=dict(family=FONT_DISPLAY, size=11, color=COLOR_TEXT_SECONDARY),
            standoff=12
        )
    fig.update_xaxes(**xaxis_config)
    
    yaxis_config = dict(
        gridcolor='rgba(255, 255, 255, 0.04)',
        linecolor='rgba(255, 255, 255, 0.12)',
        tickfont=dict(family=FONT_MONO, size=10, color=COLOR_TEXT_SECONDARY),
        showgrid=True,
        zeroline=False,
        fixedrange=True
    )
    if y_title:
        clean_y = remove_hyphens(str(y_title)).upper()
        yaxis_config['title'] = dict(
            text=clean_y,
            font=dict(family=FONT_DISPLAY, size=11, color=COLOR_TEXT_SECONDARY),
            standoff=14
        )
    fig.update_yaxes(**yaxis_config)
    
    return fig

def create_bar_chart(df, x, y, title="", color=COLOR_F1_RED, orientation='v', height=360, x_title=None, y_title=None):
    """
    Generate high precision motorsport bar chart with explicit X and Y axis labels.
    """
    fig = go.Figure()
    if orientation == 'h':
        # Clean categories
        y_vals = df[y].astype(str).apply(remove_hyphens)
        fig.add_trace(go.Bar(
            y=y_vals,
            x=df[x],
            orientation='h',
            marker=dict(
                color=color,
                opacity=0.88,
                line=dict(color='rgba(255, 255, 255, 0.15)', width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Value: <b>%{x:,}</b><extra></extra>"
        ))
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        computed_x_title = x_title or format_axis_title(x)
        computed_y_title = y_title or format_axis_title(y)
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
        computed_x_title = x_title or format_axis_title(x)
        computed_y_title = y_title or format_axis_title(y)
        
    return apply_f1_theme(fig, title=title, height=height, x_title=computed_x_title, y_title=computed_y_title)

def create_line_chart(df, x, y, title="", color=COLOR_F1_RED, height=360, x_title=None, y_title=None):
    """
    Generate smooth telemetry line chart with explicit X and Y axis labels.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x].astype(str).apply(remove_hyphens),
        y=df[y],
        mode='lines+markers',
        line=dict(color=color, width=2.5, shape='spline'),
        marker=dict(size=6, color=color, line=dict(color='#08090A', width=1.5)),
        hovertemplate="%{x}<br>Value: <b>%{y}</b><extra></extra>"
    ))
    computed_x_title = x_title or format_axis_title(x)
    computed_y_title = y_title or format_axis_title(y)
    return apply_f1_theme(fig, title=title, height=height, x_title=computed_x_title, y_title=computed_y_title)

def create_multi_line_chart(df, x, y, group_col, title="", height=400, x_title=None, y_title=None):
    """
    Generate multi line chart with distinct motorsport contrast colors and explicit X and Y axis labels.
    """
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
    computed_x_title = x_title or format_axis_title(x)
    computed_y_title = y_title or format_axis_title(y)
    return apply_f1_theme(fig, title=title, height=height, x_title=computed_x_title, y_title=computed_y_title)

def create_scatter_plot(df, x, y, title="", hover_name=None, height=380, x_title=None, y_title=None):
    """
    Generate scatter plot for motorsport telemetry correlations with explicit X and Y axis labels.
    """
    fig = go.Figure()
    text_vals = df[hover_name].apply(remove_hyphens) if hover_name and hover_name in df.columns else None
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
        hovertemplate="<b>%{text}</b><br>Grid: P%{x}<br>Finish: P%{y}<extra></extra>" if hover_name and hover_name in df.columns else "Grid: P%{x}<br>Finish: P%{y}<extra></extra>"
    ))
    computed_x_title = x_title or format_axis_title(x)
    computed_y_title = y_title or format_axis_title(y)
    return apply_f1_theme(fig, title=title, height=height, x_title=computed_x_title, y_title=computed_y_title)

def create_global_map(circuits_df, title="Global Circuit Footprint", height=480):
    """
    Generate dark monochromatic world map showing all F1 circuit venues with explicit coordinates notation.
    """
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
        annotations=[
            dict(
                text="X AXIS: LONGITUDE (°E / °W) • Y AXIS: LATITUDE (°N / °S)",
                xref="paper", yref="paper",
                x=0.02, y=0.02,
                showarrow=False,
                font=dict(family=FONT_DISPLAY, size=10, color=COLOR_TEXT_SECONDARY),
                bgcolor="rgba(14, 16, 20, 0.85)",
                bordercolor="rgba(255, 255, 255, 0.12)",
                borderwidth=1,
                borderpad=5
            )
        ],
        margin=dict(t=40, r=0, b=0, l=0)
    )
    return fig

def create_radar_chart(categories, drivers_data, title="Head to Head Driver Telemetry", height=420):
    """
    Generate radar comparison chart for multiple drivers with explicit polar axes notation.
    """
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
                tickfont=dict(family=FONT_MONO, size=9, color=COLOR_TEXT_MUTED),
                title=dict(
                    text="RATING (0 TO 100)",
                    font=dict(family=FONT_DISPLAY, size=10, color=COLOR_TEXT_SECONDARY)
                )
            ),
            angularaxis=dict(
                linecolor='rgba(255, 255, 255, 0.12)',
                gridcolor='rgba(255, 255, 255, 0.06)',
                tickfont=dict(family=FONT_DISPLAY, size=11, color=COLOR_TEXT_WHITE)
            )
        ),
        annotations=[
            dict(
                text="RADIAL AXIS: RATING SCALE (0 TO 100) • ANGULAR AXIS: PERFORMANCE ATTRIBUTES",
                xref="paper", yref="paper",
                x=0.02, y=0.02,
                showarrow=False,
                font=dict(family=FONT_DISPLAY, size=9.5, color=COLOR_TEXT_SECONDARY),
                bgcolor="rgba(14, 16, 20, 0.85)",
                bordercolor="rgba(255, 255, 255, 0.12)",
                borderwidth=1,
                borderpad=4
            )
        ],
        margin=dict(t=50, r=40, b=40, l=40)
    )
    return fig
