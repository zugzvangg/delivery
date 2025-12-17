from loguru import logger
from sqlalchemy.orm import Session

from src.delivery.core.application.use_cases.commands.move_couriers_command import (
    MoveCouriersCommand,
    MoveCouriersUseCase,
)
from api.db import get_session


def move_couriers_job():
    logger.info("Move couriers job")
    with get_session() as db:
        assign_order_use_case: MoveCouriersUseCase = MoveCouriersUseCase(db)
        assign_order_use_case.handle(MoveCouriersCommand())
