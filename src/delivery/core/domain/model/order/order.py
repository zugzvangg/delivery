import uuid
from typing import Optional

from src.delivery.core.domain.model.common import validate_uuid
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order_status import (
    NotAssignedOrderStatus,
    NotCreatedOrderStatus,
    OrderStatus,
)


class InvalidOrderLocationError(Exception):
    pass


class InvalidOrderVolumeError(Exception):
    pass


class Order:
    """Aggragate заказа"""

    def __init__(
        self,
        id: uuid.UUID,
        location: Location,
        volume: int,
    ):
        validate_uuid(id, "id")
        self.__validate_location(location)
        self.__validate_volume(volume)

        self.__id: uuid.UUID = id
        self.__location: Location = location
        self.__volume: int = volume
        self.__courier_id: uuid.UUID = None
        self.__status: OrderStatus = OrderStatus.CREATED

    @staticmethod
    def __validate_location(location: Location) -> None:
        if not isinstance(location, Location):
            raise InvalidOrderLocationError(
                "'location' variable should be of Location type"
            )

    @staticmethod
    def __validate_volume(volume: int):
        if not isinstance(volume, int) or volume <= 0:
            raise InvalidOrderVolumeError("volume must be a positive integer")

    # Геттеры для доступа к приватным полям
    @property
    def id(self) -> uuid.UUID:
        """Уникальный идентификатор Order"""
        return self.__id

    @property
    def location(self) -> Location:
        """Location доставки заказа"""
        return self.__location

    @property
    def volume(self) -> int:
        """volume доставки заказа"""
        return self.__volume

    @property
    def courier_id(self) -> Optional[uuid.UUID]:
        """courier_id доставки заказа"""
        return self.__courier_id

    @property
    def status(self) -> OrderStatus:
        """OrderStatus доставки заказа"""
        return self.__status

    def assign(self, courier_id: uuid.UUID) -> None:
        validate_uuid(courier_id, "courier_id")
        if self.__status != OrderStatus.CREATED:
            raise NotCreatedOrderStatus("Can only assign orders with CREATED status")

        self.__status = OrderStatus.ASSIGNED
        self.__courier_id = courier_id

    def complete(self) -> None:
        if self.__status != OrderStatus.ASSIGNED:
            raise NotAssignedOrderStatus(
                "Can only complete orders with ASSIGNED status"
            )
        self.__status = OrderStatus.COMPLETED

    @classmethod
    def create(cls, order_id: uuid.UUID, location: Location, volume: int):
        return cls(id=order_id, location=location, volume=volume)
