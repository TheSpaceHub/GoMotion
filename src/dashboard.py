from __future__ import annotations

import streamlit as st
import pandas as pd
import datetime
import numpy as np
from datetime import date
from metadata_manager import MetadataManager
import database_connection as db
import sqlalchemy as sql
import os

TRANSLATIONS = {
    "es": {
        "title": "Movilidad en Barcelona",
        "daily_summary": "Resumen Diario",
        "total_traffic": "Tráfico Total",
        "anomalies": "Nº ANOMALÍAS",
        "events": "Eventos",
        "no_events": "No hay eventos",
        "holiday": "FESTIVO",
        "workday": "LABORABLE",
        "holiday_status_normal": "Día Normal",
        "holiday_status_fest": "Festivo",
        "temp_label": "Temp. Máx. / Mín.",
        "precip_label": "Precipitación",
        "i_label": "Intensidad",
        "heatmap": "Mapa de calor",
        "select_date": "Seleccione fecha",
        "ranking": "Ranking por barrio",
        "traffic": "Tráfico",
        "festive_day_label": "DÍA FESTIVO",
        "neighborhood": "Barrio",
        "peak": "Pico",
        "density": "Densidad",
        "deviation": "Desviación",
        "event_details": "Ver detalles de eventos",
        "no_events_for_today": "No se registraron eventos para la fecha seleccionada.",
        "neighborhood_ranking": "Ranking por barrio",
        "chart_weekly": "PERFIL SEMANAL DE TRÁFICO",
        "chart_monthly": "EVOLUCIÓN MENSUAL DE TRÁFICO",
        "chart_events": "IMPACTO MEDIO DE EVENTOS",
        "chart_rain": "CORRELACIÓN PRECIPITACIÓN / INTENSIDAD",
        "chart_holiday": "DISTRIBUCIÓN: LABORABLE VS FESTIVO",
        "chart_i_s": "INTENSIDAD / SUPERFICIE (TODOS LOS BARRIOS)",
        "weekdays": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        "months": ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
               'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        "intensity_axis": "INTENSIDAD MEDIA",
        "detailed_analysis": "ANÁLISIS DETALLADO",
        "model_analysis": "ANÁLISIS DEL MODELO",
        "shap_importance": "IMPORTANCIAS DE LAS CARACTERISTICAS SHAP",
        "model_precision": 'PRECISIÓN DEL MODELO',
        "peak_ok": 'Pico Acertado',
        "peak_under": 'Subestimación',
        "peak_over": "Sobrestimación",
        "all_stats": "ESTADÍSTICAS DE TODOS LOS BARRIOS",
        "dotw_i_excess": "EXCESO DE INTENSIDAD POR DÍA DE LA SEMANA",
        "month_i_excess": "EXCESO DE INTENSIDAD MENSUAL",
        "i_excess": "Exceso de Intensidad",
        "traffic_i": "Intensidad de Tráfico",
        "surface": "Superficie",
        "day": "Día",
        "month": "Mes",
    },
    "en": {
        "title": "Mobility in Barcelona",
        "daily_summary": "Daily Summary",
        "total_traffic": "Total Traffic",
        "anomalies": "NO. OF ANOMALIES",
        "events": "Events",
        "no_events": "No events",
        "holiday": "HOLIDAY",
        "workday": "WORKDAY",
        "neighborhood": "Neighborhood",
        "holiday_status_normal": "Regular Day",
        "holiday_status_fest": "Holiday",
        "temp_label": "Max / Min Temp.",
        "precip_label": "Precipitation",
        "i_label": "Intensity",
        "heatmap": "Heatmap",
        "select_date": "Select Date",
        "ranking": "Neighborhood Ranking",
        "traffic": "Traffic",
        "festive_day_label": "HOLIDAY",
        "peak": "Peak",
        "density": "Density",
        "deviation": "Deviation",
        "event_details": "See event details",
        "no_events_for_today": "No recorded events for the selected day.",
        "neighborhood_ranking": "Neighborhood ranking",
        "chart_weekly": "WEEKLY TRAFFIC PROFILE",
        "chart_monthly": "MONTHLY TRAFFIC EVOLUTION",
        "chart_events": "AVG EVENT IMPACT",
        "chart_rain": "CORRELATION RAIN / INTENSITY",
        "chart_holiday": "DISTRIBUTION: WORKDAY VS HOLIDAY",
        "chart_i_s": "INTENSITY / SURFACE AREA",
        "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "months": ['January', 'February', 'March', 'Aprli', 'May', 'June', 'July',
               'August', 'September', 'October', 'November', 'December'],
        "intensity_axis": "AVG INTENSITY",
        "detailed_analysis": "DETAILED ANALYSIS",
        "model_analysis": "MODEL ANALYSIS",
        "shap_importance": "SHAP FEATURE IMPORTANCE",
        "model_precision": 'MODEL PRECISION',
        "peak_ok": 'Predicted peak',
        "peak_under": 'Underestimation',
        "peak_over": "Overestimation",
        "all_stats": "STATISTICS FOR ALL NEIGHBORHOODS",
        "dotw_i_excess": "INTENSITY EXCESS BY DAY OF THE WEEK",
        "month_i_excess": "INTENSITY EXCESS BY MONTH",
        "i_excess": "Intensity Excess",
        "traffic_i": "Traffic Intensity",
        "surface": "Surface",
        "day": "Day",
        "month": "Month",
    }
}

