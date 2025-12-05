import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from src.delivery.adapters.out.postgres.models.models import Base


@pytest.fixture(scope="session")
def postgres_container():
    """Создаём контейнер Postgres для тестов"""
    container = PostgresContainer("postgres:15-alpine")
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="session")
def engine(postgres_container):
    """Синхронный движок SQLAlchemy"""
    sync_url = postgres_container.get_connection_url()
    engine = create_engine(sync_url, echo=False)

    # Создаём все таблицы из моделей
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture()
def db(engine):
    """Сессия для теста"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    finally:
        session.rollback()
        session.close()
