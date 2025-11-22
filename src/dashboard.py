import streamlit as st
import pandas as pd
from datetime import datetime
import barri_manager as bm
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd

# Loads again if any changes
@st.cache_data  
def load_df() -> pd.DataFrame:
    """Loads final_data DataFrame"""
    
    df = pd.read_csv('./data/final_data.csv')
    df['day'] = pd.to_datetime(df['day'])
    return df

# Loads once at the beggining
@st.cache_resource  
def load_geodata() -> tuple[nx.Graph, gpd.GeoDataFrame]:
    """Loads once Graph and gdf"""
    
    G = bm.create_graph()
    gdf = bm.load_gdf().rename(columns={"nom_barri": "barri"})
    return G, gdf


st.set_page_config(
    page_title="Datos Diarios de Intensidad",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    df = load_df()
    G, gdf = load_geodata()
    
except FileNotFoundError:
    st.error("Error: Archivo no encontrado.")
    st.stop()

st.sidebar.title("📅 Seleccionar Fecha")

# Intervalo de fechas (max_date lo cambiaremos por el ultimo dia q podamos predecir con open_meteo)
min_date = df['day'].min().date()
max_date = df['day'].max().date()

selected_date = st.sidebar.date_input(
    "Escoge el día para ver los datos",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

df_filtered = df[df['day'].dt.date == selected_date].copy()

st.title("Mapa de Calor de Intensidades Relativas por Barrio")
st.subheader(f"Día: **{selected_date.strftime('%d de %B de %Y')}**")

st.markdown("---")


def zvalue_to_color(z: float, cmap=plt.cm.plasma) -> tuple[float,float,float,float]:
    """Given a z-value, maps it to a color in a plasma colour map"""
    
    if pd.isna(z):
        return (0.8, 0.8, 0.8, 1)

    remove_outlier_z = min(max(z, -2.57), 2.57)   # z-value for 99% Exclude outliers
    norm = (remove_outlier_z + 2.57) / 5.14      # Normalize 

    return cmap(norm)

@st.cache_data
def compute_zscore_stats(df) -> pd.DataFrame:
    """Returns a DataFrame with columns: barri, mean, std. Calculates means and std of all days"""
    
    stats = df.groupby("barri")["intensity"].agg(['mean','std'])
    return stats

stats = compute_zscore_stats(df)

df_day = df_filtered.merge(stats, on="barri", how="left")
df_day["zscore"] = (df_day["intensity"] - df_day["mean"]) / df_day["std"]


gdf_day = gdf.merge(df_day[["barri","zscore"]], on="barri", how="left")
gdf_day["color"] = gdf_day["zscore"].apply(zvalue_to_color)

fig, ax = plt.subplots(figsize=(10, 10))
gdf_day.plot(ax=ax, color=gdf_day['color'], edgecolor='black')
ax.set_axis_off()
st.pyplot(fig, use_container_width=False)

st.title("Lista de Intensidades por Barrio")

st.markdown("---")

if not df_filtered.empty:

    df_display = df_filtered.rename(columns={
        'barri': 'Barrio',
        'intensity': 'Intensidad de Movilidad',
        'temperature_2m_max (°C)': 'Temperatura Máxima',
        'temperature_2m_min (°C)': 'Temperatura Mínima',        
    })
    
    columnas_a_mostrar = [
        'Barrio', 
        'Intensidad de Movilidad', 
        'Temperatura Máxima',
        'Temperatura Mínima'
    ]
    
    columnas_existentes = [col for col in columnas_a_mostrar if col in df_display.columns]

    st.dataframe(
        df_display[columnas_existentes].sort_values('Intensidad de Movilidad', ascending=False),
        hide_index=True,
        use_container_width=True
    )

    st.caption(f"Mostrando {len(df_filtered)} registros de barrios.")

else:
    st.warning(f"No hay datos para el día {selected_date.strftime('%d/%m/%Y')}. ")