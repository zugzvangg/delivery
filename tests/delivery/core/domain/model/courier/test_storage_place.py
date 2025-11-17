import uuid
import pytest
from src.delivery.core.domain.model.courier.storage_place import StoragePlace


class TestStoragePlace:
    """Тесты для класса StoragePlace"""

    def test_create_storage_place_with_default_values(self):
        """Тест создания места хранения с дефолтными значениями"""
        # Act
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        
        # Assert
        assert storage.name == "Рюкзак"
        assert storage.total_volume == 50
        assert storage.order_id is None
        assert isinstance(storage.id, uuid.UUID)

    def test_create_storage_place_with_custom_id(self):
        """Тест создания места хранения с кастомным ID"""
        # Arrange
        custom_id = uuid.uuid4()
        
        # Act
        storage = StoragePlace(
            id=custom_id,
            name="Багажник", 
            total_volume=100
        )
        
        # Assert
        assert storage.id == custom_id
        assert storage.name == "Багажник"
        assert storage.total_volume == 100

    def test_create_storage_place_with_order_id(self):
        """Тест создания места хранения с order_id"""
        # Arrange
        order_id = uuid.uuid4()
        
        # Act
        storage = StoragePlace(
            name="Рюкзак",
            total_volume=50,
            order_id=order_id
        )
        
        # Assert
        assert storage.order_id == order_id

    def test_equality_based_on_id(self):
        """Тест сравнения объектов по ID"""
        # Arrange
        same_id = uuid.uuid4()
        storage1 = StoragePlace(id=same_id, name="Рюкзак", total_volume=50)
        storage2 = StoragePlace(id=same_id, name="Багажник", total_volume=100)
        storage3 = StoragePlace(name="Сумка", total_volume=30)
        
        # Assert
        assert storage1 == storage2
        assert storage1 != storage3
        assert storage1 != "not_a_storage_place"

    def test_can_store_when_empty_and_sufficient_volume(self):
        """Тест can_store когда место пустое и объем достаточен"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        
        # Act & Assert
        assert storage.can_store(30) is True
        assert storage.can_store(50) is True

    def test_cannot_store_when_occupied(self):
        """Тест can_store когда место занято"""
        # Arrange
        order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак", 
            total_volume=50, 
            order_id=order_id
        )
        
        # Act & Assert
        assert storage.can_store(10) is False

    def test_cannot_store_when_volume_exceeds_capacity(self):
        """Тест can_store когда объем превышает вместимость"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        
        # Act & Assert
        assert storage.can_store(51) is False

    def test_can_store_raises_error_for_invalid_volume(self):
        """Тест can_store с некорректным объемом"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Volume must be a positive integer!"):
            storage.can_store(0)
        
        with pytest.raises(ValueError, match="Volume must be a positive integer!"):
            storage.can_store(-10)
        
        with pytest.raises(ValueError, match="Volume must be a positive integer!"):
            storage.can_store("invalid")

    def test_store_successfully(self):
        """Тест успешного размещения заказа"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        order_id = uuid.uuid4()
        
        # Act
        storage.store(order_id, 30)
        
        # Assert
        assert storage.order_id == order_id

    def test_store_fails_when_occupied(self):
        """Тест store когда место уже занято"""
        # Arrange
        existing_order_id = uuid.uuid4()
        new_order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак", 
            total_volume=50, 
            order_id=existing_order_id
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot store order - storage is occupied or volume exceeds capacity"):
            storage.store(new_order_id, 10)

    def test_store_fails_when_volume_exceeds(self):
        """Тест store когда объем превышает вместимость"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        order_id = uuid.uuid4()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot store order - storage is occupied or volume exceeds capacity"):
            storage.store(order_id, 51)

    def test_store_fails_with_invalid_order_id(self):
        """Тест store с некорректным order_id"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Order ID must be a UUID"):
            storage.store("invalid_order_id", 30)

    def test_clear_successfully(self):
        """Тест успешного извлечения заказа"""
        # Arrange
        order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак", 
            total_volume=50, 
            order_id=order_id
        )
        
        # Act
        storage.clear(order_id)
        
        # Assert
        assert storage.order_id is None
        assert storage.is_empty is True

    def test_clear_fails_when_empty(self):
        """Тест clear когда место пустое"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        order_id = uuid.uuid4()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot clear - storage is not occupied"):
            storage.clear(order_id)

    def test_clear_fails_when_order_id_mismatch(self):
        """Тест clear когда order_id не совпадает"""
        # Arrange
        stored_order_id = uuid.uuid4()
        wrong_order_id = uuid.uuid4()
        storage = StoragePlace(
            name="Рюкзак", 
            total_volume=50, 
            order_id=stored_order_id
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Order ID does not match the stored order"):
            storage.clear(wrong_order_id)

    def test_is_empty_property(self):
        """Тест свойства is_empty"""
        # Arrange & Assert - пустое место
        empty_storage = StoragePlace(name="Рюкзак", total_volume=50)
        assert empty_storage.is_empty is True
        
        # Arrange & Assert - занятое место
        order_id = uuid.uuid4()
        occupied_storage = StoragePlace(
            name="Рюкзак", 
            total_volume=50, 
            order_id=order_id
        )
        assert occupied_storage.is_empty is False

    def test_immutability(self):
        """Тест неизменяемости объекта"""
        # Arrange
        storage = StoragePlace(name="Рюкзак", total_volume=50)
        
        # Act & Assert - попытка изменить атрибут должна вызвать ошибку
        with pytest.raises(Exception):
            storage.name = "Новое название"

    def test_extra_fields_forbidden(self):
        """Тест что дополнительные поля запрещены"""
        # Act & Assert
        with pytest.raises(ValueError):
            StoragePlace(
                name="Рюкзак",
                total_volume=50,
                invalid_field="should_fail"
            )

    def test_validation_name_min_length(self):
        """Тест валидации минимальной длины имени"""
        # Act & Assert
        with pytest.raises(ValueError):
            StoragePlace(name="", total_volume=50)

    def test_validation_total_volume_positive(self):
        """Тест валидации положительного объема"""
        # Act & Assert
        with pytest.raises(ValueError):
            StoragePlace(name="Рюкзак", total_volume=0)
        
        with pytest.raises(ValueError):
            StoragePlace(name="Рюкзак", total_volume=-10)

    @pytest.mark.parametrize("name,total_volume", [
        ("Рюкзак", 50),
        ("Багажник", 100),
        ("Сумка", 20),
    ])
    def test_create_with_class_method(self, name, total_volume):
        """Параметризованный тест фабричного метода create"""
        # Act
        storage = StoragePlace.create(name=name, total_volume=total_volume)
        
        # Assert
        assert storage.name == name
        assert storage.total_volume == total_volume
        assert storage.order_id is None
        assert isinstance(storage.id, uuid.UUID)