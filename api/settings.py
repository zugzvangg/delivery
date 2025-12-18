from functools import lru_cache

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    # Service
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Factorial API application"
    version: str = "0.0.0"
    allowed_hosts: list[str] = ["*"]


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
