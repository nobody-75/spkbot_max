from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ========== ДОБАВЛЯЕМ КОРЕНЬ ПРОЕКТА ==========
sys.path.append(str(Path(__file__).parent.parent))

# ========== ИМПОРТ НАСТРОЕК И МОДЕЛЕЙ ==========
from src.config.settings import settings
from src.database.models import Base

# this is the Alembic Config object
config = context.config

# ========== БЕРЁМ URL ИЗ НАСТРОЕК ==========
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ========== МЕТАДАННЫЕ ==========
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # БЕРЁМ URL НАПРЯМУЮ ИЗ НАСТРОЕК
    url = settings.DATABASE_URL_SYNC

    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()