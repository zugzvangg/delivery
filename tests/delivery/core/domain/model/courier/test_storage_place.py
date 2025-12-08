import uuid

import pytest

from src.delivery.core.domain.model.common import InvalidUUIDError
from src.delivery.core.domain.model.courier.storage_place import (
    InvalidStoragePlaceName,
    InvalidStoragePlaceVolume,
    StorageOccupiedError,
    StoragePlace,
    StoragePlaceClearWrongOrderId,
)


class TestStoragePlace:
    """Тесты для класса StoragePlace"""

    def test_create_storage_place_with_default_values(self):
        """Тест создания места хранения с дефолтными значениями"""
        # Act
        courier_id = uuid.uuid4()
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=courier_id)

        # Assert
        assert storage.id is not None
        assert storage.name == "Рюкзак"
        assert storage.total_volume == 50
        assert storage.order_id is None
        assert storage.courier_id == courier_id
        assert isinstance(storage.id, uuid.UUID)

    def test_if_private_variables_are_available(self):
        """Тест что приватные переменные недоступны"""
        name, total_volume = "Рюкзак", 50
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())

        with pytest.raises(AttributeError):
            storage.__name == name
        with pytest.raises(AttributeError):
            storage.__total_volume == total_volume

    def test_create_storage_place_with_order_id(self):
        """Тест создания места хранения с order_id"""
        # Arrange
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()

        # Act
        storage = StoragePlace(
            name="Рюкзак", total_volume=50, order_id=order_id, courier_id=courier_id
        )

        # Assert
        assert storage.order_id == order_id

    def test_equality_based_on_id(self):
        """Тест сравнения объектов по ID"""
        # Arrange
        same_id = uuid.uuid4()
        storage1 = StoragePlace(
            id=same_id, name="Рюкзак", total_volume=50, courier_id=uuid.uuid4()
        )
        storage2 = StoragePlace(
            id=same_id, name="Багажник", total_volume=100, courier_id=uuid.uuid4()
        )
        storage3 = StoragePlace(name="Сумка", total_volume=30, courier_id=uuid.uuid4())

        # Assert
        assert storage1 == storage2
        assert storage1 != storage3
        assert storage1 != "not_a_storage_place"

    def test_can_store_when_empty_and_sufficient_volume(self):
        """Тест can_store когда место пустое и объем достаточен"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())

        # Act & Assert
        assert storage.can_store(30) is True
        assert storage.can_store(50) is True

    def test_cannot_store_when_occupied(self):
        """Тест can_store когда место занято"""
        # Arrange
        order_id = uuid.uuid4()
        courier_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак", total_volume=50, order_id=order_id, courier_id=courier_id
        )

        # Act & Assert
        assert storage.can_store(10) is False

    def test_cannot_store_when_volume_exceeds_capacity(self):
        """Тест can_store когда объем превышает вместимость"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())

        # Act & Assert
        assert storage.can_store(51) is False

    def test_can_store_raises_error_for_invalid_volume(self):
        """Тест can_store с некорректным объемом"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())

        # Act & Assert
        with pytest.raises(
            InvalidStoragePlaceVolume, match="Volume must be a positive integer!"
        ):
            storage.can_store(0)

        with pytest.raises(
            InvalidStoragePlaceVolume, match="Volume must be a positive integer!"
        ):
            storage.can_store(-10)

        with pytest.raises(
            InvalidStoragePlaceVolume, match="Volume must be a positive integer!"
        ):
            storage.can_store("invalid")

    def test_store_successfully(self):
        """Тест успешного размещения заказа"""
        # Arrange
        courier_id = uuid.uuid4()
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=courier_id)
        order_id = uuid.uuid4()

        # Act
        storage.store(order_id, 30)

        # Assert
        assert storage.order_id == order_id
        assert storage.courier_id == courier_id

    def test_store_fails_when_occupied(self):
        """Тест store когда место уже занято"""
        # Arrange
        existing_order_id = uuid.uuid4()
        new_order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак",
            total_volume=50,
            order_id=existing_order_id,
            courier_id=uuid.uuid4(),
        )

        # Act & Assert
        with pytest.raises(
            StorageOccupiedError,
            match="Cannot store order - storage is occupied or volume exceeds capacity",
        ):
            storage.store(new_order_id, 10)

    def test_store_fails_when_volume_exceeds(self):
        """Тест store когда объем превышает вместимость"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())
        order_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(
            StorageOccupiedError,
            match="Cannot store order - storage is occupied or volume exceeds capacity",
        ):
            storage.store(order_id, 51)

    def test_store_fails_with_invalid_order_id(self):
        """Тест store с некорректным order_id"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())

        # Act & Assert
        with pytest.raises(
            InvalidUUIDError, match="order_id if must be of type uuid.UUID"
        ):
            storage.store("invalid_order_id", 30)

    def test_clear_successfully(self):
        """Тест успешного извлечения заказа"""
        # Arrange
        order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак", total_volume=50, order_id=order_id, courier_id=uuid.uuid4()
        )

        # Act
        storage.clear(order_id)

        # Assert
        assert storage.order_id is None
        assert storage.is_empty is True

    def test_clear_fails_when_empty(self):
        """Тест clear когда место пустое"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())
        order_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(
            StorageOccupiedError, match="Cannot clear - storage is not occupied"
        ):
            storage.clear(order_id)

    def test_clear_fails_when_order_id_mismatch(self):
        """Тест clear когда order_id не совпадает"""
        # Arrange
        stored_order_id = uuid.uuid4()
        wrong_order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак",
            total_volume=50,
            order_id=stored_order_id,
            courier_id=uuid.uuid4(),
        )

        # Act & Assert
        with pytest.raises(
            StoragePlaceClearWrongOrderId,
            match="Order ID does not match the stored order",
        ):
            storage.clear(wrong_order_id)

    def test_is_empty_property(self):
        """Тест свойства is_empty"""
        # Arrange & Assert - пустое место
        empty_storage = StoragePlace(
            name="Рюкзак", total_volume=50, courier_id=uuid.uuid4()
        )
        assert empty_storage.is_empty is True

        # Arrange & Assert - занятое место
        order_id = uuid.uuid4()
        occupied_storage = StoragePlace(
            name="Рюкзак", total_volume=50, order_id=order_id, courier_id=uuid.uuid4()
        )
        assert occupied_storage.is_empty is False

    def test_immutability(self):
        """Тест неизменяемости объекта"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50, courier_id=uuid.uuid4())

        # Act & Assert - попытка изменить атрибут должна вызвать ошибку
        with pytest.raises(Exception):
            storage.name = "Новое название"

    def test_extra_fields_forbidden(self):
        """Тест что дополнительные поля запрещены"""
        # Act & Assert
        with pytest.raises(TypeError):
            StoragePlace(name="Рюкзак", total_volume=50, invalid_field="should_fail")

    def test_validation_name_min_length(self):
        """Тест валидации минимальной длины имени"""
        # Act & Assert
        with pytest.raises(InvalidStoragePlaceName):
            StoragePlace(name="", total_volume=50, courier_id=uuid.uuid4())

    def test_validation_total_volume_positive(self):
        """Тест валидации положительного объема"""
        # Act & Assert
        courier_id = uuid.uuid4()
        with pytest.raises(InvalidStoragePlaceVolume):
            StoragePlace(name="Рюкзак", total_volume=0, courier_id=courier_id)

        with pytest.raises(InvalidStoragePlaceVolume):
            StoragePlace(name="Рюкзак", total_volume=-10, courier_id=courier_id)

    def test_courier_id(self):
        """Тест валидации поля courier_id"""
        # Act & Assert
        courier_id = "10"
        with pytest.raises(InvalidUUIDError):
            StoragePlace(name="Рюкзак", total_volume=10, courier_id=courier_id)

    @pytest.mark.parametrize(
        "name,total_volume,courier_id",
        [
            ("Рюкзак", 50, uuid.uuid4()),
            ("Багажник", 100, uuid.uuid4()),
            ("Сумка", 20, uuid.uuid4()),
        ],
    )
    def test_create_with_class_method(self, name, total_volume, courier_id):
        """Параметризованный тест фабричного метода create"""
        # Act
        storage = StoragePlace.create(
            name=name, total_volume=total_volume, courier_id=courier_id
        )

        # Assert
        assert storage.name == name
        assert storage.total_volume == total_volume
        assert storage.order_id is None
        assert storage.courier_id == courier_id
        assert isinstance(storage.id, uuid.UUID)
        assert isinstance(storage.courier_id, uuid.UUID)

    def test_storage_place_from_persistence(self):
        sp_id = uuid.uuid4()
        courier_id = uuid.uuid4()
        order_id = uuid.uuid4()

        restored = StoragePlace._from_persistence(
            id=sp_id,
            name="Сумка",
            total_volume=15,
            courier_id=courier_id,
            order_id=order_id,
        )

        assert restored.id == sp_id
        assert restored.total_volume == 15
        assert restored.name == "Сумка"
        assert restored.courier_id == courier_id
        assert restored.order_id == order_id


