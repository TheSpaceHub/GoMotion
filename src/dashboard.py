import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Datos Diarios de Intensidad",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    df = pd.read_csv('./data/final_data.csv')
    df['day'] = pd.to_datetime(df['day'])
    
except FileNotFoundError:
    st.error("Error: Archivo 'final_data.csv' no encontrado.")
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

st.title("Lista de Intensidades por Barrio")
st.subheader(f"Día: **{selected_date.strftime('%d de %B de %Y')}**")

st.markdown("---")

if not df_filtered.empty:

    df_display = df_filtered.rename(columns={
        'barri': 'Barrio',
        'intensity': 'Intensidad de Movilidad'
    })
    
    columnas_a_mostrar = [
        'Barrio', 
        'Intensidad de Movilidad', 
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