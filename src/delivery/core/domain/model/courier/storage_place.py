import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StoragePlace(BaseModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Уникальный идентификатор места хранения",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    name: str = Field(
        min_length=1,
        description="Название места хранения: рюкзак, багажник и т.п.",
        examples=["Рюкзак"],
    )
    total_volume: int = Field(
        gt=0,
        description="Допустимый объем (должен быть больше 0)",
        examples=[50],
    )
    order_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Идентификатор заказа, который хранится в месте хранения",
        examples=["b2c3d4e5-f6g7-8901-bcde-f23456789012"],
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "name": "Рюкзак",
                "total_volume": 50,
                "order_id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
            }
        },
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StoragePlace):
            return False
        return self.id == other.id

    @classmethod
    def create(cls, name: str, total_volume: int):
        return cls(name=name, total_volume=total_volume)

    def can_store(self, volume: int) -> bool:
        """Проверка возможности размещения заказа"""

        if not isinstance(volume, int) or volume <= 0:
            raise ValueError("Volume must be a positive integer!")
        if volume > self.total_volume:
            return False
        if self._is_occupied():
            return False
        return True

    def store(self, order_id: uuid.UUID, volume: int) -> None:
        """Размещение заказа в месте хранения"""
        if not isinstance(order_id, uuid.UUID):
            raise ValueError("Order ID must be a UUID")
        if not self.can_store(volume):
            raise ValueError(
                "Cannot store order - storage is occupied or volume exceeds capacity"
            )

        # NOTE: кривовато, но pydantic не дает создавать названия переменных вида "_<name>" или "__<name>", но зато атрибуты приватные
        object.__setattr__(self, "order_id", order_id)

    def clear(self, order_id: uuid.UUID) -> None:
        """Извлечение заказа из места хранения"""
        if not self._is_occupied():
            raise ValueError("Cannot clear - storage is not occupied")
        if self.order_id != order_id:
            raise ValueError("Order ID does not match the stored order")
        # NOTE: кривовато, но pydantic не дает создавать названия переменных вида "_<name>" или "__<name>", но зато атрибуты приватные
        object.__setattr__(self, "order_id", None)

    def _is_occupied(self) -> bool:
        """Приватный метод проверки занятости"""
        return self.order_id is not None

    @property
    def is_empty(self) -> bool:
        """Публичное свойство для проверки пустоты"""
        return not self._is_occupied()
