from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import config

engine = create_async_engine(config.db_url)
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

__all__ = ['engine', 'async_session']