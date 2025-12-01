from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    # раскладываем Location по отдельным полям согласно: https://platform.microarch.ru/pl/teach/control/lesson/view?id=343667792
    location_x: Mapped[int] = mapped_column(Integer)
    location_y: Mapped[int] = mapped_column(Integer)
    volume: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    courier_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("couriers.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    @classmethod
    def from_domain_object(cls, order: Order) -> "OrderModel":
        """Модель из доменного объекта."""
        return OrderModel(
            id=order.id,
            location_x=order.location.x,
            location_y=order.location.y,
            volume=order.volume,
            status=order.status.name,
            courier_id=order.courier_id,
        )

    def to_domain_object(self) -> Order:
        """Модель в доменный объект."""
        location = Location(x=self.location_x, y=self.location_y)
        order_status = OrderStatus(self.status)
        # Создаем экземпляр без вызова __init__
        order = Order(id=self.id, location=location, volume=self.volume)

        # NOTE: допустимо ли так делать? Если нет, то как, если атрибуты приватные?
        # Восстанавливаем состояние, эти атрибуты не можем менять
        order._Order__status = order_status
        order._Order__courier_id = self.courier_id

        return order
