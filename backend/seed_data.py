#!/usr/bin/env python3
"""
seed_data.py — Populate Sentinel Logistics DB with 10 real Patiala, Punjab locations.

Usage (from the /backend directory with venv active):
    python seed_data.py

Run this AFTER starting the app once so that DB tables exist, OR call
create_db_and_tables() directly below (already handled).
"""

import sys
import os

# Ensure the backend package is importable when run from /backend
sys.path.insert(0, os.path.dirname(__file__))

from app.core.db import create_db_and_tables, engine
from app.models import DeliveryStop
from sqlmodel import Session, select

# ── Real Patiala Locations ────────────────────────────────────────────────────

PATIALA_STOPS = [
    {
        "name": "Thapar University",
        "address": "Bhadson Rd, Adarsh Nagar, Patiala, Punjab 147004",
        "latitude": 30.3519,
        "longitude": 76.3647,
        "status": "pending",
        "area_type": "residential",
    },
    {
        "name": "Urban Estate Phase I",
        "address": "Urban Estate Phase 1, Patiala, Punjab 147002",
        "latitude": 30.3398,
        "longitude": 76.4020,
        "status": "delivered",
        "area_type": "residential",
    },
    {
        "name": "Leela Bhawan Market",
        "address": "Leela Bhawan, Patiala, Punjab 147001",
        "latitude": 30.3398,
        "longitude": 76.3869,
        "status": "pending",
        "area_type": "commercial",
    },
    {
        "name": "Model Town",
        "address": "Model Town, Patiala, Punjab 147001",
        "latitude": 30.3317,
        "longitude": 76.3930,
        "status": "failed",
        "area_type": "residential",
    },
    {
        "name": "Rajindra Hospital",
        "address": "Bhupindra Rd, Patiala, Punjab 147001",
        "latitude": 30.3444,
        "longitude": 76.3866,
        "status": "delivered",
        "area_type": "commercial",
    },
    {
        "name": "Moti Bagh Palace Gate",
        "address": "Moti Bagh, Patiala, Punjab 147001",
        "latitude": 30.3248,
        "longitude": 76.3888,
        "status": "pending",
        "area_type": "residential",
    },
    {
        "name": "Patiala Industrial Focal Point",
        "address": "Industrial Focal Point, Patiala, Punjab 147003",
        "latitude": 30.3627,
        "longitude": 76.4145,
        "status": "pending",
        "area_type": "industrial",
    },
    {
        "name": "Bhupindra Road Hub",
        "address": "Bhupindra Rd, Patiala, Punjab 147001",
        "latitude": 30.3357,
        "longitude": 76.3980,
        "status": "delivered",
        "area_type": "commercial",
    },
    {
        "name": "Sirhind Road Depot",
        "address": "Sirhind Rd, Patiala, Punjab 147001",
        "latitude": 30.3600,
        "longitude": 76.3750,
        "status": "failed",
        "area_type": "industrial",
    },
    {
        "name": "Nabha Gate Market",
        "address": "Nabha Gate, Old City, Patiala, Punjab 147001",
        "latitude": 30.3351,
        "longitude": 76.3840,
        "status": "pending",
        "area_type": "commercial",
    },
]


def seed():
    # Ensure tables exist
    create_db_and_tables()

    with Session(engine) as session:
        # Clear existing stops to avoid duplicates on re-run
        existing = session.exec(select(DeliveryStop)).all()
        for stop in existing:
            session.delete(stop)
        session.commit()
        print(f"[CLEAR] Cleared {len(existing)} existing stop(s).")

        # Insert fresh stops
        for data in PATIALA_STOPS:
            db_stop = DeliveryStop(**data)
            # Native seeding logic to avoid dynamic DB deadlock on startup
            db_stop.traffic_density = 0.2
            db_stop.failure_risk = 0.2
            db_stop.weather_condition = "Clear"
            db_stop.ambient_light = "Daylight"
            db_stop.recommendation = "Active Tracking Mode"
            session.add(db_stop)

        session.commit()
        print(f"[OK] Seeded {len(PATIALA_STOPS)} Patiala delivery stops into the database.\n")

        # Verify
        all_stops = session.exec(select(DeliveryStop)).all()
        for s in all_stops:
            print(f"  #{s.id:2d}  {s.name:<35} [{s.area_type:<12}]  {s.status}")

    print("\n[READY] Database ready. Start the API with: uvicorn main:app --reload")


if __name__ == "__main__":
    seed()
