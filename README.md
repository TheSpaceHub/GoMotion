<p align="center">
  <img src="media/GoMotionLogo.png" alt="Logo GoMotion" width="200">
</p>

## Predicción de picos de movilidad en Barcelona

El proyecto de GoMotion consiste en la creación de un sistema de predicción de picos de movilidad utilizando datos históricos de Telefónica combinados con datos públicos como son archivos metereologicos y calendarios de eventos. Se implementan modelos predictivos que anticipen flujos de movilidad con la finalidad de mejorar la red de movilidad local.

## Importante

GoMotion ha sido creado con la única intención de hacer una gran predicción de la movilidad en Barcelona para poder detectar grandes picos de movilidad y comprender de donde vienen. La falta de datos precisos e útiles sobre el transporte público en Barcelona hace que no tenga sentido intentar proponer cambios en el transporte para lidiar con los picos de movilidad. Sin embargo, hemos creado un modelo capaz de predecir picos de movilidad con gran precisión que hace que sea fácil, teniendo datos de calidad sobre el transporte público de Barcelona (como proporciones de trayectos en transporte privado / público, capacidades exactas de autobuses y metro, número de buses/metro de cada linea que hay cada día...etc), proponer cambios en éste para hacer frente a estos picos.

## Requisitos
- Python 3.12+
- Conexión a internet
- Acceso a la carpeta `output_limite_legal` proporcionada por Telefónica
- Acceso a los archivos `barris.csv`, `events.csv` y `festius.csv`
- Una llave de API para Gemini

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
|   └── metadata_manager.py # Metadatos 
|   └── stats.py            # Cálculo de estadísticas útiles
|   └── xgb_model.py        # Modelo de xgb para la predicción
|   └── event_encoder       # Conversión de eventos para una mejor predicción
|   └── hyperparameter_optimizer.py # Entrenamiento y optimización de modelo de predicción
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

### 1.3. Metadatos
A lo largo del uso del programa hay información que necesita compartirse entre varios archivos y entre sesiones que no corresponde a datos en sí. Esta información la denominamos metadatos y la almacenamos en `data/metadata.py` (archivo creado automáticamente). No conviene modificar manualmente los metadatos, pues pueden haber comportamientos inesperados.

### 1.4. Dot-env
Este proyecto hace uso de la API de Google Gemini. Su utilización está sujeta a la posesión de una llave que deberá almacenarse en un archivo `.env` en el mismo directorio que el resto de carpetas.

## 2. Predicción de Picos de Movilidad

GoMotion es capaz de predecir las intensidades de cada barrio con 7 días de antelación.

### 2.1. Datos Futuros de Meteorología
De la misma manera que para el archivo meteorológico, utilizaremos la API de `OpenMeteo` (en `meteo.py`) para obtener las predicciones de temperatura y lluvia de la semana siguiente.

### 2.2. Datos Futuros de Festivos y Eventos
Para conocer los eventos y los de la semana siguiente hemos creado un sistema de **web-scrapping**. En `llm_scrapper.py`, utilizamos `playwright` y `bs4` para obtener el texto de las páginas web de nuestro interés, y un LLM (`gemini`) que formatea los eventos y festivos encontrados para dejarlos listos para entrenar al modelo.

### 2.3. Codificación de Eventos
Con la finalidad de extraer la información más importante y usarla en nuestro modelo de predicción, codificamos los eventos de un día en un barrio en un espacio latente de 5 dimensiones. Para ello entrenamos 2 modelos: un codificador y un descodificador. Esta arquitectura permite entrenar un modelo usando los eventos como *input* y *validation* al mismo tiempo, pues el descodificador debería actuar como una función inversa y llevar el vector del espacio latente de vuelta al espacio de eventos.

Una vez tenemos el modelo entrenado, guardamos la primera mitad del modelo entrenado en `models/encoder.keras`. Además, codificamos los eventos hasta la fecha necesaria (una semana a partir del día en el que se ejecuta el programa) usando el codificador. El resultado se guarda en `data/encoded_events.csv`.

### 2.4. Creación de Modelo de Predicción
La predicción de los datos se hará usando un modelo de extreme gradient boosting (`XGBoost`), dado que es una arquitectura que:
- permite la fácil integración de características categóricas
- tiene documentación y uso extensos
- es una de las más adecuadas para tratar datos de naturaleza tabular (todos nuestros datos se estructuran en archivos `.csv`)

La definición del modelo y las herramientas para su entrenamiento y su optimización se encuentran en el archivo `hyperparameter_optimizer.py`.

