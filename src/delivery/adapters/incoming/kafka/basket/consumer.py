from fastapi import Depends
from faststream.kafka.fastapi import KafkaRouter

from src.delivery.core.application.use_cases.commands.create_order_command import (
    CreateOrderCommand,
    CreateOrderUseCase,
)

# from .schemas import BasketConfirmedEvent

# Инициализация брокера
router = KafkaRouter(bootstrap_servers="kafka:19092", include_in_schema=False)


@router.subscriber(
    "baskets.events",
    group_id="basket-confirmed-group",
)
async def process_basket_confirmed(
    # msg: BasketConfirmedEvent,
    msg,
) -> None:
    """
    Обработчик события подтверждения корзины.
    """
    use_case: CreateOrderUseCase = CreateOrderUseCase()
    await use_case.handle(
        CreateOrderCommand(
            order_id=msg.basket_id, street=msg.address.street, volume=msg.volume
        )

    )
