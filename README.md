<p align="center">
  <img src="media/GoMotionLogo.png" alt="Logo GoMotion" width="200">
</p>

## Predicción de picos de movilidad en Barcelona

El proyecto de GoMotion consiste en la creación de un sistema de predicción de picos de movilidad utilizando datos históricos de Telefónica combinados con datos públicos como son archivos metereologicos y calendarios de eventos. Se implementan modelos predictivos que anticipen flujos de movilidad con la finalidad de mejorar la red de movilidad local.

## Requisitos
- Python 3.12+
- Conexión a internet
- Acceso a la carpeta `output_limite_legal` proporcionada por Telefónica
- Acceso a los archivos `barris.csv`, `events.csv` y `festius.csv`

## Instalación

Para poder utilizar GoMotion, es necesario crear un entorno virtual y descargar las librerías necesarias.

1) Crear el entorno virtual:
`python -m venv .venv`
2) Activar el entorno virtual:
- MacOS / Linux: `source .venv/bin/activate`
- Windows PowerShell / Windows Cmd: `.venv\Scripts\Activate.ps1` / `.venv\Scripts\activate.bat`
3) Descargar librerías
`pip install -r requirements.txt`

## Estructura del Proyecto

```
GoMotion/
├── data/                   
│   ├── output_limite_legal # Datos proporcionados por Telefónica
│   └── events.csv          # Registro de eventos brutos
|   └── holidays.csv          # Registro de festivos brutos
│
├── media/                  
│    └── GoMotionLogo.png    
|    └── GoMotionShortLogo.png  
|    └── GoMotionShortLogo.ico 
│
├── src/                    
│   ├── llm_scraper.py      # Extracción de eventos y festivos con web scrapping
│   └── barri_manager.py    # Creación del "mapa/grafo" con los barrios de Barcelona
|   └── metadata_manager.py # Metadatos Supongo (dan ayuda)
|   └── stats.py            # Cálculo de estadísticas útiles
|   └── xgb_model.py        # Modelo de xgb para la predicción
|   └── event_encoder       # Conversión de eventos para una mejor predicción
|   └── hyperparameter_optimizer.py # Dan ayuda
|   └── peak_classifier.py  # Definición y clasificación de picos
|   └── data_filler.py      # Realizar Predicciones (1 semana)
|   └── meteo.py            # Archivo y predicción meteorológica
|   └── intensities.py      # Modelo matemático para definir las intensidades
|   └── pipeline.py         # Pipeline y archivo principal del proyecto
|   └── dashboard.py        # Visualización con Streamlit
│
├── .env                    # Variables de entorno (API Keys - No subir al repo)
└── requirements.txt        # Dependencias del proyecto
```

## Ejecución
Para acceder a todas las funciones del proyecto es suficiente con ejecutar el pipeline.  
Desde **la raiz** del proyecto: `python3 src/pipeline.py`

## 1. Preparación de los datos

### 1.1. Limpieza y organización de datos 
Una vez descargados los datos movilidad entre barrios proporcionados por Telefónica, eliminaremos las columnas irrelevantes para nuestro proyecto, y nos quedaremos únicamente con
las columnas siguientes: `day`, `barrio_origen_name`, `barrio_destino_name` y `viajes`.  
Utilizaremos el dataset resultante y el modelo explicado en el pdf adjunto para crear un nuevo dataset con las siguientes columnas: `day`, `barri`, `intensity`.  
Estas funciones se implementan en los archivos `barri_manager.py` y `intensities.py`

### 1.2. Archivo de Eventos, Festivos y Meteorología
Para mejorar la precisión de nuestro modelo utilizaremos datos históricos de eventos, festivos y meteorología.  
Los archivos de eventos y festivos han sido recopilados a mano y se encuentran en `data/events.csv` y `data/holidays.csv` respectivamente.  
Cada evento tiene asociados una fecha, una categoría, una lista de barrios en los que tiene lugar, y un impacto (del 1 al 5) relativo a su categoría. Los festivos únicamente tienen asociada una fecha.
Para recopilar archivos meteorológicos utilizaremos la API de `OpenMeteo`, en el archivo `meteo.py`. Por simplicidad y porque creemos que es lo mejor para el modelo, recopilaremos para cada día, el nivel de lluvia y las temperaturas máxima y mínima .

## 2. Predicción de Picos de Movilidad

GoMotion es capaz de predecir las intensidades de cada barrio con 7 días de antelación.

### 2.1. Datos Futuros de Meteorología
De la misma manera que para el archivo meteorológico, utilizaremos la API de `OpenMeteo` (en `meteo.py`) para obtener las predicciones de temperatura y lluvia de la semana siguiente.

### 2.2. Datos Futuros de Festivos y Eventos
Para conocer los eventos y los de la semana siguiente hemos creado un sistema de **web-scrapping**. En `llm_scrapper.py`, utilizamos `playwright` y `bs4` para obtener el texto de las páginas web de nuestro interés, y un LLM (`gemini`) que formatea los eventos y festivos encontrados para dejarlos listos para entrenar al modelo.

### 2.3. Codificación de Eventos

## Autores
- Javier Badesa
- Alexander Cameron Hall
- Oscar Senesi Aladjem
- Dan Manuel Vancea