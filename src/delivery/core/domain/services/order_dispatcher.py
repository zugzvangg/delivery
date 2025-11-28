# Теперь координация происходит на уровне сервиса:
from typing import Optional

from src.delivery.core.domain.model.courier.courier import (
    Courier,
    CourierCanNotTakeOrderError,
)
from src.delivery.core.domain.model.order.order import NotCreatedOrderStatus, Order
from src.delivery.core.domain.model.order.order_status import OrderStatus
from src.delivery.core.domain.services.order_dispatcher_interface import (
    InvalidCourierType,
    InvalidOrderType,
    OrderDispatcherInterface,
)


class OrderDispatcher(OrderDispatcherInterface):
    def dispatch(self, order: Order, courier: Courier) -> None:
        self.__validate_order(order)
        self.__validate_courier(courier)
        if not courier.can_take_order(order):
            raise CourierCanNotTakeOrderError("Courier cannot take this order")
        courier.take_order(order)
        order.assign(courier.id)

    def complete(self, order: Order, courier: Courier) -> None:
        self.__validate_order(order)
        self.__validate_courier(courier)
        courier.complete_order(order)
        order.complete()

    def find_best_courier(
        self, order: Order, couriers: list[Courier]
    ) -> Optional[Courier]:

        self.__validate_order(order)
        self.__validate_couriers_list(couriers)

        if order.status != OrderStatus.CREATED:
            raise NotCreatedOrderStatus("Can only score orders with 'created' status")

        fastest_courier = None
        minimal_time_to_delivery: float = float("inf")
        for courier in couriers:
            if courier.can_take_order(order):
                time_to_delivery = courier.calculate_time_to_location(order.location)
                if time_to_delivery < minimal_time_to_delivery:
                    fastest_courier = courier
                    minimal_time_to_delivery = time_to_delivery
        return fastest_courier

    def assign_to_best_courier(
        self, order: Order, couriers: list[Courier]
    ) -> Optional[Courier]:
        """Найти и назначить лучшего курьера на заказ"""
        best_courier = self.find_best_courier(order, couriers)

        if not best_courier:
            return None

        self.dispatch(order, best_courier)
        return best_courier

    @staticmethod
    def __validate_order(order: Order) -> None:
        if not isinstance(order, Order):
            raise InvalidOrderType("'order' should be of type Order")

    @staticmethod
    def __validate_courier(courier: Courier) -> None:
        if not isinstance(courier, Courier):
            raise InvalidCourierType("'courier' should be of type Courier")

    @staticmethod
    def __validate_couriers_list(couriers: list[Courier]) -> None:
        if not isinstance(couriers, list):
            raise InvalidCourierType("'couriers' should be a list")

        for courier in couriers:
            if not isinstance(courier, Courier):
                raise InvalidCourierType(
                    "All items in 'couriers' should be of type Courier"
                )
