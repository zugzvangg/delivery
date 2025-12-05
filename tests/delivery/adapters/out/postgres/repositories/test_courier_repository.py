import uuid

from src.delivery.adapters.out.postgres.models.models import (
    CourierModel,
    StoragePlaceModel,
)
from src.delivery.adapters.out.postgres.repositories.courier_repository import (
    CourierRepository,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location


class TestCourierRepository:

    def test_add_courier(self, db):
        repo = CourierRepository(db)

        courier = Courier(
            name="Иван",
            speed=12,
            location=Location(3, 4),
        )

        # Добавим storage place
        courier.add_storage_place(name="Рюкзак", volume=50)

        # --- Act ---
        saved_courier = repo.add(courier)

        # --- Assert (domain) ---
        assert saved_courier.name == "Иван"
        assert saved_courier.location.x == 3
        assert saved_courier.location.y == 4
        # это уже второе место
        assert len(saved_courier.storage_places) == 2

        saved_sp = saved_courier.storage_places[1]
        assert saved_sp.name == "Рюкзак"
        assert saved_sp.total_volume == 50

        # --- Assert (DB) ---
        db_courier = db.get(CourierModel, courier.id)
        assert db_courier is not None

        db_sp_list = db.query(StoragePlaceModel).filter_by(courier_id=courier.id).all()
        assert len(db_sp_list) == 2
        assert db_sp_list[1].name == "Рюкзак"
        assert db_sp_list[1].total_volume == 50
        # изначально задаваемый
        assert db_sp_list[0].name == "Сумка"
        assert db_sp_list[0].total_volume == 10
