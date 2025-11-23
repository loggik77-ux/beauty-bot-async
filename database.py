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
        "Please create a .env file with DATABASE_URL=postgresql+asyncpg://user:password@host:port/database"
    )

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
        # async with автоматически закрывает сессию, дополнительный close не нужен