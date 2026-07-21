import pandas as pd
import numpy as np
import os
from datetime import datetime
import uuid

CACHE_DIR = "backend/cache"

def process_file(source_url: str, filetype: str) -> str:
    """
    Process flight test data file.
    Supports local Parquet, CSV, HDF5 files or generates realistic mock aircraft telemetry.
    Always caches as efficient Parquet for downstream analysis and plotting.
    """
    print(f"Processing {source_url} of type {filetype}...")
    
    df = None
    
    # Try to load real data if local file exists
    if os.path.exists(source_url):
        lower_url = source_url.lower()
        try:
            if lower_url.endswith('.parquet'):
                df = pd.read_parquet(source_url, engine='pyarrow')
                print(f"Loaded real Parquet data with {len(df)} rows and columns: {list(df.columns)[:10]}...")
            elif lower_url.endswith('.csv'):
                df = pd.read_csv(source_url)
                print(f"Loaded CSV data with {len(df)} rows")
            elif lower_url.endswith(('.h5', '.hdf5', '.hdf')):
                df = pd.read_hdf(source_url)
                print(f"Loaded HDF5 data with {len(df)} rows")
        except Exception as e:
            print(f"Failed to load real file {source_url}: {e}. Falling back to mock data.")
            df = None
    
    if df is None:
        # Generate realistic mock flight test telemetry data (time series)
        n_points = 8000  # ~13+ minutes at 10Hz
        # High resolution time index
        base_time = datetime.now().replace(microsecond=0)
        timestamps = pd.date_range(start=base_time, periods=n_points, freq='100ms')
        
        t = np.linspace(0, 2 * np.pi * 3, n_points)  # ~3 cycles for maneuvers
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'altitude_ft': 15000 + np.cumsum(np.random.randn(n_points) * 8) + 2000 * np.sin(t * 0.3),
            'airspeed_kt': np.clip(280 + np.random.randn(n_points) * 12 + 30 * np.sin(t), 180, 380),
            'vertical_speed_fpm': np.random.randn(n_points) * 250 + 500 * np.sin(t * 1.5),
            'pitch_deg': np.clip(2.5 * np.sin(t * 0.8) + np.random.randn(n_points) * 0.8, -15, 20),
            'roll_deg': np.clip(5 * np.sin(t * 1.2) + np.random.randn(n_points) * 1.5, -35, 35),
            'heading_deg': (np.linspace(90, 450, n_points) + np.random.randn(n_points) * 0.5) % 360,
            'aoa_deg': np.clip(4 + 2 * np.sin(t * 0.6) + np.random.randn(n_points) * 0.3, 0, 12),
            'g_force': np.clip(1.0 + 0.3 * np.sin(t * 2) + np.random.randn(n_points) * 0.1, 0.5, 2.5)
        })
        print("Generated realistic mock aircraft flight test telemetry.")
    
    # Ensure we have a usable timestamp column
    if 'timestamp' not in df.columns:
        df.insert(0, 'timestamp', pd.date_range(start=datetime.now(), periods=len(df), freq='S'))
    
    # Normalize timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Save as Parquet (efficient, columnar, great for large flight test datasets and D3 viz)
    unique_id = str(uuid.uuid4())
    pq_filename = f"{unique_id}.parquet"
    pq_path = os.path.join(CACHE_DIR, pq_filename)
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    df.to_parquet(pq_path, engine='pyarrow', compression='snappy', index=False)
    
    print(f"Cached processed flight data to {pq_path} ({len(df)} rows)")
    
    return pq_path

def get_data_frame(processed_path: str) -> pd.DataFrame:
    """
    Retrieve DataFrame from cached Parquet (or legacy H5) file.
    """
    if not os.path.exists(processed_path):
        raise FileNotFoundError(f"Cached file {processed_path} not found.")
    
    if processed_path.lower().endswith('.parquet'):
        return pd.read_parquet(processed_path, engine='pyarrow')
    else:
        # Legacy support
        return pd.read_hdf(processed_path, key='flight_data')
