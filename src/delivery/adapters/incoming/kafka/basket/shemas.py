from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class Address(BaseModel):
    country: str
    city: str
    street: str
    house: str
    apartment: str


class Item(BaseModel):
    id: UUID
    goodId: str
    title: str
    price: Decimal
    quantity: int


class DeliveryPeriod(BaseModel):
    from_: int = Field(..., alias="from")
    to: int


class BasketConfirmedEvent(BaseModel):
    basket_id: UUID = Field(..., alias="basketId")
    address: Address
    items: List[Item]
    delivery_period: DeliveryPeriod = Field(..., alias="deliveryPeriod")
    volume: int

    class Config:
        # разрешаем создавать объект по alias
        allow_population_by_field_name = True
        # при генерации JSON будет camelCase
        alias_generator = lambda s: "".join(
            [s[0].lower()] + [c if c.islower() else f"{c}" for c in s[1:]]
        )
