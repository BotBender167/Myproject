#!/usr/bin/env python3
"""
generate_historical_data.py — Populate Sentinel Logistics DB with 10,000 synthetic 
historical records within Patiala, Punjab bounds, utilizing the Cyber-Amber schema.

Usage (from the /backend directory with venv active):
    python scripts/generate_historical_data.py
"""

import sys
import os
import random
import uuid

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.db import create_db_and_tables, engine
from app.models import HistoricalDelivery
from sqlmodel import Session, select
from sqlalchemy import delete

# Patiala Bounding Box
LAT_MIN = 30.3100
LAT_MAX = 30.3800
LNG_MIN = 76.3500
LNG_MAX = 76.4300

WEATHER_CONDITIONS = ["Clear", "Clear", "Clear", "Rain", "Rain", "Storm"]

def generate_record():
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lng = random.uniform(LNG_MIN, LNG_MAX)
    
    weather = random.choice(WEATHER_CONDITIONS)
    
    # 0.0 to 1.0 logic
    base_traffic = 0.5 if weather == "Storm" else 0.1
    traffic_level = round(min(1.0, base_traffic + random.uniform(0.0, 0.5)), 3)
    
    # Heuristic for success
    fail_chance = 0.05
    if traffic_level > 0.7:
        fail_chance += 0.2
    if weather == "Storm":
        fail_chance += 0.3
        
    was_successful = random.random() > fail_chance
        
    return HistoricalDelivery(
        stop_id=f"ZMT-{uuid.uuid4().hex[:8].upper()}",
        lat=lat,
        lng=lng,
        weather_at_time=weather,
        traffic_level=traffic_level,
        was_successful=was_successful
    )

def seed_big_data():
    print("Initiating DB Check...")
    create_db_and_tables()

    with Session(engine) as session:
        # Fast delete all existing records
        print("Clearing old HistoricalDelivery records...")
        session.exec(delete(HistoricalDelivery))
        session.commit()
        
        TOTAL_RECORDS = 10000
        BATCH_SIZE = 2500
        
        print(f"Generating {TOTAL_RECORDS} records for Patiala region...")
        records = [generate_record() for _ in range(TOTAL_RECORDS)]
        
        print("Inserting records in batches...")
        for i in range(0, TOTAL_RECORDS, BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            session.add_all(batch)
            session.commit()
            print(f"  -> Inserted {i + len(batch)} / {TOTAL_RECORDS} records")
            
        print("\n[OK] Historical Data Generation Complete!")

if __name__ == "__main__":
    seed_big_data()
