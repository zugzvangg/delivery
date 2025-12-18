# src/delivery/db.py

from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class Settings(BaseSettings):
    # app
    app_name: str = Field(..., env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")

    # db
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_database: str = Field(..., env="DB_DATABASE")
    db_echo: bool = Field(False, env="DB_ECHO")
    db_pool_size: int = Field(10, env="DB_POOL_SIZE")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:"
            f"{self.db_port}/"
            f"{self.db_database}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
print(settings.database_url)



engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    pool_pre_ping=True,
)

SessionFactory = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_session() -> Session:
    return SessionFactory()
