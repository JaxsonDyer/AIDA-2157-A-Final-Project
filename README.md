# Wildfire AI Pipeline

## Project Files
- **`app.py`**: The main execution script that orchestrates the entire workflow: environment validation, Docker setup, data generation, model training, evaluation, and simulating live tactical emergency briefings.
- **`docker_sql_start.py`**: Uses the Python Docker SDK to verify, start, or create a Microsoft SQL Server Docker container.
- **`data_generator.py`**: Generates synthetic wildfire-related ML data (weather, terrain, actions) and inserts it into a table in the MS-SQL database.
- **`models.py`**: Connects to the database to load data and train 10 different Machine Learning models (using Scikit-Learn Logistic Regression and Random Forests) for various prediction tasks.
- **`test_odbc.py`**: A utility script that checks whether the Microsoft ODBC Driver for SQL Server is installed on the host system.

## Sample Output

```text
Verifying MS-SQL Docker container...
Success: Container 'aida2157a-SQL-pgnaawmszydfuzabwixtlmbnainwxztt' is already running.
Initiating Data Generation...
[01:41:29] Table 'Wildfire_ML_Training_Data' already exists and overwrite=False. Aborting data generation.
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