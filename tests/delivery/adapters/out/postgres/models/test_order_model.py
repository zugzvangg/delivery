# tests/infrastructure/persistence/sqlalchemy/test_order_model_mappers.py
import uuid
from datetime import datetime

import pytest

from src.delivery.adapters.out.postgres.models.models import OrderModel
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus


class TestOrderModelMappers:
    """Тесты для методов преобразования ORM OrderModel <-> DTO Order"""

    def test_from_domain_object_creates_model_with_correct_fields(self):
        """Тест: from_domain_object создает модель с правильными полями"""
        # Arrange
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()
        domain_order = Order.create(
            order_id=order_id, location=Location.create(5, 7), volume=15
        )
        domain_order.assign(courier_id)  # Назначаем курьера

        # Act
        order_model = OrderModel.from_domain_object(domain_order)

        # Assert
        assert order_model.id == order_id
        assert order_model.location_x == 5
        assert order_model.location_y == 7
        assert order_model.volume == 15
        assert order_model.status == OrderStatus.ASSIGNED.value
        assert order_model.courier_id == courier_id

    def test_from_domain_object_for_created_order(self):
        """Тест: from_domain_object для заказа в статусе CREATED"""
        # Arrange
        domain_order = Order.create(
            order_id=uuid.uuid4(), location=Location.create(1, 1), volume=10
        )
        # Заказ остается в статусе CREATED

        # Act
        order_model = OrderModel.from_domain_object(domain_order)

        # Assert
        assert order_model.status == OrderStatus.CREATED.value
        assert order_model.courier_id is None
        assert order_model.volume == 10

    def test_from_domain_object_for_completed_order(self):
        """Тест: from_domain_object для заказа в статусе COMPLETED"""
        # Arrange
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()
        domain_order = Order.create(order_id, Location.create(2, 2), 8)
        domain_order.assign(courier_id)
        domain_order.complete()  # Завершаем заказ

        # Act
        order_model = OrderModel.from_domain_object(domain_order)

        # Assert
        assert order_model.status == OrderStatus.COMPLETED.value
        assert order_model.courier_id == courier_id
        assert order_model.location_x == 2
        assert order_model.location_y == 2

    def test_to_domain_object_restores_all_fields(self):
        """Тест: to_domain_object восстанавливает все поля доменного объекта"""
        # Arrange
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()

        order_model = OrderModel(
            id=order_id,
            location_x=3,
            location_y=4,
            volume=12,
            status=OrderStatus.ASSIGNED.value,
            courier_id=courier_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        domain_order = order_model.to_domain_object()

        # Assert
        assert isinstance(domain_order, Order)
        assert domain_order.id == order_id
        assert domain_order.location.x == 3
        assert domain_order.location.y == 4
        assert domain_order.volume == 12
        assert domain_order.status == OrderStatus.ASSIGNED
        assert domain_order.courier_id == courier_id

    def test_to_domain_object_without_courier(self):
        """Тест: to_domain_object для заказа без курьера"""
        # Arrange
        order_model = OrderModel(
            id=uuid.uuid4(),
            location_x=5,
            location_y=5,
            volume=20,
            status=OrderStatus.CREATED.value,
            courier_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        domain_order = order_model.to_domain_object()

        # Assert
        assert domain_order.status == OrderStatus.CREATED
        assert domain_order.courier_id is None
        assert domain_order.location.x == 5
        assert domain_order.location.y == 5

    def test_round_trip_conversion_preserves_all_data(self):
        """Тест: полный цикл Domain -> Model -> Domain сохраняет все данные"""
        # Arrange
        original_order_id = uuid.uuid4()
        original_courier_id = uuid.uuid4()

        original_order = Order.create(
            order_id=original_order_id, location=Location.create(7, 3), volume=18
        )
        original_order.assign(original_courier_id)
        original_order.complete()  # Переводим в COMPLETED

        # Act
        # Domain -> Model
        order_model = OrderModel.from_domain_object(original_order)

        # Model -> Domain
        restored_order = order_model.to_domain_object()

        # Assert
        assert restored_order.id == original_order_id
        assert restored_order.location.x == 7
        assert restored_order.location.y == 3
        assert restored_order.volume == 18
        assert restored_order.status == OrderStatus.COMPLETED
        assert restored_order.courier_id == original_courier_id

    def test_to_domain_object_creates_new_order_instance(self):
        """Тест: to_domain_object создает новый экземпляр Order"""
        # Arrange
        order_model = OrderModel(
            id=uuid.uuid4(),
            location_x=1,
            location_y=1,
            volume=5,
            status=OrderStatus.CREATED.value,
            courier_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        domain_order1 = order_model.to_domain_object()
        domain_order2 = order_model.to_domain_object()

        # Assert - должны быть разные объекты
        assert domain_order1 is not domain_order2
        assert domain_order1.id == domain_order2.id  # Но ID одинаковые
        assert domain_order1.location == domain_order2.location

    def test_from_domain_object_does_not_modify_original(self):
        """Тест: from_domain_object не изменяет исходный доменный объект"""
        # Arrange
        original_order = Order.create(uuid.uuid4(), Location.create(3, 4), 10)

        # Запоминаем исходное состояние
        original_id = original_order.id
        original_location = original_order.location
        original_volume = original_order.volume
        original_status = original_order.status

        # Act
        order_model = OrderModel.from_domain_object(original_order)

        # Assert - исходный объект не изменился
        assert original_order.id == original_id
        assert original_order.location == original_location
        assert original_order.volume == original_volume
        assert original_order.status == original_status

        # Проверяем что модель создана корректно
        assert order_model.id == original_id
        assert order_model.location_x == original_location.x
        assert order_model.location_y == original_location.y
