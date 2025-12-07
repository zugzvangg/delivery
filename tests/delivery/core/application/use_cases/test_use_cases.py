import uuid

from src.delivery.core.application.use_cases.commands.add_storage_place_command import (
    AddStoragePlaceCommand,
    AddStoragePlaceUseCase,
)
from src.delivery.core.application.use_cases.commands.assign_order import (
    AssignOrderCommand,
    AssignOrderUseCase,
)
from src.delivery.core.application.use_cases.commands.create_courier_command import (
    CreateCourierCommand,
    CreateCourierUseCase,
)
from src.delivery.core.application.use_cases.commands.create_order_command import (
    CreateOrderCommand,
    CreateOrderUseCase,
)
from src.delivery.core.application.use_cases.commands.move_couriers_command import (
    MoveCouriersCommand,
    MoveCouriersUseCase,
)
from src.delivery.core.application.use_cases.queries.get_all_couriers_query import (
    CourierDTO,
    GetAllCouriersQuery,
    GetAllCouriersUseCase,
)
from src.delivery.core.application.use_cases.queries.get_not_completed_orders_query import (
    GetNotCompletedOrdersQuery,
    GetNotCompletedOrdersUseCase,
    OrderDTO,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.order.order import Order


class TestCourierUseCases:
    def test_courier_use_cases(self, db):
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
        needed_courier: Courier = create_courier_use_case.courier_repo.get_by_id(
            created_courier.id
        )
        # добавилось
        assert len(needed_courier.storage_places) == 2

        # и заодно тестим query

        create_order_use_case: GetAllCouriersUseCase = GetAllCouriersUseCase(db)
        all_couriers: list[CourierDTO] = create_order_use_case.handle(
            GetAllCouriersQuery()
        )
        for c in all_couriers:
            assert isinstance(c, CourierDTO)
        courier_dto = all_couriers[0]
        assert courier_dto.id == needed_courier.id
        assert courier_dto.name == needed_courier.name
        assert courier_dto.location == needed_courier.location


class TestOrderUseCases:
    def test_order_use_vases(self, db):
        create_order_use_case: CreateOrderUseCase = CreateOrderUseCase(db)
        order_id = uuid.uuid4()
        command = CreateOrderCommand(order_id=order_id, street="Pushkina", volume=10)
        create_order_use_case.handle(command)
        created_order: Order = create_order_use_case.order_repo.get_by_id(order_id)
        # заказ действительно есть в базе
        assert created_order.volume == 10

        get_all_not_completed_orders_use_case: GetNotCompletedOrdersUseCase = (
            GetNotCompletedOrdersUseCase(db)
        )
        all_not_completed_orders: list[OrderDTO] = (
            get_all_not_completed_orders_use_case.handle(GetNotCompletedOrdersQuery)
        )
        for order in all_not_completed_orders:
            assert isinstance(order, OrderDTO)
        assert len(all_not_completed_orders) == 1
        not_completed_order = all_not_completed_orders[0]
        assert not_completed_order.id == created_order.id
        assert not_completed_order.location == created_order.location


class TestOtherUseCases:
    def test_assigning_order_uses_case(self, db):
        # создаем один заказ и одного дальнего, одного ближнего курьера
        create_courier_use_case: CreateCourierUseCase = CreateCourierUseCase(db)
        create_courier_use_case.handle(CreateCourierCommand(name="Иван", speed=10))
        create_courier_use_case.handle(CreateCourierCommand(name="Петр", speed=20))

        create_order_use_case: CreateOrderUseCase = CreateOrderUseCase(db)
        order_id = uuid.uuid4()
        command = CreateOrderCommand(order_id=order_id, street="Pushkina", volume=10)
        create_order_use_case.handle(command)

        # смотрим, что работает
        # точность алгоритма не можем проверить точно, так как пока что локации создаются случайно
        assign_order_use_case: AssignOrderUseCase = AssignOrderUseCase(db)
        assign_order_use_case.handle(AssignOrderCommand())

        # TODO: доделать тесты, когда локации будут генериться неслучайно

    def test_move_couriers(self, db):
        # создаем заказ и курьера
        create_courier_use_case: CreateCourierUseCase = CreateCourierUseCase(db)
        create_courier_use_case.handle(CreateCourierCommand(name="Иван", speed=10))

        create_order_use_case: CreateOrderUseCase = CreateOrderUseCase(db)
        order_id = uuid.uuid4()
        create_order_use_case.handle(
            CreateOrderCommand(order_id=order_id, street="Pushkina", volume=5)
        )

        # назначаем заказ на курьера
        assign_order_use_case: AssignOrderUseCase = AssignOrderUseCase(db)
        assign_order_use_case.handle(AssignOrderCommand())

        # двигаем курьера
        move_courier_use_case: MoveCouriersUseCase = MoveCouriersUseCase(db)
        move_courier_use_case.handle(MoveCouriersCommand())

        # TODO: доделать тесты, когда локации будут генериться неслучайно
