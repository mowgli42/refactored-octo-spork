from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DataFileBase(BaseModel):
    filename: str
    source_url: str
    filetype: str

class DataFileCreate(DataFileBase):
    pass

class DataFile(DataFileBase):
    id: int
    event_id: int
    processed_file_path: Optional[str] = None

    class Config:
        from_attributes = True

class FlightEventBase(BaseModel):
    name: str
    description: Optional[str] = None
    import_status: Optional[str] = "Pending"
    parse_status: Optional[str] = "Pending"
    analysis_status: Optional[str] = "Pending"

class FlightEventCreate(FlightEventBase):
    pass

class FlightEvent(FlightEventBase):
    id: int
    date: datetime
    files: List[DataFile] = []

    class Config:
        from_attributes = True
