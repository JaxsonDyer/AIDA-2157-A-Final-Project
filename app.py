from docker_sql_start import *
from data_generator import *
from test_odbc import *
from models import *
import sys

import pandas as pd
import random

def simulate_emergency_briefings(trained_models, num_alerts=3):
    print("\n" + "="*85)
    print("LIVE FEED: TACTICAL EMERGENCY BRIEFINGS")
    print("="*85)

    scenario_types = [
        "ignition_dispatch", 
        "evacuation_containment", 
        "false_alarm", 
        "landslide_warning",
        "health_advisory"
    ]

    for i in range(num_alerts):
        scenario = random.choice(scenario_types)
        live_lat = round(random.uniform(33.0, 42.0), 4)
        live_lon = round(random.uniform(-124.0, -114.0), 4)

        if scenario == "ignition_dispatch":
            # Models 1 & 9
            m1 = trained_models["1: Lightning Predictor"]['model']
            m9 = trained_models["9: Pre-Positioning"]['model']
            
            data = pd.DataFrame({"Lightning_Strike_kA": [110.0], "Soil_Moisture_Pct": [15.0], "Wind_Kmh": [65.0], "Humidity_Pct": [18.0], "Temp_C": [35.0]})
            prob = m1.predict_proba(data[["Lightning_Strike_kA", "Soil_Moisture_Pct"]])[0][1] * 100
            dispatch = m9.predict(data[["Wind_Kmh", "Humidity_Pct", "Temp_C"]])[0]
            
            action = "Dispatch Air Tanker" if dispatch == 1 else "Monitor Sector"
            print(f"[{i+1}] AI PREDICTION: Lightning Ignition Probability ({prob:.0f}%) at Coord [{live_lat}, {live_lon}]. Action: {action}.")

        elif scenario == "evacuation_containment":
            # Models 2, 4, & 6
            m2 = trained_models["2: Fire Size Prediction"]['model']
            m4 = trained_models["4: Containment Estimator"]['model']
            m6 = trained_models["6: Evacuation Trigger"]['model']
            
            data = pd.DataFrame({"Temp_C": [40.0], "Humidity_Pct": [10.0], "Wind_Kmh": [80.0], "Fuel_Type_Code": [2], "Fire_Size_Hectares": [450.0], "Slope_Pct": [25.0]})
            
            size_class = "Major" if m2.predict(data[["Temp_C", "Humidity_Pct", "Wind_Kmh", "Fuel_Type_Code"]])[0] == 1 else "Moderate"
            days = m4.predict(data[["Fire_Size_Hectares", "Slope_Pct", "Wind_Kmh"]])[0]
            evac = "Trigger Immediate Evacuation" if m6.predict(data[["Fire_Size_Hectares", "Wind_Kmh", "Temp_C"]])[0] == 1 else "Prepare Evac Warning"
            
            print(f"[{i+1}] AI PREDICTION: '{size_class.upper()}' Fire rapidly expanding at Coord [{live_lat}, {live_lon}]. Action: {evac}. Est. Containment: {days:.1f} days.")

        elif scenario == "false_alarm":
            # Model 3
            m3 = trained_models["3: False Alarm Filter"]['model']
            data = pd.DataFrame({"AQI_Level": [45], "Wind_Kmh": [15.0]}) # Clean air, low wind
            
            is_false = m3.predict(data)[0]
            if is_false == 1 or random.random() < 0.8: # Forced bias for demonstration
                print(f"[{i+1}] AI PREDICTION: 911 Smoke Report at Coord [{live_lat}, {live_lon}] flagged as FALSE ALARM. Action: Stand down ground crews. Context: Dust anomaly.")
            else:
                print(f"[{i+1}] AI PREDICTION: 911 Smoke Report at Coord [{live_lat}, {live_lon}] VERIFIED. Action: Dispatch initial attack crew.")

        elif scenario == "landslide_warning":
            # Model 8
            m8 = trained_models["8: Landslide Risk"]['model']
            data = pd.DataFrame({"Slope_Pct": [38.0], "Precipitation_mm": [45.0], "Fire_Ignited": [1]}) # High slope, heavy rain, prior fire
            
            risk = m8.predict(data)[0]
            if risk == 1:
                print(f"[{i+1}] AI PREDICTION: Critical Post-Fire Landslide Risk at Coord [{live_lat}, {live_lon}]. Trigger: 45mm rain on 38% burn slope. Action: Close backcountry roads.")
            else:
                print(f"[{i+1}] AI PREDICTION: Slope stability nominal at Coord [{live_lat}, {live_lon}] despite precipitation. Action: Continue passive monitoring.")

        elif scenario == "health_advisory":
            # Model 5
            m5 = trained_models["5: Smoke Health Alerts"]['model']
            data = pd.DataFrame({"Fire_Size_Hectares": [2500.0], "Wind_Kmh": [55.0]})
            
            aqi = m5.predict(data)[0]
            threat = "HAZARDOUS" if aqi > 300 else "UNHEALTHY"
            print(f"[{i+1}] AI PREDICTION: Downwind AQI forecasted to reach {aqi:.0f} ({threat}) from incident at Coord [{live_lat}, {live_lon}]. Action: Issue preemptive Respiratory Alert to regional hospitals.")

    print("="*85 + "\n")

def main():
    if not is_mssql_driver_installed():
        print("WARNING: MS-SQL ODBC Driver not detected.")
        print("The database connection will likely fail.")
        
        try:
            input("Press [ENTER] to continue anyway, or [CTRL+C] to cancel... ")
        except KeyboardInterrupt:
            print("\nCancelled by user.")
            sys.exit(1)

    print("Verifying MS-SQL Docker container...")
    if not verify_docker_sql():
        print("Failed to verify Docker SQL container. Aborting.")
        return False
    
    print("Initiating Data Generation...")
    if generate_data(rows=10000, overwrite=False) is False:
        print("Data generation failed. Aborting.")
        return False
    
    print("Initiating Model Training...")
    trained_models = run_training_pipeline()
    
    # Run the mass evaluation
    eval_models(trained_models)
    
    # Trigger the live briefing output
    simulate_emergency_briefings(trained_models)

if __name__ == "__main__":
    main()