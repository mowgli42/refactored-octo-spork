from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
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

@app.post("/events/{event_id}/files/", response_model=schemas.DataFile)
def create_file_for_event(
    event_id: int, file: schemas.DataFileCreate, db: Session = Depends(get_db)
):
    return crud.create_event_file(db=db, file=file, event_id=event_id)

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
    return {"message": "Welcome to Flight Test Dashboard API"}
