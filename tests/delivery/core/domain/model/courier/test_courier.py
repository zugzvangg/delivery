import uuid

import pytest

from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.location.location import Location


class TestStoragePlace:
    """Тесты для класса Courier"""

    def test_create_courier_with_default_values(self):
        name = "Артемий"
        speed = 322
        location = Location(x=2, y=3)

        courier = Courier(name=name, speed=speed, location=location)
        assert courier.location == location
        assert courier.speed == speed
        assert courier.name == name