A continuación están las características utilizadas y su descripción:
| Característica | Tipo | Descripción |
| ------------- |-------------| -------------|
| barri | Categórica | Nombre del barrio |
| temperature_2m_max | Numérica | Temperatura máxima para el día (ºC) |
| temperature_2m_min | Numérica | Temperatura mínima para el día (ºC) |
| precipitation_sum | Numérica | Suma de mm de precipitación en el día |
| is_holiday | Booleana | Si el día es festivo o no |
| month_cat | Categórica | Nombre del mes |
| day_cat | Categórica | Día de la semana |
| lag_7 | Numérica | Intensidad calculada hace 7 días |
| lag_14 | Numérica | Intensidad calculada hace 14 días |
| lag_21 | Numérica | Intensidad calculada hace 21 días |
| lag_28 | Numérica | Intensidad calculada hace 28 días |
| dt_7_w1 | Numérica | Derivada discreta de la semana más reciente: (lag_7 - lag_14) / 7 |
| dt_7_w2 | Numérica | Derivada discreta de la segunda semana más reciente: (lag_14 - lag_21) / 7 |
| enc1 | Numérica | Coordenada 1 de la codificación de los eventos para el día en el barrio especificado |
| enc2 | Numérica | Coordenada 2 de la codificación de los eventos para el día en el barrio especificado |
| enc3 | Numérica | Coordenada 3 de la codificación de los eventos para el día en el barrio especificado |
| enc4 | Numérica | Coordenada 4 de la codificación de los eventos para el día en el barrio especificado |
| enc5 | Numérica | Coordenada 5 de la codificación de los eventos para el día en el barrio especificado |

El archivo permite entrenar el modelo en una variedad de hiperparámetros. Para ello implementa un *grid search* personalizado: dada una colección de rangos de hiperparámetros, se entrenan modelos para todos los elementos de su producto cartesiano y se guarda aquel con mayor precisión (evaluada según los aciertos en la predicción). Los hiperparámetros que se pueden ajustar son:

- Base de los pesos: el modelo XGBoost asigna unos pesos a los errores de cada muestra según su *z-score* con la siguiente formula: $weight = max(1, base ^{\text{z-score}})$. Aumentar el hiperparámetro *base* pondera más fuertemente los errores en días con movilidad excesiva.
- Learning rate: se permite modificar el *learning rate* para variar el ritmo de convergencia y explorar nuevos mínimos
- Tree depth: también se permite modificar el número máximo de árboles que puede usar el modelo (más información en https://xgboosting.com/configure-xgboost-max_depth-parameter/)

Cuando se escoge el mejor modelo, se guarda en `models/regressor.joblib`.


## 3. Dashboard y Visualización
Con el fin de entender mejor las predicciones, hemos implementado un dashboard utilizando `streamlit`.
 
### 3.1. Carga de Datos
Nada más entrar al dashboard se llamará a la función `fill_data()`, que se encuentra en `data_filler.py`. Así nos aseguramos de tener los datos y las predicciones de los días que nos interesan.

### 3.2. Métricas Diarias
Tendremos la opción de seleccionar una fecha. Una vez seleccionada, se nos mostrarán algunas métricas relevantes de ese día: temperatura, lluvia, eventos, festivos y el tráfico total del día. Además obtenemos una comparación histórica de estos valores. En concreto:  
Temperatura y Precipitaciones: Comparación con la media de los últimos 30 días.  
Eventos: Comparación con la media de eventos diarios que hubo en los últimos 30 días.  
Tráfico Total: Comparación con la media de los 4 últimos días con el mísmo día de la semana (por ej. Domingo)

### 3.3. Tabla de Barrios
Para el día seleccionado se nos mostrará una tabla con, para cada barrio, su intensidad, la media histórica de esta, su z-score, y su saturación (es decir, como se compara a la media histórica de ese barrio).

### 3.4. Mapa de Calor
Además se mostrará un mapa de calor de las intensidades de cada barrio. Estas intensidades son relativas al barrio, es decir: se considera que hay un pico cuando el valor se aleja mucho de lo que suele haber en ese barrio. Podremos hacer clic en un barrio en concreto para seleccionarlo.

### 3.5. Análisis Detallado por Barrio
Una vez seleccionado un barrio en el mapa, obtendremos una serie de gráficas que explican como afecta cada variable a la intensidad histórica de ese barrio. En concreto:  
- Impacto festivo/laborable
- Impacto de cada tipo de evento
- Impacto del día de la semana
- Impacto del mes
- Impacto de la precipitación


## Autores
- Javier Badesa
- Alexander Cameron Hall
- Oscar Senesi Aladjem
- Dan Manuel Vancea