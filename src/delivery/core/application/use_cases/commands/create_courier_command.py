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
    name: str
    speed: int


class CreateCourierUseCase(CommandHandler):
    def __init__(self, session: Session):
        self.courier_repo: CourierRepository = CourierRepository(session)

    def handle(self, command: CreateCourierCommand) -> None:

        location: Location = Location.create_random()

        courier = Courier(name=command.name, speed=command.speed, location=location)
        self.courier_repo.add(courier)
