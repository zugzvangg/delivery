import asyncio

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def event_loop():
    """Позволяет async тестам работать на уровне session."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    container = PostgresContainer("postgres:15-alpine")
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="session")
async def async_engine(postgres_container):
    engine = create_async_engine(
        postgres_container.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        ),
        echo=False,
        future=True,
    )

    # Применяем миграции alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url", postgres_container.get_connection_url()
    )
    command.upgrade(alembic_cfg, "head")

    yield engine

    await engine.dispose()


@pytest.fixture()
async def db(async_engine):
    """ДАЁТ Асинхронную сессию для каждого теста"""
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        yield session
        await session.rollback()  # чистим изменения

