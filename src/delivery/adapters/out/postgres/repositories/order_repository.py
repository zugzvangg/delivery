import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.models.models import OrderModel
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus
from src.delivery.core.ports.order_repository import OrderRepositoryInterface


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order) -> Order:
        """Добавить заказ в БД и вернуть доменный объект"""
        if not isinstance(order, Order):
            raise ValueError("'order' should be the domain model Order")
        orm_order = OrderModel.from_domain_object(order)
        self.session.add(orm_order)
        self.session.commit()
        self.session.refresh(orm_order)  # подгружаем все поля после commit
        return orm_order.to_domain_object()

    def update(self, order: Order) -> Order:
        """Обновить существующий заказ"""

        db_order: OrderModel = self.session.get(OrderModel, order.id)
        if db_order is None:
            raise ValueError(f"Order {order.id=} not found")

        # Обновляем поля
        db_order.location_x = order.location.x
        db_order.location_y = order.location.y
        db_order.volume = order.volume
        db_order.status = order.status.name
        db_order.courier_id = order.courier_id

        self.session.commit()
        self.session.refresh(db_order)

        return db_order.to_domain_object()

    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        """Получить заказ по идентификатору"""
        if not isinstance(order_id, uuid.UUID):
            raise ValueError("'order_id' should be of uuid.UUID type")
        db_order: OrderModel = self.session.get(OrderModel, order_id)
        if db_order is None:
            raise ValueError(f"Order {order_id} not found")
        return db_order.to_domain_object()

    def get_any_created(self) -> Optional[Order]:
        """Получить 1 любой заказ со статусом 'Created'"""
        any_created_order = (
            select(OrderModel)
            .where(OrderModel.status == OrderStatus.CREATED.value)
            .limit(1)
        )
        orm_order = self.session.execute(any_created_order).scalars().first()

        if orm_order is None:
            raise ValueError("No 'created' orders")
        return orm_order.to_domain_object()

    def get_all_assigned(self) -> List[Order]:
        """Получить все назначенные заказы (со статусом 'Assigned')"""
        all_assigned_orders = select(OrderModel).where(
            OrderModel.status == OrderStatus.ASSIGNED.value
        )
        orm_order = self.session.execute(all_assigned_orders).scalars()
        if orm_order is None:
            raise ValueError("No 'assigned' orders")
        return [x.to_domain_model() for x in orm_order]
