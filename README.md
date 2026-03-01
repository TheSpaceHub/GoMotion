<p align="center">
  <img src="media/GoMotionLogo.png" alt="Logo GoMotion" width="200">
</p>

## Predicción de picos de movilidad en Barcelona

El proyecto de **GoMotion** es una plataforma de inteligencia urbana orientada a la predicción de picos de movilidad. Utilizando un modelo base entrenado con datos históricos de telecomunicaciones y alimentado en tiempo real con datos meteorológicos y calendarios de eventos, el sistema anticipa flujos masivos de personas con hasta 7 días de antelación. Nuestro objetivo es proporcionar herramientas analíticas precisas para optimizar la red de movilidad y el transporte público a nivel local.

For the English version of this readme, go <a href="README.en.md">here</a>.

## Importante: Alcance y Automatización

- GoMotion detecta fuertes picos de movilidad y desglosa los factores que los originan (clima, festividades, eventos masivos). Con esta información, entidades de gestión urbana pueden anticipar y dimensionar correctamente los servicios de transporte público (frecuencias de metro/bus, capacidades, etc.) para hacer frente a la demanda extraordinaria.
- Para sustentar el proyecto con rigor, se ha desarrollado el documento `mathematical_model.pdf`, el cual detalla la abstracción matemática utilizada para modelar la intensidad de movimiento en la ciudad a partir de los datos.
- **Automatización y Ventana Predictiva:** El alcance predictivo del programa es de 7 días. Para mantener el sistema actualizado sin intervención manual, hemos implementado un pipeline automatizado (`daily_pipeline.py`) ejecutado diariamente mediante **GitHub Actions**. Este proceso calcula los rezagos históricos (lags), extrae nuevos eventos, consulta previsiones meteorológicas y actualiza las predicciones directamente en nuestra base de datos relacional. 

## Requisitos Técnicos 

Si deseas contribuir al motor de GoMotion o ejecutar el entorno en local:

- **Frontend**: Node.js 18+ y un gestor de paquetes (npm o yarn) para la aplicación Next.js/React.
- **Backend / Data Pipeline**: Python 3.11+ con las librerías especificadas en `requirements.txt` (incluyendo SQLAlchemy, XGBoost, TensorFlow y Pandas).
- **Base de Datos**: Acceso a la instancia de la base de datos de GoMotion (PostgreSQL/MySQL).
- **Variables de Entorno**: Configuración de un archivo `.env` que contenga la clave de API de Gemini (`GEMINI_API_KEY`) y la URI de conexión a la base de datos.

## Estructura del Proyecto

```text
GoMotion/
├── .github/workflows/                  
│     └── daily_action.yaml          # Automatización del pipeline predictivo
│    
├── media/               
│    └── GoMotionLogo.png    
│    └── ... (activos gráficos y capturas)
│ 
├── nextjs/gomotion/                 # Frontend (Next.js App Router)
│    ├── app/                        
│    │   ├── data/                   
│    │   │   └── barris.json         # Información geográfica de los barrios
│    │   ├── barriInfo.tsx           # Componente de análisis detallado por barrio
│    │   ├── db.ts                   # Configuración y conexión a la base de datos
│    │   ├── heatmap.tsx             # Visualización del mapa de calor interactivo
│    │   ├── plot.tsx                # Gráficas analíticas (SHAP, tendencias)
│    │   ├── server_data.ts          # Lógica Server-Side y peticiones a DB
│    │   ├── eventDetails.tsx        # Análisis del impacto de eventos
│    │   ├── layout.tsx & page.tsx   # Estructura principal del Dashboard
│    │   └── translations.ts         # Sistema multiidioma
│    │
│    ├── public/                     # Estilos (globals.css, mobile.css) y estáticos
│    ├── next.config.ts & package.json
│    └── tsconfig.json               
│ 
├── src/                             # Backend y Machine Learning
│   ├── barri_manager.py & intensities.py # Lógica de modelado matemático
│   ├── daily_pipeline.py            # Orquestador principal de actualización de DB
│   ├── database_connection.py       # Interfaz SQLAlchemy
│   ├── event_encoder.py             # Codificador de eventos en espacio latente
│   ├── hyperparameter_optimizer.py  # Grid search y entrenamiento XGBoost
│   ├── llm_scraper.py               # Web-scraping con Playwright y Gemini
│   ├── meteo.py                     # Integración con OpenMeteo API
│   └── xgb_model.py                 # Definición del regresor
│    
├── mathematical_model.pdf 
├── README.md
└── requirements.txt 

```

## 1. Gestión de Datos y ETL

El sistema ha evolucionado de usar archivos locales a una arquitectura centralizada en base de datos, garantizando escalabilidad y fiabilidad.

### 1.1. Ingesta Histórica y Estructuración

Inicialmente, los datos de movilidad proporcionados por Telefónica se limpiaron, eliminando ruido y dejando las variables esenciales. Utilizando el modelo explicado en el pdf adjunto, estos datos se transformaron en un índice de `intensity` por `barri` y `day`, almacenándose de forma persistente en nuestra base de datos para servir como "ground truth" del modelo.

### 1.2. Meteorología, Eventos y Festivos

Para la predicción contextual, el pipeline integra:

* **Meteorología:** Uso de la API de `OpenMeteo` (`meteo.py`) para capturar y predecir lluvia diaria y temperaturas extremas.
* **Eventos y Festivos:** Módulo de extracción automatizada de los principales focos de movimiento en la ciudad (Estadio Olímpico, FC Barcelona, Primavera Sound, Fira de Barcelona, etc.). Los eventos procesados se almacenan dinámicamente en la tabla `events` de la base de datos.

