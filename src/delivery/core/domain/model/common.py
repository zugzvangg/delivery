import uuid


class InvalidUUIDError(Exception):
    pass


def validate_uuid(id: uuid.UUID, id_name: str):
    """Может провалидировать и id, и order_id"""
    if not isinstance(id, uuid.UUID):
        raise InvalidUUIDError(f"{id_name} if must be of type uuid.UUID")
