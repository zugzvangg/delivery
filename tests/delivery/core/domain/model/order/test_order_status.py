import uuid
from unittest.mock import Mock

import pytest

from src.delivery.core.domain.model.common import InvalidUUIDError
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import (
    InvalidVolume,
    Order,
    WrongLocationTypeError,
)
from src.delivery.core.domain.model.order.order_status import (
    NotAssignedOrderStatus,
    NotCreatedOrderStatus,
    OrderStatus,
)


class TestOrder:
    """Тесты для агрегата Order"""

    @pytest.fixture
    def valid_order_id(self):
        return uuid.uuid4()

    @pytest.fixture
    def valid_location(self):
        return Mock(spec=Location)

    @pytest.fixture
    def valid_volume(self):
        return 10

    @pytest.fixture
    def valid_courier_id(self):
        return uuid.uuid4()

    def test_create_order_success(self, valid_order_id, valid_location, valid_volume):
        """Тест успешного создания заказа"""
        # Act
        order = Order.create(valid_order_id, valid_location, valid_volume)

        # Assert
        assert order.id == valid_order_id
        assert order.location == valid_location
        assert order.volume == valid_volume
        assert order.status == OrderStatus.CREATED
        assert order.courier_id is None

    def test_create_order_with_invalid_id(self, valid_location, valid_volume):
        """Тест создания заказа с невалидным UUID"""
        # Arrange
        invalid_id = "not-a-uuid"

        # Act & Assert
        with pytest.raises(InvalidUUIDError):
            Order.create(invalid_id, valid_location, valid_volume)

    def test_create_order_with_invalid_location_type(
        self, valid_order_id, valid_volume
    ):
        """Тест создания заказа с невалидным типом location"""
        # Arrange
        invalid_location = "not-a-location"

        # Act & Assert
        with pytest.raises(WrongLocationTypeError):
            Order.create(valid_order_id, invalid_location, valid_volume)

    def test_create_order_with_invalid_volume_type(
        self, valid_order_id, valid_location
    ):
        """Тест создания заказа с невалидным типом volume"""
        # Arrange
        invalid_volume = "not-an-int"

        # Act & Assert
        with pytest.raises(InvalidVolume):
            Order.create(valid_order_id, valid_location, invalid_volume)

    def test_create_order_with_non_positive_volume(
        self, valid_order_id, valid_location
    ):
        """Тест создания заказа с неположительным volume"""
        # Arrange
        non_positive_volumes = [0, -1, -10]

        for volume in non_positive_volumes:
            # Act & Assert
            with pytest.raises(InvalidVolume):
                Order.create(valid_order_id, valid_location, volume)

    def test_assign_order_success(
        self, valid_order_id, valid_location, valid_volume, valid_courier_id
    ):
        """Тест успешного назначения заказа курьеру"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)

        # Act
        order.assign(valid_courier_id)

        # Assert
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == valid_courier_id

    def test_assign_order_with_invalid_courier_id(
        self, valid_order_id, valid_location, valid_volume
    ):
        """Тест назначения заказа с невалидным courier_id"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)
        invalid_courier_id = "not-a-uuid"

        # Act & Assert
        with pytest.raises(InvalidUUIDError):
            order.assign(invalid_courier_id)

    def test_assign_already_assigned_order(
        self, valid_order_id, valid_location, valid_volume, valid_courier_id
    ):
        """Тест попытки назначения уже назначенного заказа"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)
        order.assign(valid_courier_id)

        another_courier_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(NotCreatedOrderStatus):
            order.assign(another_courier_id)

        # Проверяем, что состояние не изменилось
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == valid_courier_id

    def test_assign_completed_order(
        self, valid_order_id, valid_location, valid_volume, valid_courier_id
    ):
        """Тест попытки назначения завершенного заказа"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)
        order.assign(valid_courier_id)
        order.complete()

        another_courier_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(NotCreatedOrderStatus):
            order.assign(another_courier_id)

        # Проверяем, что состояние не изменилось
        assert order.status == OrderStatus.COMPLETED
        assert order.courier_id == valid_courier_id

    def test_complete_order_success(
        self, valid_order_id, valid_location, valid_volume, valid_courier_id
    ):
        """Тест успешного завершения заказа"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)
        order.assign(valid_courier_id)

        # Act
        order.complete()

        # Assert
        assert order.status == OrderStatus.COMPLETED
        assert order.courier_id == valid_courier_id

    def test_complete_not_assigned_order(
        self, valid_order_id, valid_location, valid_volume
    ):
        """Тест попытки завершения неназначенного заказа"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)

        # Act & Assert
        with pytest.raises(NotAssignedOrderStatus):
            order.complete()

        # Проверяем, что состояние не изменилось
        assert order.status == OrderStatus.CREATED
        assert order.courier_id is None

    def test_complete_already_completed_order(
        self, valid_order_id, valid_location, valid_volume, valid_courier_id
    ):
        """Тест попытки завершения уже завершенного заказа"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)
        order.assign(valid_courier_id)
        order.complete()

        # Act & Assert
        with pytest.raises(NotAssignedOrderStatus):
            order.complete()

        # Проверяем, что состояние не изменилось
        assert order.status == OrderStatus.COMPLETED

    def test_order_immutability_through_properties(
        self, valid_order_id, valid_location, valid_volume
    ):
        """Тест, что приватные поля нельзя изменить через свойства"""
        # Arrange
        order = Order.create(valid_order_id, valid_location, valid_volume)

        # Act & Assert - попытка изменить свойства должна вызвать ошибку
        with pytest.raises(AttributeError):
            order.id = uuid.uuid4()

        with pytest.raises(AttributeError):
            order.location = Mock(spec=Location)

        with pytest.raises(AttributeError):
            order.volume = 20

        with pytest.raises(AttributeError):
            order.status = OrderStatus.ASSIGNED

        with pytest.raises(AttributeError):
            order.courier_id = uuid.uuid4()

    def test_multiple_operations_flow(
        self, valid_order_id, valid_location, valid_volume, valid_courier_id
    ):
        """Тест полного жизненного цикла заказа"""
        # Arrange & Act
        order = Order.create(valid_order_id, valid_location, valid_volume)
        assert order.status == OrderStatus.CREATED
        assert order.courier_id is None

        order.assign(valid_courier_id)
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == valid_courier_id

        order.complete()
        assert order.status == OrderStatus.COMPLETED
        assert order.courier_id == valid_courier_id

    def test_different_valid_volumes(self, valid_order_id, valid_location):
        """Тест создания заказа с разными валидными объемами"""
        # Arrange
        valid_volumes = [1, 5, 100, 1000]

        for volume in valid_volumes:
            # Act
            order = Order.create(valid_order_id, valid_location, volume)

            # Assert
            assert order.volume == volume
