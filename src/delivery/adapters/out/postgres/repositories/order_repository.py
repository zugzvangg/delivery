import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from src.delivery.adapters.out.postgres.database import Database
from src.delivery.adapters.out.postgres.models.order_model import OrderModel
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.ports.order_repository import OrderRepositoryInterface


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, database: Database):
        self._db = database

    def add(self, order: Order) -> None:
        """Добавить заказ"""
        pass

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
