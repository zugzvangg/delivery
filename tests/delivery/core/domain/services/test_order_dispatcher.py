import uuid
from unittest.mock import Mock

import pytest

from src.delivery.core.domain.model.courier.courier import (
    Courier,
    CourierCanNotCompleteOrderError,
    CourierCanNotTakeOrderError,
)
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus
from src.delivery.core.domain.services.order_dispatcher import (
    InvalidCourierType,
    InvalidOrderType,
    OrderDispatcher,
)


class TestOrderDispatcher:
    """Тесты для сервиса OrderDispatcher"""

    @pytest.fixture
    def dispatcher(self):
        return OrderDispatcher()

    @pytest.fixture
    def valid_courier(self):
        return Courier.create("Test Courier", 2, Location.create(1, 1))

    @pytest.fixture
    def valid_order(self):
        order_id = uuid.uuid4()
        return Order.create(order_id, Location.create(5, 5), volume=5)

    @pytest.fixture
    def large_order(self):
        order_id = uuid.uuid4()
        return Order.create(order_id, Location.create(5, 5), volume=15)

    def test_dispatch_success(self, dispatcher, valid_courier, valid_order):
        """Тест успешного назначения заказа курьеру"""
        # Arrange
        initial_order_status = valid_order.status
        initial_courier_storage_empty = all(
            storage.order_id is None for storage in valid_courier.storage_places
        )
        # изначально пустой
        assert initial_courier_storage_empty
        # Act
        dispatcher.dispatch(valid_order, valid_courier)

        # Assert
        # Проверяем что Order изменился
        assert valid_order.status == OrderStatus.ASSIGNED
        assert valid_order.courier_id == valid_courier.id
        assert valid_order.status != initial_order_status

        # Проверяем что Courier изменился
        initial_courier_storage_empty = all(
            storage.order_id is None for storage in valid_courier.storage_places
        )
        assert not initial_courier_storage_empty  # Был пуст, теперь нет
        order_in_storage = any(
            storage.order_id == valid_order.id
            for storage in valid_courier.storage_places
        )
        assert order_in_storage is True

    def test_dispatch_when_courier_cannot_take_order(
        self, dispatcher, valid_courier, large_order
    ):
        """Тест попытки назначения заказа когда курьер не может его взять"""
        # Arrange
        initial_order_status = large_order.status

        # ничего не произойдет
        dispatcher.dispatch(large_order, valid_courier)

        # Проверяем что состояние не изменилось
        assert large_order.status == initial_order_status
        assert large_order.courier_id is None
        assert valid_courier.get_assigned_order_id() is None

    def test_complete_success(self, dispatcher, valid_courier, valid_order):
        """Тест успешного завершения заказа"""
        # Arrange
        dispatcher.dispatch(valid_order, valid_courier)
        assigned_order_id_before = valid_courier.get_assigned_order_id()

        # Act
        dispatcher.complete(valid_order, valid_courier)

        # Assert
        # Проверяем что Order завершен
        assert valid_order.status == OrderStatus.COMPLETED
        assert valid_order.courier_id == valid_courier.id  # courier_id остается

        # Проверяем что Courier очистил storage
        assert valid_courier.get_assigned_order_id() is None
        assert assigned_order_id_before == valid_order.id  # Был назначен

    def test_complete_order_not_assigned_to_courier(
        self, dispatcher, valid_courier, valid_order
    ):
        """Тест завершения заказа который не назначен этому курьеру"""
        # Arrange
        # Order создан, но не назначен через dispatcher
        initial_order_status = valid_order.status

        # Act & Assert
        with pytest.raises(CourierCanNotCompleteOrderError):
            dispatcher.complete(valid_order, valid_courier)

        # Проверяем что состояние не изменилось
        assert valid_order.status == initial_order_status
        assert valid_courier.get_assigned_order_id() is None

    def test_dispatch_invalid_order_type(self, dispatcher, valid_courier):
        """Тест назначения с невалидным типом заказа"""
        # Arrange
        invalid_order = "not_an_order"

        # Act & Assert
        with pytest.raises(InvalidOrderType):
            dispatcher.dispatch(invalid_order, valid_courier)

    def test_dispatch_invalid_courier_type(self, dispatcher, valid_order):
        """Тест назначения с невалидным типом курьера"""
        # Arrange
        invalid_courier = "not_a_courier"

        # Act & Assert
        with pytest.raises(InvalidCourierType):
            dispatcher.dispatch(valid_order, invalid_courier)

    def test_complete_invalid_order_type(self, dispatcher, valid_courier):
        """Тест завершения с невалидным типом заказа"""
        # Arrange
        invalid_order = "not_an_order"

        # Act & Assert
        with pytest.raises(InvalidOrderType):
            dispatcher.complete(invalid_order, valid_courier)

    def test_complete_invalid_courier_type(self, dispatcher, valid_order):
        """Тест завершения с невалидным типом курьера"""
        # Arrange
        invalid_courier = "not_a_courier"

        # Act & Assert
        with pytest.raises(InvalidCourierType):
            dispatcher.complete(valid_order, invalid_courier)

    def test_multiple_operations_flow(self, dispatcher, valid_courier):
        """Тест полного цикла: назначение -> завершение -> новое назначение"""
        # Arrange
        order1_id = uuid.uuid4()
        order1 = Order.create(order1_id, Location.create(2, 2), volume=5)
        order2_id = uuid.uuid4()
        order2 = Order.create(order2_id, Location.create(3, 3), volume=3)

        # Act & Assert - первый заказ
        dispatcher.dispatch(order1, valid_courier)
        assert order1.status == OrderStatus.ASSIGNED
        assert valid_courier.get_assigned_order_id() == order1.id

        # Завершаем первый заказ
        dispatcher.complete(order1, valid_courier)
        assert order1.status == OrderStatus.COMPLETED
        assert valid_courier.get_assigned_order_id() is None

        # Назначаем второй заказ
        dispatcher.dispatch(order2, valid_courier)
        assert order2.status == OrderStatus.ASSIGNED
        assert valid_courier.get_assigned_order_id() == order2.id

    def test_dispatch_already_assigned_order(
        self, dispatcher, valid_courier, valid_order
    ):
        """Тест назначения уже назначенного заказа"""
        # Arrange
        dispatcher.dispatch(valid_order, valid_courier)

        another_courier = Courier.create("Another Courier", 3, Location.create(2, 2))

        # Act & Assert
        with pytest.raises(Exception):  # Order уже в статусе ASSIGNED
            dispatcher.dispatch(valid_order, another_courier)

        # Проверяем что заказ остался у первого курьера
        assert valid_order.courier_id == valid_courier.id
        assert valid_courier.get_assigned_order_id() == valid_order.id
        assert another_courier.get_assigned_order_id() is None
