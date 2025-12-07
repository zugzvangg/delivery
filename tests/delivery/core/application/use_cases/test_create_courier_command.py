import uuid

from src.delivery.core.application.use_cases.commands.create_courier_command import (
    CreateCourierCommand,
    CreateCourierUseCase,
)
from src.delivery.core.domain.model.courier.courier import Courier


class TestCreateCourierCommand:
    def test_create_courier_command(self, db):
        create_courier_use_case: CreateCourierUseCase = CreateCourierUseCase(db)

        command = CreateCourierCommand(name="Иван", speed=10)
        create_courier_use_case.handle(command)
        # он один свободный и тот, что мы создали
        created_couriers: Courier = create_courier_use_case.courier_repo.get_all_free()
        created_courier = created_couriers[0]
        assert created_courier.name == "Иван"
        assert created_courier.speed == 10
