import random

import pytest
from pydantic import ValidationError

from src.delivery.core.domain.model.location.location import Location


class TestLocation:
    """Тесты для класса Location"""

    def test_create_valid_location(self):
        """Тест создания Location с валидными координатами"""
        location = Location(x=5, y=5)
        assert location.x == 5
        assert location.y == 5

    def test_create_min_coordinates(self):
        """Тест создания Location с минимальными координатами"""
        location = Location(x=1, y=1)
        assert location.x == 1
        assert location.y == 1

    def test_create_max_coordinates(self):
        """Тест создания Location с максимальными координатами"""
        location = Location(x=10, y=10)
        assert location.x == 10
        assert location.y == 10

    def test_create_invalid_x_coordinate_too_low(self):
        """Тест создания Location с x координатой меньше минимальной"""
        with pytest.raises(ValidationError):
            Location(x=0, y=5)

    def test_create_invalid_x_coordinate_too_high(self):
        """Тест создания Location с x координатой больше максимальной"""
        with pytest.raises(ValidationError):
            Location(x=11, y=5)

    def test_create_invalid_y_coordinate_too_low(self):
        """Тест создания Location с y координатой меньше минимальной"""
        with pytest.raises(ValidationError):
            Location(x=5, y=0)

    def test_create_invalid_y_coordinate_too_high(self):
        """Тест создания Location с y координатой больше максимальной"""
        with pytest.raises(ValidationError):
            Location(x=5, y=11)

    def test_equality(self):
        """Тест сравнения двух одинаковых Location"""
        loc1 = Location(x=3, y=4)
        loc2 = Location(x=3, y=4)
        assert loc1 == loc2

    def test_inequality(self):
        """Тест сравнения двух разных Location"""
        loc1 = Location(x=3, y=4)
        loc2 = Location(x=3, y=5)
        assert loc1 != loc2

    def test_distance_to_same_location(self):
        """Тест расстояния до той же Location"""
        location = Location(x=5, y=5)
        distance = location.distance_to(location)
        assert distance == 0

    def test_distance_to_horizontal(self):
        """Тест расстояния по горизонтали"""
        loc1 = Location(x=2, y=5)
        loc2 = Location(x=7, y=5)
        distance = loc1.distance_to(loc2)
        assert distance == 5

    def test_distance_to_vertical(self):
        """Тест расстояния по вертикали"""
        loc1 = Location(x=5, y=2)
        loc2 = Location(x=5, y=7)
        distance = loc1.distance_to(loc2)
        assert distance == 5

    def test_distance_to_diagonal(self):
        """Тест расстояния по диагонали"""
        loc1 = Location(x=2, y=3)
        loc2 = Location(x=5, y=7)
        distance = loc1.distance_to(loc2)
        assert distance == 7

    def test_distance_commutative(self):
        """Тест коммутативности расстояния"""
        loc1 = Location(x=3, y=4)
        loc2 = Location(x=7, y=2)
        distance1 = loc1.distance_to(loc2)
        distance2 = loc2.distance_to(loc1)
        assert distance1 == distance2

    def test_create_class_method(self):
        """Тест фабричного метода create"""
        location = Location.create(8, 9)
        assert location.x == 8
        assert location.y == 9
        assert isinstance(location, Location)

    def test_immutability(self):
        """Тест неизменяемости Location"""
        location = Location(x=4, y=6)

        # Попытка изменить атрибут должна вызвать ошибку
        with pytest.raises(ValidationError):
            location.x = 5

        with pytest.raises(ValidationError):
            location.y = 7
