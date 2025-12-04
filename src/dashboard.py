from __future__ import annotations  # <--- MUST be the very first line of the file

import streamlit as st
import pandas as pd
import datetime
import numpy as np
import locale
from datetime import date
from metadata_manager import MetadataManager

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain') 
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

PRIMARY_TEXT_COLOR = "#0f172a"  
ACCENT_COLOR = '#577399'
BACKGROUND_COLOR = "#FAFAFA"    
SECONDARY_BACKGROUND = "#F4F7F9" 
SUBTITLE_COLOR = "#4B5563"      
DELTA_POSITIVE_COLOR = "#10B981" 
DELTA_NEGATIVE_COLOR = "#EF4444" 
GRID_COLOR = '#E5E7EB' # Usado para la cuadrícula y simular el borde sutil
TITLE_FONT = dict(size=11, color=PRIMARY_TEXT_COLOR, family='Segoe UI, sans-serif')
AXIS_FONT = dict(size=10, color=SUBTITLE_COLOR, family='Segoe UI, sans-serif')

st.set_page_config(
    page_title="GoMotion: Movilidad en Barcelona",
    page_icon="media/GoMotionShortLogo.ico",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    :root {
        --primary-color: #0f172a; /* primary color (buttons, selectboxes) */
        --background-color: #FAFAFA; /* background (main app) */
        --secondary-background-color: #F4F7F9; /* secondary background (components, sidebar) */
        --text-color: #0f172a; /* text color */
        --font: 'Segoe UI', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True
)

SECONDARY_BACKGROUND = "#F4F7F9" 
GRID_COLOR = '#E5E7EB' 

CARD_STYLE_CSS = f"""
    <style>
    /* Estilo para envolver el contenedor (st.container o columna) que contiene el gráfico.
    El selector apunta al div principal de un bloque vertical (como el generado por st.container() o st.column()).
    */
    div[data-testid="stVerticalBlock"] > div:has(.stPlotlyChart) > div:first-child {{
        background-color: {SECONDARY_BACKGROUND};
        border: 1px solid {GRID_COLOR}; 
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); 
        margin-bottom: 15px;
    }}
    </style>
"""
st.markdown(CARD_STYLE_CSS, unsafe_allow_html=True)

st.markdown(f"""
<style>
/* Hide Streamlit default elements */
#MainMenu, footer {{visibility: hidden;}}

/* General Layout & Background */
.stApp {{
    background-color: {BACKGROUND_COLOR};    st.markdown(f'<p class="subtitle">Movilidad en Barcelona</p>', unsafe_allow_html=True)

    color: {PRIMARY_TEXT_COLOR};
    padding-top: 2rem;
}}

/* Subtitle (Movilidad en Barcelona) - Dark Gray, Subtle */
.subtitle {{
    color: {SUBTITLE_COLOR}; 
    font-size: 1.3rem;
    font-weight: 400;
    margin-bottom: 30px;
    padding-left: 5px; /* Slight alignment adjustment */
}}

/* Section Header (Uppercase, small, clean) */
.section-header {{
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: {PRIMARY_TEXT_COLOR};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}}

/* KPI Metrics Styling (Clean, rounded, secondary background) */
[data-testid="stMetric"] {{
    background-color: {SECONDARY_BACKGROUND};
    border: 1px solid #E5E7EB; /* Very subtle light border */
    border-radius: 8px;
    padding: 15px 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03); /* Extremely light shadow */
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.9rem !important;
    color: {SUBTITLE_COLOR};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
[data-testid="stMetricValue"] {{
    font-size: 1.8rem !important;
    color: {PRIMARY_TEXT_COLOR}; /* Now the same color as the title */
    font-weight: 700;
}}

/* Clean Divider */
hr {{
    margin: 30px 0;
    border-color: #E5E7EB; 
}}

</style>
""", unsafe_allow_html=True)

def centered_image(path: str, width_ratio=50):
    """Centers the image using columns"""
    _, col, _ = st.columns([ (100-width_ratio)/2, width_ratio, (100-width_ratio)/2 ]) 
    
    with col:
        return st.image(path, use_container_width=True)

def capitalize_first_letter(s) -> str:
    """Given a string makes first letter capital letter"""
    if not isinstance(s, str) or s.strip() == "":
        return s
    return s[0].upper() + s[1:]

@st.cache_data
def update_predictions() -> None:
    #lazy imports to improve speed
    from data_filler import fill_data
    from meteo import ONE_WEEK

    manager = MetadataManager()
    last_date_str = str(manager.get("last_predicted_day"))
    print(type(last_date_str))
    print("STRING:", last_date_str)
    if last_date_str == "nan":
        fill_data(pd.read_csv('data/data_processed.csv'), pd.to_datetime(ONE_WEEK.strftime("%Y-%m-%d")))
    else:
        fill_data(pd.read_csv('data/data_extended.csv'), pd.to_datetime(ONE_WEEK.strftime("%Y-%m-%d")))
    manager.set("last_predicted_day", ONE_WEEK.strftime("%Y-%m-%d"))


@st.cache_data  
def load_df() -> pd.DataFrame:
    """Loads and returs data_extended DataFrame"""
    df = pd.read_csv('data/data_extended.csv')
    df['day'] = pd.to_datetime(df['day'])
    df['barri'] = df['barri'].apply(capitalize_first_letter)
    return df

@st.cache_data  
def load_event_df() -> pd.DataFrame:
    df = pd.read_csv('data/all_events.csv')
    df['day'] = pd.to_datetime(df['day'])
    df['barri'] = df['barri'].apply(capitalize_first_letter)
    return df

@st.cache_resource  
def load_geodata() -> tuple[nx.Graph, gpd.GeoDataFrame]:
    """Returns Graph and GeoDataFrame"""
    #lazy imports to improve speed
    import geopandas as gpd
    import networkx as nx
    import barri_manager as bm
    
    G = bm.create_graph()
    gdf = bm.load_gdf().rename(columns={"nom_barri": "barri"})
    gdf["barri"] = gdf["barri"].apply(capitalize_first_letter)
    if gdf.crs is None:
        try:
            gdf.set_crs("EPSG:25831", allow_override=True, inplace=True)
        except: pass 
    try:
        gdf = gdf.to_crs("EPSG:4326")
    except Exception: 
        pass
    return G, gdf

@st.cache_data
def compute_zscore_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Returns dataframe with columns barri, mean and std of intensities"""
    stats = df.groupby("barri")["intensity"].agg(['mean','std'])
    return stats

@st.cache_data
def avg_month_events(df_events: pd.DataFrame, max_date: date) -> float:
    """
    Filters events to the last 30 days, counts events per day, 
    and returns the mean of those daily counts.
    """
    
    max_date = pd.to_datetime(max_date)
    last_month = max_date - pd.Timedelta(days=30)

    df_last_month = df_events[
        (df_events['day'] >= last_month) & 
        (df_events['day'] <= max_date)
    ].copy()
    if df_last_month.empty:
        return 0.0
   
    daily_event_counts = df_last_month.groupby(df_last_month['day'].dt.date).size()
    average_daily_events = daily_event_counts.mean()
    
    return round(average_daily_events, 1)


@st.cache_data
def avg_month_temp(df: pd.DataFrame) -> float:
    """Returns average temp of last month"""
    
    df_daily_temps = df.groupby('day').agg(
        daily_max=('temperature_2m_max', 'mean'),
        daily_min=('temperature_2m_min', 'mean')
    ).reset_index()

    df_daily_temps['daily_mean_temp'] = (
        df_daily_temps['daily_max'] + df_daily_temps['daily_min']
    ) / 2

    return round(df_daily_temps['daily_mean_temp'].mean(), 1)

@st.cache_data
def avg_month_precipitation(df: pd.DataFrame) -> float:
    """Returns the average daily precipitation sum for the last 30 days."""
    
    df_daily_precip = df.groupby('day')['precipitation_sum'].mean().reset_index(name='daily_precip_sum')
    return round(df_daily_precip['daily_precip_sum'].mean(), 1)

def handle_map_selection() -> None: 
    """Saves the name of the barrio selected on the map to Session State."""

    selection_data = st.session_state.get('barri_heatmap_chart', {}).get('selection', {})
    if selection_data:
        if 'points' in selection_data and selection_data['points']:
            first_point = selection_data['points'][0]
            if 'hovertext' in first_point:
                barri_name = first_point['hovertext']
                st.session_state.selected_barri_from_map = barri_name

def plot_barri_heatmap(df_current_day: pd.DataFrame, stats: pd.DataFrame, gdf: gpd.GeoDataFrame):
    #lazy imports to improve speed
    import geopandas as gpd
    import plotly.express as px 
    
    
    df_day = df_current_day.merge(stats, on="barri", how="left")
    df_day['intensity'] = np.ceil(df_day['intensity']).astype(int)
    df_day["zscore"] = (df_day["intensity"] - df_day["mean"]) / df_day["std"]
    
    gdf_day = gdf.merge(df_day[["barri", "intensity", "zscore"]], on="barri", how="left")
    gdf_day["zscore"] = gdf_day["zscore"].fillna(0)
    gdf_day["intensity"] = gdf_day["intensity"].fillna(0)

    lat_center = 41.395
    lon_center = 2.17
    
    fig = px.choropleth_mapbox(
        gdf_day,
        geojson=gdf_day.geometry,     
        locations=df_day.index,     
        color="zscore",               
        color_continuous_scale="plasma", 
        range_color=[-2.5, 2.5],    
        mapbox_style="carto-positron", 
        opacity=0.75,  
        zoom=11.1,
        center={"lat": lat_center, "lon": lon_center},
        hover_name="barri",
        hover_data={"intensity": ":.0f", "zscore": False}
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(
            title="Intensidad",
            tickvals=[-2.5, 0, 2.5],
            ticktext=["Baja", "Media", "Alta"],
            lenmode="fraction", len=0.5,
            thickness=15, yanchor="middle", y=0.5,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            title_font=dict(color="#333", size=11),
            tickfont=dict(color="#555", size=9)
        )
    )
    return fig


def render_header() -> None:
    """Renders the main title and subtitle using the defined CSS classes."""
    st.image("media/GoMotionLogo.png", width=300)
    st.markdown(f'<p class="subtitle">Movilidad en Barcelona</p>', unsafe_allow_html=True)

def render_kpis(df_filtered: pd.DataFrame, df_prev_month: pd.DataFrame, df_events: pd.DataFrame, max_date: date) -> None:
    """Renders KPI cards with updated Daily Summary content in 5 columns"""
    
    target_date = st.session_state.selected_date
    target_date_pddatetime = pd.to_datetime(target_date)
    st.markdown('<div class="section-header">Resumen Diario</div>', unsafe_allow_html=True)

    traffic_today = int(df_filtered["intensity"].sum()) // 2
    daily_sums = df_prev_month.groupby('day')['intensity'].sum()
    daily_intensity_half = daily_sums // 2 
    traffic_mean = daily_intensity_half.mean()
    delta_traffic = (traffic_today - traffic_mean)
    delta_traffic_str = f"{(delta_traffic / traffic_mean) * 100:.1f}%"

    num_anomalies_today = len(df_events[df_events["day"] == target_date_pddatetime]["description"].unique())
    num_anomalies_prev = avg_month_events(df_events, max_date)
    delta_anomalies = num_anomalies_today - num_anomalies_prev
    delta_anomalies_str = f"{delta_anomalies:.1f}"
    
    is_holiday = (df_filtered.iloc[0] == 1).any()
    holiday_status = "Día Normal" if not is_holiday else "Festivo"

    temp_max_today = df_filtered["temperature_2m_max"].iloc[0]
    temp_min_today = df_filtered["temperature_2m_min"].iloc[0]

    avg_prev = avg_month_temp(df_prev_month)
    avg_target_date = (temp_max_today + temp_min_today) / 2
    delta_temp_str = f"{avg_target_date - avg_prev:.1f}°C"

    precip_today = df_filtered["precipitation_sum"].iloc[0]
    precip_prev = avg_month_precipitation(df_prev_month)
    delta_precip_str = f"{precip_today - precip_prev:+.0f} mm"

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Tráfico Total", traffic_today, delta=delta_traffic_str)

    with col2: 
        st.metric("Nº Anomalías", f"{num_anomalies_today} Eventos", delta=delta_anomalies_str)

    with col3: 
        st.markdown(f"""
        <div data-testid="stMetric" style="background-color: {SECONDARY_BACKGROUND}; border: 1px solid #E5E7EB; border-radius: 8px; padding: 13px 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
            <div data-testid="stMetricLabel" style="color: {SUBTITLE_COLOR}; text-transform: uppercase; font-size: 0.9rem;">DÍA FESTIVO</div>
            <div data-testid="stMetricValue" style="color: {PRIMARY_TEXT_COLOR}; font-size: 1.8rem; font-weight: 700;">
                {is_holiday}
            </div>
            <div style="font-size: 0.9rem; color: {SUBTITLE_COLOR}; padding-top: 5px; font-weight: 500;">
                {holiday_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4: 
        st.metric("Temp. Máx. / Mín.", f"{temp_max_today}°C / {temp_min_today}°C", delta=delta_temp_str) 

    with col5: 
        st.metric("Precipitación", f"{precip_today} mm", delta=delta_precip_str) 
        
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True) 
    with st.expander(f"Ver Detalles de Anomalías ({num_anomalies_today} Eventos)", expanded=False):
        if num_anomalies_today > 0:
            df_events_today = df_events[(df_events["day"] == target_date_pddatetime)]
            df_events_today = df_events_today[["category","description","barri","impact"]]
            df_events_today = df_events_today.rename(columns=str.capitalize)
            st.dataframe(
                df_events_today,
                hide_index=True
            )
        else:
            st.info("No se registraron anomalías para la fecha seleccionada.")

def render_map_ranking_section(df_day: pd.DataFrame, stats: pd.DataFrame, gdf: gpd.GeoDataFrame, min_date: date, max_date: date) -> None:
    """Renders heat map, date selector and ranking"""
    #lazy imports to improve speed
    import geopandas as gpd
    
    c_map, c_tab = st.columns([1.17, 1], gap="large")

    with c_map:
        st.markdown('<div class="section-header">Mapa de calor</div>', unsafe_allow_html=True)
        fig = plot_barri_heatmap(df_day, stats, gdf)
        st.plotly_chart(
                    fig,
                    use_container_width=True,
                    on_select=handle_map_selection, 
                    selection_mode="points",       
                    key="barri_heatmap_chart"
                )
    with c_tab:
        
        st.markdown('<div class="section-header">Seleccione fecha</div>', unsafe_allow_html=True)
        st.date_input(
            "Fecha",
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed",
            key="selected_date"  
        )
        st.markdown('<div class="section-header">Ranking por barrio</div>', unsafe_allow_html=True)
        if not df_day.empty:
            df_view = df_day.merge(stats, on="barri", how="left")
            df_view['Actual'] = np.ceil(df_view['intensity']).astype(int)
            df_view['Media'] = np.ceil(df_view['mean']).astype(int)
            
            df_view['Saturación'] = df_view['Actual'] / df_view['Media']
            df_view['Nivel Z'] = (df_view['Actual'] - df_view['Media']) / df_view['std']

            cols_final = df_view[['barri', 'Actual', 'Media', 'Saturación', 'Nivel Z']].sort_values('Actual', ascending=False)
            
            st.dataframe(
                cols_final.style.background_gradient(
                    subset=['Nivel Z'], cmap="plasma", vmin=-2.5, vmax=2.5
                ).format({
                    'Saturación': '{:.1%}', 
                    'Nivel Z': '{:.2f}'
                }),
                column_config={
                    "barri": "Barrio",
                    "Actual": st.column_config.NumberColumn("Tráfico", format="%d"),
                    "Media": "Media Hist.",
                    "Saturación": st.column_config.ProgressColumn(
                        "Saturación Relativa",
                        format="%.2f",
                        min_value=0,
                        max_value=2, 
                    ),
                    "Nivel Z": "Desviación"
                },
                hide_index=True,
                use_container_width=True,
                height=550
            )
        else:
            st.info("No hay datos disponibles para la fecha seleccionada.")



def wrap_chart_in_card(fig, title_text, height=300):
    """Configures the figure with a background and title and renders it inside the Streamlit container."""
    
    fig.update_layout(
        paper_bgcolor=SECONDARY_BACKGROUND, 
        plot_bgcolor=SECONDARY_BACKGROUND,
        title=dict(text=title_text, font=TITLE_FONT, x=0.01),
        margin=dict(t=50, b=20, l=20, r=20),
        height=height,
        autosize=True,
        template='plotly_white', 
        font=dict(family='Segoe UI, sans-serif')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def plot_barri_details(df_full: pd.DataFrame, df_events: pd.DataFrame) -> None:
    """Plots details about a given barri"""
    
    import pandas as pd
    import streamlit as st
    import plotly.express as px 
    import plotly.graph_objects as go
        
    barri_name = st.session_state.selected_barri_from_map
    
    df_barri = df_full[df_full['barri'] == barri_name].copy()
    df_events_barri = df_events[df_events["barri"] == barri_name].copy()
    st.markdown(f'<div class="section-header">ANÁLISIS DETALLADO: <span style="color:{PRIMARY_TEXT_COLOR};">{barri_name.upper()}</span></div>', unsafe_allow_html=True)
    
    # ----------------------------------------------------------------------
    # 1. Perfil Semanal (Bar Chart)
    # ----------------------------------------------------------------------
    df_barri['weekday_num'] = df_barri['day'].dt.weekday
    df_barri['day_of_the_week'] = df_barri['day'].dt.strftime('%A')
    weekly_stats = df_barri.groupby('weekday_num').agg({'intensity': 'mean', 'day_of_the_week': 'first'}).sort_index()
    dias_espanol = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    if len(weekly_stats) == 7: weekly_stats['day_of_the_week'] = dias_espanol

    fig_week = go.Figure(go.Bar(
        x=weekly_stats['day_of_the_week'], y=weekly_stats['intensity'], marker_color=ACCENT_COLOR, opacity=0.9,
        text=weekly_stats['intensity'].round(0), textposition='outside', hovertemplate='Día: %{x}<br>Intensidad Media: %{y:.0f}<extra></extra>'
    ))
    fig_week.update_layout(bargap=0.3, xaxis=dict(showgrid=False, title_text='', tickfont=AXIS_FONT),
                           yaxis=dict(title_text='INTENSIDAD MEDIA', showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 2. Evolución Mensual (Line Chart) -> CAMBIO DE COLOR A ROJO
    # ----------------------------------------------------------------------
    df_barri['month_name'] = df_barri['day'].dt.strftime('%B')
    df_barri['month_num'] = df_barri['day'].dt.month
    mon_stats = df_barri.groupby('month_num').agg({'intensity': 'mean', 'month_name': 'first'}).sort_index()
    
    fig_mon = go.Figure()
    fig_mon.add_trace(go.Scatter(x=mon_stats['month_name'], y=mon_stats['intensity'], mode='lines+markers',
        # Usamos DELTA_NEGATIVE_COLOR (Rojo) y ajustamos la opacidad del relleno
        line=dict(color=DELTA_NEGATIVE_COLOR, width=3, shape='spline'), 
        marker=dict(size=8, color=DELTA_NEGATIVE_COLOR, line=dict(width=2, color=SECONDARY_BACKGROUND)), 
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.1)', # Relleno rojo claro
        hovertemplate='Mes: %{x}<br>Intensidad Media: %{y:.0f}<extra></extra>'))
    fig_mon.update_layout(xaxis=dict(showgrid=False, title_text='', tickfont=AXIS_FONT), 
                          yaxis=dict(title_text='INTENSIDAD MEDIA', showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 3. Impacto Medio por Evento (Horizontal Bar Chart)
    # ----------------------------------------------------------------------
    cat_stats = pd.merge(left=df_events_barri, right=df_barri, on=['day', 'barri']).groupby('category')['intensity'].mean().reset_index().sort_values('intensity', ascending=True)
    
    fig_cat = go.Figure(go.Bar(x=cat_stats['intensity'], y=cat_stats['category'], orientation='h',
        marker=dict(color=cat_stats['intensity'], colorscale=[(0, SUBTITLE_COLOR), (1, ACCENT_COLOR)], line=dict(color=GRID_COLOR, width=1.5)), 
        opacity=0.9, hovertemplate='Categoría: %{y}<br>Intensidad Media: %{x:.0f}<extra></extra>'))
    fig_cat.update_layout(xaxis=dict(title_text='INTENSIDAD MEDIA', showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT),
                          yaxis=dict(title_text='', tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 4. Distribución: Festivo vs Laborable (Box Plot)
    # ----------------------------------------------------------------------
    fig_hol = px.box(df_barri, x='is_holiday', y='intensity', color='is_holiday',
        color_discrete_map={0.0: ACCENT_COLOR, 1.0: DELTA_POSITIVE_COLOR}, 
        labels={'is_holiday': 'Tipo de Día', 'intensity': 'Intensidad de Tráfico'}, hover_data={'is_holiday': False})
    fig_hol.update_traces(marker_size=5, line_width=1.5, selector=dict(type='box'))
    fig_hol.update_layout(showlegend=False, xaxis=dict(title_text='', tickvals=[0, 1], ticktext=['LABORABLE', 'FESTIVO'], 
        showgrid=False, tickfont=AXIS_FONT),
        yaxis=dict(title_text='INTENSIDAD DE TRÁFICO', showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 5. Correlación Lluvia / Tráfico (Scatter Plot)
    # ----------------------------------------------------------------------
    fig_rain = px.scatter(df_barri, x="precipitation_sum", y="intensity", trendline="ols", 
        trendline_color_override=DELTA_NEGATIVE_COLOR, opacity=0.6, color_discrete_sequence=[ACCENT_COLOR], 
        labels={"precipitation_sum": "Precipitación (mm)", "intensity": "Intensidad de Tráfico"},
        hover_data={"day": "|%Y-%m-%d", "precipitation_sum": ':.1f', "intensity": ':.0f'})
    fig_rain.update_traces(marker=dict(size=8, line=dict(width=1, color=SECONDARY_BACKGROUND)))
    fig_rain.update_layout(xaxis_title="PRECIPITACIÓN (MM)", yaxis_title="INTENSIDAD",
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT), 
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # Display Layout: FILA 1 (3 PLOTS) y FILA 2 (2 PLOTS)
    # ----------------------------------------------------------------------
    
    # FILA 1: 3 PLOTS (Ajustamos el tamaño de columna para 3 elementos)
    c1, c2, c3 = st.columns([1, 1, 1], gap="medium") # [1, 1, 1] asegura 3 columnas de igual ancho
    
    with c1: 
        st.markdown('<div class="kpi-plot-card-style">', unsafe_allow_html=True)
        with st.container():
            wrap_chart_in_card(fig_week, "PERFIL SEMANAL DE TRÁFICO")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2: 
        st.markdown('<div class="kpi-plot-card-style">', unsafe_allow_html=True)
        with st.container():
            wrap_chart_in_card(fig_mon, "EVOLUCIÓN MENSUAL DE TRÁFICO") 
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c3: 
        st.markdown('<div class="kpi-plot-card-style">', unsafe_allow_html=True)
        with st.container():
            wrap_chart_in_card(fig_cat, "IMPACTO MEDIO DE EVENTOS")
        st.markdown('</div>', unsafe_allow_html=True)


    # FILA 2: 2 PLOTS (Ajustamos el tamaño de columna para 2 elementos)
    c4, c5 = st.columns([1, 1], gap="medium")
    
    with c4: 
        st.markdown('<div class="kpi-plot-card-style">', unsafe_allow_html=True)
        with st.container():
            wrap_chart_in_card(fig_hol, "DISTRIBUCIÓN: LABORABLE VS FESTIVO")
        st.markdown('</div>', unsafe_allow_html=True)

    with c5: 
        st.markdown('<div class="kpi-plot-card-style">', unsafe_allow_html=True)
        with st.container():
            wrap_chart_in_card(fig_rain, "CORRELACIÓN PRECIPITACIÓN / INTENSIDAD")
        st.markdown('</div>', unsafe_allow_html=True)


def main() -> None:
    """Main function"""
    
    loading_logo = centered_image("media/GoMotionShortLogo.png", width_ratio=30)
    
    with st.spinner("Cargando..."):
        try:
            update_predictions()
        except:
            st.error("Error: No se han podido crear las predicciones.")
        
        try:
            df = load_df()
            G, gdf = load_geodata()
            stats = compute_zscore_stats(df)
        except FileNotFoundError:
            st.error("Error: Archivo de datos no encontrado.")
            st.stop()

        try:
            df_events = load_event_df()
        except FileNotFoundError:
            st.error("Error: Archivo de datos no encontrado.")
            st.stop()
            


    loading_logo.empty()
    render_header()

     
    min_date = df['day'].min().date()
    max_date = df['day'].max().date()
        
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = max_date 
    if "selected_barri_from_map" not in st.session_state:
        st.session_state.selected_barri_from_map = "El Raval" 
            
    selected_date = st.session_state.selected_date

    #df_barri['weekday_num'] = df_barri['day'].dt.weekday
    #df_barri['day_of_the_week'] = df_barri['day'].dt.strftime('%A')
    
    df_filtered = df[df['day'].dt.date == selected_date].copy()
    df_prev_month = df[(df['day'].dt.date >= (selected_date - datetime.timedelta(days=30))) & (df['day'].dt.date < selected_date)].copy()
    print(selected_date)
    print(df_prev_month.head())
    df_prev_month = df_prev_month[pd.to_datetime(df_prev_month['day']).dt.dayofweek == pd.to_datetime(selected_date).dayofweek]
    render_kpis(df_filtered, df_prev_month, df_events, max_date)
    render_map_ranking_section(df_filtered, stats, gdf, min_date, max_date)
    plot_barri_details(df, df_events)

if __name__ == "__main__":
    main()