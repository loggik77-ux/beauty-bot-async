# main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from database import engine
from routers import appointment
import logging
# Import models to register them with SQLModel.metadata
from models import Salon, Client, Appointment, Reminder

logger = logging.getLogger(__name__)

app = FastAPI(title="Beauty Bot Async")

app.include_router(appointment.router)

@app.on_event("startup")
async def on_startup():
    """
    Создает таблицы в БД при старте приложения.
    В продакшене лучше использовать миграции Alembic.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database or create tables: {e}")
        logger.warning("Application will continue, but database operations may fail")
        # Не прерываем запуск приложения, если БД недоступна