import uuid
from typing import List, Optional, Union

from fastapi import APIRouter, Body, Depends

from api.db import get_session
from api.http.schemas import CourierTest, Error, NewCourierTest, Order
from src.delivery.core.application.use_cases.commands.add_storage_place_command import (
    AddStoragePlaceCommand,
    AddStoragePlaceUseCase,
)
from src.delivery.core.application.use_cases.commands.create_courier_command import (
    CreateCourierCommand,
    CreateCourierUseCase,
)
from src.delivery.core.application.use_cases.commands.create_order_command import (
    CreateOrderCommand,
    CreateOrderUseCase,
)
from src.delivery.core.application.use_cases.queries.get_all_couriers_query import (
    GetAllCouriersQuery,
    GetAllCouriersUseCase,
)
from src.delivery.core.application.use_cases.queries.get_not_completed_orders_query import (
    GetNotCompletedOrdersQuery,
    GetNotCompletedOrdersUseCase,
)

router = APIRouter(prefix="/api/v1")


@router.post(
    "/couriers",
    response_model=None,
    responses={
        "default": {"model": Error},
        "400": {"model": Error},
        "409": {"model": Error},
    },
)
def create_courier(
    body: NewCourierTest = Body(),
) -> Optional[Error]:
    """
    Добавить курьера
    """
    command = CreateCourierCommand(
        name=body.name,
        speed=body.speed,
    )
    with get_session() as db:
        use_case: CreateCourierUseCase = CreateCourierUseCase(db)
        use_case.handle(command)


@router.get(
    "/couriers",
    response_model=List[CourierTest],
    responses={"default": {"model": Error}},
)
def get_couriers() -> Union[List[CourierTest], Error]:
    """
    Получить всех курьеров
    """
    query: GetAllCouriersQuery = GetAllCouriersQuery()
    with get_session() as db:
        use_case: GetAllCouriersUseCase = GetAllCouriersUseCase(db)
    return use_case.handle(query)


@router.post("/orders", response_model=None, responses={"default": {"model": Error}})
def create_order() -> Optional[Error]:
    """
    Создать заказ
    """
    command: CreateOrderCommand = CreateOrderCommand(
        order_id=uuid.uuid4(),
        street="test",
        volume=1,
    )
    with get_session() as db:
        use_case: CreateOrderUseCase = CreateOrderUseCase(db)
        use_case.handle(command)


@router.get(
    "/orders/active",
    response_model=List[Order],
    responses={"default": {"model": Error}},
)
def get_orders() -> Union[List[Order], Error]:
    """
    Получить все незавершенные заказы
    """
    query: GetNotCompletedOrdersQuery = GetNotCompletedOrdersQuery()
    with get_session() as db:
        use_case: GetNotCompletedOrdersUseCase = GetNotCompletedOrdersUseCase(db)
        use_case.handle(query)
