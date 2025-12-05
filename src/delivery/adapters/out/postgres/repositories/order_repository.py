import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.models.models import OrderModel
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.ports.order_repository import OrderRepositoryInterface


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order) -> Order:
        """Добавить заказ в БД и вернуть доменный объект"""
        orm_order = OrderModel.from_domain_object(order)
        self.session.add(orm_order)
        self.session.commit()
        self.session.refresh(orm_order)  # подгружаем все поля после commit
        return orm_order.to_domain_object()

    def update(self, order: Order) -> None:
        """Обновить заказ"""
        pass

    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        """Получить заказ по идентификатору"""
        pass

    def get_any_created(self) -> Optional[Order]:
        """Получить 1 любой заказ со статусом 'Created'"""
        pass

    def get_all_assigned(self) -> List[Order]:
        """Получить все назначенные заказы (со статусом 'Assigned')"""
        pass
        """Получить все назначенные заказы (со статусом 'Assigned')"""
        pass
        pass
