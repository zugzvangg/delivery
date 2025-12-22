from fastapi import Depends
from faststream.kafka.fastapi import KafkaRouter

from api.db import get_session
from src.delivery.adapters.incoming.kafka.basket.shemas import BasketConfirmedEvent
from src.delivery.core.application.use_cases.commands.create_order_command import (
    CreateOrderCommand,
    CreateOrderUseCase,
)

router = KafkaRouter(bootstrap_servers="kafka:19092", include_in_schema=False)


@router.subscriber(
    "baskets.events",
    group_id="basket-confirmed-group",
)
def process_basket_confirmed(
    msg: BasketConfirmedEvent,
) -> None:
    """
    Обработчик события подтверждения корзины.
    """
    with get_session() as db:
        use_case: CreateOrderUseCase = CreateOrderUseCase(db)
        use_case.handle(
            CreateOrderCommand(
                order_id=msg.basket_id, street=msg.address.street, volume=msg.volume
            )
        )
