# src/delivery/core/domain/ports/courier_repository.py
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from src.delivery.core.domain.model.courier.courier import Courier


class CourierRepository(ABC):
    """Порт для работы с хранилищем курьеров"""

    @abstractmethod
    def add(self, courier: Courier) -> None:
        """Добавить курьера"""
        pass

    @abstractmethod
    def update(self, courier: Courier) -> None:
        """Обновить курьера"""
        pass

    @abstractmethod
    def get_by_id(self, courier_id: uuid.UUID) -> Optional[Courier]:
        """Получить курьера по идентификатору"""
        pass

    @abstractmethod
    def get_all_free(self) -> List[Courier]:
        """Получить всех свободных курьеров (у которых все места хранения свободны)"""
        pass
