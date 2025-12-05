import uuid

from src.delivery.adapters.out.postgres.models.models import OrderModel
from src.delivery.adapters.out.postgres.repositories.order_repository import (
    OrderRepository,
)
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


class TestOrderRepository:
    def test_add_order(self, db):
        # --- Arrange ---
        repo = OrderRepository(db)
        order_id = uuid.uuid4()
        location = Location(1, 2)
        order = Order(
            id=order_id,
            location=location,
            volume=5,
        )

        # --- Act ---
        saved_order = repo.add(order)

        # --- Assert ---
        assert saved_order.id == order.id
        assert saved_order.location.x == 1
        assert saved_order.location.y == 2
        assert saved_order.volume == 5
        assert saved_order.status == OrderStatus.CREATED

        # Проверяем, что запись действительно в БД
        db_order = db.get(OrderModel, order.id)
        assert db_order is not None
        assert db_order.volume == 5
        assert db_order.location_x == 1
        assert db_order.location_y == 2
        assert db_order.id == order_id
        
