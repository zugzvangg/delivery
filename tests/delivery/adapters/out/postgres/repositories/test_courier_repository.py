import uuid

import pytest

from src.delivery.adapters.out.postgres.models.models import (
    CourierModel,
    StoragePlaceModel,
)
from src.delivery.adapters.out.postgres.repositories.courier_repository import (
    CourierRepository,
)
from src.delivery.core.domain.model.courier.courier import Courier
from src.delivery.core.domain.model.courier.storage_place import StoragePlace
from src.delivery.core.domain.model.location.location import Location


def test():
    assert 1 == 1


@pytest.mark.asyncio
async def test_storage_place_model_integration(db):
    # --- Arrange ---
    courier = Courier.create(
        name="Иван",
        speed=10,
        location=Location(5, 5),
    )

    courier_model = CourierModel.from_domain_object(courier)
    db.add(courier_model)
    await db.flush()

    # создаём storage_place в домене
    sp_domain = StoragePlace(
        name="Рюкзак", total_volume=20, id=uuid.uuid4(), occupied_volume=5
    )

    # создаём ORM модель
    sp_model = StoragePlaceModel.from_domain_object(sp_domain, courier_id=courier.id)
    db.add(sp_model)
    await db.commit()

    # --- Act ---
    loaded_sp: StoragePlaceModel = await db.get(StoragePlaceModel, sp_domain.id)
    restored_domain_sp = loaded_sp.to_domain_object()

    # --- Assert ---
    assert restored_domain_sp.id == sp_domain.id
    assert restored_domain_sp.name == "Рюкзак"
    assert restored_domain_sp.total_volume == 20  # --- Assert ---
    assert restored_domain_sp.id == sp_domain.id
    assert restored_domain_sp.name == "Рюкзак"
    assert restored_domain_sp.total_volume == 20
