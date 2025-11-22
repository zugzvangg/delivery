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


class InvalidCourierLocationTypeError(Exception):
    pass


class Courier:
    """Aggragate курьера"""

    def __init__(self, name: str, speed: int, location: Location):

        self.__validate_name(name)
        self.__validate_speed(speed)
        self.__validate_location(location)

        self.__id = uuid.uuid4()
        self.__name = name
        self.__speed = speed
        self.__location = location
        self.__storage_places: list[StoragePlace] = [
            StoragePlace(name="Сумка", total_volume=10)
        ]

    @staticmethod
    def __validate_name(name: str) -> None:
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise InvalidCourierNameError("Name must be a non-empty string")

    @staticmethod
    def __validate_speed(name: str) -> None:
        if not isinstance(name, int):
            raise InvalidCourierSpeedError("Speed must be a positive integer")

    @staticmethod
    def __validate_location(location: Location) -> None:
        if not isinstance(location, Location):
            raise InvalidCourierLocationTypeError(
                "'location' variable should be of Location type"
            )

    def add_storage_place(self, name: str, volume: int):
        storage_place = StoragePlace(name=name, total_volume=volume)
        self.__storage_places.append(storage_place)

    def can_take_order(self, order: Order) -> bool:
        for storage_place in self.__storage_places:
            if storage_place.can_store(order.volume):
                return True
        return False

    def take_order(self, order: Order) -> None:
        pass

    def complete_order(order: Order) -> None:
        pass

    def calculate_time_to_location(self, location: Location) -> float:
        pass

    def move(self, target: Location) -> None:
        pass

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
        return self.__storage_places

    @classmethod
    def create(cls, name: str, speed: int, location: Location):
        return cls(name=name, speed=speed, location=location)
