from sqlalchemy.orm import Session
from . import models, schemas

def get_flight_event(db: Session, event_id: int):
    return db.query(models.FlightEvent).filter(models.FlightEvent.id == event_id).first()

def get_flight_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FlightEvent).offset(skip).limit(limit).all()

def create_flight_event(db: Session, event: schemas.FlightEventCreate):
    db_event = models.FlightEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def create_event_file(db: Session, file: schemas.DataFileCreate, event_id: int):
    db_file = models.DataFile(**file.dict(), event_id=event_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def update_event_status(db: Session, event_id: int, status_type: str, status: str):
    event = get_flight_event(db, event_id)
    if not event:
        return None
    if status_type == "import":
        event.import_status = status
    elif status_type == "parse":
        event.parse_status = status
    elif status_type == "analysis":
        event.analysis_status = status
    db.commit()
    db.refresh(event)
    return event
