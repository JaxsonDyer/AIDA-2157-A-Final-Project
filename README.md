# Wildfire AI Pipeline

## Project Files

- **`app.py`**: The main execution script that orchestrates the entire workflow: environment validation, Docker setup, data generation, model training, evaluation, and simulating live tactical emergency briefings.
- **`docker_sql_start.py`**: Uses the Python Docker SDK to verify, start, or create a Microsoft SQL Server Docker container.
- **`data_generator.py`**: Generates synthetic wildfire-related ML data (weather, terrain, actions) and inserts it into a table in the MS-SQL database.
- **`models.py`**: Connects to the database to load data and train 10 different Machine Learning models (using Scikit-Learn Logistic Regression and Random Forests) for various prediction tasks.
- **`test_odbc.py`**: A utility script that checks whether the Microsoft ODBC Driver for SQL Server is installed on the host system.

## Synthetic Data Architecture

To bypass the lack of a centralized, real-world wildfire database, `data_generator.py` programmatically generates a flattened dataset specifically engineered to train complex Machine Learning algorithms. The generator enforces strict logical correlations (e.g., high wind + low humidity + pine forests = major fires) to ensure the models learn realistic environmental physics.

### Full Data Dictionary

The synthetic data generator produces the following 22 columns upon execution:

| Column Name | Description | Data Type |
| :--- | :--- | :--- |
| Date | Timestamp of the simulated daily log | Datetime |
| Latitude | GPS Latitude coordinate | Float |
| Longitude | GPS Longitude coordinate | Float |
| Fuel_Type | Primary vegetation (Pine Forest, Grassland, etc.) | String |
| Slope_Pct | Topographical incline percentage | Float |
| Soil_Moisture_Pct | Ground moisture baseline percentage | Float |
| Temp_C | Ambient temperature in Celsius | Float |
| Humidity_Pct | Relative atmospheric humidity percentage | Float |
| Wind_Kmh | Wind speed in kilometers per hour | Float |
| Precipitation_mm | Rainfall volume in millimeters | Float |
| Lightning_Strike_kA | Intensity of a recorded lightning strike in kiloamps | Float |
| Fire_Ignited | Binary trigger (1 = yes, 0 = no) indicating if a fire started | Integer |
| Fire_Classification | Categorical severity size (None, Minor, Moderate, Major) | String |
| Fire_Size_Hectares | Final burned area size in hectares | Float |
| Days_to_Contain | Estimated days until the fire is 100% contained | Integer |
| Is_False_Alarm | Binary trigger indicating a false 911 smoke report | Integer |
| AQI_Level | Local Air Quality Index reading (10-500+) | Integer |
| Evac_Triggered | Binary trigger indicating an evacuation order | Integer |
| Road_Closure_Flag | Binary trigger indicating a backcountry road closure | Integer |
| Landslide_Risk_Flag | Binary trigger for post-fire slope collapse risk | Integer |
| Dispatch_Air_Tanker | Binary trigger for preemptive aerial dispatch | Integer |
| Powerline_Risk_Flag | Binary trigger for vegetation interference on the grid | Integer |

## Machine Learning Models & Target Variables

The pipeline trains 10 distinct predictive models. The synthetic data provides both the features (the scenario) and the target variables (the correct answer) to train these systems:

- **Model 1: Lightning Predictor**
  - **Target (y):** `Fire_Ignited`
  - **Goal:** Predict if a specific lightning strike starts a fire based on `Lightning_Strike_kA` and `Soil_Moisture_Pct`.

- **Model 2: Fire Size Prediction**
  - **Target (y):** `Fire_Classification`
  - **Goal:** Categorize new ignitions as Minor, Moderate, or Major. *Note: The data generator guarantees that "Major" fires (>100 Hectares) strongly correlate with Pine fuel, dry conditions, and high wind.*

- **Model 3: False Alarm Filter**
  - **Target (y):** `Is_False_Alarm`
  - **Goal:** Determine if a 911 smoke report is a real fire or a false alarm (e.g., farming dust) based on wind and AQI.

- **Model 4: Containment Time Estimator**
  - **Target (y):** `Days_to_Contain` (Regression)
  - **Goal:** Predict the exact number of days to fully contain a fire.

- **Model 5: Smoke Health Alerts**
  - **Target (y):** `AQI_Level` (Regression)
  - **Goal:** Forecast the Air Quality Index for downwind communities.

- **Models 6 & 7: Evacuation & Road Closures**
  - **Targets (y):** `Evac_Triggered` and `Road_Closure_Flag`
  - **Goal:** Automatically flag backcountry roads and neighborhoods for emergency action based on fire presence and wind speed.

- **Model 8: Landslide Risk (Post-Fire)**
  - **Target (y):** `Landslide_Risk_Flag`
  - **Goal:** Identify burned hillsides at risk of collapse. *Note: Specifically triggers when Slope > 25% and Rain > 15mm.*

- **Model 9: Pre-Positioning Dispatch**
  - **Target (y):** `Dispatch_Air_Tanker`
  - **Goal:** Automate aerial dispatch based on extreme forecasted weather.

- **Model 10: Infrastructure Priority**
  - **Target (y):** `Powerline_Risk_Flag`
  - **Goal:** Identify high-risk vegetation zones near power lines that require clearing.

## Sample Output

```text
Verifying MS-SQL Docker container...
Success: Container 'aida2157a-SQL-pgnaawmszydfuzabwixtlmbnainwxztt' is already running.
Initiating Data Generation... Table 'Wildfire_ML_Training_Data' already exists and overwrite=False. Aborting data generation.
Initiating Model Training...
Loading data from MS-SQL...
Training 10 Machine Learning Models...
Training complete.

=============================================
          MODEL EVALUATION REPORT
=============================================
1: Lightning Predictor       | Accuracy: 92.75%
2: Fire Size Prediction      | Accuracy: 90.35%
3: False Alarm Filter        | Accuracy: 94.90%
4: Containment Estimator     | RMSE: 0.79 units
5: Smoke Health Alerts       | RMSE: 11.50 units
6: Evacuation Trigger        | Accuracy: 100.00%
7: Road Closure Auto         | Accuracy: 97.55%
8: Landslide Risk            | Accuracy: 99.25%
9: Pre-Positioning           | Accuracy: 99.95%
10: Infra Priority           | Accuracy: 97.55%
=============================================

=====================================================================================
LIVE FEED: TACTICAL EMERGENCY BRIEFINGS
=====================================================================================
[1] AI PREDICTION: 911 Smoke Report at Coord [38.1975, -114.6614] flagged as FALSE ALARM. Action: Stand down ground crews. Context: Dust anomaly.
[2] AI PREDICTION: Lightning Ignition Probability (43%) at Coord [37.8313, -121.7405]. Action: Monitor Sector.
[3] AI PREDICTION: Lightning Ignition Probability (43%) at Coord [40.4011, -121.8862]. Action: Monitor Sector.
=====================================================================================
```