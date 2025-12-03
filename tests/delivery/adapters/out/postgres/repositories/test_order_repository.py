import uuid
from datetime import datetime

import pytest

from src.delivery.adapters.out.postgres.repositories.order_repository import (
    OrderRepository,
)
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


# @pytest.mark.asyncio
# async def test_add_order(db_session_with_commit):
#     """Тест добавления заказа в репозиторий."""
#     # Arrange
#     repository = OrderRepository(db_session_with_commit)
#     location = Location.create(x=1, y=1)
#     order = Order.create(order_id=uuid.uuid4(), location=location, volume=100)

#     # Act
#     saved_order = await repository.add_order(order)

#     # Assert
#     assert isinstance(saved_order, Order)
#     assert saved_order.id == order.id
#     assert saved_order.location == order.location
#     assert saved_order.volume == order.volume
#     assert saved_order.status.name == OrderStatus.CREATED
#     assert saved_order.courier_id is None
