import uuid

import pytest

from src.delivery.adapters.out.postgres.models.models import OrderModel
from src.delivery.adapters.out.postgres.repositories.courier_repository import (
    CourierRepository,
)
from src.delivery.adapters.out.postgres.repositories.order_repository import (
    OrderRepository,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus
from src.delivery.core.domain.services.order_dispatcher import OrderDispatcher


class TestOrderRepository:
    def test_add_order(self, db):
        # --- Arrange ---
        repo = OrderRepository(db)
        order_id = uuid.uuid4()
        location = Location(1, 2)
        order = Order(
            id=order_id,
            location=location,
            volume=5,
        )

        # --- Act ---
        saved_order = repo.add(order)

        # --- Assert ---
        assert saved_order.id == order.id
        assert saved_order.location.x == 1
        assert saved_order.location.y == 2
        assert saved_order.volume == 5
        assert saved_order.status == OrderStatus.CREATED

        # Проверяем, что запись действительно в БД
        db_order = db.get(OrderModel, order.id)
        assert db_order is not None
        assert db_order.volume == 5
        assert db_order.location_x == 1
        assert db_order.location_y == 2
        assert db_order.id == order_id

    def test_update_order(self, db):
        order_repo = OrderRepository(db)
        courier_repo = CourierRepository(db)
        order_id = uuid.uuid4()
        # --- Arrange ---
        order = Order(
            id=order_id,
            location=Location(5, 5),
            volume=10,
        )

        # Добавляем в БД
        order_repo.add(order)

        courier = Courier(name="Вася", speed=10, location=Location(4, 5))
        courier_id = courier.id
        order.assign(courier_id=courier_id)
        assert order.courier_id == courier_id
        assert order.status == OrderStatus.ASSIGNED
        courier_repo.add(courier)

        # --- Act ---
        updated = order_repo.update(order)

        # --- Assert ---
        assert updated.id == order.id
        assert updated.courier_id == courier_id
        assert updated.status == OrderStatus.ASSIGNED

        # Проверяем через БД
        db_order = db.get(OrderModel, order.id)
        assert db_order.location_x == 5
        assert db_order.location_y == 5
        assert db_order.volume == 10
        assert db_order.status == "ASSIGNED"
        assert db_order.courier_id == courier_id

    def test_get_any_created(self, db):
        order_repo = OrderRepository(db)
        order_id1 = uuid.uuid4()
        order_id2 = uuid.uuid4()
        order_id3 = uuid.uuid4()
        # --- Arrange ---

        order1 = Order(
            id=order_id1,
            location=Location(6, 6),
            volume=5,
        )
        order2 = Order(
            id=order_id2,
            location=Location(7, 7),
            volume=20,
        )
        order3 = Order(
            id=order_id3,
            location=Location(8, 8),
            volume=30,
        )

        order_repo.add(order1)
        order_repo.add(order2)
        order_repo.add(order3)

        any_created_order = order_repo.get_any_created()
        assert isinstance(any_created_order, Order)

    def test_if_there_are_no_created_orders_we_get_value_error(self, db):
        order_repo = OrderRepository(db)
        with pytest.raises(ValueError):
            order_repo.get_any_created()

    def test_all_workaround(self, db):
        order_repo = OrderRepository(db)
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
        courier3 = Courier(
            name="Вася",
            speed=15,
            location=Location(2, 6),
        )
        courier_repo.add(courier1)
        courier_repo.add(courier2)
        courier_repo.add(courier3)
        # добавляем курьеров

        order_id1 = uuid.uuid4()
        order_id2 = uuid.uuid4()
        order_id3 = uuid.uuid4()

        order1 = Order(
            id=order_id1,
            location=Location(6, 6),
            volume=5,
        )
        order2 = Order(
            id=order_id2,
            location=Location(7, 7),
            volume=20,
        )
        order3 = Order(
            id=order_id3,
            location=Location(9, 9),
            volume=10,
        )
        # добавляем заказы
        order_repo.add(order1)
        order_repo.add(order2)
        order_repo.add(order3)

        # добавляем двум курьерам по месту хранения и апдейтим их
        courier1.add_storage_place(name="Рюкзак", volume=50)
        courier2.add_storage_place(name="Мешок", volume=30)
        # апдейтим их
        courier_repo.update(courier1)
        courier_repo.update(courier2)

        # должно быть 3 свободных курьера
        free_couriers = courier_repo.get_all_free()
        assert len(free_couriers) == 3

        # ассайним и обновляем заказы и курьеров
        courier1.take_order(order1)
        order1.assign(courier1.id)
        courier_repo.update(courier1)
        order_repo.update(order1)

        courier2.take_order(order2)
        order2.assign(courier2.id)
        courier_repo.update(courier2)
        order_repo.update(order2)

        # order3 должен остаться свободным
        created_order = order_repo.get_any_created()
        assert created_order.volume == 10  # как у order3
        assert created_order.location == Location(9, 9)  # как у order3

        # order2 и order3 должны быть assigned
        all_assigned_orders = order_repo.get_all_assigned()
        assert len(all_assigned_orders) == 2
        assert all_assigned_orders[0].courier_id is not None
        assert all_assigned_orders[0].status == OrderStatus.ASSIGNED
        assert all_assigned_orders[1].courier_id is not None
        assert all_assigned_orders[1].status == OrderStatus.ASSIGNED

        # получаем одного свободного курьера
        all_free_couriers = courier_repo.get_all_free()
        assert len(all_free_couriers) == 1
        assert all_free_couriers[0].id == courier3.id
        assert all_free_couriers[0].name == "Вася"

        # и смотрим, что заказы завершаются
        courier2.complete_order(order2)
        order2.complete()
        courier_repo.update(courier2)
        order_repo.update(order2)

        # и смотрим, что курьер свободен, а заказ завершен
        courier_who_completed = courier_repo.get_by_id(courier2.id)
        completed_order = order_repo.get_by_id(order2.id)
        assert (
            courier_who_completed.storage_places[0].order_id is None
            and courier_who_completed.storage_places[1].order_id is None
        )
        assert completed_order.status == OrderStatus.COMPLETED
