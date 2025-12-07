from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.models.models import CourierModel
from src.delivery.core.application.use_cases.queries.base import Query, QueryHandler
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order


@dataclass
class CourierDTO:
    id: UUID
    name: str
    location: Location


@dataclass
class GetAllCouriersQuery(Query):
    pass


class GetAllCouriersUseCase(QueryHandler):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetAllCouriersQuery) -> list[CourierDTO]:
        # не используем репозитории
        stmt = select(CourierModel)
        orm_couriers = self.session.execute(stmt).unique().scalars().all()
        return [
            CourierDTO(c.id, c.name, Location(c.location_x, c.location_y))
            for c in orm_couriers
        ]
