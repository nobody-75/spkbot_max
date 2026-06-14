from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine  # 👈 добавляем синхронный движок
from src.config.settings import settings

# Асинхронный движок (для бота)
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False,
    pool_size=10,
    max_overflow=20
)
# Синхронный движок (только для Alembic, в коде бота не использовать!)
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=False
)
# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
# Базовый класс для моделей
Base = declarative_base()
# Асинхронная функция для получения сессии БД (для FastAPI)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
# Импортируем модели после объявления Base, чтобы избежать круговых импортов
from src.database.models import User

__all__ = [
    'Base',
    'engine',
    'sync_engine',
    'AsyncSessionLocal',
    'get_db',
    'User',
]

