# database.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please create a .env file with DATABASE_URL=postgresql+psycopg.async://user:password@host:port/database"
    )

# Railway предоставляет DATABASE_URL в формате postgresql://
# Для async SQLAlchemy с psycopg3 нужен формат postgresql+psycopg.async://
if DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg.async://", 1)
elif DATABASE_URL.startswith("postgresql+psycopg://") and ".async" not in DATABASE_URL:
    # Если уже есть postgresql+psycopg://, добавляем .async
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg.async://", 1)

# Явно указываем использование psycopg для async
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
        # async with автоматически закрывает сессию, дополнительный close не нужен