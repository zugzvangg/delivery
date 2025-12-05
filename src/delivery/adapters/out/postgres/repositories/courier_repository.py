import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.models.models import CourierModel
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.ports.courier_repository import CourierRepositoryInterface


class CourierRepository(CourierRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def add(self, courier: Courier) -> Courier:
        """Добавить курьера в БД и вернуть доменный объект"""
        if not isinstance(courier, Courier):
            raise ValueError("'courier' should be the domain model Order")
        orm_order = CourierModel.from_domain_object(courier)
        self.session.add(orm_order)
        self.session.commit()
        self.session.refresh(orm_order)  # подгружаем все поля после commit
        return orm_order.to_domain_object()
        

    def update(self, courier: Courier) -> None:
        pass

    def get_by_id(self, courier_id: uuid.UUID) -> Optional[Courier]:
        pass

    def get_all_free(self) -> List[Courier]:
        pass

    def get_all_free(self) -> List[Courier]:
        pass
        pass
        pass
