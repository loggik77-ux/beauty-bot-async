# crud.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta, date
from typing import List
from models import Appointment, Client, Reminder, ReminderType, ReminderStatus, Salon, AppointmentStatus
from schemas import AppointmentCreate

async def get_free_slots(session: AsyncSession, salon_id: int, date: date, duration_min: int = 60) -> List[datetime]:
    salon = await session.get(Salon, salon_id)
    if not salon:
        return []

    weekday = date.strftime("%A").lower()
    if weekday not in salon.working_hours:
        return []

    open_str, close_str = salon.working_hours[weekday]
    day_start = datetime.combine(date, datetime.strptime(open_str, "%H:%M").time())
    day_end = datetime.combine(date, datetime.strptime(close_str, "%H:%M").time())

    # Получаем все записи, которые пересекаются с рабочим днем
    # (начинаются до конца дня и заканчиваются после начала дня)
    statement = select(Appointment).where(
        Appointment.salon_id == salon_id,
        Appointment.start_at < day_end,
        Appointment.end_at > day_start,
        Appointment.status != AppointmentStatus.cancelled
    )
    busy = (await session.exec(statement)).all()

    current = day_start
    step = timedelta(minutes=30)
    duration = timedelta(minutes=duration_min)
    free: List[datetime] = []

    while current + duration <= day_end:
        slot_end = current + duration
        # Проверяем, что слот не пересекается ни с одной занятой записью
        # Два интервала пересекаются, если: slot_start < busy_end AND slot_end > busy_start
        is_free = not any(
            current < b.end_at and slot_end > b.start_at
            for b in busy
        )
        if is_free:
            free.append(current)
        current += step

    return free

async def create_appointment(session: AsyncSession, appointment_in: AppointmentCreate) -> Appointment:
    client = await session.get(Client, appointment_in.client_tg_id)
    if not client:
        client = Client(tg_id=appointment_in.client_tg_id)
        session.add(client)
        await session.flush()  # Нужно для foreign key constraint

    free = await get_free_slots(
        session=session,
        salon_id=appointment_in.salon_id,
        date=appointment_in.start_at.date(),
        duration_min=appointment_in.duration_min,
    )
    if appointment_in.start_at not in free:
        raise ValueError("Время занято или вне рабочих часов")

    appointment = Appointment(
        salon_id=appointment_in.salon_id,
        client_tg_id=appointment_in.client_tg_id,
        service_name=appointment_in.service_name,
        start_at=appointment_in.start_at,
        end_at=appointment_in.start_at + timedelta(minutes=appointment_in.duration_min),
        status=AppointmentStatus.confirmed,
    )
    session.add(appointment)
    await session.flush()

    session.add_all([
        Reminder(appointment_id=appointment.id, client_tg_id=appointment_in.client_tg_id,
                 remind_at=appointment_in.start_at - timedelta(hours=24), type=ReminderType.h24),
        Reminder(appointment_id=appointment.id, client_tg_id=appointment_in.client_tg_id,
                 remind_at=appointment_in.start_at - timedelta(hours=1), type=ReminderType.h1),
    ])

    await session.commit()
    await session.refresh(appointment)
    return appointment