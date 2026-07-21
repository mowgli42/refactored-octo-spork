from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

from . import crud, models, schemas, processing
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Test Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. In prod, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events/", response_model=schemas.FlightEvent)
def create_event(event: schemas.FlightEventCreate, db: Session = Depends(get_db)):
    return crud.create_flight_event(db=db, event=event)

@app.get("/events/", response_model=List[schemas.FlightEvent])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_flight_events(db, skip=skip, limit=limit)
    return events

@app.get("/events/{event_id}", response_model=schemas.FlightEvent)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_flight_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

def process_file_task(file_id: int, event_id: int, source_url: str, filetype: str):
    # Create a new session for the background task
    db = SessionLocal()
    try:
        # Update status to processing
        crud.update_event_status(db, event_id, "parse", "Processing")
        
        # Run processing
        processed_path = processing.process_file(source_url, filetype)
        
        # Save result path
        crud.update_file_processed_path(db, file_id, processed_path)
        
        # Update status to complete
        crud.update_event_status(db, event_id, "parse", "Complete")
        crud.update_event_status(db, event_id, "analysis", "Ready")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        crud.update_event_status(db, event_id, "parse", "Error")
    finally:
        db.close()

@app.post("/events/{event_id}/files/", response_model=schemas.DataFile)
def create_file_for_event(
    event_id: int, 
    file: schemas.DataFileCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Register file
    db_file = crud.create_event_file(db=db, file=file, event_id=event_id)
    
    # Update event status
    crud.update_event_status(db, event_id, "import", "Complete")
    
    # Trigger processing in background
    background_tasks.add_task(process_file_task, db_file.id, event_id, db_file.source_url, db_file.filetype)
    
    return db_file

@app.get("/files/{file_id}/data")
def get_file_data(
    file_id: int, 
    limit: int = 3000,
    columns: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return (downsampled) flight data for D3.js visualization."""
    db_file = crud.get_data_file(db, file_id)
    if not db_file or not db_file.processed_file_path:
        raise HTTPException(status_code=404, detail="File not found or not yet processed")
    
    try:
        df = processing.get_data_frame(db_file.processed_file_path)
        
        # Select specific columns if requested
        if columns:
            requested = [c.strip() for c in columns.split(",") if c.strip()]
            available = [c for c in requested if c in df.columns]
            if available:
                keep = available
                if "timestamp" in df.columns and "timestamp" not in keep:
                    keep = ["timestamp"] + keep
                df = df[keep]
        
        # Downsample for frontend performance (D3 handles thousands well)
        if len(df) > limit:
            step = max(1, len(df) // limit)
            df = df.iloc[::step].copy()
        
        # Prepare timestamp for JSON (ISO format)
        if "timestamp" in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                df["timestamp"] = df["timestamp"].astype(str)
        
        return {
            "file_id": file_id,
            "filename": db_file.filename,
            "row_count": len(df),
            "total_rows_original": len(processing.get_data_frame(db_file.processed_file_path)),
            "columns": list(df.columns),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

@app.patch("/events/{event_id}/status", response_model=schemas.FlightEvent)
def update_status(
    event_id: int, 
    status_type: str, 
    status: str, 
    db: Session = Depends(get_db)
):
    valid_types = ["import", "parse", "analysis"]
    if status_type not in valid_types:
         raise HTTPException(status_code=400, detail="Invalid status type")
         
    updated_event = crud.update_event_status(db, event_id, status_type, status)
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@app.get("/")
def read_root():
    return {"message": "Welcome to Flight Test Dashboard API - now with Parquet + D3 ready!"}
