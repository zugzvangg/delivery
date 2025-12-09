import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_, exists

from src.delivery.adapters.out.postgres.models.models import (
    CourierModel,
    StoragePlaceModel,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.ports.courier_repository import CourierRepositoryInterface


class CourierRepository(CourierRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def add(self, courier: Courier) -> Courier:
        """Добавить курьера в БД и вернуть доменный объект"""
        if not isinstance(courier, Courier):
            raise ValueError("'courier' should be the domain model Order")
        orm_courier = CourierModel.from_domain_object(courier)
        self.session.add(orm_courier)
        # из-за orphan не нужно добавлять отдельно
        # self.session.add_all(orm_courier.storage_places)
        # нельзя завершать транзакцию в репозитории, только в юзкейсе
        # self.session.commit()
        self.session.flush()
        self.session.refresh(orm_courier)
        return orm_courier.to_domain_object()

    def update(self, courier: Courier) -> None:
        """Обновить существующего курьера"""
        db_courier: CourierModel = self.session.get(CourierModel, courier.id)
        if db_courier is None:
            raise ValueError(f"Courier {courier.id=} not found")
        db_courier.name = courier.name
        db_courier.speed = courier.speed
        db_courier.location_x = courier.location.x
        db_courier.location_y = courier.location.y
        db_courier.storage_places = [
            StoragePlaceModel.from_domain_object(x) for x in courier.storage_places
        ]
        # нельзя завершать транзакцию в репозитории, только в юзкейсе
        # self.session.commit()
        self.session.flush()
        self.session.refresh(db_courier)
        return db_courier.to_domain_object()

    def get_by_id(self, courier_id: uuid.UUID) -> Optional[Courier]:
        """Получить курьера по идентификатору"""
        if not isinstance(courier_id, uuid.UUID):
            raise ValueError("'courier_id' should be of uuid.UUID type")
        orm_courier: CourierModel = self.session.get(CourierModel, courier_id)
        if orm_courier is None:
            raise ValueError(f"Courier {courier_id} not found")
        return orm_courier.to_domain_object()

    def get_all_free(self) -> List[Courier]:
        busy_couriers_subq = (
            select(
                StoragePlaceModel.courier_id,
            )
            .where(StoragePlaceModel.order_id.is_not(None))
            .distinct()
        )

        stmt = select(CourierModel).where(CourierModel.id.not_in(busy_couriers_subq))

        orm_couriers = self.session.execute(stmt).unique().scalars().all()
        return [c.to_domain_object() for c in orm_couriers]
