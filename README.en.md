<p align="center">
  <img src="media/GoMotionLogo.png" alt="Logo GoMotion" width="200">
</p>

## Mobility Peak Prediction in Barcelona

The **GoMotion** project is an urban intelligence platform aimed at predicting mobility peaks. Using a base model trained on historical telecommunications data and fed in real-time with weather data and event calendars, the system anticipates massive flows of people up to 7 days in advance. Our goal is to provide precise analytical tools to optimize the local mobility network and public transport.

For the Spanish version of this readme, go <a href="README.md">here</a>.

## Important: Scope and Automation

- GoMotion detects strong mobility peaks and breaks down the factors that cause them (weather, holidays, massive events). With this information, urban management entities can anticipate and correctly size public transport services (metro/bus frequencies, capacities, etc.) to cope with extraordinary demand.
- To support the project with rigor, the document `mathematical_model.pdf` was developed, which details the mathematical abstraction used to model the movement intensity in the city based on the provided data.
- **Automation and Predictive Window:** The program's predictive scope is 7 days. To keep the system updated without manual intervention, we have implemented an automated pipeline (`daily_pipeline.py`) executed daily via **GitHub Actions**. This process calculates historical lags, extracts new events, queries weather forecasts, and updates the predictions directly in our relational database.

## Technical Requirements 

If you wish to contribute to the GoMotion engine or run the environment locally:

- **Frontend**: Node.js 18+ and a package manager (npm or yarn) for the Next.js/React application.
- **Backend / Data Pipeline**: Python 3.11+ with the libraries specified in `requirements.txt` (including SQLAlchemy, XGBoost, TensorFlow, and Pandas).
- **Database**: Access to the GoMotion database instance (PostgreSQL/MySQL).
- **Environment Variables**: Configuration of a `.env` file containing the Gemini API key (`GEMINI_API_KEY`) and the database connection URI.

## Project Structure

```text
GoMotion/
├── .github/workflows/                  
│     └── daily_action.yaml          # Predictive pipeline automation
│    
├── media/               
│    └── GoMotionLogo.png    
│    └── ... (graphic assets and screenshots)
│ 
├── nextjs/gomotion/                 # Frontend (Next.js App Router)
│    ├── app/                        
│    │   ├── data/                   
│    │   │   └── barris.json         # Geographical information of the neighborhoods
│    │   ├── barriInfo.tsx           # Detailed analysis component by neighborhood
│    │   ├── db.ts                   # Database configuration and connection
│    │   ├── heatmap.tsx             # Interactive heatmap visualization
│    │   ├── plot.tsx                # Analytical charts (SHAP, trends)
│    │   ├── server_data.ts          # Server-Side logic and DB queries
│    │   ├── eventDetails.tsx        # Event impact analysis
│    │   ├── layout.tsx & page.tsx   # Main Dashboard structure
│    │   └── translations.ts         # Multi-language system
│    │
│    ├── public/                     # Styles (globals.css, mobile.css) and statics
│    ├── next.config.ts & package.json
│    └── tsconfig.json               
│ 
├── src/                             # Backend and Machine Learning
│   ├── barri_manager.py & intensities.py # Mathematical modeling logic
│   ├── daily_pipeline.py            # Main orchestrator for DB updates
│   ├── database_connection.py       # SQLAlchemy Interface
│   ├── event_encoder.py             # Event encoder in latent space
│   ├── hyperparameter_optimizer.py  # Grid search and XGBoost training
│   ├── llm_scraper.py               # Web-scraping with Playwright and Gemini
│   ├── meteo.py                     # Integration with OpenMeteo API
│   └── xgb_model.py                 # Regressor definition
│    
├── mathematical_model.pdf 
├── README.md
└── requirements.txt 

```

## 1. Data Management and ETL

The system has evolved from using local files to a centralized database architecture, ensuring scalability and reliability.

### 1.1. Historical Ingestion and Structuring

Initially, the mobility data provided by Telefónica was cleaned, removing noise and keeping only the essential variables. Using the model explained in the attached pdf, this data was transformed into an `intensity` index per `barri` (neighborhood) and `day`, being stored persistently in our database to serve as the "ground truth" for the model.

### 1.2. Meteorology, Events, and Holidays

For contextual prediction, the pipeline integrates:

* **Meteorology:** Use of the `OpenMeteo` API (`meteo.py`) to capture and predict daily rain and extreme temperatures.
* **Events and Holidays:** Automated extraction module for the main movement hubs in the city (Olympic Stadium, FC Barcelona, Primavera Sound, Fira de Barcelona, etc.). Processed events are dynamically stored in the `events` table of the database.

## 2. Predictive Pipeline (Daily Pipeline)

Data prediction is performed using an **XGBoost** model (`regressor.joblib`), executed automatically by GitHub Actions. The `daily_pipeline.py` orchestrator performs the following tasks unattended:

1. **Event Scraping and Processing:** Extracts upcoming events for the following week using `llm_scraper.py` (powered by Gemini) and breaks them down by affected neighborhood.
2. **Event Encoding (Deep Learning):** Events are passed through a previously trained Autoencoder model (`encoder.keras`), transforming categorical and text features into a dense 5-dimensional vector (`enc1` to `enc5`).
3. **Temporal Variables Calculation (Lags):** Through optimized queries with local database caching, it calculates the neighborhood's intensity 7, 14, 21, and 28 days ago, as well as their discrete derivatives.
4. **Prediction and Storage:** Generates intensity predictions for the next 7 days and dumps the results directly into the `display_data` table, ready to be consumed by the Dashboard.

