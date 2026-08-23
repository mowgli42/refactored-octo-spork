#!/usr/bin/env python3
"""
Generate realistic aircraft flight-test telemetry for the analysis workspace.
Includes continuous performance/attitude/propulsion parameters and discrete
subsystem states (gear, pumps, hydraulics) so time-aligned multi-panel plots
and a map track can be demonstrated.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_flight_test_data(num_points: int = 8000, output_dir: str = ".") -> pd.DataFrame:
    np.random.seed(42)
    start_time = datetime(2026, 7, 15, 14, 30, 0)
    dt = 0.1  # 10 Hz
    timestamps = [start_time + timedelta(seconds=i * dt) for i in range(num_points)]
    t = np.linspace(0, 2 * np.pi * 5, num_points)  # several maneuver cycles

    # --- Continuous performance / navigation ---
    altitude = 15000 + np.cumsum(np.random.randn(num_points) * 4) + 2500 * np.sin(t * 0.15)
    altitude = np.clip(altitude, 8000, 32000)
    airspeed = np.clip(280 + np.random.randn(num_points) * 6 + 35 * np.sin(t * 0.4), 190, 380)
    vs = np.random.randn(num_points) * 180 + 700 * np.sin(t * 1.1)

    # --- Attitude ---
    pitch = np.clip(1.8 * np.sin(t * 0.65) + np.random.randn(num_points) * 0.5, -12, 14)
    roll = np.clip(9 * np.sin(t * 1.05) + np.random.randn(num_points) * 1.0, -35, 35)
    heading = (np.linspace(45, 520, num_points) + np.random.randn(num_points) * 0.25) % 360
    aoa = np.clip(3.2 + 2.2 * np.sin(t * 0.55) + np.random.randn(num_points) * 0.35, 0, 13)
    g = np.clip(1.0 + 0.45 * np.sin(t * 1.7) + np.random.randn(num_points) * 0.07, 0.55, 2.9)

    # --- Position (ground track integrated from heading and airspeed) ---
    hdg_rad = np.deg2rad(heading)
    dist_nm = airspeed * dt / 3600.0
    lat = 34.05 + np.cumsum((dist_nm / 60.0) * np.cos(hdg_rad))
    lon = -118.25 + np.cumsum((dist_nm / 60.0) * np.sin(hdg_rad) / np.cos(np.deg2rad(34.05)))

    # --- Propulsion (throttle-driven) ---
    throttle = 55 + 25 * np.sin(t * 0.22) + np.random.randn(num_points) * 2.5
    throttle = np.clip(throttle, 15, 98)
    engine_rpm = 1800 + (throttle / 100) * 900 + np.random.randn(num_points) * 15
    fuel_flow = 180 + (throttle / 100) * 420 + np.random.randn(num_points) * 8
    oil_pressure = 45 + 0.12 * (engine_rpm - 1800) + np.random.randn(num_points) * 1.2
    oil_pressure = np.clip(oil_pressure, 25, 80)
    hyd_pressure = 3000 + np.random.randn(num_points) * 40 + 80 * np.sin(t * 0.3)
    fuel_qty = 4200 - np.cumsum(fuel_flow * dt / 3600)

    # --- Discrete subsystem states ---
    gear = np.zeros(num_points, dtype=int)
    gear_start = int(num_points * 0.82)
    gear_end = int(num_points * 0.88)
    gear[gear_start:gear_end] = 1          # transition
    gear[gear_end:] = 2                    # down

    fuel_pump = np.ones(num_points, dtype=int)
    oil_pump = np.ones(num_points, dtype=int)
    fuel_pump[int(num_points * 0.35):int(num_points * 0.37)] = 0
    oil_pump[int(num_points * 0.55):int(num_points * 0.56)] = 0

    hyd_ok = np.ones(num_points, dtype=int)
    hyd_ok[int(num_points * 0.62):int(num_points * 0.64)] = 0

    master_caution = ((fuel_pump == 0) | (oil_pump == 0) | (hyd_ok == 0)).astype(int)

    data = {
        "timestamp": timestamps,
        "altitude_ft": altitude,
        "airspeed_kt": airspeed,
        "vertical_speed_fpm": vs,
        "latitude": lat,
        "longitude": lon,
        "pitch_deg": pitch,
        "roll_deg": roll,
        "heading_deg": heading,
        "aoa_deg": aoa,
        "g_force": g,
        "throttle_pct": throttle,
        "engine_rpm": engine_rpm,
        "fuel_flow_pph": fuel_flow,
        "oil_pressure_psi": oil_pressure,
        "hydraulic_pressure_psi": hyd_pressure,
        "fuel_qty_lb": fuel_qty,
        "landing_gear": gear,           # 0=up, 1=transition, 2=down
        "fuel_pump_on": fuel_pump,
        "oil_pump_on": oil_pump,
        "hyd_system_ok": hyd_ok,
        "master_caution": master_caution,
    }

    df = pd.DataFrame(data)

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "sample_flight_test_data.csv")
    json_path = os.path.join(output_dir, "sample_flight_test_data.json")
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", date_format="iso")

    try:
        parquet_path = os.path.join(output_dir, "sample_flight_test_data.parquet")
        df.to_parquet(parquet_path, engine="pyarrow", compression="snappy", index=False)
        print(f"Parquet written: {parquet_path}")
    except Exception as e:
        print(f"Parquet skipped ({e})")

    print(f"Generated {num_points} rows → {csv_path} and {json_path}")
    print("Columns:", list(df.columns))
    return df


if __name__ == "__main__":
    generate_flight_test_data(num_points=8000, output_dir="sample-data")
