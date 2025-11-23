# routers/appointment.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import date
from typing import List
import crud
import schemas
from database import get_session
from models import Appointment, AppointmentStatus

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=schemas.AppointmentOut, status_code=201)
async def create_appointment(
    appointment_in: schemas.AppointmentCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await crud.create_appointment(session=session, appointment_in=appointment_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Обработка других ошибок (например, foreign key constraint)
        raise HTTPException(status_code=400, detail=f"Ошибка при создании записи: {str(e)}")

@router.get("/free-slots/", response_model=schemas.FreeSlotsResponse)
async def free_slots(
    salon_id: int,
    date_str: str,
    duration_min: int = 60,
    session: AsyncSession = Depends(get_session),
):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Формат даты: YYYY-MM-DD")
    
    from models import Salon
    salon = await session.get(Salon, salon_id)
    if not salon:
        raise HTTPException(status_code=404, detail="Салон не найден")
    
    slots = await crud.get_free_slots(session, salon_id, target_date, duration_min)
    return schemas.FreeSlotsResponse(slots=slots)

@router.get("/my/", response_model=List[schemas.AppointmentOut])
async def my_appointments(client_tg_id: int, session: AsyncSession = Depends(get_session)):
    statement = select(Appointment).where(
        Appointment.client_tg_id == client_tg_id,
        Appointment.status != AppointmentStatus.cancelled
    ).order_by(Appointment.start_at.desc())
    result = await session.exec(statement)
    return result.all()

@router.patch("/{appointment_id}/cancel", response_model=schemas.AppointmentOut)
async def cancel_appointment(
    appointment_id: int,
    client_tg_id: int,
    session: AsyncSession = Depends(get_session),
):
    appointment = await session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    if appointment.client_tg_id != client_tg_id:
        raise HTTPException(status_code=403, detail="Это не твоя запись")
    if appointment.status == AppointmentStatus.cancelled:
        raise HTTPException(status_code=400, detail="Запись уже отменена")
    appointment.status = AppointmentStatus.cancelled
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return appointment