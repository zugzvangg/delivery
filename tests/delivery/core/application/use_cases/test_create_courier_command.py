import uuid

from src.delivery.core.application.use_cases.commands.add_storage_place_command import (
    AddStoragePlaceCommand,
    AddStoragePlaceUseCase,
)
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
        created_couriers: list[Courier] = (
            create_courier_use_case.courier_repo.get_all_free()
        )
        created_courier: Courier = created_couriers[0]
        assert created_courier.name == "Иван"
        assert created_courier.speed == 10

        # дальше смотрим, как отрабатывает AddStoragePlaceUseCase, так как курьер уже создан
        add_storage_place_use_case: AddStoragePlaceUseCase = AddStoragePlaceUseCase(db)
        command = AddStoragePlaceCommand(
            courier_id=created_courier.id, name="Рюкзак", total_volume=20
        )
        add_storage_place_use_case.handle(command)
        needed_courier: Courier = create_courier_use_case.courier_repo.get_by_id(created_courier.id)
        # добавилось
        assert len(needed_courier.storage_places) == 2
