import uuid


class InvalidUUIDError(Exception):
    pass


class WrongSerializationJsonError(Exception):
    pass


def validate_uuid(id: uuid.UUID, id_name: str):
    """Может провалидировать UUID, который много где нужен в проекте"""
    if not isinstance(id, uuid.UUID):
        raise InvalidUUIDError(f"{id_name} if must be of type uuid.UUID")
