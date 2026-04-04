import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import urllib.parse
from sqlalchemy import inspect
from db import get_db_engine

def _generate_synthetic_dataframe(num_rows):
    """Internal helper function to generate the flattened ML dataset."""
    print(f"Generating {num_rows} rows of synthetic ML data in memory...")
    np.random.seed(42)
    random.seed(42)
    
    start_date = datetime.now() - timedelta(days=365*5)
    dates = [start_date + timedelta(days=random.randint(0, 365*5)) for _ in range(num_rows)]
    
    latitudes = np.random.uniform(33.0, 42.0, num_rows).round(4)
    longitudes = np.random.uniform(-124.0, -114.0, num_rows).round(4)
    fuel_types = np.random.choice(['Pine Forest', 'Grassland', 'Chaparral', 'Mixed Hardwood'], num_rows, p=[0.35, 0.35, 0.20, 0.10])
    slopes = np.random.uniform(0, 45, num_rows).round(1)
    soil_moisture = np.random.uniform(5, 60, num_rows).round(1)
    
    temps = np.random.normal(25, 10, num_rows).round(1)
    humidities = np.clip(np.random.normal(40, 20, num_rows), 5, 100).round(1)
    wind_speeds = np.clip(np.random.normal(20, 15, num_rows), 0, 120).round(1)
    precip_mm = np.where(np.random.rand(num_rows) < 0.2, np.random.uniform(1, 50, num_rows), 0).round(1)
    
    lightning_intensity = np.zeros(num_rows)
    fire_ignited = np.zeros(num_rows, dtype=int)
    fire_class = ["None"] * num_rows
    fire_size_ha = np.zeros(num_rows)
    days_to_contain = np.zeros(num_rows)
    is_false_alarm = np.zeros(num_rows, dtype=int)
    aqi = np.random.randint(10, 50, num_rows)
    evac_trigger = np.zeros(num_rows, dtype=int)
    road_closure = np.zeros(num_rows, dtype=int)
    landslide_risk = np.zeros(num_rows, dtype=int)
    dispatch_air_tanker = np.zeros(num_rows, dtype=int)
    powerline_risk = np.zeros(num_rows, dtype=int)

    for i in range(num_rows):
        if random.random() < 0.3:
            lightning_intensity[i] = round(random.uniform(10, 150), 1)
            if lightning_intensity[i] > 70 and soil_moisture[i] < 20:
                fire_ignited[i] = 1

        is_pine = (fuel_types[i] == 'Pine Forest')
        is_dry = (humidities[i] < 25.0)
        is_windy = (wind_speeds[i] > 40.0)
        
        base_ignition = 0.02
        if is_dry and is_windy: base_ignition += 0.15
        if is_pine: base_ignition += 0.05
        
        if fire_ignited[i] == 1 or random.random() < base_ignition:
            fire_ignited[i] = 1
            if is_pine and is_dry and is_windy:
                fire_class[i] = "Major"
                fire_size_ha[i] = round(random.uniform(101.0, 5000.0), 1)
                days_to_contain[i] = random.randint(14, 45)
            elif is_dry or is_windy:
                fire_class[i] = "Moderate"
                fire_size_ha[i] = round(random.uniform(20.0, 100.0), 1)
                days_to_contain[i] = random.randint(4, 13)
            else:
                fire_class[i] = "Minor"
                fire_size_ha[i] = round(random.uniform(0.1, 19.9), 1)
                days_to_contain[i] = random.randint(1, 3)
                
            aqi[i] = int(min(500, max(50, (fire_size_ha[i] * 0.5) + wind_speeds[i])) )
            
            if fire_class[i] in ["Major", "Moderate"]:
                evac_trigger[i] = 1
                road_closure[i] = 1
        
        if fire_ignited[i] == 0 and random.random() < 0.05:
            is_false_alarm[i] = 1
            
        if slopes[i] > 25.0 and precip_mm[i] > 15.0 and random.random() < 0.1:
            landslide_risk[i] = 1
            
        if wind_speeds[i] > 50.0 and humidities[i] < 15.0:
            dispatch_air_tanker[i] = 1
            
        if is_pine and is_dry and slopes[i] > 15.0:
            powerline_risk[i] = 1

    return pd.DataFrame({
        'Date': dates, 'Latitude': latitudes, 'Longitude': longitudes, 'Fuel_Type': fuel_types,
        'Slope_Pct': slopes, 'Soil_Moisture_Pct': soil_moisture, 'Temp_C': temps,
        'Humidity_Pct': humidities, 'Wind_Kmh': wind_speeds, 'Precipitation_mm': precip_mm,
        'Lightning_Strike_kA': lightning_intensity, 'Fire_Ignited': fire_ignited,
        'Fire_Classification': fire_class, 'Fire_Size_Hectares': fire_size_ha,
        'Days_to_Contain': days_to_contain, 'Is_False_Alarm': is_false_alarm,
        'AQI_Level': aqi, 'Evac_Triggered': evac_trigger, 'Road_Closure_Flag': road_closure,
        'Landslide_Risk_Flag': landslide_risk, 'Dispatch_Air_Tanker': dispatch_air_tanker,
        'Powerline_Risk_Flag': powerline_risk
    })

def generate_data(rows=10000, overwrite=True):
    """
    Generates synthetic wildfire ML data and inserts it into an MS-SQL Docker container.
    """
    table_name = "Wildfire_ML_Training_Data"
    
    try:
        engine = get_db_engine()
        
        # --- Check for existing table if overwrite is False ---
        if not overwrite:
            inspector = inspect(engine)
            if inspector.has_table(table_name):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Table '{table_name}' already exists and overwrite=False. Aborting data generation.")
                return # Exit gracefully without making changes

        # --- Generate Data ---
        df = _generate_synthetic_dataframe(rows)
        
        # --- Write to SQL ---
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to MS-SQL and writing data...")
        
        # if_exists='replace' will drop the table if it exists and recreate it
        # if_exists='append' will add to it (we use 'replace' because overwrite=True means wipe and rewrite)
        sql_behavior = 'replace' if overwrite else 'append'
        
        df.to_sql(
            name=table_name, 
            con=engine, 
            if_exists=sql_behavior, 
            index=False,
            chunksize=1000 # Breaks insertion into batches to prevent memory overload
        )
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Success! {len(df)} rows written to table: '{table_name}'.")

    except Exception as e:
        print(f"Database Connection or Insertion Failed: {e}")


# --- Test Execution ---
if __name__ == "__main__":
    # Test 1: Generate and overwrite
    print("--- Test 1: Overwrite = True ---")
    generate_data(rows=10000, overwrite=True)
    
    # Test 2: Try to write again without overwriting (Should abort safely)
    print("\n--- Test 2: Overwrite = False ---")
    generate_data(rows=10000, overwrite=False)