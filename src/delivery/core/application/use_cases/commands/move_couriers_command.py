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
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order


@dataclass
class MoveCouriersCommand(Command):
    pass


class MoveCouriersUseCase(CommandHandler):
    def __init__(self, session: Session):
        self.session = session
        self.courier_repo: CourierRepository = CourierRepository(session)
        self.order_repo: OrderRepository = OrderRepository(session)

    def handle(self, command: MoveCouriersCommand) -> None:
        all_assigned_orders: list[Order] = self.order_repo.get_all_assigned()
        for order in all_assigned_orders:
            courier = self.courier_repo.get_by_id(order.courier_id)
            courier.move(order.location)
            self.courier_repo.update(courier)
            # если совпадают, завершаем заказ
            if courier.location == order.location:
                courier.complete_order(order)
                order.complete()
                self.courier_repo.update(courier)
                self.order_repo.update(order)
        self.session.commit()
