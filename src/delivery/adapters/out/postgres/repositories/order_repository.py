import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.delivery.adapters.out.postgres.models.order_model import OrderModel
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.ports.order_repository import OrderRepositoryInterface


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, order: Order) -> Order:
        """Добавить заказ"""
        data = {
            "id": order.id,
            "location_x": order.location.x,
            "location_y": order.location.y,
            "volume": order.volume,
            "status": order.status.name,
            "courier_id": order.courier_id,
        }
        stmt = insert(OrderModel).values(data).returning(OrderModel)
        result = await self.session.execute(stmt)
        order_model = result.unique().scalar_one()
        return order_model.to_domain_object()

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