## 3. Mobility Peak Prediction

GoMotion is capable of predicting the intensities of each neighborhood 7 days in advance.

### 3.1. Future Weather Data

In the same way as for historical weather data, we use the `OpenMeteo` API (in `meteo.py`) to obtain temperature and rain predictions for the following week.

### 3.2. Future Holiday and Event Data

To find out about events and holidays for the following week, we have created a **web-scraping** system. In `llm_scrapper.py`, we use `playwright` and `bs4` to obtain the text from our websites of interest (mentioned in section 1.2.1), and an LLM (`gemini`) that formats the found events and holidays to get them ready to train the model.

### 3.3. Event Encoding

In order to extract the most important information and use it in our prediction model, we encode the events of a given day in a neighborhood into a 5-dimensional latent space. For this, we trained 2 models: an encoder and a decoder. This architecture allows training a model using the events as *input* and *validation* simultaneously, since the decoder should act as an inverse function and bring the latent space vector back to the event space.

Once we have the trained model, we save the first half of the trained model in `models/encoder.keras`. Additionally, we encode the events up to the required date (one week from the day the program is executed) using the encoder. The result is saved in `data/encoded_events.csv`.

### 3.4. Prediction Model Creation

Data prediction is done using an extreme gradient boosting (`XGBoost`) model, as it is an architecture that:

* allows for easy integration of categorical features
* has extensive documentation and usage
* is one of the most suitable for handling tabular nature data (all our data is structured in databases)

The model definition and the tools for its training and optimization are found in the `hyperparameter_optimizer.py` file.

Below are the features used and their descriptions:

| Feature | Type | Description |
| --- | --- | --- |
| barri | Categorical | Neighborhood name |
| temperature_2m_max | Numerical | Maximum temperature for the day (ºC) |
| temperature_2m_min | Numerical | Minimum temperature for the day (ºC) |
| precipitation_sum | Numerical | Sum of precipitation in mm for the day |
| is_holiday | Boolean | Whether the day is a holiday or not |
| month_cat | Categorical | Month name |
| day_cat | Categorical | Day of the week |
| lag_7 | Numerical | Intensity calculated 7 days ago |
| lag_14 | Numerical | Intensity calculated 14 days ago |
| lag_21 | Numerical | Intensity calculated 21 days ago |
| lag_28 | Numerical | Intensity calculated 28 days ago |
| dt_7_w1 | Numerical | Discrete derivative of the most recent week: (lag_7 - lag_14) / 7 |
| dt_7_w2 | Numerical | Discrete derivative of the second most recent week: (lag_14 - lag_21) / 7 |
| enc1 | Numerical | Coordinate 1 of the event encoding for the specified day in the neighborhood |
| enc2 | Numerical | Coordinate 2 of the event encoding for the specified day in the neighborhood |
| enc3 | Numerical | Coordinate 3 of the event encoding for the specified day in the neighborhood |
| enc4 | Numerical | Coordinate 4 of the event encoding for the specified day in the neighborhood |
| enc5 | Numerical | Coordinate 5 of the event encoding for the specified day in the neighborhood |

The file allows training the model on a variety of hyperparameters. To do this, it implements a custom *grid search*: given a collection of hyperparameter ranges, models are trained for all elements of their Cartesian product, and the one with the highest precision (evaluated based on successful predictions) is saved. The hyperparameters that can be adjusted are:

* Weight base: the XGBoost model assigns weights to the errors of each sample according to its *z-score* with the following formula: $weight = max(1, base ^{\text{z-score}})$. Increasing the *base* hyperparameter weights the errors more heavily on days with excessive mobility.
* Learning rate: it allows modifying the *learning rate* to vary the convergence pace and explore new minimums. The special value `None` implements the following schedule:

| Cutoff round | Learning rate |
| --- | --- |
| 0 | 0.1 |
| 100 | 0.001 |
| 150 | 0.0001 |

* Tree depth: it also allows modifying the maximum number of trees the model can use.

When the best model is chosen, it is saved in `models/regressor.joblib`.

## 4. Dashboard and Visualization (Next.js)

GoMotion features a modern analytical web interface, developed with **Next.js** and **React**, designed to offer an intuitive, fast experience connected in real-time to our database.

* **Daily Summary:** Top control panel showing total traffic, detected events, holiday status, and the weather for the selected day.
* **Peak Detection and Heatmap:** Interactive geographical visualization using Leaflet/heatmap that illuminates Barcelona's neighborhoods based on their movement density and intensity. It allows identifying anomalies visually and instantly.
* **Detailed Statistics by Neighborhood:** By selecting an area on the table or the map, exclusive metrics for the neighborhood are rendered, including its weekly traffic, historical differences, population density, and the average impact according to the event category.
* **Impact and Model Analysis (SHAP):** A specific analytical module (`plot.tsx`) that graphs the importance of the XGBoost model variables (SHAP Feature Importances). This visually demonstrates the weight of historical data (`lag_7`) versus external factors (weather, events).
* **Dynamic Performance and Design:** Built on the Next.js *App Router*, it uses `server_data.ts` to execute heavy data operations on the server. The design is *responsive* (`mobile.css`) and includes model precision metrics (percentage of accurate predictions, underestimations, and overestimations).

## Authors

* Javier Badesa Pérez
* Alexander Cameron Hall Parrilla
* Oscar Senesi Aladjem
* Dan Manuel Vancea Boros
