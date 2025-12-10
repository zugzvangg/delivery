from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.models.models import CourierModel, OrderModel
from src.delivery.core.application.use_cases.queries.base import Query, QueryHandler
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


@dataclass
class OrderDTO:
    id: UUID
    location: Location


@dataclass
class GetNotCompletedOrdersQuery(Query):
    pass


class GetNotCompletedOrdersUseCase(QueryHandler):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetNotCompletedOrdersQuery) -> list[OrderDTO]:
        # не используем репозитории
        stmt = select(OrderModel).where(OrderModel.status != OrderStatus.COMPLETED.value)
        orm_orders = self.session.execute(stmt).unique().scalars().all()
        return [
            OrderDTO(c.id, Location(c.location_x, c.location_y)) for c in orm_orders
        ]
