# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List

class AppointmentCreate(BaseModel):
    salon_id: int
    client_tg_id: int
    service_name: str
    start_at: datetime
    duration_min: int = 60

class AppointmentOut(BaseModel):
    id: int
    salon_id: int
    client_tg_id: int
    service_name: str
    start_at: datetime
    end_at: datetime
    status: str

    class Config:
        from_attributes = True

class FreeSlotsResponse(BaseModel):
    slots: List[datetime]