import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import barri_manager as bm
import networkx as nx
import geopandas as gpd
import plotly.express as px 
import locale

# Fecha en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain') 
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

st.set_page_config(page_title="Datos Diarios de Intensidad", layout="wide", initial_sidebar_state="expanded")

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
        except:
            pass 
    try:
        gdf = gdf.to_crs("EPSG:4326")
    except Exception as e:
        st.warning(f"Aviso: No se pudo convertir coordenadas geográficas: {e}")

    return G, gdf

@st.cache_data
def compute_zscore_stats(df) -> pd.DataFrame:
    stats = df.groupby("barri")["intensity"].agg(['mean','std'])
    return stats

def plot_barri_heatmap(df_current_day: pd.DataFrame, stats: pd.DataFrame, gdf: gpd.GeoDataFrame):
    """
    Versión INTERACTIVA con Plotly.
    Calcula Z-Score y muestra el mapa con tooltip al pasar el ratón.
    """
    # Calcular Z-Scores
    df_day = df_current_day.merge(stats, on="barri", how="left")
    df_day['intensity'] = np.ceil(df_day['intensity']).astype(int)
    df_day["zscore"] = (df_day["intensity"] - df_day["mean"]) / df_day["std"]
    
    # Importante: mantenemos el gdf como base para no perder la info geográfica
    gdf_day = gdf.merge(df_day[["barri", "intensity", "zscore", "temperature_2m_max"]], on="barri", how="left")
    
    # Rellenar nulos para que no rompan el mapa 
    gdf_day["zscore"] = gdf_day["zscore"].fillna(0)
    gdf_day["intensity"] = gdf_day["intensity"].fillna(0)

    lat_center = 41.39
    lon_center = 2.17
    
    fig = px.choropleth_mapbox(
        gdf_day,
        geojson=gdf_day.geometry,     
        locations=df_day.index,     
        color="zscore",               
        
        color_continuous_scale="plasma",
        range_color=[-2.57, 2.57],    
        mapbox_style="white-bg",
        opacity=0.6,
        zoom=11.5,
        center={"lat": lat_center, "lon": lon_center},
        
        hover_name="barri",
        hover_data={
            "intensity": ":.0f", # Formato numérico
            "zscore": False,
        }
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(
            title="Intensidad",
            tickvals=[-2.57, 0, 2.57],
            ticktext=["Baja", "Media", "Alta"],
            lenmode="fraction", len=0.5,
            yanchor="bottom", y=0.05,
            xanchor="left", x=0.02,
            bgcolor="rgba(255,255,255,0.5)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

try:
    df = load_df()
    G, gdf = load_geodata()
    stats = compute_zscore_stats(df)
except FileNotFoundError:
    st.error("Error: Archivo no encontrado.")
    st.stop()

st.sidebar.title("Seleccionar Fecha")
min_date = df['day'].min().date()
max_date = df['day'].max().date()
selected_date = st.sidebar.date_input("Escoge el día para ver los datos", value=max_date, min_value=min_date, max_value=max_date)

df_filtered = df[df['day'].dt.date == selected_date].copy()

st.title(f"Día: **{selected_date.strftime('%d de %B de %Y')}**")
st.markdown("---")
st.subheader("Características del día")
st.badge(f"Temperatura Máxima: **{df_filtered['temperature_2m_max'].iloc[0]} (°C)**", color='orange')
st.badge(f"Temperatura Mínima: **{df_filtered['temperature_2m_min'].iloc[0]} (°C)**", color='blue')
st.badge(f"Precipitaciones: **{df_filtered['precipitation_sum'].iloc[0]} (mm)**")

if df_filtered['category'].iloc[0] != "0":
    st.badge(f"Evento(s): **{df_filtered['category'].iloc[0]}**", color = "yellow")
else: 
    st.badge(f"No hay eventos este día.", color = "yellow")

if df_filtered['is_holiday'].iloc[0] != 0.0:
    st.badge(f"Festivo: **Si**", color = "green")
else: 
    st.badge(f"Festivo: **No**", color = "green")

st.markdown("---")

st.subheader("Mapa de calor de las intensidades relativas")


# Renderizar el mapa
plot_barri_heatmap(df_filtered, stats, gdf)

st.markdown("---")

st.subheader("Lista de Intensidades por Barrio")

if not df_filtered.empty:
    #Fusionar con las estadísticas para obtener la media histórica
    df_temp = df_filtered.merge(stats[['mean']], on="barri", how="left")
    df_temp['intensity'] = np.ceil(df_temp['intensity']).astype(int)
    df_temp['mean'] = np.ceil(df_temp['mean']).astype(int)

    df_display = df_temp.rename(columns={
        'barri': 'Barrio',
        'intensity': 'Intensidad de Movilidad',
        'mean': 'Intensidad Media Histórica'
       
    })
    
    columnas_a_mostrar = ['Barrio', 'Intensidad de Movilidad', 'Intensidad Media Histórica']
    
    columnas_existentes = [col for col in columnas_a_mostrar if col in df_display.columns]

    st.dataframe(df_display[columnas_existentes].sort_values('Intensidad de Movilidad', ascending=False), hide_index=True, use_container_width=True)
    st.caption(f"Mostrando {len(df_filtered)} registros de barrios.")
else:
    st.warning(f"No hay datos para el día {selected_date.strftime('%d/%m/%Y')}. ")