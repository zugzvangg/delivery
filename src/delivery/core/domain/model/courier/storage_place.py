import uuid
from typing import Optional


class NotEnoughVolumeError(Exception):
    pass


class StorageOccupiedError(Exception):
    pass


class InvalidUUIDError(Exception):
    pass


class InvalidStoragePlaceName(Exception):
    pass


class InvalidStoragePlaceVolume(Exception):
    pass


class StoragePlaceClearWrongOrderId(Exception):
    pass


class StoragePlace:
    """Entity места хранения"""

    def __init__(
        self,
        name: str,
        total_volume: int,
        id: Optional[uuid.UUID] = None,
        order_id: Optional[uuid.UUID] = None,
    ):
        self.__validate_name(name)
        self.__validate_total_volume(total_volume)
        if id:
            self.__validate_id(id, "id")
        if order_id:
            self.__validate_id(order_id, "order_id")

        self.__id = id if id is not None else uuid.uuid4()
        self.__name = name
        self.__total_volume = total_volume
        self.__order_id = order_id

    @classmethod
    def create(cls, name: str, total_volume: int) -> "StoragePlace":
        """Фабричный метод для создания места хранения"""
        return cls(name=name, total_volume=total_volume)

    # Геттеры для доступа к приватным полям
    @property
    def id(self) -> uuid.UUID:
        """Уникальный идентификатор места хранения"""
        return self.__id

    @property
    def name(self) -> str:
        """Название места хранения: рюкзак, багажник и т.п."""
        return self.__name

    @property
    def total_volume(self) -> int:
        """Допустимый объем (должен быть больше 0)"""
        return self.__total_volume

    @property
    def order_id(self) -> Optional[uuid.UUID]:
        """Идентификатор заказа, который хранится в месте хранения"""
        return self.__order_id

    @staticmethod
    def __validate_id(id: uuid.UUID, var_name: str) -> None:
        """Может провалидировать и id, и order_id"""
        if not isinstance(id, uuid.UUID):
            raise InvalidUUIDError(f"{var_name} if must be of type uuid.UUID")

    @staticmethod
    def __validate_name(name: str) -> None:
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise InvalidStoragePlaceName("Name must be a non-empty string")

    @staticmethod
    def __validate_total_volume(total_volume: int) -> None:
        if not isinstance(total_volume, int) or total_volume <= 0:
            raise InvalidStoragePlaceVolume("Total volume must be a positive integer")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StoragePlace):
            return False
        return self.id == other.id

    def can_store(self, volume: int) -> bool:
        """Проверка возможности размещения заказа"""
        if not isinstance(volume, int) or volume <= 0:
            raise InvalidStoragePlaceVolume("Volume must be a positive integer!")
        if volume > self.__total_volume:
            return False
        if self.__is_occupied():
            return False
        return True

    def store(self, order_id: uuid.UUID, volume: int) -> None:
        """Размещение заказа в месте хранения"""
        self.__validate_id(order_id, "order_id")
        if not self.can_store(volume):
            raise StorageOccupiedError(
                "Cannot store order - storage is occupied or volume exceeds capacity"
            )
        self.__order_id = order_id

    def clear(self, order_id: uuid.UUID) -> None:
        """Извлечение заказа из места хранения"""
        if not self.__is_occupied():
            raise StorageOccupiedError("Cannot clear - storage is not occupied")
        if self.__order_id != order_id:
            raise StoragePlaceClearWrongOrderId(
                "Order ID does not match the stored order"
            )
        self.__order_id = None

    def __is_occupied(self) -> bool:
        """Приватный метод проверки занятости"""
        return self.__order_id is not None

    @property
    def is_empty(self) -> bool:
        """Публичное свойство для проверки пустоты"""
        return not self.__is_occupied()
