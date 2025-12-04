from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.domain.model.order.order import Order
from src.delivery.core.domain.model.order.order_status import OrderStatus

Base = declarative_base()


class CourierModel(Base):
    __tablename__ = "couriers"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    speed: Mapped[int] = mapped_column(Integer)
    location_x: Mapped[int] = mapped_column(Integer)
    location_y: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    storage_places: Mapped[list["StoragePlaceModel"]] = relationship(
        back_populates="courier",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="courier",
        lazy="selectin",
    )

    @classmethod
    def from_domain_object(cls, courier: Courier) -> "CourierModel":
        model = CourierModel(
            id=courier.id,
            name=courier.name,
            speed=courier.speed,
            location_x=courier.location.x,
            location_y=courier.location.y,
        )

        # Прикладываем storage_places
        model.storage_places = [
            StoragePlaceModel.from_domain_object(sp) for sp in courier.storage_places
        ]

        return model

    def to_domain_object(self) -> Courier:
        location = Location(self.location_x, self.location_y)

        courier = Courier(
            name=self.name,
            speed=self.speed,
            location=location,
        )

        # восстанавливаем id (перезаписываем приватное поле)
        # тут точно только так, так как по доменной модели у курьера всегда генерируется id
        courier._Courier__id = self.id

        # восстанавливаем storage_places
        # Но если не так, то как лучше сделать?
        # Через add_storage_place в цикле нельзя, так как там уже лежит объект
        courier._Courier__storage_places = [
            sp.to_domain_object() for sp in self.storage_places
        ]

        return courier


class StoragePlaceModel(Base):
    __tablename__ = "storage_places"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    total_volume: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("orders.id"), nullable=True
    )

    courier_id: Mapped[UUID] = mapped_column(ForeignKey("couriers.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    courier: Mapped["CourierModel"] = relationship(back_populates="storage_places")

    order: Mapped["OrderModel"] = relationship(
        back_populates="storage_place",
        lazy="joined",
    )

    # domain → ORM
    @classmethod
    def from_domain_object(cls, storage_place: StoragePlace) -> "StoragePlaceModel":

        return StoragePlaceModel(
            id=storage_place.id,
            name=storage_place.name,
            total_volume=storage_place.total_volume,
            order_id=storage_place.order_id,
            courier_id=storage_place.courier_id,
        )

    # ORM → domain
    def to_domain_object(self) -> StoragePlace:
        sp = StoragePlace(
            name=self.name,
            total_volume=self.total_volume,
            id=self.id,
            order_id=self.order_id,
            courier_id=self.courier_id,
        )
        return sp


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)

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

    courier: Mapped["CourierModel"] = relationship(back_populates="orders")

    storage_place: Mapped["StoragePlaceModel"] = relationship(
        back_populates="order",
        uselist=False,
    )

    # domain → ORM
    @classmethod
    def from_domain_object(cls, order: Order) -> "OrderModel":
        return OrderModel(
            id=order.id,
            location_x=order.location.x,
            location_y=order.location.y,
            volume=order.volume,
            status=order.status.name,
            courier_id=order.courier_id,
        )

    # ORM → domain
    def to_domain_object(self) -> Order:
        location = Location(self.location_x, self.location_y)
        order = Order(id=self.id, location=location, volume=self.volume)
        status = OrderStatus(self.status)
        if status == OrderStatus.CREATED:
            return order

        if status == OrderStatus.ASSIGNED:
            order.assign(self.courier_id)
            return order

        if status == OrderStatus.COMPLETED:
            order.assign(self.courier_id)
            order.complete()
            return order
