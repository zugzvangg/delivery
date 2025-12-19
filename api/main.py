import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.lifespan import lifespan
from api.settings import get_settings
from api.http.router import router
from src.delivery.adapters.incoming.kafka.basket.consumer import router as kafka_router


def get_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(**settings.model_dump(), lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router)
    # application.include_router(kafka_router)
    return application


app = get_application()
