import streamlit as st
import pandas as pd
from datetime import datetime
import barri_manager as bm
import networkx as nx
import geopandas as gpd
import plotly.express as px 

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
    df_day["zscore"] = (df_day["intensity"] - df_day["mean"]) / df_day["std"]
    
    # Importante: mantenemos el gdf como base para no perder la info geográfica
    gdf_day = gdf.merge(df_day[["barri", "intensity", "zscore", "temperature_2m_max (°C)"]], on="barri", how="left")
    
    # Rellenar nulos para que no rompan el mapa 
    gdf_day["zscore"] = gdf_day["zscore"].fillna(0)
    gdf_day["intensity"] = gdf_day["intensity"].fillna(0)

    lat_center = 41.39
    lon_center = 2.17
    
    fig = px.choropleth_mapbox(
        gdf_day,
        geojson=gdf_day.geometry,     
        locations=gdf_day.index,     
        color="zscore",               
        
        color_continuous_scale="plasma",
        range_color=[-2.57, 2.57],    
        mapbox_style="white-bg",
        opacity=0.6,
        zoom=11.5,
        center={"lat": lat_center, "lon": lon_center},
        
        # ✨ INTERACTIVIDAD (Tooltip)
        hover_name="barri",
        hover_data={
            "intensity": ":,.0f", # Formato numérico
            "zscore": ":.2f",
            "temperature_2m_max (°C)": ":.1f"
        }
    )
    
    # Ajustes estéticos finales
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

st.sidebar.title("📅 Seleccionar Fecha")
min_date = df['day'].min().date()
max_date = df['day'].max().date()
selected_date = st.sidebar.date_input("Escoge el día para ver los datos", value=max_date, min_value=min_date, max_value=max_date)

df_filtered = df[df['day'].dt.date == selected_date].copy()

st.title("Mapa de Calor de Intensidades Relativas por Barrio")
st.subheader(f"Día: **{selected_date.strftime('%d de %B de %Y')}**")
st.markdown("---")

# Renderizar el mapa
plot_barri_heatmap(df_filtered, stats, gdf)

st.title("Lista de Intensidades por Barrio")
st.markdown("---")

if not df_filtered.empty:
    df_display = df_filtered.rename(columns={
        'barri': 'Barrio',
        'intensity': 'Intensidad de Movilidad',
        'temperature_2m_max (°C)': 'Temperatura Máxima',
        'temperature_2m_min (°C)': 'Temperatura Mínima',        
    })
    columnas_a_mostrar = ['Barrio', 'Intensidad de Movilidad', 'Temperatura Máxima', 'Temperatura Mínima']
    columnas_existentes = [col for col in columnas_a_mostrar if col in df_display.columns]

    st.dataframe(df_display[columnas_existentes].sort_values('Intensidad de Movilidad', ascending=False), hide_index=True, use_container_width=True)
    st.caption(f"Mostrando {len(df_filtered)} registros de barrios.")
else:
    st.warning(f"No hay datos para el día {selected_date.strftime('%d/%m/%Y')}. ")