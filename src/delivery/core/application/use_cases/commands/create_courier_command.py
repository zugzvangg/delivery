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
from src.delivery.core.domain.model.location.location import Location


@dataclass
class CreateCourierCommand(Command):
    def __init__(self, name: str, speed: int):
        if not name or not name.strip():
            raise ValueError("name must be a non-empty string")

        if not isinstance(speed, int) or speed <= 0:
            raise ValueError("speed must be a positive integer")

        self.__name = name
        self.__speed = speed

    @property
    def name(self) -> str:
        return self.__name

    @property
    def speed(self) -> int:
        return self.__speed


class CreateCourierUseCase(CommandHandler):
    def __init__(self, session: Session):
        self.courier_repo: CourierRepository = CourierRepository(session)

    def handle(self, command: CreateCourierCommand) -> None:

        location: Location = Location.create_random()

        courier = Courier(name=command.name, speed=command.speed, location=location)
        self.courier_repo.add(courier)
