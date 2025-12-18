from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from src.delivery.adapters.out.grpc.geo.client import GRPCGeoService
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
    def __init__(self, order_id: UUID, street: str, volume: int):
        if not isinstance(order_id, UUID):
            raise ValueError("order_id must be a UUID")

        if not street or not street.strip():
            raise ValueError("street must be a non-empty string")

        if not isinstance(volume, int) or volume <= 0:
            raise ValueError("volume must be a positive integer")

        self._order_id = order_id
        self._street = street
        self._volume = volume

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def street(self) -> str:
        return self._street

    @property
    def volume(self) -> int:
        return self._volume


class CreateOrderUseCase(CommandHandler):
    def __init__(self, session: Session):
        self.session = session
        self.order_repo: OrderRepository = OrderRepository(session)
        self.geo_service = GRPCGeoService()

    def handle(self, command: CreateOrderCommand) -> None:
        location: Location = self.geo_service.get_location(command.street)

        order = Order(id=command.order_id, location=location, volume=command.volume)
        self.order_repo.add(order)
        self.session.commit()
