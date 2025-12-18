from abc import ABC, abstractmethod

from src.delivery.core.domain.model.location.location import Location


class GeoServiceInterface(ABC):
    @abstractmethod
    def get_location(self, street: str) -> Location:
        pass
