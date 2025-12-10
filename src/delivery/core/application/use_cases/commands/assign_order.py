from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.repositories.courier_repository import (
    CourierRepository,
)
from src.delivery.adapters.out.postgres.repositories.order_repository import (
    OrderRepository,
)
from src.delivery.core.application.use_cases.commands.base import (
    Command,
    CommandHandler,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.services.order_dispatcher import OrderDispatcher


@dataclass
class AssignOrderCommand(Command):
    pass


class AssignOrderUseCase(CommandHandler):
    def __init__(self, session: Session):
        self.session = session
        self.courier_repo: CourierRepository = CourierRepository(session)
        self.order_repo: OrderRepository = OrderRepository(session)
        self.order_dispatcher: OrderDispatcher = OrderDispatcher()

    def handle(self, command: AssignOrderCommand) -> None:
        order: Order = self.order_repo.get_any_created()
        if not order:
            return
        couriers: list[Courier] = self.courier_repo.get_all_free()
        if len(couriers) == 0:
            return
        best_courier: Courier = self.order_dispatcher.assign_to_best_courier(
            order=order, couriers=couriers
        )
        if not best_courier:
            return
        self.order_repo.update(order)
        self.courier_repo.update(best_courier)
        self.session.commit()
