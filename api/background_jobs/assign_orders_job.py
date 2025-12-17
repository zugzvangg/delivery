from loguru import logger
from sqlalchemy.orm import Session

from api.db import get_session
from src.delivery.core.application.use_cases.commands.assign_order import (
    AssignOrderCommand,
    AssignOrderUseCase,
)


def assign_orders_job():
    logger.info("Running assign orders job")
    with get_session() as db:
        assign_order_use_case: AssignOrderUseCase = AssignOrderUseCase(db)
        assign_order_use_case.handle(AssignOrderCommand())
