from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.repositories.order_repository import (
    OrderRepository,
)
from src.delivery.core.application.use_cases.commands.base import (
    Command,
    CommandHandler,
)
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order

@dataclass
class CreateOrderCommand(Command):
    order_id: UUID
    street: str
    volume: int


class CreateOrderUseCase(CommandHandler):
    def __init__(self, session: Session):
        # NOTE: позже добавит GeoService зависимость, пока создаем случайную location
        self.order_repo: OrderRepository = OrderRepository(session)

    def handle(self, command: CreateOrderCommand) -> None:
        # NOTE: потом будем получать из сервиса Geo
        location: Location = Location.create_random()

        order = Order(id=command.order_id, location=location, volume=command.volume)
        self.order_repo.add(order)
