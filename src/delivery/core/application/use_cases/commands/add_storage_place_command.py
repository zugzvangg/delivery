from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from src.delivery.adapters.out.postgres.repositories.courier_repository import (
    CourierRepository,
)
from src.delivery.core.application.use_cases.commands.base import (
    Command,
    CommandHandler,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location


@dataclass
class AddStoragePlaceCommand(Command):
    def __init__(self, courier_id: UUID, name: str, total_volume: int):
        if not isinstance(courier_id, UUID):
            raise ValueError("courier_id must be a UUID")
        if not name or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(total_volume, int) or total_volume <= 0:
            raise ValueError("total_volume must be positive")

        self.__courier_id = courier_id
        self.__name = name
        self.__total_volume = total_volume

    @property
    def courier_id(self):
        return self.__courier_id

    @property
    def name(self):
        return self.__name

    @property
    def total_volume(self):
        return self.__total_volume


class AddStoragePlaceUseCase(CommandHandler):
    def __init__(self, session: Session):
        self.courier_repo: CourierRepository = CourierRepository(session)
        self.session = session

    def handle(self, command: AddStoragePlaceCommand) -> None:

        # сперва получаем существующего курьера, если его нет, упадет ошибка
        courier: Courier = self.courier_repo.get_by_id(courier_id=command.courier_id)
        courier.add_storage_place(name=command.name, volume=command.total_volume)
        # и обновляем его в базе
        self.courier_repo.update(courier)
        self.session.commit()
