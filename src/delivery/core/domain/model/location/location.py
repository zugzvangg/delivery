import json
import random

from src.delivery.core.domain.model.common import WrongSerializationJsonError


class WrongCoordinateError(Exception):
    pass


class Location:
    """Value Object, представляющий координату на доске"""

    def __init__(self, x: int, y: int):
        self.__MIN_COORD: int = 1
        self.__MAX_COORD: int = 10
        self._validate_coord(x, "x")
        self._validate_coord(y, "y")
        self.__x: int = x
        self.__y: int = y

    @property
    def x(self) -> int:
        """Горизонтальная координата"""
        return self.__x

    @property
    def y(self) -> int:
        """Вертикальная координата"""
        return self.__y

    def _validate_coord(self, coord: int, coord_name: str) -> None:
        """Валидация координаты"""
        if not isinstance(coord, int):
            raise WrongCoordinateError(f"{coord_name} должен быть целым числом")
        if not (self.__MIN_COORD <= coord <= self.__MAX_COORD):
            raise WrongCoordinateError(
                f"{coord_name} должен быть в диапазоне "
                f"{self.__MIN_COORD}-{self.__MAX_COORD}, получено {coord}"
            )

    def __eq__(self, other: "Location") -> bool:
        if not isinstance(other, Location):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def distance_to(self, other: "Location") -> int:
        """Расстояние между Location - это совокупное количество шагов по X и Y, которое необходимо сделать курьеру, чтобы достигнуть точки"""
        return abs(self.x - other.x) + abs(self.y - other.y)

    @classmethod
    def create_random(cls, self):
        x = random.randint(self.__MIN_COORD, self.__MAX_COORD)
        y = random.randint(self.__MIN_COORD, self.__MAX_COORD)
        return cls(x=x, y=y)

    @classmethod
    def create(cls, x: int, y: int):
        return cls(x=x, y=y)

    def serialize(self) -> dict:
        return {"x": self.__x, "y": self.__y}

    @classmethod
    def deserialize(cls, data: dict):
        if not isinstance(data, dict):
            raise WrongSerializationJsonError("Should be of dict type")

        x = data.get("x")
        y = data.get("y")
        if x is None or y is None:
            raise WrongSerializationJsonError("Data must contain 'x' and 'y' keys")

        return cls(x=x, y=y)
