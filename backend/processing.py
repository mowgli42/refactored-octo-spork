import pandas as pd
import numpy as np
import os
from datetime import datetime
import uuid

CACHE_DIR = "backend/cache"

def process_file(source_url: str, filetype: str) -> str:
    """
    Mock parser that takes a source URL, generates/reads data, 
    and saves it as an H5 file.
    """
    
    # In a real scenario, we would download the file from source_url if it's http,
    # or read it directly if it's local. 
    # For now, we'll generate mock data to simulate parsing.
    
    print(f"Processing {source_url} of type {filetype}...")
    
    # Mock Flight Data Generation
    # Create a time series
    dates = pd.date_range(start=datetime.now(), periods=1000, freq='S')
    
    # Create some mock telemetry parameters
    df = pd.DataFrame({
        'timestamp': dates,
        'altitude': np.cumsum(np.random.randn(1000)) + 10000,
        'airspeed': np.random.normal(250, 10, 1000),
        'vertical_speed': np.random.normal(0, 5, 1000),
        'latitude': np.linspace(34.0, 34.1, 1000),
        'longitude': np.linspace(-118.0, -117.9, 1000)
    })
    
    # Generate a unique filename for the H5 cache
    unique_id = str(uuid.uuid4())
    h5_filename = f"{unique_id}.h5"
    h5_path = os.path.join(CACHE_DIR, h5_filename)
    
    # Ensure directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Save to HDF5
    # using 'table' format allows for querying
    df.to_hdf(h5_path, key='flight_data', mode='w', format='table')
    
    print(f"Saved processed data to {h5_path}")
    
    return h5_path

def get_data_frame(h5_path: str) -> pd.DataFrame:
    """
    Retrieve DataFrame from H5 file.
    """
    if not os.path.exists(h5_path):
        raise FileNotFoundError(f"Cached file {h5_path} not found.")
        
    return pd.read_hdf(h5_path, key='flight_data')
