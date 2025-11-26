import uuid
from unittest.mock import Mock

import pytest

from src.delivery.core.domain.model.courier.courier import (
    Courier,
    CourierCanNotTakeOrderError,
)
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import NotCreatedOrderStatus, Order
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
    def sample_order(self):
        order_id = uuid.uuid4()
        return Order.create(order_id, Location.create(5, 5), volume=5)

    @pytest.fixture
    def large_order(self):
        order_id = uuid.uuid4()
        return Order.create(order_id, Location.create(3, 3), volume=15)

    @pytest.fixture
    def fast_courier(self):
        return Courier.create("Fast Courier", 3, Location.create(3, 3))

    @pytest.fixture
    def slow_courier(self):
        return Courier.create("Slow Courier", 1, Location.create(1, 1))

    @pytest.fixture
    def distant_courier(self):
        return Courier.create("Distant Courier", 2, Location.create(10, 10))

    # Тесты для метода dispatch
    def test_dispatch_success(self, dispatcher, sample_order, fast_courier):
        """Тест успешного назначения заказа курьеру"""
        # Arrange
        initial_order_status = sample_order.status

        # Act
        dispatcher.dispatch(sample_order, fast_courier)

        # Assert
        assert sample_order.status == OrderStatus.ASSIGNED
        assert sample_order.courier_id == fast_courier.id
        assert sample_order.status != initial_order_status

        # Проверяем что курьер хранит заказ
        assert fast_courier.get_assigned_order_id() == sample_order.id

    def test_dispatch_courier_cannot_take_order(
        self, dispatcher, large_order, fast_courier
    ):
        """Тест назначения когда курьер не может взять заказ"""
        # Arrange
        initial_order_status = large_order.status

        # Act & Assert
        with pytest.raises(
            CourierCanNotTakeOrderErrorDisp
        ):  # CourierCanNotTakeOrderError из take_order
            dispatcher.dispatch(large_order, fast_courier)

        # Проверяем что состояние не изменилось
        assert large_order.status == initial_order_status
        assert large_order.courier_id is None
        assert fast_courier.get_assigned_order_id() is None

    def test_dispatch_invalid_order_type(self, dispatcher, fast_courier):
        """Тест назначения с невалидным типом заказа"""
        # Act & Assert
        with pytest.raises(InvalidOrderType):
            dispatcher.dispatch("invalid_order", fast_courier)

    def test_dispatch_invalid_courier_type(self, dispatcher, sample_order):
        """Тест назначения с невалидным типом курьера"""
        # Act & Assert
        with pytest.raises(InvalidCourierType):
            dispatcher.dispatch(sample_order, "invalid_courier")

    # Тесты для метода complete
    def test_complete_success(self, dispatcher, sample_order, fast_courier):
        """Тест успешного завершения заказа"""
        # Arrange
        dispatcher.dispatch(sample_order, fast_courier)

        # Act
        dispatcher.complete(sample_order, fast_courier)

        # Assert
        assert sample_order.status == OrderStatus.COMPLETED
        assert fast_courier.get_assigned_order_id() is None

    def test_complete_order_not_assigned(self, dispatcher, sample_order, fast_courier):
        """Тест завершения неназначенного заказа"""
        # Act & Assert
        with pytest.raises(Exception):  # CourierCanNotCompleteOrderError
            dispatcher.complete(sample_order, fast_courier)

    def test_complete_invalid_order_type(self, dispatcher, fast_courier):
        """Тест завершения с невалидным типом заказа"""
        # Act & Assert
        with pytest.raises(InvalidOrderType):
            dispatcher.complete("invalid_order", fast_courier)

    def test_complete_invalid_courier_type(self, dispatcher, sample_order):
        """Тест завершения с невалидным типом курьера"""
        # Act & Assert
        with pytest.raises(InvalidCourierType):
            dispatcher.complete(sample_order, "invalid_courier")

    # Тесты для метода find_best_courier
    def test_find_best_courier_success(
        self, dispatcher, sample_order, fast_courier, slow_courier
    ):
        """Тест успешного поиска лучшего курьера"""
        # Arrange
        couriers = [slow_courier, fast_courier]

        # Act
        best_courier = dispatcher.find_best_courier(sample_order, couriers)

        # Assert
        assert best_courier == fast_courier
        # Проверяем что заказ НЕ назначен
        assert sample_order.status == OrderStatus.CREATED
        assert sample_order.courier_id is None

    def test_find_best_courier_returns_fastest(
        self, dispatcher, sample_order, fast_courier, slow_courier, distant_courier
    ):
        """Тест что возвращается действительно самый быстрый курьер"""
        # Arrange
        couriers = [slow_courier, distant_courier, fast_courier]

        # Act
        best_courier = dispatcher.find_best_courier(sample_order, couriers)

        # Assert
        assert best_courier == fast_courier

    def test_find_best_courier_no_available_couriers(
        self, dispatcher, sample_order, fast_courier
    ):
        """Тест когда нет подходящих курьеров"""
        # Arrange
        # Занимаем место хранения у курьера
        other_order = Order.create(uuid.uuid4(), Location.create(2, 2), volume=10)
        fast_courier.take_order(other_order)
        couriers = [fast_courier]

        # Act
        best_courier = dispatcher.find_best_courier(sample_order, couriers)

        # Assert
        assert best_courier is None

    def test_find_best_courier_empty_list(self, dispatcher, sample_order):
        """Тест с пустым списком курьеров"""
        # Act
        best_courier = dispatcher.find_best_courier(sample_order, [])

        # Assert
        assert best_courier is None

    def test_find_best_courier_order_not_created(self, dispatcher, fast_courier):
        """Тест поиска для заказа не в статусе CREATED"""
        # Arrange
        order = Order.create(uuid.uuid4(), Location.create(1, 1), volume=5)
        order.assign(uuid.uuid4())  # Меняем статус на ASSIGNED
        couriers = [fast_courier]

        # Act & Assert
        with pytest.raises(NotCreatedOrderStatus):
            dispatcher.find_best_courier(order, couriers)

    def test_find_best_courier_invalid_order_type(self, dispatcher, fast_courier):
        """Тест с невалидным типом заказа"""
        # Act & Assert
        with pytest.raises(InvalidOrderType):
            dispatcher.find_best_courier("invalid_order", [fast_courier])

    def test_find_best_courier_invalid_couriers_list(self, dispatcher, sample_order):
        """Тест с невалидным списком курьеров"""
        # Act & Assert
        with pytest.raises(InvalidCourierType):
            dispatcher.find_best_courier(sample_order, "invalid_list")

    def test_find_best_courier_invalid_courier_in_list(
        self, dispatcher, sample_order, fast_courier
    ):
        """Тест с невалидным курьером в списке"""
        # Act & Assert
        with pytest.raises(InvalidCourierType):
            dispatcher.find_best_courier(
                sample_order, [fast_courier, "invalid_courier"]
            )

    # Тесты для метода assign_to_best_courier
    def test_assign_to_best_courier_success(
        self, dispatcher, sample_order, fast_courier, slow_courier
    ):
        """Тест успешного назначения лучшего курьера"""
        # Arrange
        couriers = [slow_courier, fast_courier]

        # Act
        assigned_courier = dispatcher.assign_to_best_courier(sample_order, couriers)

        # Assert
        assert assigned_courier == fast_courier
        assert sample_order.status == OrderStatus.ASSIGNED
        assert sample_order.courier_id == fast_courier.id
        assert fast_courier.get_assigned_order_id() == sample_order.id

    def test_assign_to_best_courier_no_available(
        self, dispatcher, sample_order, fast_courier
    ):
        """Тест когда нет доступных курьеров"""
        # Arrange
        # Занимаем место хранения
        other_order = Order.create(uuid.uuid4(), Location.create(2, 2), volume=10)
        fast_courier.take_order(other_order)
        couriers = [fast_courier]

        # Act
        assigned_courier = dispatcher.assign_to_best_courier(sample_order, couriers)

        # Assert
        assert assigned_courier is None
        assert sample_order.status == OrderStatus.CREATED
        assert sample_order.courier_id is None

    def test_assign_to_best_courier_empty_list(self, dispatcher, sample_order):
        """Тест назначения с пустым списком курьеров"""
        # Act
        assigned_courier = dispatcher.assign_to_best_courier(sample_order, [])

        # Assert
        assert assigned_courier is None

    def test_assign_to_best_courier_complex_scenario(self, dispatcher):
        """Тест сложного сценария с несколькими курьерами"""
        # Arrange
        order = Order.create(uuid.uuid4(), Location.create(8, 8), volume=5)

        # Создаем курьеров с разными характеристиками
        courier1 = Courier.create("Close but busy", 2, Location.create(7, 7))
        courier2 = Courier.create("Far but fast", 4, Location.create(1, 1))
        courier3 = Courier.create("Best choice", 3, Location.create(6, 6))

        # Занимаем место у первого курьера
        busy_order = Order.create(uuid.uuid4(), Location.create(2, 2), volume=10)
        courier1.take_order(busy_order)

        couriers = [courier1, courier2, courier3]

        # Act
        assigned_courier = dispatcher.assign_to_best_courier(order, couriers)

        # Assert
        assert (
            assigned_courier == courier3
        )  # Должен победить courier3 как самый быстрый из доступных
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == courier3.id

    # Интеграционные тесты
    def test_full_workflow(self, dispatcher):
        """Тест полного рабочего процесса: поиск -> назначение -> завершение"""
        # Arrange
        order = Order.create(uuid.uuid4(), Location.create(5, 5), volume=5)
        courier1 = Courier.create("Courier1", 2, Location.create(3, 3))
        courier2 = Courier.create("Courier2", 3, Location.create(4, 4))
        couriers = [courier1, courier2]

        # Act & Assert - поиск лучшего
        best_courier = dispatcher.find_best_courier(order, couriers)
        assert best_courier == courier2
        assert order.status == OrderStatus.CREATED

        # Act & Assert - назначение
        assigned_courier = dispatcher.assign_to_best_courier(order, couriers)
        assert assigned_courier == courier2
        assert order.status == OrderStatus.ASSIGNED

        # Act & Assert - завершение
        dispatcher.complete(order, courier2)
        assert order.status == OrderStatus.COMPLETED
        assert courier2.get_assigned_order_id() is None