## 2. Pipeline Predictivo (Daily Pipeline)

La predicción de los datos se realiza mediante un modelo **XGBoost** (`regressor.joblib`), ejecutado automáticamente por GitHub Actions. El orquestador `daily_pipeline.py` realiza las siguientes tareas de forma desatendida:

1. **Scraping y Procesamiento de Eventos:** Extrae eventos de la semana siguiente usando `llm_scraper.py` (impulsado por Gemini) y los desglosa por barrio afectado.
2. **Codificación de Eventos (Deep Learning):** Los eventos se pasan por un modelo Autoencoder (`encoder.keras`) previamente entrenado, transformando las características categóricas y textuales en un vector denso de 5 dimensiones (`enc1` a `enc5`).
3. **Cálculo de Variables Temporales (Lags):** Mediante consultas optimizadas con caché local a la base de datos, calcula la intensidad del barrio hace 7, 14, 21 y 28 días, además de sus derivadas discretas.
4. **Predicción y Guardado:** Genera las predicciones de intensidad para los próximos 7 días y vuelca los resultados directamente en la tabla `display_data`, listos para ser consumidos por el Dashboard.
## 3. Predicción de Picos de Movilidad

GoMotion es capaz de predecir las intensidades de cada barrio con 7 días de antelación.

### 3.1. Datos Futuros de Meteorología

De la misma manera que para los datos meteorológicos históricos, utilizaremos la API de `OpenMeteo` (en `meteo.py`) para obtener las predicciones de temperatura y lluvia de la semana siguiente.

### 3.2. Datos Futuros de Festivos y Eventos

Para conocer los eventos de la semana siguiente hemos creado un sistema de **web-scrapping**. En `llm_scrapper.py`, utilizamos `playwright` y `bs4` para obtener el texto de las páginas web de nuestro interés (mencionadas en el apartado [1.2.1](https://www.google.com/search?q=%23121-eventos-seleccionados)), y un LLM (`gemini`) que formatea los eventos y festivos encontrados para dejarlos listos para entrenar al modelo.

### 3.3. Codificación de Eventos

Con la finalidad de extraer la información más importante y usarla en nuestro modelo de predicción, codificamos los eventos de un día en un barrio en un espacio latente de 5 dimensiones. Para ello entrenamos 2 modelos: un codificador y un descodificador. Esta arquitectura permite entrenar un modelo usando los eventos como *input* y *validation* al mismo tiempo, pues el descodificador debería actuar como una función inversa y llevar el vector del espacio latente de vuelta al espacio de eventos.

Una vez tenemos el modelo entrenado, guardamos la primera mitad del modelo entrenado en `models/encoder.keras`. Además, codificamos los eventos hasta la fecha necesaria (una semana a partir del día en el que se ejecuta el programa) usando el codificador. El resultado se guarda en `data/encoded_events.csv`.

### 3.4. Creación de Modelo de Predicción

La predicción de los datos se hará usando un modelo de extreme gradient boosting (`XGBoost`), dado que es una arquitectura que:

* permite la fácil integración de características categóricas
* tiene documentación y uso extensos
* es una de las más adecuadas para tratar datos de naturaleza tabular (todos nuestros datos se estructuran en bases de datos)

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

* Base de los pesos: el modelo XGBoost asigna unos pesos a los errores de cada muestra según su *z-score* con la siguiente formula: $weight = max(1, base ^{\text{z-score}})$. Aumentar el hiperparámetro *base* pondera más fuertemente los errores en días con movilidad excesiva.
* Learning rate: se permite modificar el *learning rate* para variar el ritmo de convergencia y explorar nuevos mínimos. El valor especial `None` implementa el siguiente schedule:

| Ronda de corte | Learning rate |
| --- | --- |
| 0 | 0.1 |
| 100 | 0.001 |
| 150 | 0.0001 |

* Tree depth: también se permite modificar el número máximo de árboles que puede usar el modelo.

Cuando se escoge el mejor modelo, se guarda en `models/regressor.joblib`.


## 4. Dashboard y Visualización (Next.js)

GoMotion cuenta con una interfaz web analítica moderna, desarrollada con **Next.js** y **React**, diseñada para ofrecer una experiencia intuitiva, rápida y conectada en tiempo real a nuestra base de datos.

* **Resumen Diario (Daily Summary):** Panel superior de control que muestra el tráfico total, eventos detectados, estado festivo y clima del día seleccionado.
* **Detección de Picos y Mapa de Calor:** Visualización geográfica interactiva mediante Leaflet/heatmap que ilumina los barrios de Barcelona según su densidad e intensidad de movimiento. Permite identificar anomalías visualmente al instante.
* **Estadísticas Detalladas por Barrio:** Al seleccionar una zona en la tabla o el mapa, se renderizan métricas exclusivas del barrio, incluyendo su tráfico semanal, diferencias históricas, densidad poblacional y el impacto promedio según la categoría de evento.
* **Análisis de Impacto y Modelo (SHAP):** Un módulo específico de analítica (`plot.tsx`) que grafica la importancia de las variables del modelo XGBoost (SHAP Feature Importances). Aquí se demuestra visualmente el peso del histórico (`lag_7`) frente a los factores externos (clima, eventos).
* **Rendimiento Dinámico y Diseño:** Construido sobre el *App Router* de Next.js, usa `server_data.ts` para ejecutar operaciones pesadas de datos en el servidor. El diseño es *responsive* (`mobile.css`) e incluye métricas de precisión del modelo (porcentaje de aciertos, subestimaciones y sobrestimaciones).

## Autores

* Javier Badesa Pérez
* Alexander Cameron Hall Parrilla
* Oscar Senesi Aladjem
* Dan Manuel Vancea Boros
