#!/usr/bin/env python3
"""
Rider Simulator
Simulates a live Zomato rider traversing Patiala, sending GPS positions every 2 seconds.
"""
import time
import uuid
import random
import requests
from datetime import datetime, timezone

# Patiala roughly bounded
LAT_MIN, LAT_MAX = 30.3300, 30.3700
LNG_MIN, LNG_MAX = 76.3600, 76.4200

WEBHOOK_URL = "http://localhost:8000/api/webhook/zomato"

def get_random_coord():
    return random.uniform(LAT_MIN, LAT_MAX), random.uniform(LNG_MIN, LNG_MAX)

def interpolate(start, end, steps):
    lat_step = (end[0] - start[0]) / steps
    lng_step = (end[1] - start[1]) / steps
    return [(start[0] + lat_step * i, start[1] + lng_step * i) for i in range(steps + 1)]

def main():
    order_id = f"ZOM-{uuid.uuid4().hex[:6].upper()}"
    print(f"=== Sentinel Logistics Rider Simulator ===")
    print(f"Assigning Order ID : {order_id}")
    
    start = get_random_coord()
    end = get_random_coord()
    num_steps = random.randint(10, 15)
    
    path = interpolate(start, end, num_steps)
    
    print(f"Origin      : {start}")
    print(f"Destination : {end}")
    print(f"Steps calc'd: {num_steps}")
    print("------------------------------------------\n")
    
    for i, (lat, lng) in enumerate(path):
        payload = {
            "order_id": order_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat": lat,
            "lng": lng,
            "delivery_address": "Simulated Live Destination"
        }
        
        try:
            res = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            if res.status_code == 200:
                print(f"[RIDER] Step {i+1}/{num_steps+1} | Location UPSERT: [{lat:.5f}, {lng:.5f}]")
            else:
                print(f"[RIDER][ERROR] Failed to upsert. Status Code: {res.status_code}")
        except Exception as e:
            print(f"[RIDER][ERROR] Connection Error: {e}")
            
        time.sleep(2.0)

    print("\n[RIDER] Destination Reached.")

if __name__ == "__main__":
    main()
