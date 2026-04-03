import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib.parse
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error

class WildfireModelTrainer:
    def __init__(self):
        # Database setup
        username = 'sa'
        password = urllib.parse.quote_plus('eKyhH>"UGj]W=bqT|t,VMF?<Qj"%ow£YS[;=!|i]GTjR_GqIpG')
        server = 'localhost'
        database = 'master'
        self.engine = create_engine(f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server")
        self.df = None

    def load_data(self):
        print("Loading data from MS-SQL...")
        self.df = pd.read_sql("SELECT * FROM Wildfire_ML_Training_Data", self.engine)
        
        # Preprocessing: Convert categorical variables to numeric codes
        self.df['Fuel_Type_Code'] = self.df['Fuel_Type'].astype('category').cat.codes
        self.df['Fire_Class_Code'] = self.df['Fire_Classification'].astype('category').cat.codes
        return self.df

    def build_model(self, model_type, features, target):
        X = self.df[features]
        y = self.df[target]
        
        # Split data (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize the correct algorithm
        if model_type == 'LogisticRegression':
            model = LogisticRegression(max_iter=1000)
        elif model_type == 'RandomForestClassifier':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'RandomForestRegressor':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            
        # Train the model
        model.fit(X_train, y_train)
        
        # Bundle the model with its specific test data so the evaluator can use it later
        return {
            'model': model,
            'X_test': X_test,
            'y_test': y_test,
            'type': model_type
        }

def run_training_pipeline():
    trainer = WildfireModelTrainer()
    trainer.load_data()
    
    # Format: (Name, ModelType, [Features], TargetColumn)
    configs = [
        ("1: Lightning Predictor", "LogisticRegression", ["Lightning_Strike_kA", "Soil_Moisture_Pct"], "Fire_Ignited"),
        ("2: Fire Size Prediction", "RandomForestClassifier", ["Temp_C", "Humidity_Pct", "Wind_Kmh", "Fuel_Type_Code"], "Fire_Class_Code"),
        ("3: False Alarm Filter", "LogisticRegression", ["AQI_Level", "Wind_Kmh"], "Is_False_Alarm"),
        ("4: Containment Estimator", "RandomForestRegressor", ["Fire_Size_Hectares", "Slope_Pct", "Wind_Kmh"], "Days_to_Contain"),
        ("5: Smoke Health Alerts", "RandomForestRegressor", ["Fire_Size_Hectares", "Wind_Kmh"], "AQI_Level"),
        ("6: Evacuation Trigger", "RandomForestClassifier", ["Fire_Size_Hectares", "Wind_Kmh", "Temp_C"], "Evac_Triggered"),
        ("7: Road Closure Auto", "LogisticRegression", ["Fire_Ignited", "Wind_Kmh"], "Road_Closure_Flag"),
        ("8: Landslide Risk", "RandomForestClassifier", ["Slope_Pct", "Precipitation_mm", "Fire_Ignited"], "Landslide_Risk_Flag"),
        ("9: Pre-Positioning", "RandomForestClassifier", ["Wind_Kmh", "Humidity_Pct", "Temp_C"], "Dispatch_Air_Tanker"),
        ("10: Infra Priority", "LogisticRegression", ["Fuel_Type_Code", "Humidity_Pct", "Slope_Pct"], "Powerline_Risk_Flag")
    ]
    
    trained_bundle = {}
    print("Training 10 Machine Learning Models...")
    for name, m_type, feats, target in configs:
        trained_bundle[name] = trainer.build_model(m_type, feats, target)
        
    print("Training complete.")
    return trained_bundle

def eval_models(trained_models):
    print("\n" + "="*45)
    print("          MODEL EVALUATION REPORT")
    print("="*45)
    
    for name, package in trained_models.items():
        model = package['model']
        X_test = package['X_test']
        y_test = package['y_test']
        m_type = package['type']
        
        # Generate predictions using the held-out test data
        predictions = model.predict(X_test)
        
        # Calculate the appropriate metric based on the algorithm type
        if m_type == 'LogisticRegression' or m_type == 'RandomForestClassifier':
            score = accuracy_score(y_test, predictions) * 100
            metric_label = "Accuracy"
            score_format = f"{score:.2f}%"
        elif m_type == 'RandomForestRegressor':
            score = np.sqrt(mean_squared_error(y_test, predictions))
            metric_label = "RMSE"
            score_format = f"{score:.2f} units"
            
        # Print formatted output
        print(f"{name.ljust(28)} | {metric_label}: {score_format}")
        
    print("="*45)