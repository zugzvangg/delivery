# Теперь координация происходит на уровне сервиса:
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.order.order import Order


class InvalidOrderType(Exception):
    pass


class InvalidCourierType(Exception):
    pass


class OrderDispatcher:
    def dispatch(self, order: Order, courier: Courier) -> None:
        self.__validate_order(order)
        self.__validate_courier(courier)
        if courier.can_take_order(order):
            courier.take_order(order)
            order.assign(courier.id)

    def complete(self, order: Order, courier: Courier) -> None:
        self.__validate_order(order)
        self.__validate_courier(courier)
        courier.complete_order(order)
        order.complete()

    @staticmethod
    def __validate_order(order: Order) -> None:
        if not isinstance(order, Order):
            raise InvalidOrderType("'order' should be of type Order")

    @staticmethod
    def __validate_courier(courier: Courier) -> None:
        if not isinstance(courier, Courier):
            raise InvalidCourierType("'courier' should be of type Courier")
