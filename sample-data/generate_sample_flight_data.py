#!/usr/bin/env python3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
def generate_flight_test_data(num_points: int = 5000, output_dir: str = ".") -> dict:
    np.random.seed(42)
    start_time = datetime(2026, 7, 15, 14, 30, 0)
    timestamps = [start_time + timedelta(seconds=i * 0.1) for i in range(num_points)]
    t = np.linspace(0, 2 * np.pi * 4, num_points)
    data = {
        'timestamp': timestamps,
        'altitude_ft': 15000 + np.cumsum(np.random.randn(num_points) * 5) + 3000 * np.sin(t * 0.2),
        'airspeed_kt': np.clip(280 + np.random.randn(num_points) * 8 + 40 * np.sin(t * 0.5), 200, 380),
        'vertical_speed_fpm': np.random.randn(num_points) * 200 + 800 * np.sin(t * 1.2),
        'pitch_deg': np.clip(1.5 * np.sin(t * 0.7) + np.random.randn(num_points) * 0.6, -12, 15),
        'roll_deg': np.clip(8 * np.sin(t * 1.1) + np.random.randn(num_points) * 1.2, -30, 30),
        'heading_deg': (np.linspace(45, 405, num_points) + np.random.randn(num_points) * 0.3) % 360,
        'aoa_deg': np.clip(3.5 + 2.5 * np.sin(t * 0.6) + np.random.randn(num_points) * 0.4, 0, 14),
        'g_force': np.clip(1.0 + 0.4 * np.sin(t * 1.8) + np.random.randn(num_points) * 0.08, 0.6, 2.8),
        'latitude': 34.05 + np.cumsum(np.random.randn(num_points) * 0.00005),
        'longitude': -118.25 + np.cumsum(np.random.randn(num_points) * 0.00008),
    }
    df = pd.DataFrame(data)
    df['altitude_ft'] = df['altitude_ft'].clip(5000, 35000)
    df['airspeed_kt'] = df['airspeed_kt'].clip(180, 400)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "sample_flight_test_data.csv"), index=False)
    df.to_json(os.path.join(output_dir, "sample_flight_test_data.json"), orient='records', date_format='iso')
    try:
        df.to_parquet(os.path.join(output_dir, "sample_flight_test_data.parquet"), engine='pyarrow', compression='snappy', index=False)
    except:
        pass
    return df
if __name__ == "__main__":
    generate_flight_test_data(num_points=8000, output_dir="sample-data")