# alembic/env.py

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url
from alembic import context

# Подключаем metadata из вашего SQLAlchemy Base
from app.db.base import Base  # <--- здесь путь может отличаться, смотрите вашу структуру

# ------------------------------------------------------------
# Если в alembic.ini прописаны какие-то логгеры, они будут настроены:
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Подключаем вашу MetaData для поддержки автогенерации миграций:
target_metadata = Base.metadata
# ------------------------------------------------------------

# Примерная идея:
#  - читаем URL из переменной окружения
#  - если URL начинается с postgresql+asyncpg://,
#    то заменяем префикс на postgresql+psycopg2://,
#    чтобы Alembic мог создать синхронный psycopg2 engine.

def get_alembic_url() -> str:
    """
    Считываем строку подключения из переменной окружения DATABASE_URL.
    Если не задана – падаем с ошибкой.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Переменная окружения DATABASE_URL не найдена")

    # Если URL использует asyncpg, заменим его на psycopg2
    # чтобы внутри Alembic получилось sync-подключение.
    parsed = make_url(url)
    if parsed.drivername.startswith("postgresql+asyncpg"):
        # Заменяем driver на psycopg2
        # Например: postgresql+asyncpg://user:pass@host:port/dbname
        # превратится в: postgresql+psycopg2://user:pass@host:port/dbname
        parsed = parsed.set(drivername="postgresql+psycopg2")
        return str(parsed)
    else:
        # Если там уже “postgresql+psycopg2” или “postgresql://”,
        # просто возвращаем как есть
        return url


def run_migrations_offline() -> None:
    """
    Запускаем миграции в offline-режиме (только SQL-консольный вывод).
    """
    url = get_alembic_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Запускаем миграции в online-режиме (через реальное подключение Engine).
    """
    # Забираем URL уже с поправкой на psycopg2 (если исходный был asyncpg)
    url = get_alembic_url()

    # Передаём в config здесь «любые» доп. опции,
    # но главное – мы хотим переопределить sqlalchemy.url:
    alembic_section = config.get_section(config.config_ini_section) or {}
    alembic_section["sqlalchemy.url"] = url

    connectable = engine_from_config(
        alembic_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                # include_schemas=True,  # если нужны схемы
                # compare_type=True,     # если нужно сравнивать типы колонок
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
