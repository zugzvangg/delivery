import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from src.delivery.core.domain.model.order.order import Order


class OrderRepository(ABC):
    """Порт для работы с хранилищем заказов"""

    @abstractmethod
    def add(self, order: Order) -> None:
        """Добавить заказ"""
        pass

    @abstractmethod
    def update(self, order: Order) -> None:
        """Обновить заказ"""
        pass

    @abstractmethod
    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        """Получить заказ по идентификатору"""
        pass

    @abstractmethod
    def get_any_created(self) -> Optional[Order]:
        """Получить 1 любой заказ со статусом 'Created'"""
        pass

    @abstractmethod
    def get_all_assigned(self) -> List[Order]:
        """Получить все назначенные заказы (со статусом 'Assigned')"""
        pass
