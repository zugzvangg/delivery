import uuid
import pytest
from src.delivery.adapters.out.postgres.models.models import (
    CourierModel,
    StoragePlaceModel,
)
from src.delivery.adapters.out.postgres.repositories.courier_repository import (
    CourierRepository,
)
from src.delivery.adapters.out.postgres.repositories.order_repository import (
    OrderRepository,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order


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

    def test_get_by_id(self, db):
        courier_repo = CourierRepository(db)
        courier1 = Courier(
            name="Иван",
            speed=12,
            location=Location(3, 4),
        )

        courier2 = Courier(
            name="Петр",
            speed=20,
            location=Location(5, 8),
        )
        # получаем его id, чтобы сверить
        courier_id = courier1.id
        courier_repo.add(courier1)
        courier_repo.add(courier2)

        courier = courier_repo.get_by_id(courier_id)
        assert courier.id == courier1.id
        assert courier.name == courier1.name
        # от случайного получает ошибку, так как его нет
        with pytest.raises(ValueError):
            courier_repo.get_by_id(uuid.uuid4())

    def test_get_all_free(self, db):
        courier_repo = CourierRepository(db)
        order_repo = OrderRepository(db)

        courier1 = Courier(
            name="Иван",
            speed=12,
            location=Location(3, 4),
        )

        courier2 = Courier(
            name="Петр",
            speed=20,
            location=Location(5, 8),
        )
        courier3 = Courier(
            name="Вася",
            speed=15,
            location=Location(2, 6),
        )
        # на одного курьера нзначаем заказ
        order_id = uuid.uuid4()
        order = Order(id=order_id, location=Location(5, 6), volume=2)
        # StoragePlace в ORM создадутся автоматически
        courier1.take_order(order)
        # добавляем заказ в базу, иначе получим IntegrityError
        order_repo.add(order)

        # сохраняем одного занятого и одного не занятого курьера в базу
        courier_repo.add(courier1)
        courier_repo.add(courier2)
        courier_repo.add(courier3)

        # # получаем свободных курьеров, там должен быть только courier1
        free_couriers: list[Courier] = courier_repo.get_all_free()
        assert len(free_couriers) == 2
        assert free_couriers[0].name == "Петр"
        assert free_couriers[1].name == "Вася"
