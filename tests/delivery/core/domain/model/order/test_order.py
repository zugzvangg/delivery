import uuid

from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


class TestOrder:
    """Тесты для класса Order"""

    def test_create_valid_order(self):
        """Тест создания коректного Order"""

        id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        location = Location(x=5, y=5)
        volume = 30
        order = Order(id=id, location=location, volume=volume)
        assert order.id == id
        assert order.location == location
        assert order.volume == volume
        assert order.status == OrderStatus.CREATED
        assert order.courier_id is None
