import pytest

from src.delivery.core.domain.model.order.order_status import (
    NotAssignedOrderStatus,
    NotCompletedOrderStatus,
    NotCreatedOrderStatus,
    OrderStatus,
)


class TestOrderStatus:
    """Тесты для enum OrderStatus"""

    def test_order_status_values(self):
        """Тест корректности значений enum"""
        # Assert
        assert OrderStatus.CREATED.value == "CREATED"
        assert OrderStatus.ASSIGNED.value == "ASSIGNED"
        assert OrderStatus.COMPLETED.value == "COMPLETED"

    def test_order_status_members(self):
        """Тест наличия всех ожидаемых членов enum"""
        # Act
        members = list(OrderStatus)

        # Assert
        assert len(members) == 3
        assert OrderStatus.CREATED in members
        assert OrderStatus.ASSIGNED in members
        assert OrderStatus.COMPLETED in members

    def test_order_status_string_representation(self):
        """Тест строкового представления enum"""
        # Assert
        assert str(OrderStatus.CREATED) == "OrderStatus.CREATED"
        assert str(OrderStatus.ASSIGNED) == "OrderStatus.ASSIGNED"
        assert str(OrderStatus.COMPLETED) == "OrderStatus.COMPLETED"

    def test_order_status_allowed_transitions(self):
        """Тест допустимых переходов между статусами"""
        # Этот тест проверяет бизнес-логику переходов
        allowed_transitions = {
            OrderStatus.CREATED: [OrderStatus.ASSIGNED],
            OrderStatus.ASSIGNED: [OrderStatus.COMPLETED],
            OrderStatus.COMPLETED: [],  # Завершенный заказ не может менять статус
        }

        # Assert
        assert OrderStatus.ASSIGNED in allowed_transitions[OrderStatus.CREATED]
        assert OrderStatus.COMPLETED in allowed_transitions[OrderStatus.ASSIGNED]
        assert OrderStatus.CREATED not in allowed_transitions[OrderStatus.ASSIGNED]
        assert len(allowed_transitions[OrderStatus.COMPLETED]) == 0


@pytest.mark.parametrize(
    "invalid_value",
    [
        "CREATED_INVALID",
        "ASSIGNED_INVALID",
        "COMPLETED_INVALID",
        "",
        None,
        123,
    ],
)
def test_order_status_invalid_values(invalid_value):
    """Параметризованный тест невалидных значений для OrderStatus"""
    with pytest.raises(ValueError):
        OrderStatus(invalid_value)
