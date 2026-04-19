import random
import asyncio
from datetime import datetime

async def enrich_order_data(lat: float, lng: float, timestamp: str) -> dict:
    """
    Simulates external API enrichment (Google Maps Traffic, OpenWeather) 
    and returns enriched environmental metadata.
    """
    
    # Simulate network delay for API calls
    await asyncio.sleep(0.1)

    # 1. OpenWeather API Simulation
    weather_rand = random.random()
    if weather_rand > 0.85:
        weather_condition = "Storm"
    elif weather_rand > 0.60:
        weather_condition = "Rain"
    else:
        weather_condition = "Clear"
        
    # 2. Google Maps Traffic Simulation (0.0 to 1.0)
    # Give storms higher baseline traffic density
    base_traffic = 0.5 if weather_condition == "Storm" else 0.1
    traffic_density = round(min(1.0, base_traffic + random.uniform(0.0, 0.5)), 3)
    
    # 3. Ambient Light calculation
    try:
        # Assuming ISO standard timestamps e.g. "2026-04-19T20:30:00Z"
        # Or safely fallback to current time
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        hour = dt.hour
    except Exception:
        hour = datetime.now().hour
        
    if 6 <= hour <= 18:
        ambient_light = "Daylight"
    else:
        ambient_light = "Night"
        
    return {
        "traffic_density": traffic_density,
        "weather_condition": weather_condition,
        "ambient_light": ambient_light,
        "hour_of_day": hour
    }
