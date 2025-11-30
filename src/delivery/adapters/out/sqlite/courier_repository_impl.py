import uuid
from typing import List, Optional

from src.delivery.adapters.out.sqlite.database import Database
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.ports.courier_repository import CourierRepository


class SQLiteCourierRepository(CourierRepository):
    def __init__(self, database: Database):
        self._db = database

    def add(self, courier: Courier) -> None:
        pass
        # courier_data, storage_data = CourierMapper.to_db(courier)

        # cursor = self._db.get_cursor()

        # # Добавляем курьера
        # cursor.execute("""
        #     INSERT INTO couriers (id, name, speed, location_x, location_y)
        #     VALUES (:id, :name, :speed, :location_x, :location_y)
        # """, courier_data)

        # # Добавляем места хранения
        # for storage in storage_data:
        #     cursor.execute("""
        #         INSERT INTO storage_places (id, courier_id, name, total_volume, order_id)
        #         VALUES (:id, :courier_id, :name, :total_volume, :order_id)
        #     """, storage)

    def update(self, courier: Courier) -> None:
        pass

    def get_by_id(self, courier_id: uuid.UUID) -> Optional[Courier]:
        pass

    def get_all_free(self) -> List[Courier]:
        pass
