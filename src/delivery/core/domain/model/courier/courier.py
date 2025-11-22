import uuid
from typing import Optional

from src.delivery.core.domain.model.common import validate_uuid
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


class InvalidCourierNameError(Exception):
    pass


class InvalidCourierSpeedError(Exception):
    pass


class CourierCanNotCompleteOrderError(Exception):
    pass


class InvalidCourierLocationTypeError(Exception):
    pass


class CourierCanNotTakeOrderError(Exception):
    pass


class Courier:
    """Aggragate курьера"""

    def __init__(self, name: str, speed: int, location: Location):

        self.__validate_name(name)
        self.__validate_speed(speed)
        self.__validate_location(location)

        self.__id: uuid.UUID = uuid.uuid4()
        self.__name: str = name
        self.__speed: int = speed
        self.__location: Location = location
        self.__storage_places: list[StoragePlace] = [
            StoragePlace(name="Сумка", total_volume=10)
        ]

    @staticmethod
    def __validate_name(name: str) -> None:
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise InvalidCourierNameError("Name must be a non-empty string")

    @staticmethod
    def __validate_speed(speed: int) -> None:
        if not isinstance(speed, int) or speed <= 0:
            raise InvalidCourierSpeedError("Speed must be a positive integer")

    @staticmethod
    def __validate_location(location: Location) -> None:
        if not isinstance(location, Location):
            raise InvalidCourierLocationTypeError(
                "'location' variable should be of Location type"
            )

    def add_storage_place(self, name: str, volume: int) -> None:
        """Добавить место хранения"""
        storage_place = StoragePlace(name=name, total_volume=volume)
        self.__storage_places.append(storage_place)

    def can_take_order(self, order: Order) -> bool:
        """Проверка, может ли курьер взять заказ"""
        can_take_order = any(
            storage_place.can_store(order.volume)
            for storage_place in self.__storage_places
        )
        return can_take_order

    def take_order(self, order: Order) -> None:
        if not self.can_take_order(order):
            raise CourierCanNotTakeOrderError("Courier can not take this order")

        if order.status != OrderStatus.CREATED:
            raise CourierCanNotTakeOrderError("Order status is not CREATED")

        for storage_place in self.__storage_places:
            if storage_place.can_store(volume=order.volume):
                # кладём заказ в первый доступный storage_place
                storage_place.store(order_id=order.id, volume=order.volume)
                # назначаем заказ на курьера
                order.assign(self.__id)
                break

    def complete_order(self, order: Order) -> None:
        order_found = False
        for storage_place in self.__storage_places:
            if storage_place.order_id == order.id:
                storage_place.clear(order_id=order.id)
                order_found = True
                break
        if not order_found:
            raise CourierCanNotCompleteOrderError(
                "Order not found in courier's storage"
            )

        order.complete()

    def calculate_time_to_location(self, location: Location) -> float:
        self.__validate_location(location)
        return self.__location.distance_to(location) / self.__speed

    def move(self, target: Location) -> None:
        self.__validate_location(target)
        difX = target.x - self.__location.x
        difY = target.y - self.__location.y
        cruising_range = self.__speed

        moveX: int = int(max(-cruising_range, min(difX, cruising_range)))
        cruising_range -= abs(moveX)

        moveY: int = int(max(-cruising_range, min(difY, cruising_range)))

        location_create_result = Location(
            self.__location.x + moveX, self.__location.y + moveY
        )
        # меняем location курьера
        self.__location = location_create_result

    # Геттеры для доступа к приватным полям
    @property
    def id(self) -> uuid.UUID:
        """Уникальный идентификатор Courier"""
        return self.__id

    @property
    def location(self) -> Location:
        """Location курьера"""
        return self.__location

    @property
    def speed(self) -> int:
        """speed курьера"""
        return self.__speed

    @property
    def name(self) -> str:
        """name курьера"""
        return self.__name

    @property
    def storage_places(self) -> list[StoragePlace]:
        """StoragePlaces курьера"""
        return self.__storage_places.copy()

    @classmethod
    def create(cls, name: str, speed: int, location: Location):
        return cls(name=name, speed=speed, location=location)
