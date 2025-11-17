import random
from typing import ClassVar

# hope I can use it :)
from pydantic import BaseModel, ConfigDict, Field


class Location(BaseModel):
    """Value Object, представляющий координату на доске"""

    MIN_COORD: ClassVar[int] = 1
    MAX_COORD: ClassVar[int] = 10
    x: int = Field(
        ge=MIN_COORD,
        le=MAX_COORD,
        description=f"Горизонтальная координата ({MIN_COORD}-{MAX_COORD})",
    )
    y: int = Field(
        ge=MIN_COORD,
        le=MAX_COORD,
        description=f"Вертикальная координата ({MIN_COORD}-{MAX_COORD})",
    )
    model_config = ConfigDict(frozen=True)

    def __eq__(self, other: "Location") -> bool:
        return self.x == other.x and self.y == other.y

    def distance_to(self, other: "Location") -> int:
        """Расстояние между Location - это совокупное количество шагов по X и Y, которое необходимо сделать курьеру, чтобы достигнуть точки"""
        return abs(self.x - other.x) + abs(self.y - other.y)

    @classmethod
    def create_random(cls, self):
        x = random.randint(self.MIN_COORD, self.MAX_COORD)
        y = random.randint(self.MIN_COORD, self.MAX_COORD)
        return cls(x=x, y=y)

    @classmethod
    def create(cls, x: int, y: int):
        return cls(x=x, y=y)
