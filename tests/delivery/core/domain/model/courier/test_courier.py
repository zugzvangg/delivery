import uuid

import pytest

from src.delivery.core.domain.model.courier.courier import (
    Courier,
    CourierCanNotCompleteOrderError,
    CourierCanNotTakeOrderError,
    InvalidCourierLocationTypeError,
    InvalidCourierNameError,
    InvalidCourierSpeedError,
)
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


class TestCourier:
    """Тесты для агрегата Courier"""

    @pytest.fixture
    def valid_name(self):
        return "Test Courier"

    @pytest.fixture
    def valid_speed(self):
        return 2

    @pytest.fixture
    def valid_location(self):
        return Location.create(1, 1)

    @pytest.fixture
    def valid_order_id(self):
        return uuid.uuid4()

    @pytest.fixture
    def valid_courier(self, valid_name, valid_speed, valid_location):
        return Courier.create(valid_name, valid_speed, valid_location)

    @pytest.fixture
    def small_order(self, valid_order_id):
        location = Location.create(5, 5)
        return Order.create(valid_order_id, location, volume=5)

    @pytest.fixture
    def large_order(self, valid_order_id):
        location = Location.create(5, 5)
        return Order.create(valid_order_id, location, volume=15)

    def test_create_courier_success(self, valid_name, valid_speed, valid_location):
        """Тест успешного создания курьера"""
        # Act
        courier = Courier.create(valid_name, valid_speed, valid_location)

        # Assert
        assert courier.name == valid_name
        assert courier.speed == valid_speed
        assert courier.location == valid_location
        assert isinstance(courier.id, uuid.UUID)
        assert len(courier.storage_places) == 1
        assert courier.storage_places[0].name == "Сумка"
        assert courier.storage_places[0].total_volume == 10

    def test_create_courier_with_invalid_name(self, valid_speed, valid_location):
        """Тест создания курьера с невалидным именем"""
        # Arrange
        invalid_names = ["", "   ", 123, None]

        for name in invalid_names:
            # Act & Assert
            with pytest.raises(InvalidCourierNameError):
                Courier.create(name, valid_speed, valid_location)

    def test_create_courier_with_invalid_speed(self, valid_name, valid_location):
        """Тест создания курьера с невалидной скоростью"""
        # Arrange
        invalid_speeds = [0, -1, -10, "2", 2.5]

        for speed in invalid_speeds:
            # Act & Assert
            with pytest.raises(InvalidCourierSpeedError):
                Courier.create(valid_name, speed, valid_location)

    def test_create_courier_with_invalid_location(self, valid_name, valid_speed):
        """Тест создания курьера с невалидной локацией"""
        # Arrange
        invalid_locations = ["location", 123, None, [1, 1]]

        for location in invalid_locations:
            # Act & Assert
            with pytest.raises(InvalidCourierLocationTypeError):
                Courier.create(valid_name, valid_speed, location)

    def test_add_storage_place_success(self, valid_courier):
        """Тест успешного добавления места хранения"""
        # Arrange
        initial_count = len(valid_courier.storage_places)
        new_storage_name = "Багажник"
        new_storage_volume = 20

        # Act
        valid_courier.add_storage_place(new_storage_name, new_storage_volume)

        # Assert
        assert len(valid_courier.storage_places) == initial_count + 1
        assert valid_courier.storage_places[-1].name == new_storage_name
        assert valid_courier.storage_places[-1].total_volume == new_storage_volume

    def test_can_take_order_success(self, valid_courier, small_order):
        """Тест успешной проверки возможности взять заказ"""
        # Act & Assert
        assert valid_courier.can_take_order(small_order) is True

    def test_can_take_order_insufficient_volume(self, valid_courier, large_order):
        """Тест проверки когда объема недостаточно"""
        # Act & Assert
        assert valid_courier.can_take_order(large_order) is False

    def test_can_take_order_with_additional_storage(self, valid_courier, large_order):
        """Тест проверки с дополнительным местом хранения"""
        # Arrange
        valid_courier.add_storage_place("Багажник", 20)

        # Act & Assert
        assert valid_courier.can_take_order(large_order) is True

    def test_can_take_order_occupied_storage(self, valid_courier, small_order):
        """Тест проверки когда места хранения заняты"""
        # Arrange
        valid_courier.take_order(small_order)

        # Создаем второй заказ
        another_order_id = uuid.uuid4()
        another_order = Order.create(another_order_id, Location.create(3, 3), volume=5)

        # Act & Assert - не можем взять второй заказ того же объема
        assert valid_courier.can_take_order(another_order) is False

    def test_take_order_success(self, valid_courier, small_order):
        """Тест успешного взятия заказа"""
        # Arrange
        initial_order_status = small_order.status

        # Act
        valid_courier.take_order(small_order)

        # Assert
        # Проверяем что заказ помещен в storage
        order_in_storage = any(
            storage.order_id == small_order.id
            for storage in valid_courier.storage_places
        )
        assert order_in_storage is True
        assert small_order.status == OrderStatus.ASSIGNED
        assert small_order.courier_id == valid_courier.id
        assert initial_order_status == OrderStatus.CREATED

    def test_take_order_when_cannot_take(self, valid_courier, large_order):
        """Тест попытки взять заказ когда невозможно"""
        # Act & Assert
        with pytest.raises(
            CourierCanNotTakeOrderError, match="Courier can not take this order"
        ):
            valid_courier.take_order(large_order)

    def test_take_order_wrong_status(self, valid_courier, small_order):
        """Тест попытки взять заказ с неправильным статусом"""
        # Arrange
        small_order.assign(uuid.uuid4())  # Меняем статус на ASSIGNED

        # Act & Assert
        with pytest.raises(CourierCanNotTakeOrderError):
            valid_courier.take_order(small_order)

    def test_take_order_uses_first_available_storage(self, valid_courier, small_order):
        """Тест что заказ помещается в первое доступное место хранения"""
        # Arrange
        valid_courier.add_storage_place("Место1", 5)
        valid_courier.add_storage_place("Место2", 5)

        # Act
        valid_courier.take_order(small_order)

        # Assert - заказ должен быть в первом доступном месте (Сумка)
        assert valid_courier.storage_places[0].order_id == small_order.id
        assert valid_courier.storage_places[1].order_id is None
        assert valid_courier.storage_places[2].order_id is None

    def test_complete_order_success(self, valid_courier, small_order):
        """Тест успешного завершения заказа"""
        # Arrange
        valid_courier.take_order(small_order)
        initial_order_status = small_order.status

        # Act
        valid_courier.complete_order(small_order)

        # Assert
        # Проверяем что storage очищен
        order_in_storage = any(
            storage.order_id == small_order.id
            for storage in valid_courier.storage_places
        )
        assert order_in_storage is False
        assert small_order.status == OrderStatus.COMPLETED
        assert initial_order_status == OrderStatus.ASSIGNED

    def test_complete_order_not_found(self, valid_courier, small_order):
        """Тест завершения заказа который не у курьера"""
        # Act & Assert
        with pytest.raises(CourierCanNotCompleteOrderError):
            valid_courier.complete_order(small_order)

    def test_complete_order_multiple_storages(self, valid_courier, small_order):
        """Тест завершения заказа когда несколько мест хранения"""
        # Arrange
        valid_courier.add_storage_place("Багажник", 20)
        valid_courier.take_order(small_order)

        # Act
        valid_courier.complete_order(small_order)

        # Assert - все storage должны быть очищены от этого order_id
        for storage in valid_courier.storage_places:
            assert storage.order_id != small_order.id

    def test_calculate_time_to_location(self, valid_courier):
        """Тест расчета времени до локации"""
        # Arrange
        target_location = Location.create(5, 5)
        expected_distance = 8  # |1-5| + |1-5| = 8
        expected_time = expected_distance / valid_courier.speed  # 8 / 2 = 4

        # Act
        actual_time = valid_courier.calculate_time_to_location(target_location)

        # Assert
        assert actual_time == expected_time

    def test_calculate_time_to_same_location(self, valid_courier):
        """Тест расчета времени до той же локации"""
        # Arrange
        same_location = valid_courier.location

        # Act
        actual_time = valid_courier.calculate_time_to_location(same_location)

        # Assert
        assert actual_time == 0

    def test_calculate_time_invalid_location(self, valid_courier):
        """Тест расчета времени с невалидной локацией"""
        # Act & Assert
        with pytest.raises(InvalidCourierLocationTypeError):
            valid_courier.calculate_time_to_location("invalid_location")

    def test_move_toward_target(self, valid_courier):
        """Тест перемещения курьера к цели"""
        # Arrange
        initial_location = valid_courier.location
        target_location = Location.create(5, 5)

        # Act
        valid_courier.move(target_location)

        # Assert
        new_location = valid_courier.location
        assert new_location != initial_location
        # Проверяем что переместились в правильном направлении
        assert new_location.x >= initial_location.x
        assert new_location.y >= initial_location.y
        # Проверяем что не превысили скорость
        distance_moved = abs(new_location.x - initial_location.x) + abs(
            new_location.y - initial_location.y
        )
        assert distance_moved <= valid_courier.speed

    def test_move_to_same_location(self, valid_courier):
        """Тест перемещения к той же локации"""
        # Arrange
        initial_location = valid_courier.location
        same_location = Location.create(initial_location.x, initial_location.y)

        # Act
        valid_courier.move(same_location)

        # Assert
        assert valid_courier.location == initial_location

    def test_move_exact_distance(self, valid_courier):
        """Тест перемещения на точное расстояние по скорости"""
        # Arrange
        valid_courier = Courier.create("Test", 3, Location.create(1, 1))
        target_location = Location.create(4, 1)  # Расстояние 3 по X

        # Act
        valid_courier.move(target_location)

        # Assert - должен достичь цели за один ход
        assert valid_courier.location == target_location

    def test_move_partial_distance(self, valid_courier):
        """Тест частичного перемещения когда цель дальше скорости"""
        # Arrange
        target_location = Location.create(10, 10)  # Расстояние 18
        initial_location = valid_courier.location

        # Act
        valid_courier.move(target_location)

        # Assert - переместился только на 2 клетки (скорость)
        new_location = valid_courier.location
        distance_moved = abs(new_location.x - initial_location.x) + abs(
            new_location.y - initial_location.y
        )
        assert distance_moved == valid_courier.speed

    def test_move_invalid_target(self, valid_courier):
        """Тест перемещения к невалидной цели"""
        # Act & Assert
        with pytest.raises(InvalidCourierLocationTypeError):
            valid_courier.move("invalid_target")

    def test_storage_places_protection(self, valid_courier):
        """Тест что storage_places возвращает защитную копию"""
        # Arrange
        original_storages = valid_courier.storage_places

        # Act - пытаемся изменить возвращенный список
        original_storages.clear()

        # Assert - оригинальный список не должен измениться
        assert len(valid_courier.storage_places) == 1

    def test_courier_equality_by_id(self, valid_name, valid_speed, valid_location):
        """Тест равенства курьеров по ID"""
        # Arrange
        courier1 = Courier.create(valid_name, valid_speed, valid_location)
        courier2 = Courier.create(valid_name, valid_speed, valid_location)

        # Assert - разные ID, разные курьеры
        assert courier1.id != courier2.id

    def test_take_order_with_exact_volume(self, valid_courier, valid_order_id):
        """Тест взятия заказа с точным объемом места хранения"""
        # Arrange
        exact_volume_order = Order.create(
            valid_order_id, Location.create(3, 3), volume=10
        )
        # Act & Assert
        assert valid_courier.can_take_order(exact_volume_order) is True
        valid_courier.take_order(exact_volume_order)  # Не должно быть исключения

    def test_take_order_with_slightly_larger_volume(
        self, valid_courier, valid_order_id
    ):
        """Тест взятия заказа с объемом больше доступного"""
        # Arrange
        large_order = Order.create(valid_order_id, Location.create(3, 3), volume=11)

        # Act & Assert
        assert valid_courier.can_take_order(large_order) is False
        with pytest.raises(CourierCanNotTakeOrderError):
            valid_courier.take_order(large_order)

    def test_multiple_orders_flow(self, valid_courier, valid_order_id):
        """Тест полного жизненного цикла нескольких заказов"""
        # Arrange
        order1 = Order.create(valid_order_id, Location.create(2, 2), volume=5)
        order2_id = uuid.uuid4()
        order2 = Order.create(order2_id, Location.create(3, 3), volume=3)

        # Act & Assert - берем первый заказ
        valid_courier.take_order(order1)
        assert order1.status == OrderStatus.ASSIGNED
        assert any(
            storage.order_id == order1.id for storage in valid_courier.storage_places
        )

        # Не можем взять второй - места заняты
        assert valid_courier.can_take_order(order2) is False

        # Завершаем первый заказ
        valid_courier.complete_order(order1)
        assert order1.status == OrderStatus.COMPLETED
        assert not any(
            storage.order_id == order1.id for storage in valid_courier.storage_places
        )

        # Теперь можем взять второй
        assert valid_courier.can_take_order(order2) is True
        valid_courier.take_order(order2)
        assert order2.status == OrderStatus.ASSIGNED
        valid_courier.complete_order(order2)
        assert order2.status == OrderStatus.COMPLETED
        assert not any(
            storage.order_id == order2.id for storage in valid_courier.storage_places
        )

    def test_move_algorithm_correctness(self):
        """Тест корректности алгоритма перемещения"""
        # Arrange - курьер с большой скоростью
        courier = Courier.create("Fast", 5, Location.create(1, 1))
        target = Location.create(10, 10)

        # Act
        courier.move(target)

        # Assert - должен переместиться на 5 клеток в общем
        new_location = courier.location
        distance_moved = (new_location.x - 1) + (new_location.y - 1)
        assert distance_moved == 5

    def test_move_negative_direction(self):
        """Тест перемещения в отрицательном направлении"""
        # Arrange
        courier = Courier.create("Test", 3, Location.create(5, 5))
        target = Location.create(1, 1)

        # Act
        courier.move(target)

        # Assert
        new_location = courier.location
        assert new_location.x <= 5
        assert new_location.y <= 5
        distance_moved = (5 - new_location.x) + (5 - new_location.y)
        assert distance_moved == 3


@pytest.mark.parametrize(
    "speed,target_x,target_y,expected_max_move",
    [
        (2, 5, 5, 2),  # Диагональное движение
        (3, 5, 1, 3),  # Только по X
        (2, 1, 5, 2),  # Только по Y
        (5, 3, 3, 4),  # Комбинированное
    ],
)
def test_move_parametrized(speed, target_x, target_y, expected_max_move):
    """Параметризованный тест перемещения"""
    # Arrange
    courier = Courier.create("Test", speed, Location.create(1, 1))
    target = Location.create(target_x, target_y)
    initial_location = courier.location

    # Act
    courier.move(target)

    # Assert
    new_location = courier.location
    distance_moved = abs(new_location.x - initial_location.x) + abs(
        new_location.y - initial_location.y
    )
    assert distance_moved <= expected_max_move
