from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from loguru import logger

from api.background_jobs.assign_orders_job import assign_orders_job
from api.background_jobs.move_couriers_job import move_couriers_job
from api.db import engine
from src.delivery.adapters.out.postgres.models.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # создаем все realtionships
    Base.metadata.create_all(engine)
    scheduler = BackgroundScheduler()
    logger.info("Starting scheduler...")
    scheduler.add_job(assign_orders_job, trigger="interval", seconds=1)
    scheduler.add_job(move_couriers_job, trigger="interval", seconds=1)
    scheduler.start()
    yield
    scheduler.shutdown()
    logger.info("Scheduler shutdown complete")
    logger.info("Scheduler shutdown complete")
