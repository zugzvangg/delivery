from src.delivery.core.domain.model.order.order_status import OrderStatus


def test_order_status():
    # Проверяем значения
    assert OrderStatus.CREATED.value == "CREATED"
    assert OrderStatus.ASSIGNED.value == "ASSIGNED"
    assert OrderStatus.COMPLETED.value == "COMPLETED"

    # Проверяем имена
    assert OrderStatus.CREATED.name == "CREATED"
    assert OrderStatus.ASSIGNED.name == "ASSIGNED"
    assert OrderStatus.COMPLETED.name == "COMPLETED"

    # Проверяем сравнение
    assert OrderStatus.CREATED == OrderStatus.CREATED
    assert OrderStatus.ASSIGNED != OrderStatus.CREATED

    # Проверяем список всех значений
    all_statuses = list(OrderStatus)
    assert len(all_statuses) == 3
    assert OrderStatus.CREATED in all_statuses
