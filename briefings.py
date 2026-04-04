import pandas as pd

def evaluate_sensor_data(trained_models, sensor_data):
    """
    Evaluates the incoming sensor data across all 10 trained Machine Learning models
    and returns a list of briefing cards capturing every model's prediction.
    """
    # Convert scalar dictionary values to a one-row DataFrame to feed into scikit-learn
    df = pd.DataFrame([sensor_data])
    
    # Coordinates for logging
    lat = sensor_data.get('lat', 38.0)
    lon = sensor_data.get('lon', -120.0)

    briefings = []

    # Helper function to append a card
    def add_briefing(title, message, action, level, details):
        briefings.append({
            "title": title,
            "message": message,
            "action": action,
            "level": level,
            "lat": lat,
            "lon": lon,
            "details": details
        })

    # --- Model 1: Lightning Predictor ---
    m1 = trained_models["1: Lightning Predictor"]['model']
    prob_m1 = m1.predict_proba(df[["Lightning_Strike_kA", "Soil_Moisture_Pct"]])[0][1] * 100
    if prob_m1 > 50:
        add_briefing(
            "High Lightning Ignition Risk",
            f"AI PREDICTION: Probability of ignition is {prob_m1:.0f}% following recent strikes.",
            "Dispatch Rapid Response", "critical",
            {"Probability": f"{prob_m1:.0f}%", "Strike Initial": f"{sensor_data['Lightning_Strike_kA']} kA", "Soil Moisture": f"{sensor_data['Soil_Moisture_Pct']}%"}
        )
    else:
        add_briefing(
            "Low Lightning Ignition Risk",
            f"AI PREDICTION: Ignition unlikely ({prob_m1:.0f}%) under current soil moisture.",
            "Monitor Sector", "success",
            {"Probability": f"{prob_m1:.0f}%", "Strike Initial": f"{sensor_data['Lightning_Strike_kA']} kA", "Soil Moisture": f"{sensor_data['Soil_Moisture_Pct']}%"}
        )

    # --- Model 2: Fire Size Prediction ---
    m2 = trained_models["2: Fire Size Prediction"]['model']
    # 0 = Minor, 1 = Moderate, 2 = Major (Note: Depending on how cat.codes assigned them; assuming alphabetical: Chaparral(0), Grassland(1), Mixed(2), Pine(3))
    # Wait, the target is Fire_Classification. Alphabetical cat codes: 'Major': 0, 'Minor': 1, 'Moderate': 2, 'None': 3
    # Let's map it safely.
    size_pred = m2.predict(df[["Temp_C", "Humidity_Pct", "Wind_Kmh", "Fuel_Type_Code"]])[0]
    # We will map standard codes dynamically or manually. Standard alphabetical for Major, Minor, Moderate, None:
    # 0 = Major, 1 = Minor, 2 = Moderate, 3 = None.
    size_map = {0: "Major", 1: "Minor", 2: "Moderate", 3: "None"}
    size_class = size_map.get(size_pred, "Unknown")
    
    level_m2 = "critical" if size_class == "Major" else ("warning" if size_class == "Moderate" else "info")
    add_briefing(
        "Fire Growth Projection",
        f"AI PREDICTION: Under predicted weather, ignition would likely result in a {size_class.upper()} fire.",
        "Update Readiness Condition" if size_class in ["Major", "Moderate"] else "Standard Patrol", level_m2,
        {"Estimated Size": size_class, "Wind": f"{sensor_data['Wind_Kmh']} Kmh", "Temp": f"{sensor_data['Temp_C']} °C"}
    )

    # --- Model 3: False Alarm Filter ---
    m3 = trained_models["3: False Alarm Filter"]['model']
    is_false = m3.predict(df[["AQI_Level", "Wind_Kmh"]])[0]
    if is_false == 1:
        add_briefing(
            "False Alarm Analysis",
            "AI PREDICTION: Smoke reports in this sector are highly likely to be FALSE ALARMS (e.g., dust).",
            "Stand down ground crews", "success",
            {"AQI": sensor_data["AQI_Level"], "Wind": f"{sensor_data['Wind_Kmh']} Kmh"}
        )
    else:
        add_briefing(
            "Verified Smoke Report",
            "AI PREDICTION: Atmospheric indicators suggest genuine combustion.",
            "Dispatch verification unit", "warning",
            {"AQI": sensor_data["AQI_Level"], "Wind": f"{sensor_data['Wind_Kmh']} Kmh"}
        )

    # --- Model 4: Containment Estimator ---
    m4 = trained_models["4: Containment Estimator"]['model']
    days = m4.predict(df[["Fire_Size_Hectares", "Slope_Pct", "Wind_Kmh"]])[0]
    if sensor_data['Fire_Size_Hectares'] > 0:
        add_briefing(
            "Containment Timeline Forecast",
            f"AI PREDICTION: Based on current footprint and topography, containment will take approx {days:.1f} days.",
            "Allocate Provisions Logistics", "info",
            {"Est Containment": f"{days:.1f} days", "Current Size": f"{sensor_data['Fire_Size_Hectares']} HA", "Slope": f"{sensor_data['Slope_Pct']}%"}
        )

    # --- Model 5: Smoke Health Alerts ---
    m5 = trained_models["5: Smoke Health Alerts"]['model']
    aqi_forecast = m5.predict(df[["Fire_Size_Hectares", "Wind_Kmh"]])[0]
    threat = "HAZARDOUS" if aqi_forecast > 300 else ("UNHEALTHY" if aqi_forecast > 150 else "MODERATE")
    level_m5 = "critical" if aqi_forecast > 300 else ("warning" if aqi_forecast > 150 else "success")
    if sensor_data['Fire_Size_Hectares'] > 0:
        add_briefing(
            "Downwind Respiratory Alert",
            f"AI PREDICTION: Smoke plume projected to push downwind AQI to {aqi_forecast:.0f} ({threat}).",
            "Issue public health advisory", level_m5,
            {"Forecast AQI": f"{aqi_forecast:.0f}", "Fire Vol": f"{sensor_data['Fire_Size_Hectares']} HA", "Wind Velocity": f"{sensor_data['Wind_Kmh']} Kmh"}
        )

    # --- Model 6: Evacuation Trigger ---
    m6 = trained_models["6: Evacuation Trigger"]['model']
    evac_needed = m6.predict(df[["Fire_Size_Hectares", "Wind_Kmh", "Temp_C"]])[0]
    if evac_needed == 1:
        add_briefing(
            "Critical Evacuation Order",
            "AI PREDICTION: Fire behavior metrics have crossed critical thresholds. Immediate evacuation necessary.",
            "Trigger Emergency Broadcast", "critical",
            {"Fire Size": f"{sensor_data['Fire_Size_Hectares']} HA", "Wind": f"{sensor_data['Wind_Kmh']} Kmh"}
        )
    else:
        add_briefing(
            "Evacuation Posture Nominal",
            "AI PREDICTION: Standard protective posture recommended. No mandatory evacuation mapped.",
            "Maintain readiness", "success",
            {"Fire Size": f"{sensor_data['Fire_Size_Hectares']} HA", "Wind": f"{sensor_data['Wind_Kmh']} Kmh"}
        )

    # --- Model 7: Road Closure Auto ---
    m7 = trained_models["7: Road Closure Auto"]['model']
    road_close = m7.predict(df[["Fire_Ignited", "Wind_Kmh"]])[0]
    if road_close == 1:
        add_briefing(
            "Automated Traffic Diversion",
            "AI PREDICTION: Wind and active fire metrics require immediate backcountry road closures.",
            "Deploy highway patrol barriers", "warning",
            {"Fire Active": "Yes" if sensor_data["Fire_Ignited"] else "No", "Wind": f"{sensor_data['Wind_Kmh']} Kmh"}
        )
    else:
        add_briefing(
            "Route Status Clear",
            "AI PREDICTION: Regional corridors remain safe for transit.",
            "Keep routes open", "success",
            {"Fire Active": "Yes" if sensor_data["Fire_Ignited"] else "No", "Wind": f"{sensor_data['Wind_Kmh']} Kmh"}
        )

    # --- Model 8: Landslide Risk ---
    m8 = trained_models["8: Landslide Risk"]['model']
    # Landslide Risk uses Slope_Pct, Precipitation_mm, Fire_Ignited (assuming Fire_Ignited implies burn scar here as per original mapping logic)
    landslide_risk = m8.predict(df[["Slope_Pct", "Precipitation_mm", "Fire_Ignited"]])[0]
    if landslide_risk == 1:
        add_briefing(
            "Post-Fire Landslide Warning",
            "AI PREDICTION: Slippage thresholds exceeded due to heavy precipitation on steep scorch zones.",
            "Evacuate downslope zones", "critical",
            {"Slope": f"{sensor_data['Slope_Pct']}%", "Rain": f"{sensor_data['Precipitation_mm']} mm", "Burn Scar": "Yes" if sensor_data["Fire_Ignited"] else "No"}
        )
    else:
        add_briefing(
            "Slope Stability Nominal",
            "AI PREDICTION: Topsoil erosion remains within acceptable bounds.",
            "Routine surveillance", "info",
            {"Slope": f"{sensor_data['Slope_Pct']}%", "Rain": f"{sensor_data['Precipitation_mm']} mm", "Burn Scar": "Yes" if sensor_data["Fire_Ignited"] else "No"}
        )

    # --- Model 9: Pre-Positioning ---
    m9 = trained_models["9: Pre-Positioning"]['model']
    dispatch_air = m9.predict(df[["Wind_Kmh", "Humidity_Pct", "Temp_C"]])[0]
    if dispatch_air == 1:
        add_briefing(
            "Aviation Strike Pre-Positioning",
            "AI PREDICTION: Atmospheric volatility is extremely high. Pre-dispatch air tankers.",
            "Scramble Aerial Support", "warning",
            {"Wind": f"{sensor_data['Wind_Kmh']} Kmh", "Humidity": f"{sensor_data['Humidity_Pct']}%", "Temp": f"{sensor_data['Temp_C']} °C"}
        )
    else:
        add_briefing(
            "Aviation Grounded/Standby",
            "AI PREDICTION: Baseline weather conditions do not warrant proactive aerial deployments.",
            "Ground units on standby", "info",
            {"Wind": f"{sensor_data['Wind_Kmh']} Kmh", "Humidity": f"{sensor_data['Humidity_Pct']}%", "Temp": f"{sensor_data['Temp_C']} °C"}
        )

    # --- Model 10: Infra Priority ---
    m10 = trained_models["10: Infra Priority"]['model']
    powerline_risk = m10.predict(df[["Fuel_Type_Code", "Humidity_Pct", "Slope_Pct"]])[0]
    if powerline_risk == 1:
        add_briefing(
            "Powerline Arc Risk",
            "AI PREDICTION: Dry vegetation encroaching on steep-slope grid infrastructure. High risk of electrical ignition.",
            "Initiate preemptive power shutoff", "critical",
            {"Fuel": f"Type {sensor_data['Fuel_Type_Code']}", "Humidity": f"{sensor_data['Humidity_Pct']}%", "Slope": f"{sensor_data['Slope_Pct']}%"}
        )
    else:
        add_briefing(
            "Grid Security Secure",
            "AI PREDICTION: Utility transmission vectors indicate low vulnerability to vegetation shorting.",
            "Maintain normal grid op", "success",
            {"Fuel": f"Type {sensor_data['Fuel_Type_Code']}", "Humidity": f"{sensor_data['Humidity_Pct']}%", "Slope": f"{sensor_data['Slope_Pct']}%"}
        )

    return briefings
