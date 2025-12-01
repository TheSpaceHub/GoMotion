import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import barri_manager as bm
import networkx as nx
import geopandas as gpd
import plotly.express as px 
import plotly.graph_objects as go
import locale

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain') 
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

st.set_page_config(page_title="GoMotion", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    
    h1 {
        color: #0f172a;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        font-size: 3.5rem !important;
        margin: 0;
        padding: 0;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }

    [data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #0f172a;
        font-weight: 700;
    }

    .section-header {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }

    div[data-testid="stDateInput"] {
        padding: 0px;
    }

    div[data-testid="stDateInput"] input {
        font-size: 1.3rem !important;
        text-align: center;
        border: none;
        border-bottom: 3px solid #94a3b8;
        border-radius: 0px;
        padding: 5px;
        color: #0f172a;
        font-weight: 700;
        background-color: transparent;
    }

    .event-cat {
        font-weight: 800;
        font-size: 1.3rem;
        color: #9f1239;
        margin-bottom: 5px;
        padding: 15px;
        background-color: #fff1f2;
        border-radius: 8px;
        border-left: 5px solid #e11d48;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .event-desc {
        color: #4b5563;
        font-size: 1.2rem;
        font-style: italic;
        line-height: 1.4;
        padding: 15px;
        background-color: #f8fafc;
        border-radius: 8px;
        border-left: 5px solid #94a3b8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .no-event {
        color: #94a3b8;
        font-size: 1.2rem;
        font-style: italic;
        padding: 15px;
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px dashed #cbd5e1;
    }
    
    hr {
        margin: 30px 0;
        border-color: #e2e8f0;
    }
    
    div[data-testid="stSelectbox"] label {
        font-size: 1.1rem;
        font-weight: 700;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data  
def load_df() -> pd.DataFrame:
    df = pd.read_csv('./data/final_data.csv')
    df['day'] = pd.to_datetime(df['day'])
    return df

@st.cache_resource  
def load_geodata() -> tuple[nx.Graph, gpd.GeoDataFrame]:
    G = bm.create_graph()
    gdf = bm.load_gdf().rename(columns={"nom_barri": "barri"})
    if gdf.crs is None:
        try:
            gdf.set_crs("EPSG:25831", allow_override=True, inplace=True)
        except: pass 
    try:
        gdf = gdf.to_crs("EPSG:4326")
    except Exception: pass
    return G, gdf

@st.cache_data
def compute_zscore_stats(df) -> pd.DataFrame:
    stats = df.groupby("barri")["intensity"].agg(['mean','std'])
    return stats

def plot_barri_heatmap(df_current_day: pd.DataFrame, stats: pd.DataFrame, gdf: gpd.GeoDataFrame):
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
            title="Intensidad (Z)",
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
    st.plotly_chart(fig, use_container_width=True)

def plot_barri_details(df_full, barri_name):
    df_barri = df_full[df_full['barri'] == barri_name].copy()
    st.markdown(f"### 🔎 Análisis Detallado: <span style='color:#3b82f6'>{barri_name}</span>", unsafe_allow_html=True)
    
    df_barri['weekday_num'] = df_barri['day'].dt.weekday
    df_barri['day_of_the_week'] = df_barri['day'].dt.strftime('%A')
    weekly_stats = df_barri.groupby('weekday_num').agg({'intensity': 'mean', 'day_of_the_week': 'first'}).sort_index()
    dias_espanol = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    if len(weekly_stats) == 7: weekly_stats['day_of_the_week'] = dias_espanol

    fig_week = go.Figure(go.Bar(
        x=weekly_stats['day_of_the_week'],
        y=weekly_stats['intensity'],
        marker_color='#3b82f6',
        marker_line_width=0,
        opacity=0.8,
        name='Media'
    ))
    fig_week.update_layout(
        title=dict(text="Perfil Semanal", font=dict(size=16, color='#334155')),
        plot_bgcolor='white', margin=dict(t=40, b=20, l=20, r=20), height=300,
        bargap=0.4
    )

    df_barri['month_name'] = df_barri['day'].dt.strftime('%B')
    df_barri['month_num'] = df_barri['day'].dt.month
    mon_stats = df_barri.groupby('month_num').agg({'intensity': 'mean', 'month_name': 'first'}).sort_index()
    
    fig_mon = go.Figure()
    fig_mon.add_trace(go.Scatter(
        x=mon_stats['month_name'], y=mon_stats['intensity'],
        mode='lines+markers',
        line=dict(color='#f59e0b', width=3, shape='spline'),
        marker=dict(size=8, color='#d97706', line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor='rgba(245, 158, 11, 0.1)'
    ))
    fig_mon.update_layout(
        title=dict(text="Evolución Mensual", font=dict(size=16, color='#334155')),
        plot_bgcolor='white', margin=dict(t=40, b=20, l=20, r=20), height=300,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )

    cat_stats = df_barri.groupby('category')['intensity'].mean().reset_index().sort_values('intensity', ascending=True)
    fig_cat = go.Figure(go.Bar(
        x=cat_stats['intensity'], y=cat_stats['category'],
        orientation='h',
        marker=dict(color='#8b5cf6', line=dict(color='#7c3aed', width=1)),
        opacity=0.9
    ))
    fig_cat.update_layout(
        title=dict(text="Impacto Medio por Evento", font=dict(size=15, color='#334155')),
        plot_bgcolor='white', margin=dict(t=40, b=20, l=20, r=20), height=300,
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )

    hol_stats = df_barri.groupby('is_holiday')['intensity'].mean().reset_index()
    hol_stats['label'] = hol_stats['is_holiday'].map({0.0: 'No Festivo', 1.0: 'Festivo'})
    fig_hol = px.box(
        df_barri, x='is_holiday', y='intensity',
        color='is_holiday',
        color_discrete_map={0.0: '#94a3b8', 1.0: '#10b981'},
        labels={'is_holiday': 'Tipo de Día'}
    )
    fig_hol.update_layout(
        title=dict(text="Distribución: Festivo vs Laborable", font=dict(size=15, color='#334155')),
        plot_bgcolor='white', margin=dict(t=40, b=20, l=20, r=20), height=300,
        showlegend=False,
        xaxis=dict(tickvals=[0, 1], ticktext=['Laborable', 'Festivo']),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )

    fig_rain = px.scatter(
        df_barri, x="precipitation_sum", y="intensity", 
        trendline="ols", trendline_color_override="#ef4444",
        opacity=0.5, color_discrete_sequence=['#64748b']
    )
    fig_rain.update_layout(
        title=dict(text="Correlación Lluvia / Tráfico", font=dict(size=16, color='#334155')),
        xaxis_title="Precipitación (mm)", yaxis_title="Intensidad",
        plot_bgcolor='white', margin=dict(t=40, b=20, l=20, r=20), height=300,
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )

    c1, c2 = st.columns(2, gap="medium")
    with c1: st.plotly_chart(fig_week, use_container_width=True)
    with c2: st.plotly_chart(fig_mon, use_container_width=True) 
    
    c3, c4 = st.columns(2, gap="medium")
    with c3: st.plotly_chart(fig_cat, use_container_width=True)
    with c4: st.plotly_chart(fig_hol, use_container_width=True)

    st.plotly_chart(fig_rain, use_container_width=True)

def render_header():
    st.title("GoMotion")
    st.markdown('<p class="subtitle">Monitorización Avanzada de Movilidad Urbana</p>', unsafe_allow_html=True)

def render_metrics(df_day):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Máxima", f"{df_day['temperature_2m_max'].iloc[0]}°")
    with col2: st.metric("Mínima", f"{df_day['temperature_2m_min'].iloc[0]}°")
    with col3: st.metric("Lluvia", f"{df_day['precipitation_sum'].iloc[0]}mm")
    with col4:
        es_festivo = df_day['is_holiday'].iloc[0] != 0.0
        st.metric("Festivo", "Sí" if es_festivo else "No")

def render_map_ranking_section(df_day, stats, gdf):
    c_map, c_tab = st.columns([1.4, 1], gap="large")

    with c_map:
        st.subheader("Mapa de Calor")
        plot_barri_heatmap(df_day, stats, gdf)

    with c_tab:
        st.subheader("Ranking por Barrio")
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
                height=600
            )
        else:
            st.info("No hay datos disponibles para la fecha seleccionada.")

def main():
    try:
        df = load_df()
        G, gdf = load_geodata()
        stats = compute_zscore_stats(df)
    except FileNotFoundError:
        st.error("Error: Archivo de datos no encontrado.")
        st.stop()

    render_header()
    
    min_date = df['day'].min().date()
    max_date = df['day'].max().date()

    col_date, col_cat, col_desc = st.columns([1, 1.2, 1.8], gap="large")

    with col_date:
        st.markdown('<div class="section-header">📅 FECHA</div>', unsafe_allow_html=True)
        selected_date = st.date_input(
            "Seleccionar Fecha", 
            value=max_date, 
            min_value=min_date, 
            max_value=max_date,
            label_visibility="collapsed"
        )
    
    df_filtered = df[df['day'].dt.date == selected_date].copy()
    eventos_unicos = df_filtered[df_filtered['category'] != "0"]['category'].unique()

    with col_cat:
        st.markdown('<div class="section-header">📌 EVENTO(S)</div>', unsafe_allow_html=True)
        if len(eventos_unicos) > 0:
            for evento in eventos_unicos:
                st.markdown(f'<div class="event-cat">{evento}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-event">Sin eventos</div>', unsafe_allow_html=True)

    with col_desc:
        st.markdown('<div class="section-header">📋 DESCRIPCIÓN</div>', unsafe_allow_html=True)
        if len(eventos_unicos) > 0:
            for _ in eventos_unicos:
                st.markdown(f'<div class="event-desc">Descripcion detallada del evento...</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-event">—</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render_metrics(df_filtered)
    st.divider()
    render_map_ranking_section(df_filtered, stats, gdf)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    barrios_list = sorted(df['barri'].unique())
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        st.markdown("### Seleccionar Barrio")
        selected_barrio = st.selectbox("Barrio", options=barrios_list, label_visibility="collapsed")
    
    plot_barri_details(df, selected_barrio)

if __name__ == "__main__":
    main()