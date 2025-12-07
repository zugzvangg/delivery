import uuid

from src.delivery.core.application.use_cases.commands.create_order_command import (
    CreateOrderCommand,
    CreateOrderUseCase,
)
from src.delivery.core.domain.model.order.order import Order



class TestCreateOrderCommand:
    def test_create_order_command(self, db):
        create_order_use_case: CreateOrderUseCase = CreateOrderUseCase(db)
        order_id = uuid.uuid4()
        command = CreateOrderCommand(order_id=order_id, street="Pushkina", volume=10)
        create_order_use_case.handle(command)
        created_order: Order = create_order_use_case.order_repo.get_by_id(order_id)
        # заказ действительно есть в базе
        assert created_order.volume == 10


