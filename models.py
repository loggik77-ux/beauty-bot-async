# models.py
from sqlmodel import SQLModel, Field, JSON
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class AppointmentStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    noshow = "noshow"

class ReminderType(str, Enum):
    h24 = "24h"
    h1 = "1h"

class ReminderStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"

class Salon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    owner_tg_id: int = Field(unique=True)
    address: Optional[str] = None

    working_hours: Dict[str, List[str]] = Field(default={
        "monday": ["10:00", "20:00"],
        "tuesday": ["10:00", "20:00"],
        "wednesday": ["10:00", "20:00"],
        "thursday": ["10:00", "20:00"],
        "friday": ["10:00", "21:00"],
        "saturday": ["10:00", "21:00"],
        "sunday": ["10:00", "18:00"],
    }, sa_type=JSON)

class Client(SQLModel, table=True):
    tg_id: int = Field(primary_key=True)
    name: Optional[str] = None
    phone: Optional[str] = None

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    salon_id: int = Field(foreign_key="salon.id")
    client_tg_id: int = Field(foreign_key="client.tg_id")
    service_name: str
    start_at: datetime = Field(index=True)
    end_at: datetime
    status: AppointmentStatus = Field(default=AppointmentStatus.confirmed)

class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="appointment.id", ondelete="CASCADE")
    client_tg_id: int
    remind_at: datetime = Field(index=True)
    type: ReminderType
    status: ReminderStatus = Field(default=ReminderStatus.pending)