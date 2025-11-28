from abc import ABC, abstractmethod
from typing import List, Optional

from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.order.order import Order


class InvalidOrderType(Exception):
    pass


class InvalidCourierType(Exception):
    pass


class NoAvailableCouriersError(Exception):
    """Исключение когда нет подходящих курьеров"""

    pass


class OrderDispatcherInterface(ABC):
    """Domain Service для диспетчеризации заказов"""

    @abstractmethod
    def dispatch(self, order: Order, courier: Courier) -> None:
        """Назначить конкретного курьера на заказ"""
        pass

    @abstractmethod
    def complete(self, order: Order, courier: Courier) -> None:
        """Завершить заказ у курьера"""
        pass

    @abstractmethod
    def find_best_courier(
        self, order: Order, couriers: List[Courier]
    ) -> Optional[Courier]:
        """Найти лучшего курьера для заказа (только поиск, без назначения)"""
        pass

    @abstractmethod
    def assign_to_best_courier(self, order: Order, couriers: List[Courier]) -> Courier:
        """Найти и назначить лучшего курьера на заказ"""
        pass
