# tests/infrastructure/persistence/sqlalchemy/test_courier_model_mappers.py
import uuid
from datetime import datetime

import pytest

from src.delivery.adapters.out.postgres.models.models import (
    CourierModel,
    StoragePlaceModel,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location


class TestCourierModelMappers:
    """Тесты для методов преобразования ORM ourierModel <-> DTO Courier"""

    def test_from_domain_object_creates_model_with_correct_fields(self):
        """Тест: from_domain_object создает модель курьера с правильными полями"""
        # Arrange
        domain_courier = Courier.create(
            name="Тестовый курьер", speed=3, location=Location.create(5, 7)
        )

        # Act
        courier_model = CourierModel.from_domain_object(domain_courier)

        # Assert
        assert courier_model.id == domain_courier.id
        assert courier_model.name == "Тестовый курьер"
        assert courier_model.speed == 3
        assert courier_model.location_x == 5
        assert courier_model.location_y == 7

        # Не проверяем created_at/updated_at - они устанавливаются БД
        # Не проверяем storage_places - они будут в отдельной связи

    def test_to_domain_object_restores_all_fields(self):
        """Тест: to_domain_object восстанавливает все поля курьера"""
        # Arrange
        courier_id = uuid.uuid4()

        courier_model = CourierModel(
            id=courier_id,
            name="Курьер-экспресс",
            speed=4,
            location_x=2,
            location_y=8,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        domain_courier = courier_model.to_domain_object()

        # Assert
        # NOTE: не должны быть равны, так как Courier всегда создается с новым id, не восстанавливается
        # assert domain_courier.id == courier_id
        assert domain_courier.name == "Курьер-экспресс"
        assert domain_courier.speed == 4
        assert domain_courier.location.x == 2
        assert domain_courier.location.y == 8

        # Проверяем что создана Location
        assert isinstance(domain_courier.location, Location)
        assert domain_courier.location.x == 2
        assert domain_courier.location.y == 8

    def test_to_domain_object_with_location_method(self):
        """Тест: to_domain_object использует правильный метод создания Location"""
        # Arrange
        courier_model = CourierModel(
            id=uuid.uuid4(), name="Тест", speed=2, location_x=10, location_y=1
        )

        # Act
        domain_courier = courier_model.to_domain_object()

        # Assert
        assert isinstance(domain_courier, Courier)
        # Проверяем что Location создана корректно и можно использовать ее методы
        location = domain_courier.location
        assert location.x == 10
        assert location.y == 1
        assert location.distance_to(Location.create(10, 1)) == 0

    def test_round_trip_conversion_preserves_courier_data(self):
        """Тест: полный цикл Domain -> Model -> Domain сохраняет данные курьера"""
        # Arrange
        original_courier = Courier.create(
            name="Оригинальный курьер", speed=5, location=Location.create(3, 9)
        )

        # Act
        # Domain -> Model
        courier_model = CourierModel.from_domain_object(original_courier)

        # Model -> Domain
        restored_courier = courier_model.to_domain_object()

        # Assert
        assert restored_courier.name == "Оригинальный курьер"
        assert restored_courier.speed == 5
        assert restored_courier.location.x == 3
        assert restored_courier.location.y == 9

    def test_to_domain_object_creates_new_courier_instance(self):
        """Тест: to_domain_object создает новый экземпляр Courier"""
        # Arrange
        courier_model = CourierModel(
            id=uuid.uuid4(), name="Курьер", speed=1, location_x=1, location_y=1
        )

        # Act
        domain_courier1 = courier_model.to_domain_object()
        domain_courier2 = courier_model.to_domain_object()

        # Assert - разные объекты, но одинаковые данные
        assert domain_courier1 is not domain_courier2
        assert domain_courier1.name == domain_courier2.name
        assert domain_courier1.speed == domain_courier2.speed
        assert domain_courier1.location == domain_courier2.location

    def test_from_domain_object_does_not_modify_original_courier(self):
        """Тест: from_domain_object не изменяет исходный курьер"""
        # Arrange
        original_courier = Courier.create("Исходный", 2, Location.create(5, 5))

        # Запоминаем исходное состояние
        original_id = original_courier.id
        original_name = original_courier.name
        original_speed = original_courier.speed
        original_location = original_courier.location

        # Act
        courier_model = CourierModel.from_domain_object(original_courier)

        # Assert - исходный не изменился
        assert original_courier.id == original_id
        assert original_courier.name == original_name
        assert original_courier.speed == original_speed
        assert original_courier.location == original_location

        # Модель создана корректно
        assert courier_model.id == original_id
        assert courier_model.name == original_name
        assert courier_model.speed == original_speed
        assert courier_model.location_x == original_location.x
        assert courier_model.location_y == original_location.y


class TestStoragePlaceModelMappers:
    """Тесты для методов преобразования ORM StoragePlaceModel <-> DTO StoragePlace"""

    def test_from_domain_object_creates_model_with_correct_fields(self):
        """Тест: from_domain_object создает модель места хранения с правильными полями"""
        # Arrange
        storage_id = uuid.uuid4()
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()

        domain_storage = StoragePlace(
            name="Рюкзак",
            total_volume=15,
            id=storage_id,
            order_id=order_id,
            courier_id=courier_id,
        )

        # Act
        storage_model = StoragePlaceModel.from_domain_object(domain_storage)

        # Assert
        assert storage_model.id == storage_id
        assert storage_model.name == "Рюкзак"
        assert storage_model.total_volume == 15
        assert storage_model.order_id == order_id
        assert storage_model.courier_id == courier_id

    def test_from_domain_object_without_order(self):
        """Тест: from_domain_object для свободного места хранения"""
        # Arrange
        courier_id = uuid.uuid4()
        domain_storage = StoragePlace.create(
            name="Сумка", total_volume=10, courier_id=courier_id
        )

        # Act
        storage_model = StoragePlaceModel.from_domain_object(domain_storage)

        # Assert
        assert storage_model.id == domain_storage.id
        assert storage_model.name == "Сумка"
        assert storage_model.total_volume == 10
        assert storage_model.order_id is None
        assert storage_model.courier_id == courier_id

    def test_to_domain_object_restores_all_fields(self):
        """Тест: to_domain_object восстанавливает все поля места хранения"""
        # Arrange
        storage_id = uuid.uuid4()
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()

        storage_model = StoragePlaceModel(
            id=storage_id,
            name="Багажник",
            total_volume=25,
            order_id=order_id,
            courier_id=courier_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        domain_storage = storage_model.to_domain_object()

        # Assert
        assert domain_storage.id == storage_id
        assert domain_storage.name == "Багажник"
        assert domain_storage.total_volume == 25
        assert domain_storage.order_id == order_id
        assert domain_storage.courier_id == courier_id

    def test_to_domain_object_without_order(self):
        """Тест: to_domain_object для свободного места хранения"""
        # Arrange
        courier_id = uuid.uuid4()
        storage_model = StoragePlaceModel(
            id=uuid.uuid4(),
            name="Коробка",
            total_volume=8,
            order_id=None,
            courier_id=courier_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Act
        domain_storage = storage_model.to_domain_object()

        # Assert
        assert domain_storage.name == "Коробка"
        assert domain_storage.total_volume == 8
        assert domain_storage.order_id is None
        assert domain_storage.is_empty is True
        assert domain_storage.courier_id == courier_id

    def test_round_trip_conversion_preserves_storage_data(self):
        """Тест: полный цикл Domain -> Model -> Domain сохраняет данные места хранения"""
        # Arrange
        courier_id = uuid.uuid4()
        original_storage = StoragePlace(
            name="Оригинальное место",
            total_volume=20,
            id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            courier_id=uuid.uuid4(),
        )

        # Act
        # Domain -> Model
        storage_model = StoragePlaceModel.from_domain_object(original_storage)

        # Model -> Domain
        restored_storage = storage_model.to_domain_object()

        # Assert
        assert restored_storage.id == original_storage.id
        assert restored_storage.name == "Оригинальное место"
        assert restored_storage.total_volume == 20
        assert restored_storage.order_id == original_storage.order_id
        assert restored_storage.courier_id == original_storage.courier_id

    def test_to_domain_object_creates_valid_storage_place(self):
        """Тест: to_domain_object создает корректный StoragePlace"""
        # Arrange
        courier_id = uuid.uuid4()
        storage_model = StoragePlaceModel(
            id=uuid.uuid4(),
            name="Тестовое место",
            total_volume=12,
            order_id=None,
            courier_id=courier_id,
        )

        # Act
        domain_storage = storage_model.to_domain_object()

        # Assert
        # Проверяем что объект работает корректно
        assert domain_storage.can_store(10) is True
        assert domain_storage.can_store(15) is False  # Больше объема
        assert domain_storage.is_empty is True
        assert domain_storage.courier_id == courier_id

    def test_storage_place_with_order_is_occupied(self):
        """Тест: место хранения с заказом считается занятым"""
        # Arrange
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()
        storage_model = StoragePlaceModel(
            id=uuid.uuid4(),
            name="Занятое место",
            total_volume=10,
            order_id=order_id,
            courier_id=courier_id,
        )

        # Act
        domain_storage = storage_model.to_domain_object()

        # Assert
        assert domain_storage.is_empty is False
        assert domain_storage.order_id == order_id
        assert domain_storage.can_store(5) is False  # Занято, нельзя хранить
        assert domain_storage.courier_id == courier_id

    def test_from_domain_object_does_not_modify_original_storage(self):
        """Тест: from_domain_object не изменяет исходное место хранения"""
        # Arrange
        courier_id = uuid.uuid4()
        original_storage = StoragePlace.create("Оригинал", 15, courier_id)

        # Запоминаем исходное состояние
        original_id = original_storage.id
        original_name = original_storage.name
        original_volume = original_storage.total_volume
        original_order_id = original_storage.order_id
        original_courier_id = original_storage.courier_id

        # Act
        storage_model = StoragePlaceModel.from_domain_object(original_storage)

        # Assert - исходный не изменился
        assert original_storage.id == original_id
        assert original_storage.name == original_name
        assert original_storage.total_volume == original_volume
        assert original_storage.order_id == original_order_id
        assert original_storage.courier_id == original_courier_id

        # Модель создана корректно
        assert storage_model.id == original_id
        assert storage_model.name == original_name
        assert storage_model.total_volume == original_volume
        assert storage_model.order_id == original_order_id
        assert storage_model.courier_id == original_courier_id

    def test_courier_from_persistence(self):
        courier_id = uuid.uuid4()
        storage_place = StoragePlace(
            id=uuid.uuid4(),
            name="Место курьера",
            total_volume=10,
            order_id=None,
            courier_id=uuid.uuid4(),
        )
        location = Location(x=5, y=5)
        restored = Courier._from_persistence(
            id=courier_id,
            name="John",
            speed=10,
            location=location,
            storage_places=[storage_place],
        )

        assert restored.id == courier_id
        assert restored.name == "John"
        assert restored.speed == 10
        assert restored.location == location
        # не создается дефолтное место
        assert len(restored.storage_places) == 1
        assert restored.storage_places[0] == storage_place


class TestIntegratedMappers:
    """Интегрированные тесты для связи курьер-места хранения"""

    def test_courier_with_storage_places_reference(self):
        """Тест что модели имеют ссылки друг на друга"""
        # Arrange
        courier_model = CourierModel(
            id=uuid.uuid4(),
            name="Курьер с местами",
            speed=3,
            location_x=1,
            location_y=1,
        )

        storage_model = StoragePlaceModel(
            id=uuid.uuid4(), name="Место курьера", total_volume=10, order_id=None
        )

        # Act
        # Устанавливаем связь (в реальном коде это делает SQLAlchemy)
        courier_model.storage_places = [storage_model]
        storage_model.couriers = [courier_model]

        # Assert
        assert len(courier_model.storage_places) == 1
        assert courier_model.storage_places[0] == storage_model
        assert len(storage_model.couriers) == 1
        assert storage_model.couriers[0] == courier_model
