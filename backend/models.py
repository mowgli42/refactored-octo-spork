from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class FlightEvent(Base):
    __tablename__ = "flight_events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)
    
    # Status tracking
    import_status = Column(String, default="Pending")
    parse_status = Column(String, default="Pending")
    analysis_status = Column(String, default="Pending")

    files = relationship("DataFile", back_populates="event")

class DataFile(Base):
    __tablename__ = "data_files"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("flight_events.id"))
    filename = Column(String)
    filepath = Column(String)
    filetype = Column(String) # e.g. "flight_log", "video", "telemetry"
    
    event = relationship("FlightEvent", back_populates="files")
