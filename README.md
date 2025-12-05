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

## Ejecución
Para acceder a todas las funciones del proyecto es suficiente con ejecutar el pipeline.
Desde la raiz del proyecto: `python3 src/pipeline.py`

## Autores
- Javier Badesa
- Alexander Cameron Hall
- Oscar Senesi Aladjem
- Dan Manuel Vancea