lang_code = "es"

def t(key: str) -> str:
    '''Returns the translated key for the selected language'''
    return TRANSLATIONS[lang_code][key]

# Declare useful color palette and fonts
PRIMARY_TEXT_COLOR = "#0f172a"  
ACCENT_COLOR = '#577399'
BACKGROUND_COLOR = "#FAFAFA"    
SECONDARY_BACKGROUND = "#F4F7F9" 
SUBTITLE_COLOR = "#4B5563"      
DELTA_POSITIVE_COLOR = "#10B981" 
DELTA_NEGATIVE_COLOR = "#EF4444" 
GRID_COLOR = '#E5E7EB' 
TITLE_FONT = dict(size=11, color=PRIMARY_TEXT_COLOR, family='Segoe UI, sans-serif')
AXIS_FONT = dict(size=10, color=SUBTITLE_COLOR, family='Segoe UI, sans-serif')

#Supabase bucket client set up
@st.cache_resource
def get_supabase_client():
    import supabase
    url = os.getenv('SUPABASE_URL')
    key = os.getenv("SUPABASE_KEY")
    return supabase.create_client(url, key)

#Streamlit config
st.set_page_config(
    page_title="GoMotion",
    page_icon=get_supabase_client().storage.from_("images").get_public_url("GoMotionShortLogo.ico"),
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Markdown to personalize web page 
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
    div[data-testid="stSelectbox"] input {
    caret-color: transparent;
    cursor: pointer;
}
    </style>
    """, unsafe_allow_html=True
)

CARD_STYLE_CSS = f"""
    <style>
    /* Estilo para envolver el contenedor que contiene el gráfico */
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
/*# MainMenu, footer {{visibility: hidden;}}*/"""+
""".block-container {
            /*padding-bottom: 0rem !important;*/
            /*margin-top: 0rem !important;*/
        }"""+

f"""/* General Layout & Background */
.stApp {{
    background-color: {BACKGROUND_COLOR};   

    color: {PRIMARY_TEXT_COLOR};
    padding-top: 2rem;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    min-width: 80px !important;
    max-width: 100px !important;
}}

/* Subtitle */
.subtitle {{
    color: {SUBTITLE_COLOR}; 
    font-size: 1.3rem;
    font-weight: 400;
    margin-bottom: 30px;
}}

/* Section Header */
.section-header {{
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: {PRIMARY_TEXT_COLOR};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}}

/* KPI Metrics Styling */
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

def centered_image(name: str, width_ratio=50):
    """Centers the image using columns"""
    supabase = get_supabase_client()
    
    _, col, _ = st.columns([ (100-width_ratio)/2, width_ratio, (100-width_ratio)/2 ]) 
    
    with col:
        return st.image(supabase.storage.from_("images").get_public_url(name),  width="stretch")

def capitalize_first_letter(s) -> str:
    """Given a string makes first letter capital letter"""
    if not isinstance(s, str) or s.strip() == "":
        return s
    return s[0].upper() + s[1:]

@st.cache_resource
def get_db_engine() -> sql.Engine:
    engine = db.connect_to_db()
    return engine


@st.cache_data  
def load_df(_engine: sql.Engine) -> pd.DataFrame:
    """Loads the DataFrame with the relevant data from the database.

    Args:
        engine (sql.Engine): Engine object referencing the database.

    Returns:
        pd.DataFrame: DataFrame with useful data.
    """
    df = pd.read_sql("display_data", con=_engine)
    df['day'] = pd.to_datetime(df['day'])
    df['barri'] = df['barri'].apply(capitalize_first_letter)
    return df

@st.cache_data  
def load_event_df(_engine: sql.Engine) -> pd.DataFrame:
    """Loads all events from the database.

    Args:
        engine (sql.Engine): Engine object referencing the database.

    Returns:
        pd.DataFrame: DataFrame containing event information.
    """
    df = pd.read_sql('events', con=_engine)
    df['day'] = pd.to_datetime(df['day'])
    df['barri'] = df['barri'].apply(capitalize_first_letter)
    return df

@st.cache_resource  
def load_geodata(_engine: sql.Engine) -> gpd.GeoDataFrame:
    """Returns Graph of barris and GeoDataFrame storing barris geodata"""    
    import shapely
    import geopandas as gpd
    gdf = pd.read_sql("geospatial_data", con=_engine).rename(columns={"nom_barri": "barri"})
    gdf["barri"] = gdf["barri"].apply(capitalize_first_letter)
    gdf['geometria_wgs84'] = gdf['geometria_wgs84'].apply(shapely.wkt.loads)
    gdf = gpd.GeoDataFrame(
        gdf, 
        geometry='geometria_wgs84', 
        crs="EPSG:4326"
    )
    return gdf

@st.cache_data
def load_importances(_engine: sql.Engine) -> tuple:
    i_and_f_df = pd.read_sql("importances_and_features", con=_engine)
    importances = list(i_and_f_df["importances"])
    features = list(i_and_f_df["features"])
    return (importances, features)

@st.cache_data
def compute_zscore_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Returns dataframe with columns: barri, mean and std of intensities"""
    stats = df.groupby("barri")["intensity"].agg(['mean','std'])
    return stats

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

    return round(df_daily_temps['daily_mean_temp'].mean(), 3)

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

def barri_heatmap(df_current_day: pd.DataFrame, stats: pd.DataFrame, gdf: gpd.GeoDataFrame) -> plotly.graph_objects.Figure:
    """Computes and returns heatmap as a plotly figure"""
    #lazy imports to improve speed
    import plotly.express as px 
    
    df_day = df_current_day.merge(stats, on="barri", how="left")
    df_day['intensity'] = np.ceil(df_day['intensity']).astype(int)
    df_day["zscore"] = (df_day["intensity"] - df_day["mean"]) / df_day["std"]
    
    gdf_day = gdf.merge(df_day[["barri", "intensity", "zscore"]], on="barri", how="left")
    gdf_day["zscore"] = gdf_day["zscore"].fillna(0)
    gdf_day["intensity"] = gdf_day["intensity"].fillna(0)

    lat_center = 41.395
    lon_center = 2.17
    
    fig = px.choropleth_map(
        gdf_day,
        geojson=gdf_day.geometry,     
        locations=df_day.index,     
        color="zscore",               
        color_continuous_scale="plasma", 
        range_color=[-2.5, 2.5],    
        map_style="carto-positron", 
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
    """Renders main title and subtitle using the defined CSS classes"""
    supabase = get_supabase_client()
    
    col_header, col_lang = st.columns([7, 1])
    with col_lang:
        lang_selection = st.selectbox(
                "Language", 
                ["Español", "English"], 
                index=0, 
                label_visibility="collapsed"
            )
        lang_code = "es" if lang_selection == "Español" else "en"
    with col_header:
        st.image(supabase.storage.from_("images").get_public_url("GoMotionLogo.png"), width=250)
        st.markdown(f'<p class="subtitle">{TRANSLATIONS[lang_code]["title"]}</p>', unsafe_allow_html=True)
    return lang_code

def render_kpis(df_filtered: pd.DataFrame, df_prev_month: pd.DataFrame, df_events: pd.DataFrame) -> None:
    """Computes and renders KPI cards with updated Daily Summary content in 5 columns"""
    
    target_date = st.session_state.selected_date
    target_date_pddatetime = pd.to_datetime(target_date)
    st.markdown(f'<div class="section-header">{t("daily_summary")}</div>', unsafe_allow_html=True)

    traffic_today = int(df_filtered["intensity"].sum()) // 2
    daily_sums = df_prev_month.groupby('day')['intensity'].sum()
    daily_intensity_half = daily_sums // 2 
    traffic_mean = daily_intensity_half.mean()
    delta_traffic = (traffic_today - traffic_mean)
    delta_traffic_str = f"{(delta_traffic / traffic_mean) * 100:.1f}%"

    num_events = len(df_events[df_events["day"] == target_date_pddatetime]["description"].unique())
    category = t("no_events") if num_events == 0 else df_events[df_events['day'].dt.date == target_date]['category'].iloc[0]
    
    is_holiday = (df_filtered["is_holiday"].iloc[0] == 1)
    holiday_status = t("holiday_status_normal") if not is_holiday else t("holiday_status_fest")

    temp_max_today = df_filtered["temperature_2m_max"].iloc[0]
    temp_min_today = df_filtered["temperature_2m_min"].iloc[0]

    avg_prev = avg_month_temp(df_prev_month)
    avg_target_date = (temp_max_today + temp_min_today) / 2
    delta_temp_str = f"{avg_target_date - avg_prev:.1f}°C"

    precip_today = df_filtered["precipitation_sum"].iloc[0]
    precip_avg_prev = avg_month_precipitation(df_prev_month)
    delta_precip_str = f"{precip_today - precip_avg_prev:+.2f} mm"

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(t("total_traffic"), traffic_today, delta=delta_traffic_str)

    with col2: 
        st.markdown(f"""
        <div data-testid="stMetric" style="background-color: {SECONDARY_BACKGROUND}; border: 1px solid #E5E7EB; border-radius: 8px; padding: 13px 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
            <div data-testid="stMetricLabel" style="color: {SUBTITLE_COLOR}; text-transform: uppercase; font-size: 0.9rem;">{t("anomalies")}</div>
            <div data-testid="stMetricValue" style="color: {PRIMARY_TEXT_COLOR}; font-size: 1.8rem; font-weight: 700;">
                {num_events} {t("events")}
            </div>
            <div style="font-size: 0.9rem; color: {SUBTITLE_COLOR}; padding-top: 5px; font-weight: 500;">
                {category}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3: 
        st.markdown(f"""
        <div data-testid="stMetric" style="background-color: {SECONDARY_BACKGROUND}; border: 1px solid #E5E7EB; border-radius: 8px; padding: 13px 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
            <div data-testid="stMetricLabel" style="color: {SUBTITLE_COLOR}; text-transform: uppercase; font-size: 0.9rem;">{t("festive_day_label")}</div>
            <div data-testid="stMetricValue" style="color: {PRIMARY_TEXT_COLOR}; font-size: 1.8rem; font-weight: 700;">
                {is_holiday}
            </div>
            <div style="font-size: 0.9rem; color: {SUBTITLE_COLOR}; padding-top: 5px; font-weight: 500;">
                {holiday_status}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4: 
        st.metric(t("temp_label"), f"{temp_max_today}°C / {temp_min_today}°C", delta=delta_temp_str) 

    with col5: 
        st.metric(t("precip_label"), f"{precip_today} mm", delta=delta_precip_str) 
        
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True) 
    with st.expander(t("event_details"), expanded=False):
        if num_events > 0:
            df_events_today = df_events[(df_events["day"] == target_date_pddatetime)]
            df_events_today = df_events_today[["category","description","barri","impact"]]
            df_events_today = df_events_today.rename(columns=str.capitalize)
            st.dataframe(
                df_events_today,
                hide_index=True
            )
        else:
            st.info(t("no_events_for_today"))

def render_map_ranking_section(df_day: pd.DataFrame, stats: pd.DataFrame, gdf: gpd.GeoDataFrame, min_date: date, max_date: date) -> None:
    """Renders heat map, date selector and ranking"""
    #lazy imports to improve speed
    import peak_classifier
    
    c_map, c_tab = st.columns([1.17, 1], gap="large")
    
    gdf_superf = gdf[['barri','superficie','codi_districte']]
    df_day = df_day.merge(gdf_superf, on='barri', how='left')
    
    with c_map: #Heatmap 
        st.markdown(f'<div class="section-header">{t("heatmap")}</div>', unsafe_allow_html=True)
        fig = barri_heatmap(df_day, stats, gdf)
        st.plotly_chart(
                    fig,
                    width="stretch",
                    on_select=handle_map_selection, 
                    selection_mode="points",       
                    key="barri_heatmap_chart"
                )
    with c_tab: # Date selector and ranking
        
        st.markdown(f'<div class="section-header">{t("select_date")}</div>', unsafe_allow_html=True)   #Date selector
        st.date_input(
            "Fecha",
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed",
            key="selected_date"  
        )
        st.markdown(f'<div class="section-header">{t("neighborhood_ranking")}</div>', unsafe_allow_html=True) #Ranking
        if not df_day.empty:
            df_view = df_day.merge(stats, on="barri", how="left")
            df_view['Actual'] = np.ceil(df_view['intensity']).astype(int)
            df_view['Media'] = np.ceil(df_view['mean']).astype(int)
            
            df_view['Nivel Z'] = (df_view['Actual'] - df_view['Media']) / df_view['std']
            df_view['Pico'] = peak_classifier.classify_peaks(df_view["Nivel Z"])
            
            df_view['Densidad'] = (df_view['Actual'] / df_view['superficie']).fillna(0).astype(int)
            
            cols_final = df_view[['barri', 'Actual', 'Media', 'Densidad', 'Nivel Z', 'Pico']].sort_values('Actual', ascending=False)
            
            st.dataframe(
                cols_final.style.background_gradient(
                    subset=['Nivel Z'], cmap="plasma", vmin=-2.5, vmax=2.5
                ).format({
                    'Nivel Z': '{:.2f}'
                }),
                column_config={
                    "barri": t("neighborhood"),
                    "Actual": st.column_config.NumberColumn(t("traffic"), format="%d"),
                    "Media": "Media Hist.",
                    "Pico": st.column_config.TextColumn(t("peak"), width=150),
                    "Densidad": t("density"),
                    "Nivel Z": t("deviation")
                    
                },
                hide_index=True,
                width="stretch",
                height=550
            )
        else:
            st.info("No hay datos disponibles para la fecha seleccionada.")

def wrap_chart_in_card(fig: plotly.graph_objects.Figure, title_text: str, height: int = 300) -> None:
    """Plots plotly figure in a container"""
    
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
    
    st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

def plot_barri_details(df_full: pd.DataFrame, df_events: pd.DataFrame, df_filtered: pd.DataFrame, gdf: gpd.GeoDataFrame) -> None:
    """Plots details about a given selected barri"""
    
    import plotly.express as px 
    import plotly.graph_objects as go
    
    barri_name = st.session_state.selected_barri_from_map
    
    gdf = gdf[['barri','superficie','codi_districte']]
    df_filtered = df_filtered.merge(gdf, on='barri', how='left')
    df_filtered['is_selected'] = df_filtered['barri'] == barri_name
    
    
    df_barri = df_full[df_full['barri'] == barri_name].copy()
    df_events_barri = df_events[df_events["barri"] == barri_name].copy()

    # ----------------------------------------------------------------------
    # 1. Perfil Semanal (Bar Chart)
    # ----------------------------------------------------------------------
    df_barri['weekday_num'] = df_barri['day'].dt.weekday
    df_barri['day_of_the_week'] = df_barri['day'].dt.strftime('%A')
    weekly_stats = df_barri.groupby('weekday_num').agg({'intensity': 'mean', 'day_of_the_week': 'first'}).sort_index()
    dias_espanol = t("weekdays")
    if len(weekly_stats) == 7: weekly_stats['day_of_the_week'] = dias_espanol

    fig_week = go.Figure(go.Bar(
        x=weekly_stats['day_of_the_week'], y=weekly_stats['intensity'], marker_color=ACCENT_COLOR, opacity=0.9,
        text=weekly_stats['intensity'].round(0), textposition='outside', hovertemplate='Día: %{x}<br>Intensidad Media: %{y:.0f}<extra></extra>'
    ))
    fig_week.update_layout(bargap=0.3, xaxis=dict(showgrid=False, title_text='', tickfont=AXIS_FONT),
                           yaxis=dict(title_text=t("intensity_axis"), showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 2. Evolución Mensual (Line Chart) -> CAMBIO DE COLOR A ROJO
    # ----------------------------------------------------------------------
    df_barri['month_name'] = df_barri['day'].dt.strftime('%B')
    df_barri['month_num'] = df_barri['day'].dt.month
    mon_stats = df_barri.groupby('month_num').agg({'intensity': 'mean', 'month_name': 'first'}).sort_index()
    
    fig_mon = go.Figure()
    fig_mon.add_trace(go.Scatter(x=mon_stats['month_name'], y=mon_stats['intensity'], mode='lines+markers',
        line=dict(color=DELTA_NEGATIVE_COLOR, width=3, shape='spline'), 
        marker=dict(size=8, color=DELTA_NEGATIVE_COLOR, line=dict(width=2, color=SECONDARY_BACKGROUND)), 
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.1)', # Relleno rojo claro
        hovertemplate='Mes: %{x}<br>Intensidad Media: %{y:.0f}<extra></extra>'))
    fig_mon.update_layout(xaxis=dict(showgrid=False, title_text='', tickfont=AXIS_FONT), 
                          yaxis=dict(title_text=t("intensity_axis"), showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 3. Impacto Medio por Evento (Horizontal Bar Chart)
    # ----------------------------------------------------------------------
    cat_stats = pd.merge(left=df_events_barri, right=df_barri, on=['day', 'barri']).groupby('category')['intensity'].mean().reset_index().sort_values('intensity', ascending=True)
    
    fig_cat = go.Figure(go.Bar(x=cat_stats['intensity'], y=cat_stats['category'], orientation='h',
        marker=dict(color=cat_stats['intensity'], colorscale=[(0, SUBTITLE_COLOR), (1, ACCENT_COLOR)], line=dict(color=GRID_COLOR, width=1.5)), 
        opacity=0.9, hovertemplate='Categoría: %{y}<br>Intensidad Media: %{x:.0f}<extra></extra>'))
    fig_cat.update_layout(xaxis=dict(title_text=t("intensity_axis"), showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT),
                          yaxis=dict(title_text='', tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 4. Distribución: Festivo vs Laborable (Box Plot)
    # ----------------------------------------------------------------------
    fig_hol = px.box(df_barri, x='is_holiday', y='intensity', color='is_holiday',
        color_discrete_map={0.0: ACCENT_COLOR, 1.0: DELTA_NEGATIVE_COLOR}, 
        labels={'is_holiday': 'Tipo de Día', 'intensity': t("traffic_i")}, hover_data={'is_holiday': False})
    fig_hol.update_traces(marker_size=5, line_width=1.5, selector=dict(type='box'))
    fig_hol.update_layout(showlegend=False, xaxis=dict(title_text='', tickvals=[0, 1], ticktext=[t("workday"), t("holiday")], 
        showgrid=False, tickfont=AXIS_FONT),
        yaxis=dict(title_text=t("traffic_i").upper(), showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 5. Correlación Lluvia / Tráfico (Scatter Plot)
    # ----------------------------------------------------------------------
    fig_rain = px.scatter(df_barri, x="precipitation_sum", y="intensity", trendline="ols",
        trendline_color_override=DELTA_NEGATIVE_COLOR, opacity=0.6, color_discrete_sequence=[ACCENT_COLOR], 
        labels={"precipitation_sum": f"{t("precip_label")} (mm)", "intensity": t("traffic_i")},
        hover_data={"day": "|%Y-%m-%d", "precipitation_sum": ':.1f', "intensity": ':.0f'})
    fig_rain.update_traces(marker=dict(size=8, line=dict(width=1, color=SECONDARY_BACKGROUND)))
    fig_rain.update_layout(xaxis_title=f"{t("precip_label").upper()} (MM)", yaxis_title=t("i_label").upper(),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT), 
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT))

    # ----------------------------------------------------------------------
    # 6. Tráfico / superficie
    # ----------------------------------------------------------------------
    # Get the selected day from the global session state

    fig_superf = px.scatter(df_filtered, x="superficie", y="intensity", trendline="ols", hover_name="barri",
        trendline_color_override=DELTA_NEGATIVE_COLOR, opacity=0.6, color_discrete_sequence=[ACCENT_COLOR], 
        labels={"superficie": "Superficie (km^2)", "intensity": "Tráfico"},
        hover_data={"superficie": ':.1f', "intensity": ':.0f'}, color='is_selected', 
        color_discrete_map={
        True: 'red',
        False: ACCENT_COLOR
        },)
    fig_superf.update_traces(marker=dict(size=8, line=dict(width=1, color=SECONDARY_BACKGROUND)))
    fig_superf.update_layout(xaxis_title=f"{t("surface").upper()} (KM^2)", yaxis_title=t("i_label").upper(),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT), 
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, tickfont=AXIS_FONT), showlegend=False)
    
    st.markdown(f'<div class="section-header">{t("detailed_analysis")}: <span style="color:{PRIMARY_TEXT_COLOR};">{barri_name.upper()}</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small") 

    with c1: 
        wrap_chart_in_card(fig_week, t("chart_weekly"))
    
    with c2: 
        wrap_chart_in_card(fig_mon, t("chart_monthly")) 
    
    with c3: 
        wrap_chart_in_card(fig_cat, t("chart_events"))

    c4, c5, c6 = st.columns(3, gap="small")
    
    with c4: 
        wrap_chart_in_card(fig_rain, t("chart_rain"))

    with c5: 
        wrap_chart_in_card(fig_hol, t("chart_holiday"))

    with c6:
        wrap_chart_in_card(fig_superf, t("chart_i_s"))
        
def plot_model_analysis(importances_and_features: tuple, engine: sql.Engine) -> None:
    """Plots feature importances and model details"""
    import plotly.graph_objects as go
    import plotly.express as px
    
    st.markdown(f'<div class="section-header">{t("model_analysis")}<span style="color:{PRIMARY_TEXT_COLOR};"></span></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1], gap="small")   
    
    importances, features = importances_and_features
    
    event_encoding_features = {"enc1", "enc2", "enc3", "enc4", "enc5"}
    encoding_indices = [i for (i, x) in enumerate(features) if x in event_encoding_features]
    
    event_importance = sum([importances[i] for i in encoding_indices])
    importances = [importances[i] for i in range(len(importances)) if i not in encoding_indices] + [event_importance]
    features = [features[i] for i in range(len(features)) if i not in encoding_indices] + ["events"]
    
    # Feature importances
    fig_importances = go.Figure(go.Bar(
        x=importances[::-1],
        y=features[::-1],
        orientation='h',
        marker=dict(
            color=importances[::-1],
            colorscale="Viridis",
            line=dict(color='lightgrey', width=1.5)
        ),
        opacity=0.9
    ))
 
    
    manager = MetadataManager(engine)
    
    accuracy = manager.get("model_accuracy") 
    under_estimated = manager.get("model_error_under")
    over_estimated = manager.get("model_error_over")
    
    # Model precisions
    fig_precision =  px.pie(values = [float(accuracy), float(under_estimated), float(over_estimated)],
            names = [t("peak_ok"), t("peak_under"), t("peak_over") ], color = [t("peak_ok"), t("peak_under"), t("peak_over") ] ,color_discrete_map= {t("peak_ok") : "#ffd127", t("peak_under"):"#69298f", t("peak_over"):"#ffa900"})
    
    fig_precision.update_layout(
        paper_bgcolor=SECONDARY_BACKGROUND, 
        plot_bgcolor=SECONDARY_BACKGROUND,
        title=dict(text=t("model_precision"), font=TITLE_FONT, x=0.01),
        height=400,
        autosize=True,
        template='plotly_white', 
        font=dict(family='Segoe UI, sans-serif'),
        margin=dict(t=50, b=20, l=20, r=200), 
        legend=dict(
            xanchor='left',
            yanchor="top",
            font=dict(size=14) 
            )
        )
    
    with c1:    # Feature importances plot
        wrap_chart_in_card(fig_importances, t("shap_importance"), height=400)
    with c2:    # Model presicion plot
        st.plotly_chart(fig_precision, width="stretch", config={'displayModeBar': False})

@st.cache_data
def plot_stats(df: pd.DataFrame) -> None:
    """Plots general stats for all barris"""
    from stats import statistics_day_of_the_week, statistics_month
    import plotly.tools as tls
    
    fig_week = statistics_day_of_the_week.by_day_cat_analysis(df, t)
    fig_month, _ = statistics_month.by_month_analysis(df, t)
    
    c1, c2 = st.columns([1, 1], gap="small") 
    
    with c1: 
        wrap_chart_in_card(fig_week, t("dotw_i_excess"))
    with c2: 
        wrap_chart_in_card(fig_month, t("month_i_excess")) 


def main() -> None:
    """Main function"""
    loader_placeholder = st.empty()
    with loader_placeholder.container():
        centered_image("GoMotionShortLogo.png", width_ratio=30)
    
    with st.spinner("Cargando..."):
        
        engine = get_db_engine()
        
        try:
            df = load_df(engine)
            gdf = load_geodata(engine)
            importances_and_features = load_importances(engine)
            stats = compute_zscore_stats(df)
            df_events = load_event_df(engine)
        except Exception as e:
            st.error(e)
            #st.error("Error: Problema cargando datos.")
            st.stop()
            


    loader_placeholder.empty()
    global lang_code
    lang_code = render_header()

    min_date = df['day'].min().date()
    max_date = df['day'].max().date()
        
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = max_date 
    if "selected_barri_from_map" not in st.session_state:
        st.session_state.selected_barri_from_map = "El Raval" 
            
    selected_date = st.session_state.selected_date
    
    df_filtered = df[df['day'].dt.date == selected_date].copy()
    df_prev_month = df[(df['day'].dt.date >= (selected_date - datetime.timedelta(days=30))) & (df['day'].dt.date < selected_date)].copy()
    render_kpis(df_filtered, df_prev_month, df_events)
    render_map_ranking_section(df_filtered, stats, gdf, min_date, max_date)
    plot_barri_details(df, df_events, df_filtered, gdf)
    plot_model_analysis(importances_and_features, engine)
    
    with st.spinner("Cargando..."):
        st.markdown(f'<div class="section-header">{t("all_stats")}<span style="color:{PRIMARY_TEXT_COLOR};"></span></div>', unsafe_allow_html=True)
        plot_stats(df)
    
if __name__ == "__main__":
    main()