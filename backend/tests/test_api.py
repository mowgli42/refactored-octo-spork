import pytest
import os
import pandas as pd
import time
from backend.models import FlightEvent, DataFile

def test_create_event(client):
    response = client.post(
        "/events/",
        json={"name": "Test Flight 1", "description": "A test flight event"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Flight 1"
    assert "id" in data
    assert data["import_status"] == "Pending"

def test_read_events(client):
    # Create an event
    client.post("/events/", json={"name": "Event A"})
    client.post("/events/", json={"name": "Event B"})

    response = client.get("/events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Event A"
    assert data[1]["name"] == "Event B"

def test_file_registration_and_processing(client):
    # 1. Create Event
    resp_event = client.post("/events/", json={"name": "Processing Test Flight"})
    event_id = resp_event.json()["id"]

    # 2. Register File (triggers processing)
    file_payload = {
        "filename": "test_log.csv",
        "source_url": "http://example.com/data/test_log.csv",
        "filetype": "flight_log"
    }
    resp_file = client.post(f"/events/{event_id}/files/", json=file_payload)
    assert resp_file.status_code == 200
    file_data = resp_file.json()
    assert file_data["filename"] == "test_log.csv"
    
    # 3. Wait/Poll for processing
    # Since we patched SessionLocal, the background task shares the db_session.
    # However, because TestClient/Starlette runs background tasks *after* the request,
    # and we are in the same process, it should execute.
    
    # We might need to refresh the event from the API
    for _ in range(5):
        resp_event_updated = client.get(f"/events/{event_id}")
        event_data = resp_event_updated.json()
        if event_data["parse_status"] == "Complete":
            break
        time.sleep(0.1)
    
    assert event_data["parse_status"] == "Complete"
    
    # 4. Verify Parquet cache
    assert len(event_data["files"]) == 1
    file_id = event_data["files"][0]["id"]
    processed_path = event_data["files"][0]["processed_file_path"]
    assert processed_path is not None
    assert processed_path.endswith(".parquet")
    assert os.path.exists(processed_path)

    # 5. Verify Parquet content
    df = pd.read_parquet(processed_path, engine="pyarrow")
    assert not df.empty
    assert "altitude_ft" in df.columns
    assert len(df) == 8000

    # 6. Verify data API for D3 plot
    resp_data = client.get(f"/files/{file_id}/data?limit=100")
    assert resp_data.status_code == 200
    payload = resp_data.json()
    assert payload["file_id"] == file_id
    assert "timestamp" in payload["columns"]
    assert len(payload["data"]) <= 100

    # Cleanup Parquet cache
    if os.path.exists(processed_path):
        os.remove(processed_path)
